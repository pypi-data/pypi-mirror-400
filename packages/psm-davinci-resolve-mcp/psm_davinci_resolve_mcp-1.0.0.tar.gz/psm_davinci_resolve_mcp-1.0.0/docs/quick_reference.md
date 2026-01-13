# DaVinci Resolve Automation Suite - Quick Reference

## CLI Commands

### Core
```bash
resolve <command>         # Base controller
resolve-help              # Full help menu
```

### Video Production
```bash
youtube-video <cmd>       # YouTube workflow
podcast-video <cmd>       # Podcast production
music-video <cmd>         # Music video effects
vlog-video <cmd>          # Vlog editing
doc-video <cmd>           # Documentary production
```

### Processing
```bash
batch-video <files>       # Batch process multiple videos
quick-edit <file>         # Import → LUT → Export
color-grade <preset>      # Apply color preset
audio-tools <cmd>         # Audio processing
```

### Export
```bash
social-export <platform>  # Multi-platform export
export-preset <preset>    # Platform-specific settings
thumbnail <cmd>           # YouTube thumbnail generator
```

### Management
```bash
proxy-video <cmd>         # Proxy media workflow
batch-render <cmd>        # Render queue manager
project-backup <cmd>      # Backup/archive projects
```

## Color Presets
```bash
color-grade cinematic     # Teal shadows, orange highlights
color-grade teal-orange   # Classic film look
color-grade vintage       # Faded, warm film
color-grade high-contrast # Punchy blacks
color-grade black-white   # B&W with contrast
color-grade day-for-night # Night scene simulation
color-grade warm          # Golden hour
color-grade cool          # Blue, cold
color-grade bleach-bypass # Desaturated film
```

## Export Presets
```bash
export-preset youtube-4k      # 4K HDR
export-preset youtube-1080    # Standard HD
export-preset youtube-shorts  # Vertical 9:16
export-preset instagram-feed  # Square 1:1
export-preset instagram-reels # Vertical stories
export-preset tiktok          # TikTok optimized
export-preset twitter         # Twitter video
export-preset vimeo           # High quality
export-preset broadcast       # ProRes 422
export-preset cinema          # Cinema DCP
```

## Fusion Effects

### Text & Titles
- `lower_third.lua` - News-style lower third
- `add_text.lua` - Basic text overlays
- `text_reveal.lua` - Animated reveals
- `3d_text.lua` - Extruded 3D text
- `call_to_action.lua` - Subscribe buttons
- `countdown_timer.lua` - Countdown/countup

### Color & Look
- `cinematic_lut.lua` - Film LUT application
- `color_correct.lua` - Basic correction
- `color_match.lua` - Shot matching
- `vintage_look.lua` - Retro film
- `hdr_tools.lua` - HDR workflow
- `skin_retouch.lua` - Beauty/skin tools

### Effects
- `glitch_effect.lua` - Digital glitch
- `chromatic_aberration.lua` - RGB split
- `film_grain.lua` - Organic grain
- `dust_scratches.lua` - Film damage
- `lens_flare.lua` - Anamorphic flares
- `light_leak.lua` - Film light leaks
- `motion_blur.lua` - Motion blur
- `zoom_blur.lua` - Radial blur
- `shake_effect.lua` - Camera shake

### VFX
- `green_screen.lua` - Chroma key
- `auto_tracker.lua` - Motion tracking
- `face_blur.lua` - Privacy blur
- `energy_effects.lua` - Electric/plasma
- `mirror_effect.lua` - Kaleidoscope

### Transitions
- `transition_wipe.lua` - Directional wipes
- `transition_glitch.lua` - Glitch transition
- `transition_zoom.lua` - Zoom blur
- `transition_ink.lua` - Ink splatter

### Layout
- `split_screen.lua` - Multi-panel layout
- `picture_in_picture.lua` - PIP overlay
- `parallax_scroll.lua` - Depth layers
- `cinematic_bars.lua` - Letterbox
- `social_frames.lua` - Platform frames
- `watermark.lua` - Logo/watermark

### Generators
- `generator_gradient.lua` - Gradient backgrounds
- `generator_particles.lua` - Floating particles
- `generator_noise.lua` - Noise/texture
- `generator_shapes.lua` - Geometric patterns
- `animated_backgrounds.lua` - Moving BGs
- `logo_reveal.lua` - Animated logos

## Common Workflows

### YouTube Video
```bash
youtube-video import video.mp4
youtube-video intro
youtube-video color
youtube-video render
```

### Multi-Platform Export
```bash
social-export all         # Export for all platforms
social-export youtube
social-export instagram
social-export tiktok
```

### Batch Processing
```bash
batch-video *.mp4         # Process all MP4s
batch-video --lut vintage *.mov
```

### Overnight Render
```bash
batch-render add "Project 1"
batch-render add "Project 2"
batch-render overnight
```

### Project Backup
```bash
project-backup backup "My Project"
project-backup archive "Finished Film"
project-backup cloud     # Sync to cloud
```

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Media Page | Shift+2 |
| Edit Page | Shift+4 |
| Fusion Page | Shift+5 |
| Color Page | Shift+6 |
| Deliver Page | Shift+8 |
| Play/Stop | Space |
| Mark In/Out | I / O |
| Blade | Cmd+B |
| Undo | Cmd+Z |
| Save | Cmd+S |
| Add Node | Alt+S |
| Start Render | Cmd+Shift+R |

## File Locations

- CLI Commands: `~/bin/`
- Fusion Scripts: `~/davinci-resolve-mcp/fusion-scripts/`
- Workflows: `~/davinci-resolve-mcp/automation/workflows/`
- Exports: `~/ColorGrading/Exports/`
- Backups: `~/ColorGrading/Backups/`
- Logs: `~/ColorGrading/RenderLogs/`
