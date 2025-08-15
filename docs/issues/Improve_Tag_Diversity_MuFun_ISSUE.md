# Improve Tag Diversity and Precision (MuFun)

## Summary
- Observation: Generated tags often resemble example/preset lists; low diversity.
- Goal: Precise, diverse tags (lowercase-hyphenated, max 2 genres), based on audio and lyrics.

## Context / References
- See docs/CONTEXT.md for system, config, and files.
- Relevant files: scripts/tagger.py, include/mufun_loader.py, scripts/moods.py, config/config.json
- Current commit: 9219c64

## Environment
- OS: Windows 10 Pro
- GPU/VRAM: RTX 4070 Super (12 GB)
- Python: 3.11 (Conda: ace-data_v2_env)
- CUDA: 12.9

## Configuration excerpt
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

## Reproduction
1. Place 2–3 MP3 files in `data/audio/`.
2. Run tagging via WebUI.
3. Inspect `<basename>_prompt.txt` and logs.

## Evidence / Logs (fill in)
- RAW model output (first 400–800 chars) before parsing: 
- Final tags after `extract_clean_tags()`:
- BPM and position of `bpm-XXX`:

## Expected vs Actual
- Expected: hyphenated lowercase tags, max 2 genres, BPM at position 0, categories covered (vocals, instruments, mood, rap-styles if applicable), no preset copying.
- Actual: 

## Acceptance Criteria
- [ ] BPM tag always present at position 0
- [ ] Max 2 genres enforced
- [ ] At least one of each: vocals, instruments, mood (rap-styles if applicable)
- [ ] No duplicates/near-duplicates (e.g., synth vs synthesizer)
- [ ] No fallback to generic preset/example lists
- [ ] Distinct outputs across different songs when `use_audio=true`
- [ ] RAW output is logged when `debug=true`

## Tasks
- [ ] Refine prompt (remove or comment out examples; optionally require strict JSON)
- [ ] Tighten `extract_clean_tags()` (genre cap, synonym normalization, stopwords)
- [ ] Optionally tune audio window (`audio_max_seconds`) for stronger audio signal
- [ ] Add debug hook to log RAW output to `shared_logs`
- [ ] Add 2–3 regression samples

## Risks / Rollback
- Stricter filters could reduce tag count; define fallback behavior.

## Links
- docs/CONTEXT.md
- CHANGELOG.md (0.3.0)
- README.md
