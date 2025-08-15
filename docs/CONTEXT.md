# Projektkontext (Snapshot)

Dieser Snapshot hält den aktuellen Stand fest, damit neue Diskussionen/Chats ohne alte Historie direkt loslegen können.

## Repository
- Repo: https://github.com/methmx83/ACE-DATA_v2
- Branch: main
- Commit: 9219c64

## Systemumgebung
- OS: Windows 10 Pro
- GPU/VRAM: RTX 4070 Super (12 GB VRAM)
- CPU/RAM: Intel i9-14900K / 64 GB RAM
- CUDA: 12.9
- Python: 3.11 (Conda env: ace-data_v2_env)

## Aktuelle Konfiguration (`config/config.json`)
```json
{
  "input_dir": "data/audio",
  "hf_model_path": "Z:/AI/projects/.models/generative/mufun",
  "use_audio": true,
  "audio_max_seconds": 45,
  "downsample_hz": 16000,
  "empty_cache_between_files": true,
  "debug": true,
  "gen_max_new_tokens": 64,
  "gen_temperature": 0.2,
  "gen_top_p": 0.9,
  "gen_repetition_penalty": 1.1
}
```

## Relevante Dateien
- `scripts/tagger.py`: Tag-Generierung mit MuFun (HF). Lazy Loading, chat→generate Fallback, Limits.
- `include/mufun_loader.py`: Lädt MuFun (4‑bit, BitsAndBytes wenn verfügbar; sonst Fallback), eval(), pad_token fix.
- `scripts/helpers/bpm.py`: Robuste BPM-Erkennung.
- `scripts/lyrics.py`: Lyrics laden (Scrape/Datei); Cleaning über `include/clean_lyrics.py`.
- `scripts/moods.py`: `extract_clean_tags()` – Normalisierung, Formatregeln, Duplikate.
- `webui/app.py`: Minimaler UI-Flow.

## Problemfokus (aktuell)
- Beobachtung: Tags wirken teils wie Beispiel-/Preset-Tags, zu geringe Diversität.
- Hypothese: Model-Output nicht streng genug geparst; Beispiele im Prompt werden „kopiert“; Audio wird nicht immer berücksichtigt.

## Reproduktion
1. Lege 2–3 MP3s nach `data/audio/`.
2. Starte WebUI und führe Tagging aus.
3. Prüfe `_prompt.txt` und Logs.

## Zu erfassende Belege
- RAW-Model-Output (erste 400–800 Zeichen) vor dem Parsen.
- Finale Tags nach `extract_clean_tags()`.
- BPM-Wert und ob `bpm-XXX` an Position 0 steht.

## Zielbild
- Vielfältige, präzise Tags (lowercase-hyphenated, max. 2 Genres), Audio- & Lyrics-basiert.
- Kein „Kopieren“ von Beispiel-Listen; minimale Duplikate/Generika.

## Offene Entscheidungen
- Striktes JSON-Output erzwingen ("tags": [..])?
- Few-Shot-Beispiele im Prompt beibehalten oder entfernen?
- Audio-Zeitfenster (audio_max_seconds) reduzieren/erhöhen?

## Nächste Schritte (Vorschlag)
- Prompt schärfen, Beispiele kommentieren oder entfernen.
- `extract_clean_tags()` strenger machen (Genre-Limit, Stoppwörter, Mindestkategorien).
- Optional: RAW-Log in `shared_logs` aufnehmen (Debug-Schalter).
