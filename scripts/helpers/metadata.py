"""
Einfacher Helfer zum Lesen von Audiometadaten (Artist/Title/Album).
Individuelle Logik bleibt in den Skripten; hier nur sauberes Auslesen + Log.
"""

from tinytag import TinyTag
from shared_logs import log_message

def get_audio_metadata(file_path: str) -> dict:
    """
    Gibt {'title', 'artist', 'album'} zurück (Fallbacks bei fehlenden Tags).
    """
    try:
        tag = TinyTag.get(file_path)
        title = tag.title or 'Unknown Title'
        artist = tag.artist or 'Unknown Artist'
        album = tag.album or 'Unknown Album'
        log_message(f"🎵 [Tinytag] Title={title}, Artist={artist}")
        return {'title': title, 'artist': artist, 'album': album}
    except Exception as e:
        log_message(f"⚠️ Metadata error: {e}")
        return {'title': '', 'artist': '', 'album': ''}