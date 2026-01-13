#!/bin/bash
# Thumbnail Generator
# Create thumbnails with text overlays

set -e

RESOLVE_CMD="$HOME/bin/resolve"

show_help() {
    echo "Thumbnail Generator"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  capture              Capture current frame"
    echo "  setup                Setup thumbnail composition"
    echo "  text <title>         Add bold title text"
    echo "  face-zoom            Zoom on face area"
    echo "  border <color>       Add colored border"
    echo "  emoji <emoji>        Add large emoji"
    echo "  arrow                Add attention arrow"
    echo "  export               Export as PNG/JPEG"
    echo "  youtube              YouTube thumbnail template (1280x720)"
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

cmd_capture() {
    echo "Capturing thumbnail frame..."
    ensure_resolve
    $RESOLVE_CMD edit
    sleep 0.5

    echo ""
    echo "Steps to capture:"
    echo "  1. Position playhead on best frame"
    echo "  2. Right-click viewer → Grab Still"
    echo "  3. Or use: File → Export → Current Frame as Still"
    echo ""
    echo "Tip: Look for expressive faces, action, or key moments"
}

cmd_setup() {
    echo "Setting up thumbnail composition..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Set to thumbnail resolution
    comp:SetAttrs({
        COMPN_GlobalStart = 0,
        COMPN_GlobalEnd = 0,
        COMPN_RenderStart = 0,
        COMPN_RenderEnd = 0
    })

    -- Background (video frame)
    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "Thumb_Background"})
    bg.Width = 1280
    bg.Height = 720

    -- Darken edges for text pop
    local vignette = comp:AddTool("EllipseMask")
    vignette:SetAttrs({TOOLS_Name = "Thumb_Vignette"})
    vignette.Width = 2.0
    vignette.Height = 1.5
    vignette.SoftEdge = 0.5

    local vigBG = comp:AddTool("Background")
    vigBG:SetAttrs({TOOLS_Name = "Thumb_VignetteBG"})
    vigBG.TopLeftRed = 0
    vigBG.TopLeftGreen = 0
    vigBG.TopLeftBlue = 0
    vigBG.TopLeftAlpha = 0.3

    comp:Unlock()
    print("✓ Thumbnail composition ready (1280x720)")
end'
    echo "✓ Thumbnail composition setup complete"
}

cmd_text() {
    local title="${1:-WATCH THIS}"
    echo "Adding title: $title"
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Main title (big, bold, with outline)
    local text = comp:AddTool('TextPlus')
    text:SetAttrs({TOOLS_Name = 'Thumb_Title'})
    text.StyledText = '$title'
    text.Font = 'Arial Black'
    text.Size = 0.12
    text.Center = {0.5, 0.75}
    text.Red1 = 1
    text.Green1 = 1
    text.Blue1 = 0  -- Yellow

    -- Thick outline
    text.ElementShape1 = 2
    text.Thickness1 = 0.15
    text.Red2 = 0
    text.Green2 = 0
    text.Blue2 = 0

    -- Drop shadow
    local shadow = comp:AddTool('DropShadow')
    shadow:SetAttrs({TOOLS_Name = 'Thumb_Shadow'})
    shadow.ShadowOffset = {0.008, -0.008}
    shadow.Softness = 10
    shadow.ShadowDensity = 0.8

    comp:Unlock()
    print('✓ Title added: $title')
end"
    echo "✓ Title text added"
}

cmd_face_zoom() {
    echo "Adding face zoom..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local zoom = comp:AddTool("Transform")
    zoom:SetAttrs({TOOLS_Name = "Thumb_FaceZoom"})
    zoom.Size = 1.3
    zoom.Center = {0.5, 0.55}  -- Slightly up for face

    comp:Unlock()
    print("✓ Face zoom added")
    print("  Adjust Center to focus on face")
end'
    echo "✓ Face zoom added"
}

cmd_border() {
    local color="${1:-red}"
    local r=1 g=0 b=0

    case "$color" in
        red)     r=1;   g=0;   b=0 ;;
        yellow)  r=1;   g=1;   b=0 ;;
        green)   r=0;   g=1;   b=0 ;;
        blue)    r=0;   g=0.5; b=1 ;;
        white)   r=1;   g=1;   b=1 ;;
    esac

    echo "Adding $color border..."
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local borderBG = comp:AddTool('Background')
    borderBG:SetAttrs({TOOLS_Name = 'Thumb_Border'})
    borderBG.TopLeftRed = $r
    borderBG.TopLeftGreen = $g
    borderBG.TopLeftBlue = $b
    borderBG.Width = 1280
    borderBG.Height = 720

    local innerMask = comp:AddTool('RectangleMask')
    innerMask:SetAttrs({TOOLS_Name = 'Thumb_BorderMask'})
    innerMask.Width = 0.97
    innerMask.Height = 0.95
    innerMask.Invert = true

    comp:Unlock()
    print('✓ $color border added')
end"
    echo "✓ Border added"
}

cmd_emoji() {
    local emoji="${1:-😱}"
    echo "Adding emoji: $emoji"
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local em = comp:AddTool('TextPlus')
    em:SetAttrs({TOOLS_Name = 'Thumb_Emoji'})
    em.StyledText = '$emoji'
    em.Size = 0.2
    em.Center = {0.85, 0.8}

    comp:Unlock()
    print('✓ Emoji added: $emoji')
end"
    echo "✓ Emoji added"
}

cmd_arrow() {
    echo "Adding attention arrow..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local arrow = comp:AddTool("TextPlus")
    arrow:SetAttrs({TOOLS_Name = "Thumb_Arrow"})
    arrow.StyledText = "▶"
    arrow.Font = "Arial"
    arrow.Size = 0.15
    arrow.Center = {0.15, 0.5}
    arrow.Red1 = 1
    arrow.Green1 = 0
    arrow.Blue1 = 0

    -- Glow
    local glow = comp:AddTool("SoftGlow")
    glow:SetAttrs({TOOLS_Name = "Thumb_ArrowGlow"})
    glow.Threshold = 0.5
    glow.Gain = 0.5

    comp:Unlock()
    print("✓ Arrow added")
end'
    echo "✓ Arrow added"
}

cmd_export() {
    echo "Exporting thumbnail..."
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1

    echo ""
    echo "Export settings for thumbnail:"
    echo "  Format: JPEG or PNG"
    echo "  Resolution: 1280x720 (YouTube)"
    echo "  Quality: Maximum"
    echo ""
    echo "Quick export:"
    echo "  Color page → Gallery → Right-click → Export"
    echo "  Or: File → Export → Current Frame as Still"
}

cmd_youtube() {
    echo "=== YouTube Thumbnail Template ==="

    cmd_setup
    sleep 1

    cmd_face_zoom
    sleep 1

    cmd_text "TITLE HERE"
    sleep 1

    cmd_border "red"

    echo ""
    echo "YouTube thumbnail ready!"
    echo "  - 1280x720 resolution"
    echo "  - Face zoom applied"
    echo "  - Bold title with outline"
    echo "  - Red border"
    echo ""
    echo "Export as JPEG < 2MB"
}

# Main
case "$1" in
    capture)     cmd_capture ;;
    setup)       cmd_setup ;;
    text)        cmd_text "$2" ;;
    face-zoom)   cmd_face_zoom ;;
    border)      cmd_border "$2" ;;
    emoji)       cmd_emoji "$2" ;;
    arrow)       cmd_arrow ;;
    export)      cmd_export ;;
    youtube)     cmd_youtube ;;
    help|--help|-h|"") show_help ;;
    *)           echo "Unknown: $1"; show_help; exit 1 ;;
esac
