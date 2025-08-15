# scripts/tagger.py
# Version: MuFun-Swap (Ollama → MuFun), Stand 08/2025
# Hardware-Hinweis: 4-bit läuft auf RTX 4070 Super (12 GB VRAM) stabil. :contentReference[oaicite:1]{index=1}

import os
import re
import time
import unicodedata
import json
import warnings
from shared_logs import LOGS, log_message

log_message("... Music Tagger Script (MuFun) loaded ✅")

from tinytag import TinyTag
from scripts.lyrics import load_lyrics
from scripts.moods import extract_clean_tags
from scripts.helpers.bpm import detect_tempo                  # ← dein bewährtes bpm.py
from scripts.helpers.lyrics_cleaner import clean_lyrics_file  # ← unverändert
from include.clean_lyrics import bereinige_datei

# NEU: MuFun-Loader statt Ollama
from include.mufun_loader import load_mufun_model

# Torch nur verwenden, wenn für Inferenz nötig
import torch

warnings.filterwarnings("ignore", message="No ID3 tag found")
warnings.filterwarnings("ignore", message="It looks like you're loading an mp3")
warnings.filterwarnings("ignore", message="Lame tag CRC check failed")
warnings.filterwarnings("ignore", module="librosa")
warnings.filterwarnings("ignore", message="Xing stream size off by more than 1%")

# ---- Konfiguration -----------------------------------------------------------
config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
with open(config_path, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

INPUT_DIR     = config.get('input_dir', 'data/audio')
REQUEST_DELAY = float(config.get('request_delay', 1.0))  # falls vorhanden
HF_MODEL_PATH = config.get('hf_model_path', "")
USE_AUDIO     = bool(config.get('use_audio', False))

# Optional: Decoding-Defaults aus Config (falls gesetzt)
GEN_MAX_NEW_TOKENS   = int(config.get("gen_max_new_tokens", 64))
GEN_TEMPERATURE      = float(config.get("gen_temperature", 0.2))
GEN_TOP_P            = float(config.get("gen_top_p", 0.9))
GEN_REPETITION_PENALTY = float(config.get("gen_repetition_penalty", 1.1))

# ---- Lazy Loader für MuFun --------------------------------------------------
MODEL = None
TOKENIZER = None

def _get_model():
    global MODEL, TOKENIZER
    if MODEL is None or TOKENIZER is None:
        MODEL, TOKENIZER = load_mufun_model(
            HF_MODEL_PATH,
            max_new_tokens=GEN_MAX_NEW_TOKENS,
            temperature=GEN_TEMPERATURE,
            top_p=GEN_TOP_P,
            repetition_penalty=GEN_REPETITION_PENALTY,
        )
    return MODEL, TOKENIZER

# ---- Hilfsfunktionen (wie im Original) --------------------------------------
def sanitize_filename(name: str, max_length=120) -> str:
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    name = re.sub(r'[-\s]+', '_', name)
    return name[:max_length]

def save_tags(file_path, tags):
    if not tags:
        return
    out = os.path.splitext(file_path)[0] + "_prompt.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write(", ".join(tags))
    # Kein doppeltes Cleanen hier – bereits vor dem Tagging möglich

# ---- Retry-Helfer (Signaturen beibehalten; intern No-Ops) -------------------
def reset_ollama_context():
    log_message("💡 (noop) context reset (MuFun)")
    return True

def unload_model():
    log_message("♻️ (noop) unload (MuFun is in-process)")
    return True

def load_model():
    log_message("✅ (noop) load (MuFun already loaded)")
    return True

def reload_model():
    log_message("🔄 (noop) reload (MuFun)")
    return True

# ---- Kern: generate_tags (Prompt/Parsing unverändert) -----------------------
def generate_tags(file_path, prompt_guidance=None, attempt=1):
    """
    Erzeugt 12–14 Musik-Tags: Lyrics → BPM → Prompt → LLM → extract_clean_tags
    Logik & Prompt bleiben wie im Original, nur der LLM-Call ist lokal (MuFun).
    """
    lyrics_file = os.path.splitext(file_path)[0] + "_lyrics.txt"
    if os.path.exists(lyrics_file):
        log_message(f"🔧 Cleaning lyrics file: {lyrics_file}")
        try:
            bereinige_datei(lyrics_file)
            log_message(f"📄 Lyrics file cleaned: {lyrics_file}")
        except Exception as e:
            log_message(f"⚠️ Lyrics cleaning skipped (error): {e}")
    else:
        log_message(f"ℹ️ No lyrics file found to clean: {lyrics_file}")
    log_message(f"\n⏳ Starting tag generation for: {os.path.basename(file_path)}")
    start_time = time.time()

    filename = os.path.basename(file_path)
    lyrics = load_lyrics(file_path)
    bpm = detect_tempo(file_path)

    try:
        tag = TinyTag.get(file_path)
        artist = tag.artist or "Unknown"
        title  = tag.title  or "Unknown"
    except Exception:
        artist, title = "Unknown", "Unknown"

    excerpt = f"[LYRICS EXCERPT]\n{lyrics[:300]}[...]\n\n" if lyrics else ""
    bpm_int = int(round(bpm)) if isinstance(bpm, (int, float)) else None
    if bpm_int is not None:
        log_message(f"🎚️ Detected BPM: {bpm_int}")
    else:
        log_message("🎚️ BPM unknown (detection returned None)")

    # System-Prompt (Original-Regeln beibehalten)
    system_prompt = f"""
### ROLE
You are an expert music tagging AI

### METADATA
Artist: {artist}
Title: {title}
BPM: {bpm_int if bpm_int is not None else 'Unknown'}

{excerpt}### STYLE GUIDANCE
{prompt_guidance or 'Use your best judgment based on the audio'}

### RULES
1. ALWAYS include 'bpm-xxx' if BPM known
2. Generate 12-14 comma-separated tags
3. Use lowercase hyphenated format
4. Prioritize tags from Moods.md
5. Max 2 genre tags
6. Include at least one from each category: vocal type, instruments, mood , rap styles
7. For rap: include at least one rap-styles tag

### EXAMPLE
bpm-92, male/ female-vocal, synthesizer, drums, aggressive, gangsta-rap, german-rap, bass-heavy, dark, street
"""
    user_prompt = "Generate 12 music tags based on the rules above. Output ONLY comma-separated tags."

    # *** Einziger Tauschpunkt: statt HTTP-POST → lokaler MuFun-Call ***
    try:
        # Modell (lazy) laden
        model, tokenizer = _get_model()

        combined_prompt = f"{system_prompt}\n{user_prompt}"

        # Inferenz mit Fallback (chat → generate)
        with torch.inference_mode():
            raw = None
            if hasattr(model, "chat"):
                try:
                    result = model.chat(
                        prompt=combined_prompt,
                        audio_files=(file_path if USE_AUDIO else None),
                        segs=None,
                        tokenizer=tokenizer,
                        max_new_tokens=GEN_MAX_NEW_TOKENS,
                        temperature=GEN_TEMPERATURE,
                        top_p=GEN_TOP_P,
                    )
                    raw = result.get("prompt") if isinstance(result, dict) else str(result)
                except Exception as e:
                    log_message(f"ℹ️ chat() failed, fallback to text-only generate: {e}")

            if not raw:
                inputs = tokenizer(combined_prompt, return_tensors="pt")
                # Auf Modellgerät verschieben, falls vorhanden
                if hasattr(model, "device"):
                    inputs = {k: v.to(model.device) for k, v in inputs.items()}
                out = model.generate(
                    **inputs,
                    max_new_tokens=GEN_MAX_NEW_TOKENS,
                    do_sample=True,
                    top_p=GEN_TOP_P,
                    temperature=GEN_TEMPERATURE,
                    repetition_penalty=GEN_REPETITION_PENALTY,
                    pad_token_id=getattr(tokenizer, "pad_token_id", None),
                    eos_token_id=getattr(tokenizer, "eos_token_id", None),
                )
                raw = tokenizer.decode(out[0], skip_special_tokens=True)

        if not raw:
            raise ValueError("Empty response from model")

        tags = extract_clean_tags(raw)

        # BPM-Tag sicherstellen & an den Anfang setzen
        if bpm_int is not None:
            bpm_tag = f"bpm-{bpm_int}"
            if bpm_tag not in tags:
                tags.append(bpm_tag)
            if tags.index(bpm_tag) != 0:
                tags.remove(bpm_tag)
                tags.insert(0, bpm_tag)

        duration = time.time() - start_time
        log_message(f"✅ Tags generated in {duration:.2f}s: 🔥 {', '.join(tags[:5])}...")

        # Optionaler Cache-Clear zwischen Dateien
        if bool(config.get("empty_cache_between_files", False)) and torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
            except Exception:
                pass

        return tags

    except Exception as e:
        # Dein bestehendes Retry-Gerüst (Versuche, Delays, Reload-Noops)
        RETRY_COUNT = int(config.get('retry_count', 2))
        if attempt <= RETRY_COUNT:
            log_message(f"❌ Error (Attempt {attempt}/{RETRY_COUNT}): {str(e)}")
            if attempt == 1:
                reset_ollama_context()
            elif attempt == 2:
                reload_model()
            time.sleep(max(REQUEST_DELAY, 0.5) * attempt)
            return generate_tags(file_path, prompt_guidance, attempt + 1)
        log_message(f"❌ Final error at {filename}: {e}")
        return None
