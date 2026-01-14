import os
import re
import sys
import shutil
import stable_whisper
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from tqdm import tqdm
from typing import List, Optional
from contextlib import contextmanager

# ==========================================
# HELPER: SILENCE OUTPUT
# ==========================================

@contextmanager
def suppress_stdout():
    """
    Context manager to temporarily silence stdout.
    Used to stop stable_whisper from printing 'Saved...' and breaking the progress bar.
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

# ==========================================
# MODULE 1: TRANSCRIBER
# ==========================================

class AudioTranscriber:
    def __init__(self, model_size="medium", device="cpu", compute_type="int8", threads=8):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.threads = threads
        self.model = None

    def _load_model(self):
        if self.model is None:
            print(f"🔹 Loading Whisper model ({self.model_size}) on {self.device}...")
            self.model = stable_whisper.load_faster_whisper(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=self.threads
            )

    def transcribe(self, audio_path: str, cache_path: Optional[str] = None) -> stable_whisper.WhisperResult:
        if cache_path and os.path.exists(cache_path):
            print(f"✅ Found cached transcription: {cache_path}")
            return stable_whisper.WhisperResult(cache_path)

        self._load_model()
        print(f"🎙️  Transcribing {os.path.basename(audio_path)}...")
        
        result = self.model.transcribe_stable(
            audio_path,
            beam_size=5,
            vad=True,
            regroup=True
        )

        if cache_path:
            # We suppress stdout here too just to be consistent
            with suppress_stdout():
                result.save_as_json(cache_path)
            print(f"💾 Saved transcription cache to {cache_path}")
        
        return result

    @staticmethod
    def refine_segments(result: stable_whisper.WhisperResult):
        print("🔧 Refining segments (Merge & Split)...")
        result.merge_by_gap(0.5)
        result.split_by_punctuation(['.', '?', '!', '...'])
        result.split_by_length(max_chars=42)
        return result


# ==========================================
# MODULE 2: TRANSLATOR
# ==========================================

class NeuralTranslator:
    def __init__(self, model_name="facebook/nllb-200-distilled-600M", src_lang="eng_Latn", tgt_lang="nld_Latn", device=-1):
        self.model_name = model_name
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.device = device
        self.pipe = None

    def _load_pipeline(self):
        if self.pipe is None:
            print(f"🔹 Loading Translation model ({self.model_name})...")
            # Suppress loading logs from transformers if desired
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.pipe = pipeline(
                "translation",
                model=self.model,
                tokenizer=self.tokenizer,
                src_lang=self.src_lang,
                tgt_lang=self.tgt_lang,
                device=self.device
            )

    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'([.!?])([a-zA-Z])', r'\1 \2', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def distribute_text_by_duration(full_text: str, durations: List[float]) -> List[str]:
        words = full_text.split()
        total_duration = sum(durations)
        chunks = []
        current_word_idx = 0
        
        for i, duration in enumerate(durations):
            if i == len(durations) - 1:
                chunks.append(" ".join(words[current_word_idx:]))
                break
            
            percent = duration / total_duration if total_duration > 0 else 0
            target_word_count = int(len(words) * percent)
            
            if target_word_count == 0 and duration > 0.2 and current_word_idx < len(words):
                target_word_count = 1
                
            end_idx = current_word_idx + target_word_count
            chunks.append(" ".join(words[current_word_idx:end_idx]))
            current_word_idx = end_idx
            
        return chunks

    def _overwrite_segment(self, segment, new_text):
        if not segment.words:
            return

        template_word = segment.words[0]
        if isinstance(template_word, dict):
            template_word['word'] = new_text
            template_word['start'] = segment.start
            template_word['end'] = segment.end
            segment.words = [template_word]
        else:
            template_word.word = new_text
            template_word.start = segment.start
            template_word.end = segment.end
            if hasattr(template_word, 'tokens'):
                template_word.tokens = [] 
            segment.words = [template_word]

    def translate_whisper_result(self, result: stable_whisper.WhisperResult, checkpoint_path: str, progress_path: str, start_index: int = -1):
        self._load_pipeline()
        print(f"🔄 Resuming translation from segment index: {start_index + 1}")

        buffer_indices = []
        buffer_text = []
        buffer_durations = []
        
        save_counter = 0
        SAVE_FREQ = 5 
        
        total_segments = len(result.segments)
        
        # TQDM Configuration for cleaner output
        pbar = tqdm(
            total=total_segments, 
            initial=start_index + 1, 
            desc="Translating", 
            unit="seg",
            ncols=100, # Fixed width to prevent wrapping
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}"
        )

        for i, segment in enumerate(result.segments):
            if i <= start_index:
                continue

            text = segment.text.strip()
            buffer_indices.append(i)
            buffer_text.append(text)
            buffer_durations.append(segment.end - segment.start)

            is_end_of_sentence = text.endswith(('.', '?', '!', '...'))
            is_last_segment = (i == total_segments - 1)
            
            pbar.update(1)

            if is_end_of_sentence or is_last_segment:
                full_eng_sentence = " ".join(buffer_text)
                
                if full_eng_sentence.strip():
                    try:
                        output = self.pipe(full_eng_sentence, max_length=512)
                        raw_translated = output[0]['translation_text']
                        cleaned_translated = self.clean_text(raw_translated)
                        
                        split_translated = self.distribute_text_by_duration(cleaned_translated, buffer_durations)
                        
                        last_processed_idx = -1
                        
                        for j, idx in enumerate(buffer_indices):
                            if j < len(split_translated):
                                self._overwrite_segment(result.segments[idx], split_translated[j])
                            else:
                                self._overwrite_segment(result.segments[idx], "")
                            last_processed_idx = idx
                        
                        save_counter += 1
                        if save_counter >= SAVE_FREQ or is_last_segment:
                            # 1. Update postfix to show status
                            pbar.set_postfix_str("Saving...", refresh=True)
                            
                            # 2. Suppress the 'Saved: ...' print output from stable_whisper
                            with suppress_stdout():
                                result.save_as_json(checkpoint_path)
                            
                            with open(progress_path, 'w') as f:
                                f.write(str(last_processed_idx))
                                
                            # 3. Clear status or show 'Saved'
                            pbar.set_postfix_str("Saved", refresh=True)
                            save_counter = 0

                    except Exception as e:
                        pbar.write(f"\n⚠️ Error segment {i}: {e}") # Use pbar.write instead of print
                        with suppress_stdout():
                            result.save_as_json(checkpoint_path)
                        raise e

                buffer_indices = []
                buffer_text = []
                buffer_durations = []

        pbar.close()
        if os.path.exists(progress_path):
            os.remove(progress_path)


# ==========================================
# MODULE 3: PIPELINE ORCHESTRATOR
# ==========================================

class SubtitlePipeline:
    def __init__(self, 
                 src_lang="eng_Latn", 
                 tgt_lang="nld_Latn", 
                 model_size="medium",
                 translation_model="facebook/nllb-200-distilled-600M"):
        
        self.transcriber = AudioTranscriber(model_size=model_size)
        self.translator = NeuralTranslator(
            model_name=translation_model,
            src_lang=src_lang,
            tgt_lang=tgt_lang
        )

    def run(self, audio_path: str, output_srt_path: str):
        base_path = os.path.splitext(audio_path)[0]
        
        paths = {
            "source_audio": audio_path,
            "cache_en": base_path + ".stable_cache.json",
            "checkpoint_tl": base_path + ".translated_checkpoint.json",
            "progress_tl": base_path + ".translation_progress.txt",
            "output_srt": output_srt_path
        }

        result = None
        start_index = -1

        if os.path.exists(paths["checkpoint_tl"]) and os.path.exists(paths["progress_tl"]):
            print(f"🚀 Resuming from checkpoint: {paths['checkpoint_tl']}")
            try:
                with open(paths["progress_tl"], 'r') as f:
                    content = f.read().strip()
                    start_index = int(content) if content else -1
                result = stable_whisper.WhisperResult(paths["checkpoint_tl"])
            except Exception as e:
                print(f"⚠️ Checkpoint corrupted ({e}). Restarting translation.")
                start_index = -1

        if start_index == -1:
            # Note: We silence the save print here too via the Transcriber class update above
            if os.path.exists(paths["cache_en"]):
                result = self.transcriber.transcribe(paths["source_audio"], paths["cache_en"])
            else:
                result = self.transcriber.transcribe(paths["source_audio"], paths["cache_en"])
            
            result = self.transcriber.refine_segments(result)

            print(f"📝 Initializing translation checkpoint...")
            with suppress_stdout():
                result.save_as_json(paths["checkpoint_tl"])
            with open(paths["progress_tl"], 'w') as f:
                f.write("-1")

        self.translator.translate_whisper_result(
            result, 
            checkpoint_path=paths["checkpoint_tl"], 
            progress_path=paths["progress_tl"],
            start_index=start_index
        )

        print(f"✅ Saving final subtitles to {paths['output_srt']}...")
        result.to_srt_vtt(paths['output_srt'], word_level=False, min_dur=0.5)

if __name__ == "__main__":
    pipeline_runner = SubtitlePipeline(
        src_lang="eng_Latn",
        tgt_lang="nld_Latn",
        model_size="medium"
    )

    pipeline_runner.run(
        audio_path="/Users/david/code/plexflow/data/audio/output - sponge.wav",
        output_srt_path="/Users/david/code/plexflow/data/audio/output.srt"
    )