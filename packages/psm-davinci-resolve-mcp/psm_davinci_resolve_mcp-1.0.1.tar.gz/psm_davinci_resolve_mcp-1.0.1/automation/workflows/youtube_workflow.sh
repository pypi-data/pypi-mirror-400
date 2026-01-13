#!/bin/bash
# YouTube Video Production Workflow
# Full automation: Import → Edit → Color → Graphics → Export

set -e

RESOLVE_CMD="$HOME/bin/resolve"
SCRIPTS_DIR="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp"

show_help() {
    echo "YouTube Video Production Workflow"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  new <video_path>     Start new YouTube video project"
    echo "  intro                Add intro sequence"
    echo "  lower-third <name>   Add lower third with name"
    echo "  subscribe            Add subscribe reminder"
    echo "  end-screen           Add end screen template"
    echo "  color                Apply YouTube-optimized color grade"
    echo "  export               Set up YouTube export preset"
    echo "  full <video_path>    Full automated workflow"
    echo ""
    echo "Example:"
    echo "  $0 full ~/Videos/raw_footage.mp4"
}

ensure_resolve() {
    if ! pgrep -x "Resolve" > /dev/null; then
        echo "Starting DaVinci Resolve..."
        $RESOLVE_CMD launch
        sleep 5
    fi
}

run_fusion_script() {
    local script_name="$1"
    echo "$script_name" | pbcopy

    osascript << 'EOF'
tell application "DaVinci Resolve" to activate
delay 0.3
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
    local video_path="$1"

    if [ -z "$video_path" ]; then
        echo "Usage: $0 new /path/to/video.mp4"
        exit 1
    fi

    echo "=== Creating New YouTube Project ==="
    ensure_resolve

    # Import media
    echo "1. Importing footage..."
    $RESOLVE_CMD media
    sleep 1

    osascript << EOF
tell application "DaVinci Resolve" to activate
delay 0.5
tell application "System Events"
    tell process "Resolve"
        keystroke "i" using command down
        delay 1
        keystroke "g" using {command down, shift down}
        delay 0.5
        keystroke "$video_path"
        delay 0.3
        key code 36
        delay 0.5
        key code 36
    end tell
end tell
EOF

    sleep 2
    echo "   ✓ Footage imported"

    # Add to timeline
    echo "2. Creating timeline..."
    $RESOLVE_CMD edit
    sleep 1

    osascript << 'EOF'
tell application "System Events"
    tell process "Resolve"
        key code 111
    end tell
end tell
EOF

    sleep 1
    echo "   ✓ Timeline created"
    echo ""
    echo "Project ready! Use other commands to add elements."
}

cmd_intro() {
    echo "Adding intro sequence..."
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    # Create intro text
    cat << 'LUA' | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local text = comp:AddTool("TextPlus")
    text:SetAttrs({TOOLS_Name = "IntroTitle"})
    text.StyledText = "YOUR VIDEO TITLE"
    text.Font = "Arial Black"
    text.Size = 0.12
    text.Center = {0.5, 0.5}

    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "IntroBG"})
    bg.TopLeftRed = 0.1
    bg.TopLeftGreen = 0.1
    bg.TopLeftBlue = 0.1

    comp:Unlock()
    print("✓ Intro template added - customize IntroTitle text")
end
LUA

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
    echo "✓ Intro sequence added"
}

cmd_lower_third() {
    local name="${1:-Your Name}"

    echo "Adding lower third for: $name"
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    cat << LUA | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "LowerThirdBG"})
    bg.TopLeftRed = 0.15
    bg.TopLeftGreen = 0.15
    bg.TopLeftBlue = 0.15
    bg.TopLeftAlpha = 0.85

    local title = comp:AddTool("TextPlus")
    title:SetAttrs({TOOLS_Name = "LowerThirdName"})
    title.StyledText = "$name"
    title.Font = "Arial Bold"
    title.Size = 0.045
    title.Center = {0.2, 0.1}

    comp:Unlock()
    print("✓ Lower third added for: $name")
end
LUA

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
    echo "✓ Lower third added"
}

cmd_subscribe() {
    echo "Adding subscribe reminder..."
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    cat << 'LUA' | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local sub = comp:AddTool("TextPlus")
    sub:SetAttrs({TOOLS_Name = "SubscribeButton"})
    sub.StyledText = "SUBSCRIBE"
    sub.Font = "Arial Black"
    sub.Size = 0.035
    sub.Center = {0.85, 0.1}
    sub.Red1 = 1
    sub.Green1 = 0.2
    sub.Blue1 = 0.2

    local bell = comp:AddTool("TextPlus")
    bell:SetAttrs({TOOLS_Name = "BellIcon"})
    bell.StyledText = "🔔"
    bell.Size = 0.04
    bell.Center = {0.92, 0.1}

    comp:Unlock()
    print("✓ Subscribe reminder added")
end
LUA

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
    echo "✓ Subscribe reminder added"
}

cmd_end_screen() {
    echo "Adding end screen template..."
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    cat << 'LUA' | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "EndScreenBG"})
    bg.TopLeftRed = 0.05
    bg.TopLeftGreen = 0.05
    bg.TopLeftBlue = 0.08

    local thanks = comp:AddTool("TextPlus")
    thanks:SetAttrs({TOOLS_Name = "ThanksText"})
    thanks.StyledText = "Thanks for watching!"
    thanks.Font = "Arial Bold"
    thanks.Size = 0.06
    thanks.Center = {0.5, 0.7}

    local video1 = comp:AddTool("Background")
    video1:SetAttrs({TOOLS_Name = "VideoSlot1"})
    video1.TopLeftRed = 0.2
    video1.TopLeftGreen = 0.2
    video1.TopLeftBlue = 0.2

    local video2 = comp:AddTool("Background")
    video2:SetAttrs({TOOLS_Name = "VideoSlot2"})
    video2.TopLeftRed = 0.2
    video2.TopLeftGreen = 0.2
    video2.TopLeftBlue = 0.2

    comp:Unlock()
    print("✓ End screen template added")
    print("  Replace VideoSlot1/2 with your video thumbnails")
end
LUA

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
    echo "✓ End screen added"
}

cmd_color() {
    echo "Applying YouTube-optimized color grade..."
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    cat << 'LUA' | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Contrast boost for YouTube compression
    local contrast = comp:AddTool("ColorCorrector")
    contrast:SetAttrs({TOOLS_Name = "YT_Contrast"})
    contrast.MasterRGBContrast = 1.1

    -- Saturation boost (YouTube desaturates)
    local sat = comp:AddTool("ColorCorrector")
    sat:SetAttrs({TOOLS_Name = "YT_Saturation"})
    sat.MasterSaturation = 1.15

    -- Sharpening for compression
    local sharp = comp:AddTool("UnsharpMask")
    sharp:SetAttrs({TOOLS_Name = "YT_Sharpen"})
    sharp.Size = 2
    sharp.Gain = 0.4

    comp:Unlock()
    print("✓ YouTube color grade applied")
    print("  - Contrast boosted for compression")
    print("  - Saturation increased 15%")
    print("  - Sharpening added")
end
LUA

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
    echo "✓ YouTube color grade applied"
}

cmd_export() {
    echo "Setting up YouTube export..."
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1

    echo ""
    echo "YouTube Export Settings:"
    echo "========================"
    echo "Format: MP4"
    echo "Codec: H.264"
    echo "Resolution: 1920x1080 (or 3840x2160 for 4K)"
    echo "Frame Rate: Match source"
    echo "Quality: Best / Bitrate 20-50 Mbps"
    echo "Audio: AAC 320kbps"
    echo ""
    echo "✓ Deliver page ready - configure and render"
}

cmd_full() {
    local video_path="$1"

    if [ -z "$video_path" ]; then
        echo "Usage: $0 full /path/to/video.mp4"
        exit 1
    fi

    echo "========================================"
    echo "  FULL YOUTUBE WORKFLOW AUTOMATION"
    echo "========================================"
    echo ""

    cmd_new "$video_path"
    echo ""

    sleep 1
    cmd_intro
    echo ""

    sleep 1
    cmd_lower_third "Your Channel Name"
    echo ""

    sleep 1
    cmd_subscribe
    echo ""

    sleep 1
    cmd_color
    echo ""

    sleep 1
    cmd_export

    echo ""
    echo "========================================"
    echo "  WORKFLOW COMPLETE!"
    echo "========================================"
    echo ""
    echo "Added:"
    echo "  ✓ Imported footage"
    echo "  ✓ Created timeline"
    echo "  ✓ Intro sequence"
    echo "  ✓ Lower third"
    echo "  ✓ Subscribe reminder"
    echo "  ✓ YouTube color grade"
    echo ""
    echo "Next steps:"
    echo "  1. Edit your content on Edit page"
    echo "  2. Add end screen: $0 end-screen"
    echo "  3. Fine-tune in Color page"
    echo "  4. Export from Deliver page"
}

# Main
case "$1" in
    new)        cmd_new "$2" ;;
    intro)      cmd_intro ;;
    lower-third) cmd_lower_third "$2" ;;
    subscribe)  cmd_subscribe ;;
    end-screen) cmd_end_screen ;;
    color)      cmd_color ;;
    export)     cmd_export ;;
    full)       cmd_full "$2" ;;
    help|--help|-h|"") show_help ;;
    *)          echo "Unknown command: $1"; show_help; exit 1 ;;
esac
