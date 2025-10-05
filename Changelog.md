# Changelog

## [Unreleased]

### Fixed

- **Settings Persistence:** Addressed issues where runtime settings were not persisting across application resets.
  - **app.py:**
    - Modified `on_chat_start` to load initial settings from `config.json`, ensuring persisted values are reflected on application start.
    - Updated `on_settings_update` to correctly persist `system_prompt`, `character`, `reasoning_enabled`, `last_used_model`, and `tts_temperature` to `config.json`.
    - Removed redundant update for `tts_voice` in `on_settings_update`.
    - Added a `Slider` UI element for `tts_temperature` in `cl.ChatSettings`.
  - **config.json:**
    - Added new keys (`system_prompt_key`, `character`, `tts_temperature`, `reasoning_enabled`, `last_used_model`) to store persisted settings.