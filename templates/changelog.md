#Template for CHANGELOG.md file

## [Unreleased]

### Added
- feat(install): support for installing additional extension projects during main installation (recursive support).
- feat(install): added system prerequisites check (Git, Task, fzf, Node, npm, Gemini).
- feat(setup): support for loading expertises from installed extensions with strict path validation and source labels.
- feat(skeleton): moved sample skill and command from core to `extension-skeleton` and added modular installation support.
- Added detailed procedure for adding new teams and expertises in `README.md`.

### Fixed
- Corrected TOML syntax error in `commands/sample_command.toml` (replaced invalid escaped quotes `\"\"\"` with standard `"""`).
- Improved instructions in `sample_command.toml` prompt for better agent interaction.
