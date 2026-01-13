#!/bin/bash
# Vlog Production Workflow
# Quick edits, jump cuts, b-roll integration

set -e

RESOLVE_CMD="$HOME/bin/resolve"

show_help() {
    echo "Vlog Production Workflow"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  new <video>          Start new vlog project"
    echo "  talking-head         Setup for talking head shots"
    echo "  broll                Add b-roll overlay setup"
    echo "  zoom-in              Add punch-in zoom effect"
    echo "  zoom-out             Add zoom out effect"
    echo "  warp <speed>         Speed warp (2x, 4x, 0.5x)"
    echo "  text-pop <text>      Pop-up text annotation"
    echo "  arrow <direction>    Add arrow pointer"
    echo "  emoji <emoji>        Add animated emoji"
    echo "  whoosh               Add whoosh transition sound cue"
    echo "  thumbnail            Export thumbnail frame"
    echo "  full <video>         Full vlog workflow"
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

    echo "=== Creating New Vlog Project ==="
    ensure_resolve

    $RESOLVE_CMD media
    sleep 1

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

    osascript << 'EOF'
tell application "System Events"
    tell process "Resolve"
        key code 111
    end tell
end tell
EOF

    echo "✓ Vlog project created"
}

cmd_talking_head() {
    echo "Setting up talking head framing..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Rule of thirds guide
    local guide = comp:AddTool("Background")
    guide:SetAttrs({TOOLS_Name = "ThirdsGuide"})
    guide.TopLeftAlpha = 0.3
    guide.TopLeftRed = 0.5
    guide.TopLeftGreen = 0.5
    guide.TopLeftBlue = 0.5

    -- Slight zoom for tighter framing
    local zoom = comp:AddTool("Transform")
    zoom:SetAttrs({TOOLS_Name = "TightFrame"})
    zoom.Size = 1.1
    zoom.Center = {0.5, 0.55}  -- Slightly up for headroom

    -- Face tracking placeholder
    local tracker = comp:AddTool("Tracker")
    tracker:SetAttrs({TOOLS_Name = "FaceTrack"})

    comp:Unlock()
    print("✓ Talking head setup ready")
    print("  Adjust TightFrame for framing")
    print("  Use FaceTrack for auto-framing")
end'
    echo "✓ Talking head setup complete"
}

cmd_broll() {
    echo "Adding b-roll overlay setup..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- B-roll merge layer
    local merge = comp:AddTool("Merge")
    merge:SetAttrs({TOOLS_Name = "BRollMerge"})
    merge.Blend = 1

    -- B-roll transform (for positioning)
    local transform = comp:AddTool("Transform")
    transform:SetAttrs({TOOLS_Name = "BRollTransform"})
    transform.Size = 1.0

    -- Ken Burns effect
    local kb = comp:AddTool("Transform")
    kb:SetAttrs({TOOLS_Name = "KenBurns"})
    kb.Size = 1.05  -- Animate to 1.15 for slow zoom
    kb.Center = {0.5, 0.5}  -- Animate for pan

    comp:Unlock()
    print("✓ B-roll overlay ready")
    print("  Connect b-roll to BRollTransform")
    print("  Animate KenBurns for movement")
end'
    echo "✓ B-roll overlay setup added"
}

cmd_zoom_in() {
    echo "Adding punch-in zoom..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local zoom = comp:AddTool("Transform")
    zoom:SetAttrs({TOOLS_Name = "PunchIn"})
    zoom.Size = 1.3  -- 30% zoom
    zoom.Center = {0.5, 0.55}  -- Focus on face

    comp:Unlock()
    print("✓ Punch-in zoom added (1.3x)")
    print("  Use for emphasis on key points")
end'
    echo "✓ Punch-in zoom added"
}

cmd_zoom_out() {
    echo "Adding zoom out..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local zoom = comp:AddTool("Transform")
    zoom:SetAttrs({TOOLS_Name = "ZoomOut"})
    zoom.Size = 0.8
    zoom.Center = {0.5, 0.5}

    comp:Unlock()
    print("✓ Zoom out added (0.8x)")
end'
    echo "✓ Zoom out added"
}

cmd_warp() {
    local speed="${1:-2}"
    echo "Adding speed warp (${speed}x)..."
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local time = comp:AddTool('TimeSpeed')
    time:SetAttrs({TOOLS_Name = 'SpeedWarp_${speed}x'})
    time.Speed = $speed
    time.InterpolateMethod = 2  -- Optical flow

    comp:Unlock()
    print('✓ Speed warp: ${speed}x')
end"
    echo "✓ Speed warp (${speed}x) added"
}

cmd_text_pop() {
    local text="${1:-WOW!}"
    echo "Adding pop-up text: $text"
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local pop = comp:AddTool('TextPlus')
    pop:SetAttrs({TOOLS_Name = 'PopText'})
    pop.StyledText = '$text'
    pop.Font = 'Arial Black'
    pop.Size = 0.1
    pop.Center = {0.5, 0.5}
    pop.Red1 = 1
    pop.Green1 = 1
    pop.Blue1 = 0  -- Yellow

    -- Outline
    pop.ElementShape1 = 2  -- Circle
    pop.Thickness1 = 0.1
    pop.Red2 = 0
    pop.Green2 = 0
    pop.Blue2 = 0

    -- Scale animation hint
    local transform = comp:AddTool('Transform')
    transform:SetAttrs({TOOLS_Name = 'PopScale'})
    transform.Size = 1.0  -- Animate 0→1.2→1 for pop

    comp:Unlock()
    print('✓ Pop text: $text')
    print('  Animate PopScale.Size: 0→1.2→1')
end"
    echo "✓ Pop-up text added"
}

cmd_arrow() {
    local dir="${1:-right}"
    echo "Adding arrow pointing $dir..."
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local arrow = comp:AddTool('TextPlus')
    arrow:SetAttrs({TOOLS_Name = 'Arrow_$dir'})

    local arrows = {
        right = '→',
        left = '←',
        up = '↑',
        down = '↓'
    }
    arrow.StyledText = arrows['$dir'] or '→'
    arrow.Font = 'Arial'
    arrow.Size = 0.15
    arrow.Center = {0.7, 0.5}
    arrow.Red1 = 1
    arrow.Green1 = 0
    arrow.Blue1 = 0

    comp:Unlock()
    print('✓ Arrow added: $dir')
end"
    echo "✓ Arrow added"
}

cmd_emoji() {
    local emoji="${1:-😂}"
    echo "Adding emoji: $emoji"
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local em = comp:AddTool('TextPlus')
    em:SetAttrs({TOOLS_Name = 'Emoji'})
    em.StyledText = '$emoji'
    em.Size = 0.12
    em.Center = {0.8, 0.8}

    -- Bounce animation
    local transform = comp:AddTool('Transform')
    transform:SetAttrs({TOOLS_Name = 'EmojiBounce'})
    transform.Size = 1.0  -- Animate for bounce

    comp:Unlock()
    print('✓ Emoji added: $emoji')
end"
    echo "✓ Emoji added"
}

cmd_thumbnail() {
    echo "Setting up thumbnail export..."
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1

    echo "Thumbnail Export Settings:"
    echo "========================="
    echo "Format: JPEG or PNG"
    echo "Resolution: 1920x1080 (or 1280x720)"
    echo "Export: Single frame at playhead"
    echo ""
    echo "✓ Go to best frame, then export still"
}

cmd_full() {
    local video="$1"

    echo "========================================="
    echo "  VLOG WORKFLOW"
    echo "========================================="
    echo ""

    cmd_new "$video"
    sleep 1

    cmd_talking_head
    sleep 1

    cmd_broll
    sleep 1

    cmd_zoom_in

    echo ""
    echo "========================================="
    echo "  VLOG SETUP COMPLETE"
    echo "========================================="
    echo ""
    echo "Ready:"
    echo "  ✓ Talking head framing"
    echo "  ✓ B-roll overlay layer"
    echo "  ✓ Punch-in zoom"
    echo ""
    echo "Quick effects:"
    echo "  $0 text-pop 'AMAZING!'"
    echo "  $0 warp 2              # 2x speed"
    echo "  $0 emoji '🔥'"
    echo "  $0 thumbnail"
}

# Main
case "$1" in
    new)          cmd_new "$2" ;;
    talking-head) cmd_talking_head ;;
    broll)        cmd_broll ;;
    zoom-in)      cmd_zoom_in ;;
    zoom-out)     cmd_zoom_out ;;
    warp)         cmd_warp "$2" ;;
    text-pop)     cmd_text_pop "$2" ;;
    arrow)        cmd_arrow "$2" ;;
    emoji)        cmd_emoji "$2" ;;
    whoosh)       echo "Add whoosh sound from Effects Library" ;;
    thumbnail)    cmd_thumbnail ;;
    full)         cmd_full "$2" ;;
    help|--help|-h|"") show_help ;;
    *)            echo "Unknown: $1"; show_help; exit 1 ;;
esac
