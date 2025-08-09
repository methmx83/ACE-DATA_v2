import numpy as np
import librosa
from librosa.feature import rhythm
import re
import os
import sys
from shared_logs import LOGS, log_message
from scripts.bpm_librosa import detect_bpm_librosa as _detect_bpm

    # Main message when loading the file
log_message("... BPM calculation Script loaded ✅")

def detect_tempo(file_path):
    try:
        bpm = _detect_bpm(file_path)  # nutzt dein neues bpm_librosa
        return round(float(bpm)) if bpm is not None else None  # vorher: int(bpm)
    except Exception as e:
        log_message(f"⚠️ Tempo detection error: {str(e)}")
        # Fallback: BPM aus Dateinamen lesen (bpm-120 oder bpm_120)
        match = re.search(r'bpm[_-]?(\d{2,3})', os.path.basename(file_path), re.IGNORECASE)
        return int(match.group(1)) if match else None

def adjust_bpm(tempo):
    """Adjusts BPM values to ensure they are within a reasonable range."""
    if tempo is None or tempo <= 0:
        log_message("⚠️ Invalid BPM value: adjustment not possible")
        return None

    temp = float(tempo)

    # Wenn BPM über 140 liegt, halbiere den Wert (keine Floor-Division)
    while temp > 140:
        temp /= 2.0
    # Wenn BPM unter 60 liegt, verdopple den Wert
    while temp < 60:
        temp *= 2
    return int(round(temp))

def get_bpm(file_path):
    detected_tempo = detect_tempo(file_path)
    adjusted_bpm = adjust_bpm(detected_tempo)
    
    # Ausgabe der Nachricht nach der BPM-Berechnung
    log_message(f"✅ BPM calculated for {file_path}: {adjusted_bpm}")
    
    return adjusted_bpm
