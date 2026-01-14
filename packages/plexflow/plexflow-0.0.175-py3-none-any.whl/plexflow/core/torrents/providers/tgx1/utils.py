from datetime import datetime
from plexflow.core.torrents.results.torrent import Torrent
from plexflow.utils.imdb.imdb_codes import IMDbCode
import re
import unicodedata

def slugify(text: str) -> str:
    """
    Transforms a media string into a clean, URL-friendly slug.
    Example: "Bugonia (2025) [1080p] [eng]" -> "bugonia-2025-1080p-eng"
    """
    if not text:
        return ""

    # 1. Normalize Unicode characters (e.g., 'é' becomes 'e')
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

    # 2. Lowercase the string
    text = text.lower()

    # 3. Replace any non-alphanumeric character (brackets, parens, dots) with a hyphen
    # This handles [1080p], (2025), and file.name.style
    text = re.sub(r'[^a-z0-9]+', '-', text)

    # 4. Strip leading/trailing hyphens and reduce multiple hyphens (---) to one (-)
    text = text.strip('-')
    text = re.sub(r'-+', '-', text)

    return text

class TGX1SearchResult(Torrent):
    """
        {
            'pk': '813ba6', 
            'n': 'Bugonia (2025) [1080p] [eng]', 
            'a': 1764864908, 
            'c': 'Movies', 
            's': 3205694470, 
            't': None, 
            'u': 'miok', 
            'se': 191, 
            'le': 40, 
            'i': 'tt12300742', 
            'h': 'ADF0A608D8F9F3EEA6318032075391B4869B0A54', 
            'tg': ['English', '1080p']
        }
    """
    def __init__(self, **kwargs):
        super().__init__()
        self._id = kwargs.get("pk")
        self._hash = kwargs.get("h")
        self._type = kwargs.get("c")
        self._seeds = kwargs.get("se")
        self._peers = kwargs.get("le")
        self._size_bytes = kwargs.get("s")
        self._name = kwargs.get("n")
        self._imdb_code = kwargs.get("i")
        self._date_uploaded_unix = kwargs.get("a")
        self.src = "tgx1"

    @property
    def id(self) -> str:
        return self._id
    
    @property
    def url(self) -> str:
        return f'https://torrentgalaxy.one/post-detail/{self._id}/{slugify(self._name)}/'

    @property
    def magnet(self) -> str:
        return f'magnet:?xt=urn:btih:{self._hash}&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.srv00.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.therarbg.to%3A6969%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker1.myporn.club%3A9337%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.demonoid.ch%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.demonii.com%3A1337%2Fannounce&tr=udp%3A%2F%2Fwepzone.net%3A6969%2Fannounce'

    @property
    def date(self) -> datetime:
        return datetime.fromtimestamp(int(self._date_uploaded_unix))

    @property
    def seeds(self) -> int:
        return self._seeds

    @property
    def peers(self) -> int:
        return self._peers

    @property
    def size_bytes(self) -> int:
        return self._size_bytes

    @property
    def imdb_code(self) -> IMDbCode:
        return IMDbCode(self._imdb_code)

    @property
    def release_name(self) -> str:
        return self._name

    @property
    def hash(self) -> str:
        return self._hash

