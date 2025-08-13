# Changelog

Alle relevanten Änderungen an diesem Projekt werden in dieser Datei festgehalten.
Das Format orientiert sich an "Keep a Changelog" und Versionierung folgt SemVer.

## [Unreleased]
- Re-Integration: Prompt-Editor-Tab und Export-Funktion in der WebUI
- Optional: BPM-Caching pro Datei (JSON/SQLite)
- Tests: Unit-Tests für Tag-Parsing und BPM-Normalisierung
- Optionale Log-Persistenz/Rotation

## [0.2.0] - 2025-08-13
### Added
- Moods/Preset-Sammlung in `include/Moods.md`
- Lyrics-Cleaner `include/clean_lyrics.py` (Bereinigung bis zur ersten Abschnitts-Markierung `[...]`)
- Kurze BPM-Detektionslogs (sichtbarer BPM-Wert in Session-Log)

### Changed
- Stabilere BPM-Erkennung über `scripts/helpers/bpm.py::detect_tempo` (Percussion-Fokus, Halftime/Double-Faltung, Near-Integer Snap)
- Tagging-Regeln: BPM-Tag wird erzwungen und bei Bedarf nach vorn verschoben
- WebUI vereinfacht (nur Kern-Workflow auf der Startseite; Advanced-Elemente temporär entfernt)
- Konfiguration vereinheitlicht: `config/config.json` mit `input_dir = data/audio` (rekursiv)
- README auf v2-Feature-Set aktualisiert

### Fixed
- Fehlerhafte Variable im BPM-Tag-Block (`bpm_value` → `bpm_int`) und Scope/Indentation-Bug (UnboundLocalError)
- Übergabe eines nicht unterstützten Arguments an `detect_tempo` (verhinderte BPM-Erkennung → None)

### Removed
- Veraltete/duplizierte Helper (`scripts/helpers/metadata.py`)
- UI-Elemente für Prompt-Editor/Export vorerst entfernt (kommen als eigener Tab zurück)

