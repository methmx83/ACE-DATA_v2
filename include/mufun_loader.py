# include/mufun_loader.py
# Versionen empfohlen: transformers >= 4.42, bitsandbytes >= 0.43, Torch CUDA 12.x
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from shared_logs import log_message

def load_mufun_model(model_path: str | None = None,
                     max_new_tokens: int = 64,
                     temperature: float = 0.2,
                     top_p: float = 0.9,
                     repetition_penalty: float = 1.1):
    """
    Lädt MuFun-ACEStep quantisiert in 4-bit.
    - Bevorzugt lokalen Ordner (model_path), sonst Hugging Face Repo 'Yi3852/MuFun-ACEStep'
    - Setzt sinnvolle Generation-Defaults
    """
    try:
        torch.backends.cuda.matmul.allow_tf32 = True  # RTX 40xx: schneller, gleiche Qualität
    except Exception:
        pass

    quant_config = None
    try:
        from transformers import BitsAndBytesConfig
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
    except Exception as e:
        log_message(f"ℹ️ BitsAndBytes nicht verfügbar ({e}), lade ohne 4-bit")
    hf_path = model_path if (model_path and os.path.isdir(model_path)) else "Yi3852/MuFun-ACEStep"
    log_message(f"📦 Lade Modell: {hf_path}{' (4-bit)' if quant_config else ''}")

    tokenizer = AutoTokenizer.from_pretrained(hf_path, use_fast=False, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        hf_path,
        trust_remote_code=True,
        quantization_config=quant_config,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    model.eval()

    # pad_token absichern
    if getattr(tokenizer, "pad_token", None) is None and getattr(tokenizer, "eos_token", None):
        tokenizer.pad_token = tokenizer.eos_token

    # Standard-Decode-Grenzen (können bei .chat überschrieben werden)
    try:
        gc = model.generation_config
        gc.max_new_tokens = max_new_tokens
        gc.temperature = temperature
        gc.top_p = top_p
        gc.repetition_penalty = repetition_penalty
    except Exception:
        pass

    return model, tokenizer
