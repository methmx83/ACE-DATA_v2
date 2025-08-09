# 🔁 app.py

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Füge den Pfad zu shared_logs.py hinzu.

current_dir = os.path.dirname(os.path.abspath(__file__))  # webui/
project_root = os.path.dirname(current_dir)              # ace-data_tool/
sys.path.append(os.path.join(project_root, 'scripts'))
sys.path.append(os.path.join(project_root, 'include'))


import gradio as gr
from tinytag import TinyTag
from include.preset_loader import load_presets
from scripts.lyrics import load_lyrics, fetch_and_save_lyrics
from scripts.tagger import generate_tags, save_tags
from shared_logs import LOGS, log_message
# Importiere LOGS und log_message aus shared_logs.py.

import json

# AUDIO_DIR aus Konfiguration lesen (Single Source of Truth)
with open(os.path.join(project_root, 'config', 'config.json'), 'r', encoding='utf-8') as _cf:
    _conf = json.load(_cf)
AUDIO_DIR = _conf.get('input_dir', 'data')

# Lade Genre-Presets
GENRE_PRESETS = load_presets()

def process_file(mp3_path: str, overwrite_lyrics: bool = False,
                 overwrite_prompts: bool = False, prompt_guidance: str = "") -> str:
    base, _ = os.path.splitext(mp3_path)
    # TinyTag robust auslesen
    try:
        tag = TinyTag.get(mp3_path)
        artist = tag.artist or "Unknown"
        title = tag.title or "Unknown"
    except Exception:
        artist, title = "Unknown", "Unknown"

    lyrics_path = f"{base}_lyrics.txt"
    if overwrite_lyrics or not os.path.exists(lyrics_path):
        fetch_and_save_lyrics(artist, title, lyrics_path)

    lyrics = load_lyrics(mp3_path) or "–"
    if lyrics == "–":
        log_message(f"✗ No Lyrics {mp3_path} found. Abort!")
        return f"✗ {os.path.basename(mp3_path)}: No lyrics"

    tags_path = f"{base}_prompt.txt"
    if not overwrite_prompts and os.path.exists(tags_path):
        log_message(f"✓ Tags exist -> skipped: {os.path.basename(mp3_path)}")
        return "skipped"

    tags = generate_tags(mp3_path, prompt_guidance=prompt_guidance)
    save_tags(mp3_path, tags)

    log_message(f"✅ Files processed: {os.path.basename(mp3_path)}")
    return "done"

def process_all_ui(overwrite_lyrics: bool = False, overwrite_prompts: bool = False,
                   genre: str = "Choose a Preset (optional)", progress=gr.Progress()) -> str:
    base = GENRE_PRESETS.get(genre) or ""
    prompt_guidance = base.strip()

    log = []
    audio_files = []
    for root, _, files in os.walk(AUDIO_DIR):
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.flac', '.m4a')):
                audio_files.append(os.path.join(root, file))

    for file_path in progress.tqdm(audio_files, desc="Processing Songs"):
        try:
            process_file(
                file_path,
                overwrite_lyrics=overwrite_lyrics,
                overwrite_prompts=overwrite_prompts,
                prompt_guidance=prompt_guidance
            )
        except Exception as e:
            log_message(f"✗ {os.path.basename(file_path)}: {e}")

    # Log-Box: komplette Session (ggf. begrenzen)
    return "\n".join(LOGS[-1000:])


# Default Info Text
INFO_TEXT_DEFAULT = (
    "Tipps zur Nutzung:\n"
    "- Lege Audios ins konfigurierte input_dir (z. B. data/audio)\n"
    "- Preset wählen oder neutral lassen\n"
    "- 'Überschreibe Lyrics' -> *_lyrics.txt wird neu erzeugt\n"
    "- 'Überschreibe Prompts' -> *_prompt.txt wird neu erzeugt\n"
    "- Fortschritt & Status in der linken Log-Box"
)

with gr.Blocks(css="""
body { background-color: #121212; color: #f0f0f0; font-family: 'Segoe UI', sans-serif; }
.gr-button { background: linear-gradient(90deg, #8e2de2, #4a00e0); color: white; font-weight: bold; border: none; border-radius: 12px; padding: 12px 24px; transition: all 0.3s ease; }
.gr-button:hover { background: linear-gradient(90deg, #4a00e0, #8e2de2); transform: scale(1.03); }
.gr-textbox textarea { background-color: #1e1e1e; border: 1px solid #444; color: #fff; font-size: 14px; border-radius: 8px; text-align: center; }
h1, h2, h3 { color: #e0b0ff; text-shadow: 0 0 6px rgba(255, 0, 255, 0.2); }
#model_dropdown { display: none; }
""") as demo:

    gr.Markdown("# 🎧 ACE-STEP DATA-TOOL\n**Generates data-files für Ace-Step – fully automated.**")

    with gr.Row():
        genre_dropdown = gr.Dropdown(
            label="🎼 Genre-Preset",
            choices=list(GENRE_PRESETS.keys()),
            value="Choose a Preset (optional)",
            interactive=True
        )
        overwrite_lyrics_cb = gr.Checkbox(label="Überschreibe Lyrics", value=False)
        overwrite_prompts_cb = gr.Checkbox(label="Überschreibe Prompts", value=False)

    # Progress-Bar kommt aus process_all_ui via gr.Progress()

    with gr.Row():
        output_box = gr.Textbox(label="Process Log Box", lines=16, interactive=False)
        info_box = gr.Textbox(label="Info Text Box", value=INFO_TEXT_DEFAULT, lines=16, interactive=True)

    start_button = gr.Button("Start Tagging")
    start_button.click(
        fn=process_all_ui,
        inputs=[overwrite_lyrics_cb, overwrite_prompts_cb, genre_dropdown],
        outputs=output_box
    )

    

def main():
    demo.launch(server_name="127.0.0.1", server_port=7860)

if __name__ == "__main__":
    main()