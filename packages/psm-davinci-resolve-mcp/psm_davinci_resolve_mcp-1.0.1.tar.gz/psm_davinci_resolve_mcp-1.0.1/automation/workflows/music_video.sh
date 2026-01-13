#!/bin/bash
# Music Video Production Workflow
# Beat sync, effects, and performance editing

set -e

RESOLVE_CMD="$HOME/bin/resolve"

show_help() {
    echo "Music Video Production Workflow"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  new <video> <audio>   Start new music video project"
    echo "  beat-marker           Add markers on beats (manual)"
    echo "  strobe                Add strobe/flash effect"
    echo "  color-flash <color>   Add color flash (red/blue/white)"
    echo "  split-screen          Performance split screen"
    echo "  vhs                   VHS/retro effect"
    echo "  trippy                Psychedelic color effect"
    echo "  lyrics <text>         Add lyric text"
    echo "  credits               Rolling credits"
    echo "  full <video>          Full music video setup"
    echo ""
}

ensure_resolve() {
    if ! pgrep -x "Resolve" > /dev/null; then
        $RESOLVE_CMD launch
        sleep 5
    fi
}

run_lua() {
    local script="$1"
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5
    echo "$script" | pbcopy
    osascript << 'EOF'
tell application "System Events"
    tell process "Resolve"
        keystroke "v" using command down
        delay 0.2
        key code 36
    end tell
end tell
EOF
    sleep 1
}

cmd_new() {
    local video="$1"
    local audio="$2"

    echo "=== Creating Music Video Project ==="
    ensure_resolve

    $RESOLVE_CMD media
    sleep 1

    # Import video
    if [ -n "$video" ]; then
        osascript << EOF
tell application "DaVinci Resolve" to activate
delay 0.5
tell application "System Events"
    tell process "Resolve"
        keystroke "i" using command down
        delay 1
        keystroke "g" using {command down, shift down}
        delay 0.5
        keystroke "$video"
        delay 0.3
        key code 36
        delay 0.5
        key code 36
    end tell
end tell
EOF
        sleep 2
    fi

    $RESOLVE_CMD edit
    sleep 1
    echo "✓ Music video project created"
    echo "  Import your audio track and sync to video"
}

cmd_beat_marker() {
    echo "Beat Marker Mode"
    echo "================"
    echo "Press 'M' on each beat while playing"
    echo ""
    ensure_resolve
    $RESOLVE_CMD edit
    sleep 0.5

    # Start playback
    osascript << 'EOF'
tell application "System Events"
    tell process "Resolve"
        key code 49  -- Space to play
    end tell
end tell
EOF

    echo "Playing... Press Cmd+M to add markers on beats"
    echo "Press Ctrl+C when done"
}

cmd_strobe() {
    echo "Adding strobe effect..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- White flash
    local flash = comp:AddTool("Background")
    flash:SetAttrs({TOOLS_Name = "StrobeFlash"})
    flash.TopLeftRed = 1
    flash.TopLeftGreen = 1
    flash.TopLeftBlue = 1

    -- Animate opacity for strobe
    local merge = comp:AddTool("Merge")
    merge:SetAttrs({TOOLS_Name = "StrobeMerge"})
    merge.Blend = 0  -- Animate this 0->1->0 rapidly

    comp:Unlock()
    print("✓ Strobe effect added")
    print("  Animate StrobeMerge.Blend: 0→1→0 on beats")
end'
    echo "✓ Strobe effect added"
}

cmd_color_flash() {
    local color="${1:-white}"
    local r=1 g=1 b=1

    case "$color" in
        red)    r=1; g=0; b=0 ;;
        blue)   r=0; g=0.3; b=1 ;;
        green)  r=0; g=1; b=0 ;;
        purple) r=0.8; g=0; b=1 ;;
        yellow) r=1; g=1; b=0 ;;
        cyan)   r=0; g=1; b=1 ;;
        *)      r=1; g=1; b=1 ;;
    esac

    echo "Adding $color flash effect..."
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local flash = comp:AddTool('Background')
    flash:SetAttrs({TOOLS_Name = '${color}Flash'})
    flash.TopLeftRed = $r
    flash.TopLeftGreen = $g
    flash.TopLeftBlue = $b

    local merge = comp:AddTool('Merge')
    merge:SetAttrs({TOOLS_Name = '${color}FlashMerge'})
    merge.ApplyMode = 'Screen'
    merge.Blend = 0.5

    comp:Unlock()
    print('✓ $color flash added')
end"
    echo "✓ $color flash effect added"
}

cmd_split_screen() {
    echo "Adding performance split screen..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- 4-way split for performance shots
    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "SplitBG"})
    bg.TopLeftRed = 0
    bg.TopLeftGreen = 0
    bg.TopLeftBlue = 0

    -- Quadrant transforms
    local positions = {
        {name="TopLeft", x=0.25, y=0.75},
        {name="TopRight", x=0.75, y=0.75},
        {name="BottomLeft", x=0.25, y=0.25},
        {name="BottomRight", x=0.75, y=0.25}
    }

    for i, pos in ipairs(positions) do
        local t = comp:AddTool("Transform")
        t:SetAttrs({TOOLS_Name = "Perf_" .. pos.name})
        t.Size = 0.48
        t.Center = {pos.x, pos.y}
    end

    comp:Unlock()
    print("✓ 4-way performance split created")
    print("  Connect different takes to each transform")
end'
    echo "✓ Performance split screen added"
}

cmd_vhs() {
    echo "Adding VHS/retro effect..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Chromatic aberration
    local ca = comp:AddTool("Transform")
    ca:SetAttrs({TOOLS_Name = "VHS_ChromaShift"})
    ca.Center = {0.502, 0.5}

    -- Scan lines
    local scanlines = comp:AddTool("FastNoise")
    scanlines:SetAttrs({TOOLS_Name = "VHS_Scanlines"})
    scanlines.Detail = 0
    scanlines.Contrast = 5
    scanlines.XScale = 500
    scanlines.YScale = 0.5
    scanlines.Brightness = -0.3

    -- Color degradation
    local color = comp:AddTool("ColorCorrector")
    color:SetAttrs({TOOLS_Name = "VHS_Color"})
    color.MasterSaturation = 0.8
    color.MasterRGBContrast = 0.9
    color.MasterRGBGain = {1.1, 1.0, 0.95}

    -- Noise
    local noise = comp:AddTool("FilmGrain")
    noise:SetAttrs({TOOLS_Name = "VHS_Noise"})
    noise.Strength = 0.4
    noise.Size = 2

    -- Blur
    local blur = comp:AddTool("Blur")
    blur:SetAttrs({TOOLS_Name = "VHS_Blur"})
    blur.XBlurSize = 1.5
    blur.YBlurSize = 0.5

    comp:Unlock()
    print("✓ VHS effect added")
end'
    echo "✓ VHS/retro effect added"
}

cmd_trippy() {
    echo "Adding psychedelic effect..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Hue rotation
    local hue = comp:AddTool("ColorCorrector")
    hue:SetAttrs({TOOLS_Name = "Trippy_HueShift"})
    -- Animate MasterHueAngle 0 to 360

    -- Feedback/echo
    local trail = comp:AddTool("Trails")
    trail:SetAttrs({TOOLS_Name = "Trippy_Trails"})
    trail.Gain = 0.85
    trail.Restart = 0

    -- Kaleidoscope
    local mirror = comp:AddTool("CoordinateSpace")
    mirror:SetAttrs({TOOLS_Name = "Trippy_Mirror"})
    mirror.Shape = 1  -- Mirror

    -- Color boost
    local sat = comp:AddTool("ColorCorrector")
    sat:SetAttrs({TOOLS_Name = "Trippy_Saturate"})
    sat.MasterSaturation = 1.5
    sat.MasterRGBContrast = 1.2

    -- Glow
    local glow = comp:AddTool("SoftGlow")
    glow:SetAttrs({TOOLS_Name = "Trippy_Glow"})
    glow.Threshold = 0.5
    glow.Gain = 0.3

    comp:Unlock()
    print("✓ Psychedelic effect added")
    print("  Animate Trippy_HueShift.MasterHueAngle 0→360")
end'
    echo "✓ Trippy effect added"
}

cmd_lyrics() {
    local text="${1:-♪ Your lyrics here ♪}"

    echo "Adding lyrics: $text"
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local lyric = comp:AddTool('TextPlus')
    lyric:SetAttrs({TOOLS_Name = 'LyricText'})
    lyric.StyledText = '$text'
    lyric.Font = 'Arial Black'
    lyric.Size = 0.06
    lyric.Center = {0.5, 0.15}
    lyric.Red1 = 1
    lyric.Green1 = 1
    lyric.Blue1 = 1

    -- Drop shadow
    local shadow = comp:AddTool('DropShadow')
    shadow:SetAttrs({TOOLS_Name = 'LyricShadow'})
    shadow.ShadowOffset = {0.003, -0.003}
    shadow.Softness = 8

    comp:Unlock()
    print('✓ Lyrics added: $text')
end"
    echo "✓ Lyrics added"
}

cmd_credits() {
    echo "Adding rolling credits..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "CreditsBG"})
    bg.TopLeftRed = 0
    bg.TopLeftGreen = 0
    bg.TopLeftBlue = 0

    local credits = comp:AddTool("TextPlus")
    credits:SetAttrs({TOOLS_Name = "CreditsText"})
    credits.StyledText = [[
SONG TITLE
by Artist Name

Directed by
Your Name

Cinematography
Camera Person

Edited by
Editor Name

Special Thanks
Person 1
Person 2

© 2024 Your Label
]]
    credits.Font = "Arial"
    credits.Size = 0.04
    credits.Center = {0.5, -0.5}  -- Start below screen
    -- Animate Center.Y from -0.5 to 1.5 for scroll

    comp:Unlock()
    print("✓ Rolling credits added")
    print("  Animate CreditsText.Center.Y from -0.5 to 1.5")
end'
    echo "✓ Rolling credits added"
}

cmd_full() {
    local video="$1"

    echo "========================================="
    echo "  MUSIC VIDEO WORKFLOW"
    echo "========================================="
    echo ""

    cmd_new "$video"
    sleep 1

    cmd_strobe
    sleep 1

    cmd_color_flash "blue"
    sleep 1

    cmd_vhs

    echo ""
    echo "========================================="
    echo "  MUSIC VIDEO SETUP COMPLETE"
    echo "========================================="
    echo ""
    echo "Effects added:"
    echo "  ✓ Strobe flash"
    echo "  ✓ Blue color flash"
    echo "  ✓ VHS/retro look"
    echo ""
    echo "Additional commands:"
    echo "  $0 beat-marker      # Mark beats"
    echo "  $0 trippy           # Psychedelic effect"
    echo "  $0 lyrics 'Text'    # Add lyrics"
    echo "  $0 split-screen     # Performance grid"
}

# Main
case "$1" in
    new)          cmd_new "$2" "$3" ;;
    beat-marker)  cmd_beat_marker ;;
    strobe)       cmd_strobe ;;
    color-flash)  cmd_color_flash "$2" ;;
    split-screen) cmd_split_screen ;;
    vhs)          cmd_vhs ;;
    trippy)       cmd_trippy ;;
    lyrics)       cmd_lyrics "$2" ;;
    credits)      cmd_credits ;;
    full)         cmd_full "$2" ;;
    help|--help|-h|"") show_help ;;
    *)            echo "Unknown: $1"; show_help; exit 1 ;;
esac
