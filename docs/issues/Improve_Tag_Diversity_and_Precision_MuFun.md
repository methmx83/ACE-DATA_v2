# Improve Tag Diversity and Precision (MuFun)

## Summary
- Observation: Generated tags sometimes resemble example/preset lists with low diversity.
- Goal: More precise and diverse tags (lowercase-hyphenated, max 2 genres), grounded in audio and lyrics.

## Context/References
- See docs/CONTEXT.md for system, config, and files.
- Relevant files:
  - scripts/tagger.py (MuFun flow, lazy loading, fallback)
  - include/mufun_loader.py (HF loader, 4-bit + fallback)
  - scripts/moods.py (extract_clean_tags)
  - config/config.json (hf_model_path, use_audio, gen_*, debug)
- Current commit: 70826be

## Environment
- OS: Windows 10 Pro
- GPU/VRAM: RTX 4070 Super (12 GB)
- Python: 3.11 (Conda: ace-data_v2_env)
- CUDA: 12.9

## Configuration (excerpt)
```json
{
  "input_dir": "data/audio",
  "hf_model_path": "Z:/AI/projects/.models/generative/mufun",
  "use_audio": true,
  "audio_max_seconds": 45,
  "downsample_hz": 16000,
  "empty_cache_between_files": true,
  "debug": true,
  "debug_raw_max_bytes": 1048576,
  "gen_max_new_tokens": 64,
  "gen_temperature": 0.2,
  "gen_top_p": 0.9,
  "gen_repetition_penalty": 1.1
}
```

## Reproduction
1. Place 2–3 MP3 files in `data/audio/`.
2. Run tagging via WebUI.
3. Inspect `<basename>_prompt.txt` and `data/logs/<basename>_llm_raw.txt`.

## Evidence / Logs
### 1) Augen Auf (80bpm)
- RAW (excerpt 400–800): "Hip Hop/Rap, Aggressive, Exurberant, Energetic, voice, guitar, synthesizer, drums, bass-heavy, Dark, Gangsta Rap, German Hip Hop, Dark Hip Hop, Dark Rap, Release Interval, Hip Hop/Rap, Aggressive, Energetic, Exur"
- Tags (final): bpm-80, aggressive, bass-heavy, dark, drums, energetic, guitar, hip-hop, synthesizer, voice, dark-hip-hop, dark-rap, exur, exurberant, gangsta-rap, german-hip-hop
- BPM: 80 | Position in list: 0

### 2) Bei Nacht (94bpm)
- RAW (excerpt 400–800): "hiphop, male vocal, rap, synthesizer, drums, aggressive, gangsta-rap, bass, dark, street, bass-heavy, dark, hiphop, male vocal, rap, synthesizer, drums, aggressive, hiphop, male vocal, rap, synthesizer, drums, aggressive,"
- Tags (final): bpm-94, aggressive, bass, bass-heavy, dark, drums, street, synthesizer, gangsta-rap, hiphop, male-vocal
- BPM: 94 | Position in list: 0

### 3) Roller (128bpm)
- RAW (excerpt 400–800): "bass, drums, aggressive, rap, hiphop, gangsta-rap, synthesizer, male vocal, dark, street, rap-styles, piano, bass-heavy, german-rap, dark, male vocals, dark, piano, bass, drums, aggressive, rap, hiphop, h"
- Tags (final): bpm-128, aggressive, bass, bass-heavy, dark, drums, piano, street, synthesizer, gangsta-rap, german-rap, hiphop, male-vocal, male-vocals, rap-styles
- BPM: 128 | Position in list: 0

## Observed Problems
- Repetitions and preset-like lists in RAW and final tags.
- Near-duplicates and synonyms: male-vocal vs male-vocals; hiphop vs hip-hop; synth vs synthesizer.
- Genre count can exceed the “max 2 genres” rule.
- Some non-hyphenated or capitalized forms appear in RAW and leak into outputs.

## Acceptance Criteria
- [ ] BPM tag always present at position 0
- [ ] Max 2 genre tags enforced
- [ ] At least one of each: vocals, instruments, mood (rap-styles if applicable)
- [ ] No duplicates/near-duplicates (e.g., synth vs synthesizer; hiphop vs hip-hop)
- [ ] No copying from preset/example lists
- [ ] Distinct outputs across different songs when `use_audio=true`
- [ ] RAW output logged when `debug=true`

## Tasks
- [ ] Refine the prompt (remove/comment examples; optionally require strict JSON)
- [ ] Tighten `extract_clean_tags()` (genre cap, synonym normalization, stopwords/typo filter)
- [ ] Optionally tune audio window (`audio_max_seconds`) to strengthen audio signal
- [ ] Add a debug hook to also log a short RAW excerpt to `shared_logs`
- [ ] Add 2–3 regression samples

## Risks / Rollback
- Stricter filters may reduce tag count; define sensible fallback behavior.

## Links
- [docs/CONTEXT.md](../CONTEXT.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [README.md](../../README.md)

## Labels/Milestone
- Labels: enhancement, quality
- Milestone: v0.3.1
