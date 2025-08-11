<h1 align="center">🎵 ACE-Step Data-Tool</h1>
<p align="center">
  <strong>Automated tool for building music datasets compatible with ACE-Step</strong><br>
  <em>Extracts lyrics, tags & BPM from audio files – fully local with Ollama & Gradio</em>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/methmx83/ace-data_tool?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Content-License--CC--BY--NC--4.0-lightgrey.svg" alt="CC BY-NC 4.0">
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Ollama-Compatible-blue" alt="Ollama compatible">
</p>

<p align="center">
  <img src="./docs/Screenshot.png" alt="ACE-Step Data Tool Screenshot" width="100%">
</p>



## ✨ Features

- 🎙️ **Lyric Detection** – automatically via Genius.com
- 🧠 **LLM-powered Tag Generator** (genre, mood, bpm, vocals, style)
- 🕺 **BPM Analysis** via Librosa
- 🖥️ **Modern WebUI** with mood slider, genre presets & custom prompt field
- 🗂️ **Export to ACE-Step training format**
- 🔁 **Retry logic & logging built-in**



## ⚙️ Installation

👉 Prefer German? [🇩🇪 Zur deutschen Anleitung](https://github.com/methmx83/ace-data_tool/blob/main/docs/README_de.md)

```bash
# 1. Clone the repository
git clone https://github.com/methmx83/ace-data_tool.git
cd ace-data_tool

# 2. Create Conda environment
conda create -n ace-data_env python=3.13 -y
conda activate ace-data_env

# 3. Install dependencies
pip install -e .

# 4. Download NLTK data (only once)
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('stopwords')"

# 5. Install Ollama & pull a model
ollama pull (your model)
```


<h1 align="center">🎵 ACE-DATA v2 – ACE-Step Data Tool</h1>
<p align="center">
  <strong>Lokales Automations-Tool für Lyrics, Tags & BPM – kompatibel mit ACE-Step</strong><br>
  <em>Extrahiert Lyrics, generiert strukturierte Prompt-Tags & ermittelt BPM – vollständig lokal mit Ollama + Gradio</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.11-blue" alt="Python">
  <img src="https://img.shields.io/badge/Ollama-Chat_API-blue" alt="Ollama">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/Content-CC--BY--NC--4.0-lightgrey" alt="CC BY-NC 4.0">
</p>

<p align="center">
  <img src="./docs/Screenshot.png" alt="Screenshot" width="100%">
</p>

## ✨ Features (v2 Status)
- 🎙️ Automatisches Lyrics-Scraping (Genius) mit Cleaning-Pipeline
- 🧠 LLM-basierte Tag-Generierung (Genre, Mood, Rap-Style, Vocals, Instrumente, BPM)
- 🎚️ Robuste BPM-Erkennung (Librosa + Percussion-Fokus + Normalisierung)
- 💾 Automatische Ausgabe von `*_lyrics.txt` & `*_prompt.txt`
- 🧩 Tags: lowercase-hyphenated, max. 2 Genres, BPM-Tag forciert
- 🖥️ Minimalistische Gradio WebUI (nur Kern-Workflow – Advanced Tabs folgen später)
- � Retry-/Recovery-Strategien für Ollama (Reset/Reload/Delay)
- 🪵 Zentrales Logging (`shared_logs.py`)
- ⚙️ Konfigurierbar über `config/config.json`
- 🧹 Lyrics-Cleanup vor Tagging (Entfernung Intro-Müll bis erste [Section])

## 📦 Aktueller Projektstatus vs. v1
| Bereich            | v1                                     | v2 (jetzt) |
|--------------------|----------------------------------------|------------|
| Ordnerstruktur     | teils redundant                       | konsolidiert (helpers, include, scripts) |
| BPM                | einfache Schätzung                     | stabilisierte Perkussion + Faltung |
| Tagging            | generisch                              | Regelbasiert + BPM-Sicherung |
| UI                 | viele Controls                         | bewusst minimal |
| Metadata Helper    | doppelt / verstreut                    | vereinheitlicht |
| Logging            | teils print                            | zentral `log_message()` |
| Presets/Moods      | vorhanden                              | erweitert / reorganisiert |
| Export/Editor      | im UI                                  | aktuell ausgeblendet (kommt als Tab) |

## ⚙️ Installation
```bash
# 1. Repository klonen
git clone https://github.com/methmx83/ACE-DATA_v2.git
cd ACE-DATA_v2

# 2. (Optional) Virtuelle Umgebung
python -m venv .venv
# Windows:
.venv\\Scripts\\activate

# 3. Abhängigkeiten
pip install -r requirements.txt
# oder (editable)
pip install -e .

# 4. NLTK einmalig vorbereiten
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('stopwords')"

# 5. Ollama installieren & Modell ziehen
ollama pull dein-modell
```

## � Konfiguration (`config/config.json`)
```json
{
  "input_dir": "data/audio",
  "model_name": "deep-x1_q4:latest",
  "ollama_url": "http://localhost:11434/api/generate",
  "retry_count": 2,
  "request_delay": 1.5
}
```
- input_dir: Root mit Audiodateien (rekursiv)
- model_name: Ollama Modell (GGUF lokal)
- retry_count: max. Tagging-Versuche
- request_delay: Pause zwischen Retries

## 🚀 Quickstart
```bash
# Start (Batch)
RUN.bat
# oder direkt
python -m webui.app
```
Dann öffnen: http://127.0.0.1:7860

1. MP3/WAV/FLAC nach `data/audio/` legen  
2. (Optional) Preset auswählen  
3. Häkchen für Überschreiben setzen falls nötig  
4. Start Tagging  
5. Ausgabe:
```
song.mp3
song_lyrics.txt   # Bereinigte Lyrics
song_prompt.txt   # Tags: bpm-92, dark, german-rap, male-vocal, bass-heavy, ...
```

## 🧠 Tag-Format & Regeln
- Alle lowercase, mit `-` statt Leerzeichen
- Max. 2 Genre-Tags
- Mindestens: vocals, instrument(e), mood, rap-style (falls passend)
- BPM-Tag: `bpm-XXX` (falls ermittelt)
- Moods/Styles: Referenz in `include/Moods.md`
- LLM-Ansteuerung: Ollama Chat Endpoint (`/api/chat` aus `ollama_url` abgeleitet)

## 🥁 BPM-Erkennung (Kurz)
Pipeline:
1. Laden & Resample
2. HPSS → Percussion
3. Onset Strength Envelope (median)
4. Librosa tempo() mit Start-Prior
5. Halftime/Double-Korrektur in Zielbereich (70–180)
6. Near-Integer Snap
Rückgabe: Integer oder None → `bpm-<wert>` oder (fallback) Modell darf selbst einschätzen (vermeiden wir aber soweit möglich).

## 📁 Struktur (v2)
```
ACE-DATA_v2/
├── webui/            # Gradio UI (minimal)
├── scripts/          # Kernlogik (lyrics, tagger, moods, helpers)
│   └── helpers/      # bpm, lyrics_cleaner, ...
├── include/          # Moods.md, metadata, clean_lyrics
├── config/           # config.json
├── data/audio/       # Input + Output (Lyrics/Tags)
└── docs/             # Mehrsprachige Doku
```

## 🔍 Logging
- Alle Statusmeldungen zentral über `shared_logs.log_message()`
- UI zeigt letzte ~1000 Einträge
- (Optional) Später: Persistenz in Datei

## 🛡️ Hinweise
| Thema | Hinweis |
|-------|---------|
| Scraping | Nur Lyrics nutzen, für die du Rechte zur Verarbeitung hast |
| GPU | 8 GB VRAM ausreichend für kompaktes Modell |
| RAM | ~2–3 GB Laufzeitverbrauch + Modell |
| Audio-Mengen | Viele Dateien → I/O Bound; BPM kann CPU-lastig sein |
| Fehlerfälle | Leere Lyrics → Tagging wird übersprungen |

## ❗ Bekannte ToDos (Geplant)
- Neuer Tab: Prompt-Editor / Export-Funktion (reintegrieren)
- Optional: Caching von BPM pro Datei (JSON/SQLite)
- Tests: Unit-Tests für Tag-Parsing & BPM-Snap
- Changelog-Datei (siehe unten)

## 🧾 (Optional) Changelog Start
Siehe Vorschlag in Diskussion – Datei `CHANGELOG.md` kann hinzugefügt werden:
```
## [Unreleased]
- Export-Tab reaktivieren
- Preset-Verwaltung UI

## [0.2.0] - 2025-08-12
Added: BPM Robustheit, Moods.md Integration, Lyrics Cleaner
Changed: Minimal UI, Tag-Regeln geschärft
Removed: alter metadata helper
```

## 🧩 Kompatibel mit
- ACE-Step (Dataset-Aufbereitung)
- Lokale Ollama Modelle (Qwen, DeepSeek, Mistral, etc.)
- LoRA / Fine-Tuning Pipelines

## 📜 Lizenz
- Code: MIT
- Inhalte (Moods, Screenshots, ggf. generierte Datenbeispiele): CC BY-NC 4.0

---

*Automatisiere deinen Audio-Datenaufbau – schnell, lokal, strukturiert.*
