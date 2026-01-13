[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![PyPI version](https://img.shields.io/pypi/v/psm-davinci-resolve-mcp.svg)](https://pypi.org/project/psm-davinci-resolve-mcp/) [![PyPI downloads](https://img.shields.io/pypi/dm/psm-davinci-resolve-mcp.svg)](https://pypi.org/project/psm-davinci-resolve-mcp/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![MCP](https://img.shields.io/badge/MCP-Server-blue)](https://modelcontextprotocol.io)
[![DaVinci Resolve](https://img.shields.io/badge/DaVinci-Resolve-E4405F)](https://www.blackmagicdesign.com/products/davinciresolve)
[![CI](https://github.com/PurpleSquirrelMedia/davinci-resolve-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/PurpleSquirrelMedia/davinci-resolve-mcp/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/PurpleSquirrelMedia/davinci-resolve-mcp/badge)](https://securityscorecards.dev/viewer/?uri=github.com/PurpleSquirrelMedia/davinci-resolve-mcp)

# DaVinci Resolve Automation Suite

Complete automation for DaVinci Resolve (FREE version) via CLI and scripts.

## Quick Start

```bash
# Navigate pages
resolve edit / color / fusion / deliver

# YouTube video workflow
youtube-video full ~/Videos/my_footage.mp4

# Podcast production
podcast-video full ~/Videos/podcast_ep1.mp4

# Color grading presets
color-grade teal-orange

# Social media multi-export
social-export all

# Batch process clips
batch-video ~/Videos/raw_clips/ cinematic_lut

# Quick edit
quick-edit ~/video.mp4 vintage_look
```

## Features

| Feature | Free Version | Studio ($295) |
|---------|--------------|---------------|
| CLI commands (12) | ✓ | ✓ |
| Fusion scripts (38) | ✓ | ✓ |
| Workflow automation (10) | ✓ | ✓ |
| Audio tools | ✓ | ✓ |
| External MCP API | ✗ | ✓ |

**Quick Help:** `resolve-help`

---

## CLI Commands

### `resolve` - Base Controller

```bash
# App control
resolve launch / quit / status

# Page navigation
resolve media / cut / edit / fusion / color / fairlight / deliver

# Playback
resolve play / stop / forward / reverse

# Editing
resolve in / out / blade / delete / undo / redo / save

# Fusion scripting
resolve console                    # Open console
resolve type 'print("Hello")'      # Execute Lua code
```

### `youtube-video` - YouTube Production

```bash
youtube-video full ~/video.mp4     # Complete workflow
youtube-video new ~/video.mp4      # Import & create timeline
youtube-video intro                # Add intro sequence
youtube-video lower-third "Name"   # Add lower third
youtube-video subscribe            # Add subscribe reminder
youtube-video end-screen           # Add end screen
youtube-video color                # YouTube-optimized grade
youtube-video export               # Set up export
```

### `batch-video` - Batch Processing

```bash
batch-video ~/Videos/folder/ cinematic_lut
batch-video ~/Clips/ color_correct
```

### `quick-edit` - Import → LUT → Export

```bash
quick-edit ~/video.mp4 cinematic_lut
```

### `podcast-video` - Podcast Production

```bash
podcast-video full ~/podcast.mp4    # Complete workflow
podcast-video intro "My Podcast"    # Add podcast intro
podcast-video guest "Name" "Title"  # Guest lower third
podcast-video chapter "Topic"       # Chapter marker
podcast-video audiogram             # Square audiogram (1080x1080)
podcast-video outro                 # Outro with CTA
```

### `social-export` - Multi-Platform Export

```bash
social-export all             # Setup all platforms
social-export youtube         # 1920x1080
social-export instagram-feed  # 1080x1080
social-export instagram-story # 1080x1920 (9:16)
social-export tiktok          # 1080x1920 (9:16)
social-export twitter         # 1280x720
```

### `color-grade` - Quick Color Presets

```bash
color-grade cinematic       # Film look
color-grade teal-orange     # Blockbuster look
color-grade vintage         # Faded, warm
color-grade high-contrast   # Punchy
color-grade black-white     # B&W
color-grade day-for-night   # Night simulation
color-grade warm            # Warm tones
color-grade cool            # Cool/blue tones
color-grade bleach-bypass   # Desaturated contrast
```

---

## Fusion Scripts (30)

### Effects
| Script | Description |
|--------|-------------|
| `color_correct` | Basic color correction |
| `film_grain` | Film grain + vignette |
| `glitch_effect` | Digital glitch |
| `shake_effect` | Camera shake |
| `cinematic_bars` | Letterbox (2.35:1) |
| `speed_ramp` | Time remap |
| `motion_blur` | Vector motion blur |
| `zoom_blur` | Radial zoom blur |
| `chromatic_aberration` | RGB split effect |

### Keying/VFX
| Script | Description |
|--------|-------------|
| `green_screen` | Chroma key setup |
| `auto_tracker` | Planar tracker |
| `lens_flare` | Cinematic lens flare |
| `light_leak` | Film burn / light leak |

### Graphics
| Script | Description |
|--------|-------------|
| `lower_third` | Name/title overlay |
| `add_text` | Text node |
| `split_screen` | 2/3/4-way split |
| `text_reveal` | Animated text wipe |
| `picture_in_picture` | PiP layout setup |
| `parallax_scroll` | Multi-layer depth scroll |

### Color Grades
| Script | Description |
|--------|-------------|
| `cinematic_lut` | Film-look grade |
| `vintage_look` | Faded, warm, grainy |

### Templates
| Script | Description |
|--------|-------------|
| `youtube_workflow` | YouTube template |
| `social_export` | Social media presets |

### Running Scripts Manually

1. Open DaVinci Resolve
2. Go to **Fusion** page
3. **Workspace > Scripts > Comp > [script_name]**

Or via console:
```bash
resolve console
resolve type 'dofile("/path/to/script.lua")'
```

---

## How It Works

Uses **AppleScript** to control DaVinci Resolve via:
- Keyboard shortcuts (page navigation, playback)
- Menu navigation (Scripts menu)
- Clipboard paste (Lua code execution)

**No Studio version required!**

---

## File Structure

```
~/davinci-resolve-mcp/
├── automation/
│   ├── resolve              # CLI controller
│   └── workflows/
│       ├── youtube_workflow.sh
│       ├── batch_process.sh
│       └── import_lut_export.sh
├── fusion-scripts/          # Lua scripts
├── templates/               # Workflow templates
└── src/                     # MCP server (Studio)
```

---

## MCP Server (Studio Only)

If you have DaVinci Resolve Studio:

1. Preferences > System > General > External scripting: **Local**
2. Restart Resolve
3. Restart Claude Code

MCP tools become available:
- `resolve_connect`, `resolve_list_projects`
- `resolve_create_timeline`, `resolve_import_media`
- `resolve_add_marker`, `resolve_start_render`
- etc.

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `J/K/L` | Reverse/Stop/Forward |
| `I/O` | Mark In/Out |
| `B` | Blade (cut) |
| `Shift+5` | Fusion page |
| `Shift+6` | Color page |

---

## Resources

- [DaVinci Resolve Scripting API](https://deric.github.io/DaVinciResolve-API-Docs/)
- [Fusion Scripting Guide](https://documents.blackmagicdesign.com/UserManuals/Fusion_Scripting_Guide.pdf)
