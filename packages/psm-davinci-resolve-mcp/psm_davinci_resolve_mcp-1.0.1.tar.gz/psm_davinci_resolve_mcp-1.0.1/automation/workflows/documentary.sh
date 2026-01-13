#!/bin/bash
# Documentary Production Workflow
# Interview setups, archival footage, narration

set -e

RESOLVE_CMD="$HOME/bin/resolve"

show_help() {
    echo "Documentary Production Workflow"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  new <video>              Start documentary project"
    echo "  interview <name>         Setup interview frame"
    echo "  two-cam                  Two camera interview setup"
    echo "  archival                 Archival footage treatment"
    echo "  photo-ken-burns          Ken Burns photo animation"
    echo "  title-card <text>        Chapter title card"
    echo "  location <text>          Location/date super"
    echo "  quote <text> <attr>      Quote with attribution"
    echo "  narration-ducking        Audio ducking setup"
    echo "  credits-doc              Documentary end credits"
    echo "  full <video>             Full documentary setup"
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
    echo "=== Creating Documentary Project ==="
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
    echo "✓ Documentary project created"
}

cmd_interview() {
    local name="${1:-Interview Subject}"
    echo "Setting up interview frame for: $name"
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Interview framing (rule of thirds)
    local frame = comp:AddTool('Transform')
    frame:SetAttrs({TOOLS_Name = 'InterviewFrame'})
    frame.Size = 1.1
    frame.Center = {0.45, 0.52}  -- Offset for look room

    -- Name lower third
    local nameBG = comp:AddTool('Background')
    nameBG:SetAttrs({TOOLS_Name = 'NameBG'})
    nameBG.TopLeftRed = 0.1
    nameBG.TopLeftGreen = 0.1
    nameBG.TopLeftBlue = 0.1
    nameBG.TopLeftAlpha = 0.8

    local nameText = comp:AddTool('TextPlus')
    nameText:SetAttrs({TOOLS_Name = 'InterviewName'})
    nameText.StyledText = '$name'
    nameText.Font = 'Arial'
    nameText.Size = 0.035
    nameText.Center = {0.2, 0.1}

    comp:Unlock()
    print('✓ Interview setup: $name')
end"
    echo "✓ Interview frame setup complete"
}

cmd_two_cam() {
    echo "Setting up two-camera interview..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Camera A (wide)
    local camA = comp:AddTool("Transform")
    camA:SetAttrs({TOOLS_Name = "CamA_Wide"})
    camA.Size = 1.0
    camA.Center = {0.5, 0.5}

    -- Camera B (tight)
    local camB = comp:AddTool("Transform")
    camB:SetAttrs({TOOLS_Name = "CamB_Tight"})
    camB.Size = 1.4
    camB.Center = {0.45, 0.55}

    -- Dissolve for switching
    local dissolve = comp:AddTool("Dissolve")
    dissolve:SetAttrs({TOOLS_Name = "CamSwitch"})
    dissolve.Mix = 0  -- 0=CamA, 1=CamB

    comp:Unlock()
    print("✓ Two-camera setup ready")
    print("  CamA_Wide: Full shot")
    print("  CamB_Tight: Close-up")
    print("  Animate CamSwitch.Mix to cut between")
end'
    echo "✓ Two-camera setup complete"
}

cmd_archival() {
    echo "Adding archival footage treatment..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Desaturate
    local desat = comp:AddTool("ColorCorrector")
    desat:SetAttrs({TOOLS_Name = "Archival_Desat"})
    desat.MasterSaturation = 0.3

    -- Add grain
    local grain = comp:AddTool("FilmGrain")
    grain:SetAttrs({TOOLS_Name = "Archival_Grain"})
    grain.Strength = 0.5
    grain.Size = 2.5

    -- Vignette
    local vignette = comp:AddTool("EllipseMask")
    vignette:SetAttrs({TOOLS_Name = "Archival_Vignette"})
    vignette.SoftEdge = 0.5
    vignette.Width = 1.6
    vignette.Height = 1.2

    -- Slight damage/flicker
    local flicker = comp:AddTool("BrightnessContrast")
    flicker:SetAttrs({TOOLS_Name = "Archival_Flicker"})
    flicker.Gain = 1.0  -- Animate 0.95-1.05 randomly

    comp:Unlock()
    print("✓ Archival treatment added")
    print("  Animate Archival_Flicker.Gain for authentic look")
end'
    echo "✓ Archival footage treatment added"
}

cmd_photo_ken_burns() {
    echo "Adding Ken Burns photo animation..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Photo container
    local photo = comp:AddTool("Transform")
    photo:SetAttrs({TOOLS_Name = "KenBurns_Photo"})
    photo.Size = 1.0  -- Start value
    photo.Center = {0.5, 0.5}  -- Start position

    -- Animate:
    -- Size: 1.0 → 1.15 (slow zoom in)
    -- OR Center: {0.4, 0.5} → {0.6, 0.5} (pan)

    -- Subtle edge softening
    local soft = comp:AddTool("Blur")
    soft:SetAttrs({TOOLS_Name = "KenBurns_Soft"})
    soft.XBlurSize = 0.5
    soft.YBlurSize = 0.5

    comp:Unlock()
    print("✓ Ken Burns setup ready")
    print("")
    print("Animation presets:")
    print("  Zoom In: Size 1.0 → 1.15")
    print("  Zoom Out: Size 1.15 → 1.0")
    print("  Pan Left: Center.X 0.6 → 0.4")
    print("  Pan Right: Center.X 0.4 → 0.6")
end'
    echo "✓ Ken Burns animation setup added"
}

cmd_title_card() {
    local text="${1:-CHAPTER ONE}"
    echo "Adding title card: $text"
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local bg = comp:AddTool('Background')
    bg:SetAttrs({TOOLS_Name = 'TitleCardBG'})
    bg.TopLeftRed = 0.02
    bg.TopLeftGreen = 0.02
    bg.TopLeftBlue = 0.02

    local title = comp:AddTool('TextPlus')
    title:SetAttrs({TOOLS_Name = 'ChapterTitle'})
    title.StyledText = '$text'
    title.Font = 'Georgia'
    title.Size = 0.07
    title.Center = {0.5, 0.5}

    -- Fade line decoration
    local line = comp:AddTool('Background')
    line:SetAttrs({TOOLS_Name = 'TitleLine'})
    line.TopLeftRed = 0.5
    line.TopLeftGreen = 0.5
    line.TopLeftBlue = 0.5

    comp:Unlock()
    print('✓ Title card: $text')
end"
    echo "✓ Title card added"
}

cmd_location() {
    local text="${1:-New York City, 2024}"
    echo "Adding location super: $text"
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local loc = comp:AddTool('TextPlus')
    loc:SetAttrs({TOOLS_Name = 'LocationSuper'})
    loc.StyledText = '$text'
    loc.Font = 'Arial'
    loc.Size = 0.03
    loc.Center = {0.15, 0.1}
    loc.Red1 = 1
    loc.Green1 = 1
    loc.Blue1 = 1

    comp:Unlock()
    print('✓ Location: $text')
end"
    echo "✓ Location super added"
}

cmd_quote() {
    local text="${1:-This is a powerful quote.}"
    local attr="${2:-- Source Name}"
    echo "Adding quote..."
    run_lua "local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local bg = comp:AddTool('Background')
    bg:SetAttrs({TOOLS_Name = 'QuoteBG'})
    bg.TopLeftRed = 0.05
    bg.TopLeftGreen = 0.05
    bg.TopLeftBlue = 0.05
    bg.TopLeftAlpha = 0.9

    local quote = comp:AddTool('TextPlus')
    quote:SetAttrs({TOOLS_Name = 'QuoteText'})
    quote.StyledText = '\"$text\"'
    quote.Font = 'Georgia Italic'
    quote.Size = 0.045
    quote.Center = {0.5, 0.55}

    local attribution = comp:AddTool('TextPlus')
    attribution:SetAttrs({TOOLS_Name = 'QuoteAttr'})
    attribution.StyledText = '$attr'
    attribution.Font = 'Arial'
    attribution.Size = 0.025
    attribution.Center = {0.5, 0.4}
    attribution.Red1 = 0.7
    attribution.Green1 = 0.7
    attribution.Blue1 = 0.7

    comp:Unlock()
    print('✓ Quote added')
end"
    echo "✓ Quote added"
}

cmd_credits_doc() {
    echo "Adding documentary credits..."
    run_lua 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "DocCreditsBG"})
    bg.TopLeftRed = 0
    bg.TopLeftGreen = 0
    bg.TopLeftBlue = 0

    local credits = comp:AddTool("TextPlus")
    credits:SetAttrs({TOOLS_Name = "DocCredits"})
    credits.StyledText = [[
A Film By
Director Name

Executive Producer
Producer Name

Director of Photography
DP Name

Editor
Editor Name

Original Music
Composer Name

Archival Footage Courtesy Of
Archive Name

Special Thanks
Name 1
Name 2
Name 3

© 2024
]]
    credits.Font = "Georgia"
    credits.Size = 0.035
    credits.Center = {0.5, -0.5}

    comp:Unlock()
    print("✓ Documentary credits added")
    print("  Animate Center.Y: -0.5 → 1.5")
end'
    echo "✓ Documentary credits added"
}

cmd_full() {
    local video="$1"

    echo "========================================="
    echo "  DOCUMENTARY WORKFLOW"
    echo "========================================="
    echo ""

    cmd_new "$video"
    sleep 1

    cmd_interview "Interview Subject"
    sleep 1

    cmd_archival
    sleep 1

    cmd_title_card "INTRODUCTION"

    echo ""
    echo "========================================="
    echo "  DOCUMENTARY SETUP COMPLETE"
    echo "========================================="
    echo ""
    echo "Added:"
    echo "  ✓ Interview framing"
    echo "  ✓ Archival footage treatment"
    echo "  ✓ Title card"
    echo ""
    echo "Additional tools:"
    echo "  $0 two-cam"
    echo "  $0 photo-ken-burns"
    echo "  $0 location 'Place, Date'"
    echo "  $0 quote 'Text' '- Author'"
}

# Main
case "$1" in
    new)              cmd_new "$2" ;;
    interview)        cmd_interview "$2" ;;
    two-cam)          cmd_two_cam ;;
    archival)         cmd_archival ;;
    photo-ken-burns)  cmd_photo_ken_burns ;;
    title-card)       cmd_title_card "$2" ;;
    location)         cmd_location "$2" ;;
    quote)            cmd_quote "$2" "$3" ;;
    narration-ducking) echo "Use Fairlight page > Ducking for narration" ;;
    credits-doc)      cmd_credits_doc ;;
    full)             cmd_full "$2" ;;
    help|--help|-h|"") show_help ;;
    *)                echo "Unknown: $1"; show_help; exit 1 ;;
esac
