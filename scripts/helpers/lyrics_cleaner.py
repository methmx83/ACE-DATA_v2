"""
Wrapper für die bestehende Lyrics-Bereinigung aus include/clean_lyrics.py.
Ziel: zentraler Aufrufpunkt, ohne die vorhandene Logik zu verändern.
"""

from shared_logs import log_message

try:
    from include.clean_lyrics import bereinige_datei as _clean_file
except Exception:
    _clean_file = None

def clean_lyrics_file(path: str) -> bool:
    """
    Bereinigt eine Lyrics-Datei (in-place). True bei Erfolg, sonst False.
    """
    if _clean_file is None:
        log_message("❓ include.clean_lyrics.bereinige_datei nicht gefunden")
        return False
    try:
        _clean_file(path)
        log_message(f"🧹 Lyrics bereinigt: {path}")
        return True
    except Exception as e:
        log_message(f"⚠️ Lyrics-Bereinigung fehlgeschlagen: {e}")
        return False