import subprocess
from pathlib import Path
from typing import List, Optional
import re
import json
from typing import Tuple
from typing import List, Optional, Union


class FFmpegError(Exception):
    """Custom exception for FFmpeg errors."""
    pass

def extract_audio_from_video(
    video_path: Path, 
    output_dir: Path, 
    stream_indices: Optional[List[int]] = None, 
    sample_rate: Optional[int] = None,
    start_time: Union[str, int] = "00:00:00",
    end_time: Optional[Union[str, int]] = None,
    mono: bool = True,
    optimize_for_whisper: bool = False,
    output_format: str = "mp3"  # <--- New Parameter (options: "mp3", "wav")
) -> List[Path]:
    """
    Extracts audio streams from a video file using absolute ffprobe indices.
    
    Args:
        output_format: "mp3" or "wav". 
                       If "wav", the file size/bitrate limits are ignored to prevent truncation.
    """
    if isinstance(video_path, str):
        video_path = Path(video_path)
    
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)

    if not video_path.exists():
        raise FileNotFoundError(f"The video file {video_path} does not exist.")
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # --- Whisper Optimization ---
    if optimize_for_whisper:
        if sample_rate is None:
            sample_rate = 16000
        mono = True
    # ----------------------------

    if stream_indices is None:
        stream_indices = get_audio_stream_indices(video_path)

    audio_files = []
    
    # Normalize format string
    fmt = output_format.lower().strip().lstrip('.')
    if fmt not in ['mp3', 'wav']:
        raise ValueError("output_format must be 'mp3' or 'wav'")

    for index in stream_indices:
        output_file = output_dir / f'audio_stream_{index}.{fmt}'
        
        command = ['ffmpeg', '-y']
        
        if start_time:
            command.extend(['-ss', str(start_time)])
        if end_time:
            command.extend(['-to', str(end_time)])
            
        command.extend(['-i', str(video_path)])
        
        # Absolute stream mapping
        command.extend([
            '-map', f'0:{index}',     
            '-vn'
        ])
        
        # --- Codec & Format Logic ---
        if fmt == 'wav':
            # PCM 16-bit LE (Standard WAV)
            # We do NOT add -fs 18M or -b:a 160k here because WAV is uncompressed.
            # Adding a size limit to WAV would likely truncate valid audio.
            command.extend(['-c:a', 'pcm_s16le'])
        else:
            # MP3 Logic
            command.extend([
                '-c:a', 'libmp3lame',     
                '-b:a', '160k',           
                '-fs', '18M'  # Absolute file size limit safety for MP3
            ])
        # ----------------------------

        if mono:
            command.extend(['-ac', '1'])
        
        if sample_rate:
            command.extend(['-ar', str(sample_rate)])
            
        command.append(str(output_file))
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg error: {e.stderr.decode()}")
        
        audio_files.append(output_file)
    
    return audio_files


def get_audio_stream_indices(video_path: Path) -> List[int]:
    """
    Retrieves the indices of audio streams in a video file using ffmpeg.

    Parameters:
    - video_path (Path): Path to the input video file.

    Returns:
    - List[int]: List of audio stream indices.

    Raises:
    - FileNotFoundError: If the video file does not exist.
    - FFmpegError: If ffmpeg encounters an error during processing.
    """
    if isinstance(video_path, str):
        video_path = Path(video_path)

    if not video_path.exists():
        raise FileNotFoundError(f"The video file {video_path} does not exist.")
    
    command = ['ffmpeg', '-i', str(video_path)]
    
    try:
        result = subprocess.run(command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise FFmpegError(f"FFmpeg error: {e.stderr.decode()}")
    
    stderr_output = result.stderr.decode()
    audio_indices = []
    
    for line in stderr_output.splitlines():
        if 'Stream #' in line and 'Audio:' in line:
            # Extract the stream index using a regular expression
            match = re.search(r'Stream #0:(\d+)', line)
            if match:
                stream_index = int(match.group(1))
                audio_indices.append(stream_index)
    
    return audio_indices

def get_audio_stream_info(video_path: Path) -> List[Tuple[int, Optional[str]]]:
    """
    Retrieves the indices and language tags of audio streams in a video file using ffprobe.

    Parameters:
    - video_path (Path): Path to the input video file.

    Returns:
    - List[Tuple[int, Optional[str]]]: A list of tuples, where each tuple contains
      (stream_index, language_code). language_code will be None if not found.

    Raises:
    - FileNotFoundError: If the video file does not exist.
    - FFmpegError: If ffprobe encounters an error during processing or JSON parsing.
    """
    if isinstance(video_path, str):
        video_path = Path(video_path)
        
    if not video_path.exists():
        raise FileNotFoundError(f"The video file {video_path} does not exist.")
    
    command = [
        'ffprobe',
        '-v', 'error',                 # Suppress verbose output
        '-select_streams', 'a',        # Select only audio streams
        '-show_entries', 'stream=index:stream_tags=language', # Show index and language tag
        '-of', 'json',                 # Output in JSON format
        str(video_path)
    ]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        audio_stream_info = []
        for s in data.get('streams', []):
            index = s.get('index')
            language = s.get('tags', {}).get('language')
            if index is not None:
                audio_stream_info.append((index, language))
        return audio_stream_info
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        raise FFmpegError(f"FFprobe error: {e.stderr if isinstance(e, subprocess.CalledProcessError) else e}")
