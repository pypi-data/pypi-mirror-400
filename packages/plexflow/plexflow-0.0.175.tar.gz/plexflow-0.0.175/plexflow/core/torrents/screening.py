import json
import time
from plexflow.core.torrents.auto.auto_torrents import AutoTorrents
from tqdm import tqdm
import os
from mistralai import Mistral
import random

def screen_torrents_batch(expected_title: str, expected_year: int, expected_season: int, expected_episode: int, torrents: list[str]):
    all_results = []
    batch_size = 20
    max_retries = 5

    # 1. Initialize the client
    # It's best practice to use an environment variable for your key
    api_key = os.environ.get("MISTRAL_API_KEY") 
    client = Mistral(api_key=api_key)

    # 2. Define the model
    # Examples: "mistral-large-latest", "mistral-small-latest", "open-mistral-nemo"
    model = "mistral-large-latest"

    for i in tqdm(range(0, len(torrents), batch_size)):
        batch = torrents[i : i + batch_size]
        
        prompt = f"""
        For each of the following torrent release names, indicate whether it is expected to be a bad quality release based solely on the information available in the name. If there are indications of the languages of the release, also include them in the JSON format as a two letter ISO language code. Always answer with the following JSON format:

        {{"torrents": [
            {{"name": "TORRENT_RELEASE_NAME", "bad_quality": "BOOL", "reason": "WHY_IT_IS_BAD_QUALITY_OR_NOT", "languages": ["TWO_LETTER_LANGUAGE_CODES"], "title_match": "TITLE_MATCHES_EXPECTED_TITLE", "season_match": "SEASON_MATCHES_EXPECTED_SEASON", "episode_match": "EPISODE_MATCHES_EXPECTED_EPISODE"}},
        ...
        ]}}

        In determining whether a release is bad quality, you will NEVER consider the following elements:
        - resolution
        - subtitles
        - colorized versions
        - title
        - year
        - release group
        - re-encodes
        - unknown sources

        re-encodes or lower resolutions are still good quality.

        You will only look at the release quality, like CAM, TS, HDTS, WEBSCREENER, ...

        Expected title: {expected_title}
        Expected season: {expected_season if expected_season is not None else "n/a"}
        Expected episode: {expected_episode if expected_episode is not None else "n/a"}

        Torrents:
        {'\n'.join(batch)}
        """

        success = False
        attempt = 0
        
        while not success and attempt < max_retries:
            try:
                # 3. Call the API
                completion = client.chat.complete(
                    model=model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You are a media metadata parser. Always return valid JSON arrays."},
                        {"role": "user", "content": prompt},
                    ],
                )

                batch_data = json.loads(completion.choices[0].message.content)
                
                # Extract list from dictionary if needed
                if isinstance(batch_data, dict):
                    for key in batch_data:
                        if isinstance(batch_data[key], list):
                            all_results.extend(batch_data[key])
                            break
                else:
                    all_results.extend(batch_data)
                
                success = True # Exit the retry loop

            except Exception as e:
                attempt += 1
                print(f"\nError processing batch {i//batch_size + 1} (Attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    time.sleep(random.randint(1, 5) * attempt) # Exponential-ish backoff
                else:
                    print(f"Skipping batch starting at index {i} after {max_retries} failed attempts.")

    return all_results

if __name__ == "__main__":
    expected_title = "Faster"
    expected_year = 2004
    expected_season = None
    expected_episode = None
    imdb_id = 'tt0368721'

    # Fetch torrents
    torrents_data = AutoTorrents.movie(imdb_id=imdb_id, query=f"{expected_title} {expected_year}", source="tgx1", headless=True)
    
    names = [t.release_name for t in torrents_data]
    print(f"Processing {len(names)} torrents in batches of {20}...")

    results = screen_torrents_batch(expected_title, expected_year, expected_season, expected_episode, names)

    print(f"\nSuccessfully processed {len(results)} results.")
    print(json.dumps(results, indent=2))