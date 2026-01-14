# ux

uv-based Python App Launcher - distribute Python apps as single executables.

## Features

- **Single binary distribution** - End users don't need Python or uv installed
- **Cross-compilation** - Build for Linux/Windows from macOS
- **macOS .app bundle** - Native macOS application with icon support
- **Code signing & Notarization** - Distribute through macOS Gatekeeper
- **DMG creation** - Professional macOS distribution format

## Installation

Download from [Releases](https://github.com/i2y/ux/releases)

Or build from source:
```bash
cargo install --git https://github.com/i2y/ux
```

## Quick Start

### Basic bundling
```bash
# Bundle Python app into single binary
ux bundle --project /path/to/project --output ./dist/
```

### Cross-compilation
```bash
# Build for Linux from macOS
ux bundle --target linux-x86_64 --output ./dist/

# Build for Windows from macOS
ux bundle --target windows-x86_64 --output ./dist/
```

### macOS .app bundle
```bash
# Create .app bundle
ux bundle --format app --output ./dist/

# With code signing
ux bundle --format app --codesign --output ./dist/

# With notarization (requires Apple Developer account)
ux bundle --format app --notarize --output ./dist/

# Create DMG for distribution
ux bundle --format app --codesign --dmg --output ./dist/
```

## Configuration

Add `[tool.ux]` section to your `pyproject.toml`:

```toml
[project]
name = "myapp"

[project.scripts]
myapp = "myapp.main:main"  # Entry point

[tool.ux]
entry = "myapp"            # Optional: explicit entry point
include = [                # Optional: additional files to include
  "assets/",               # Include entire directory (trailing slash)
  "config.yaml",           # Include specific file
]

[tool.ux.macos]
icon = "assets/icon.png"   # PNG auto-converted to ICNS
bundle_identifier = "com.example.myapp"
bundle_name = "My App"
```

### Included files

The bundle automatically includes:
- Package directory (detected from `[project].name`, e.g., `myapp/` or `src/myapp/`)
- `pyproject.toml`, `uv.lock`
- `README.md`, `LICENSE` (if present)

Use `[tool.ux].include` to add extra files or directories (with trailing slash)

## Supported Platforms

| Target | Cross-compile from macOS |
|--------|-------------------------|
| darwin-x86_64 | Native |
| darwin-aarch64 | Native |
| linux-x86_64 | Yes |
| linux-aarch64 | Yes |
| windows-x86_64 | Yes |

## License

MIT
