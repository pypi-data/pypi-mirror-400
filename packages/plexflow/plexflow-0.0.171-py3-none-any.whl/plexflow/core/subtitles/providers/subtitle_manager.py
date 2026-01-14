import os
import time
import yaml
import redis
import requests
import gzip
import re
from datetime import datetime, timedelta, timezone
from opensubtitlescom import OpenSubtitles
from plexflow.core.subtitles.providers.oss.oss_subtitle import OSSSubtitle
from typing import List, Tuple

class SubtitleManager:
    def __init__(self, yaml_path, redis_config, download_dir):
        self.yaml_path = yaml_path
        self.download_dir = os.path.abspath(download_dir)
        self.redis_config = redis_config
        self.r = None
        self.accounts = []
        self.current_ost = None
        self.current_user = None
        self.stats = {"new": 0, "redis_skip": 0, "local_skip": 0, "fail": 0, "dry_run_found": 0}
        
        self._initialize()

    def _initialize(self):
        os.makedirs(self.download_dir, exist_ok=True)
        self.r = redis.Redis(**self.redis_config, decode_responses=True)
        self.accounts = self._load_accounts()

    def _load_accounts(self):
        try:
            with open(self.yaml_path, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('items', [])
        except Exception:
            return []

    # --- PERFECTLY ALIGNED DASHBOARD ---
    def show_dashboard(self):
        total_dl = self.r.get("stats:total_downloads") or 0
        now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        
        w_user, w_stat, w_tok, w_ttl = 20, 12, 10, 12
        line_width = w_user + w_stat + w_tok + w_ttl + 11

        print(f"\n╔{'═' * line_width}╗")
        title = f" OSS ACCOUNT POOL | TOTAL DOWNLOADS: {total_dl} | {now_utc} "
        print(f"║{title.center(line_width)}║")
        print(f"╠{'═' * (w_user+2)}╤{'═' * (w_stat+2)}╤{'═' * (w_tok+2)}╤{'═' * (w_ttl+2)}╣")
        print(f"║ {'USERNAME':<{w_user}} │ {'STATUS':<{w_stat}} │ {'TOKEN':<{w_tok}} │ {'TTL REMAIN':<{w_ttl}} ║")
        print(f"╟{'─' * (w_user+2)}┼{'─' * (w_stat+2)}┼{'─' * (w_tok+2)}┼{'─' * (w_ttl+2)}╢")

        for item in self.accounts:
            user = item.get('login', {}).get('username', 'Unknown')
            block = self.r.get(f"quota_block:{user}")
            token = self.r.get(f"token:{user}")
            ttl_val = self.r.ttl(f"quota_block:{user}")

            if block == "403": s_icon, s_text = "🚫", "FORBIDDEN"
            elif block == "true": s_icon, s_text = "⏳", "EXHAUSTED"
            elif block == "login_fail": s_icon, s_text = "⚠️", "LOGIN ERR"
            else: s_icon, s_text = "✅", "READY"

            t_icon, t_text = ("🎫", "ACTIVE") if token else ("❌", "NONE")
            ttl_str = str(timedelta(seconds=ttl_val)) if ttl_val > 0 else "---"

            status_col = f"{s_icon} {s_text:<{w_stat-2}}"
            token_col  = f"{t_icon} {t_text:<{w_tok-2}}"
            print(f"║ {user:<{w_user}} │ {status_col} │ {token_col} │ {ttl_str:<{w_ttl}} ║")

        print(f"╚{'═' * (w_user+2)}╧{'═' * (w_stat+2)}╧{'═' * (w_tok+2)}╧{'═' * (w_ttl+2)}╝\n")

    def clear_cache(self, clear_history=False, clear_blocks=False, clear_tokens=False):
        print(f"\n[!] CACHE CLEANUP")
        if clear_history:
            keys = self.r.keys("history:sub:*")
            if keys: self.r.delete(*keys)
            print(f"    - Cleared history.")
        if clear_blocks:
            keys = self.r.keys("quota_block:*")
            if keys: self.r.delete(*keys)
            print(f"    - Cleared blocks.")
        if clear_tokens:
            keys = self.r.keys("token:*")
            if keys: self.r.delete(*keys)
            print(f"    - Cleared tokens.")
        print("[!] DONE\n")

    def _slugify(self, text):
        return re.sub(r'[^\w\s-]', '', str(text)).strip().replace(' ', '_')

    def _get_sub_attr(self, sub, attr_name, default=None):
        if hasattr(sub, 'attributes'): return getattr(sub.attributes, attr_name, default)
        return getattr(sub, attr_name, default)

    def _is_valid_srt(self, content):
        try:
            text = content.decode('utf-8', errors='ignore')
            return bool(re.search(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', text))
        except: return False

    def _get_ttl_until_reset(self):
        now = datetime.now(timezone.utc)
        reset_time = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int((reset_time - now).total_seconds())

    def block_current_account(self, reason="true", duration=None):
        if self.current_user:
            ttl = duration if duration else self._get_ttl_until_reset()
            self.r.set(f"quota_block:{self.current_user}", reason, ex=ttl)
            self.r.delete(f"token:{self.current_user}") 
            print(f"!!! Account {self.current_user} exhausted. Blocked for {ttl}s.")
            self.current_ost = None
            self.current_user = None

    def refresh_session(self):
        for item in self.accounts:
            login = item.get('login', {})
            user = login.get('username')
            if not user or self.r.exists(f"quota_block:{user}"): continue
            fields = {f['name']: f['value'] for f in item.get('fields', [])}
            try:
                ost = OpenSubtitles(fields.get('User Agent'), fields.get('API Key'))
                cached_token = self.r.get(f"token:{user}")
                if cached_token:
                    ost.token = cached_token
                    print(f"--- Session: Reusing cached token for {user}")
                else:
                    time.sleep(1.5)
                    print(f"--- Session: Authenticating {user}...")
                    ost.login(user, login.get('password'))
                    self.r.set(f"token:{user}", ost.token, ex=86400)
                self.current_ost, self.current_user = ost, user
                return True
            except Exception as e:
                if "429" in str(e): time.sleep(5)
                elif "403" in str(e): self.r.set(f"quota_block:{user}", "403", ex=86400)
                else: self.block_current_account(reason="login_fail", duration=3600)
        return False

    def download_subtitles(self, imdb_id=None, query=None, languages="en", min_rating=0.0, dry_run=False) -> List[Tuple[OSSSubtitle, str]]:
        self.stats = {"new": 0, "redis_skip": 0, "local_skip": 0, "fail": 0, "dry_run_found": 0}
        
        if dry_run:
            print(f"\n{'!'*15} DRY RUN ENABLED {'!'*15}")
            print("[?] Search will occur, but no downloads will be triggered.")

        if not self.current_ost and not self.refresh_session():
            print("No accounts available.")
            return

        try:
            params = {"languages": languages}
            if imdb_id: params["imdb_id"] = imdb_id
            if query: params["query"] = query
            
            response = self.current_ost.search(**params)
            subs = getattr(response, 'data', [])
            print(f"\n>>> Search Results: {len(subs)} subtitles found.")

            subtitle_items = []

            for sub in subs:
                sub_id = str(sub.id)
                rating = self._get_sub_attr(sub, 'ratings', 0.0)
                hi = self._get_sub_attr(sub, 'hearing_impaired', False)
                release = self._get_sub_attr(sub, 'release', f"sub_{sub_id}")

                hi_suffix = ".HI" if hi else ""
                file_name = f"{self._slugify(release)}_{sub_id}{hi_suffix}.srt"
                file_path = os.path.join(self.download_dir, file_name)

                subtitle_items.append((OSSSubtitle(sub), file_path))

                if (rating or 0) < min_rating: continue

                if self.r.exists(f"history:sub:{sub_id}"):
                    print(f"[-] SKIP: Subtitle {sub_id} found in Redis Global History.")
                    self.stats["redis_skip"] += 1
                    continue

                if os.path.exists(file_path):
                    print(f"[-] SKIP: Subtitle {sub_id} exists at: {file_path}. Updating Redis.")
                    self.r.set(f"history:sub:{sub_id}", "done")
                    self.stats["local_skip"] += 1
                    continue

                if dry_run:
                    print(f"[*] DRY RUN: Would download {sub_id} ({release})")
                    self.stats["dry_run_found"] += 1
                    continue

                attempts = 0
                while attempts < 3:
                    try:
                        time.sleep(1.2)
                        print(f"[+] START: [{self.current_user}] Downloading ID {sub_id}...")
                        result = self.current_ost.download(sub)
                        raw = result if isinstance(result, bytes) else requests.get(result.link).content
                        if raw.startswith(b'\x1f\x8b'): raw = gzip.decompress(raw)

                        if self._is_valid_srt(raw):
                            with open(file_path, "wb") as f: f.write(raw)
                            self.r.set(f"history:sub:{sub_id}", "done")
                            self.r.incr("stats:total_downloads")
                            print(f"[✓] SUCCESS: Saved as {file_name}")
                            self.stats["new"] += 1
                            attempts = 3
                        else:
                            print(f"[!] FAILED: Invalid SRT content for {sub_id}.")
                            self.stats["fail"] += 1
                            break
                    except Exception as e:
                        if any(x in str(e).lower() for x in ["406", "limit", "quota"]):
                            self.block_current_account()
                            if not self.refresh_session(): return
                            attempts += 1
                        else:
                            print(f"[!] ERROR: {sub_id} -> {e}")
                            self.stats["fail"] += 1
                            break

            print(f"\n{'='*30}\nRUN SUMMARY\n{'='*30}")
            if dry_run:
                print(f"Potential New:  {self.stats['dry_run_found']}")
            else:
                print(f"New Downloads:  {self.stats['new']}")
            print(f"Global Skips:   {self.stats['redis_skip']}")
            print(f"Local Skips:    {self.stats['local_skip']}")
            print(f"Errors/Failed:  {self.stats['fail']}")
            print(f"{'='*30}\n")

            return subtitle_items

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    R_VARS = {'host': 'localhost', 'port': 6379, 'db': 0}
    YAML_PATH = "/Users/david/code/plexflow/config/credentials.yaml"
    DL_DIR = "/Users/david/Downloads/subs"

    manager = SubtitleManager(YAML_PATH, R_VARS, DL_DIR)
    manager.show_dashboard()
    
    # Set dry_run=True to test without downloading
    items = manager.download_subtitles(imdb_id="tt29567915", languages="nl", dry_run=True)

    for subtitle, path in items:
        print(subtitle.date, path)