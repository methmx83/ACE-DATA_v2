"""
Wrapper für die BPM-Ermittlung. Bevorzugt dein neues bpm_librosa.detect_tempo.
"""

from shared_logs import log_message

try:
    from scripts.bpm_librosa import detect_tempo as _detect_tempo
except Exception:
    _detect_tempo = None

def detect_tempo(file_path: str) -> int | None:
    """
    Liefert BPM als int oder None. Rundet defensiv.
    """
    if _detect_tempo is None:
        log_message("❓ scripts.bpm_librosa.detect_tempo nicht gefunden")
        return None
    try:
        bpm = _detect_tempo(file_path)
        return int(round(float(bpm))) if bpm is not None else None
    except Exception as e:
        log_message(f"⚠️ BPM-Ermittlung fehlgeschlagen: {e}")
        return None