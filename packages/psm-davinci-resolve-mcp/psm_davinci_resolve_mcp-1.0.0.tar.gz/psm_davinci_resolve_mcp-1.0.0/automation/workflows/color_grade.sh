#!/bin/bash
# Color Grading Workflow
# Quick color presets and adjustments

set -e

RESOLVE_CMD="$HOME/bin/resolve"

show_help() {
    echo "Color Grading Workflow"
    echo ""
    echo "Usage: $0 <preset>"
    echo ""
    echo "Presets:"
    echo "  cinematic        Film-style warm shadows, cool highlights"
    echo "  teal-orange      Popular blockbuster look"
    echo "  vintage          Faded, warm, low contrast"
    echo "  high-contrast    Punchy, vibrant"
    echo "  black-white      Cinematic B&W conversion"
    echo "  day-for-night    Simulate night from day footage"
    echo "  warm             Overall warm tone"
    echo "  cool             Overall cool/blue tone"
    echo "  bleach-bypass    Desaturated, high contrast"
    echo ""
}

ensure_resolve() {
    if ! pgrep -x "Resolve" > /dev/null; then
        $RESOLVE_CMD launch
        sleep 5
    fi
}

apply_grade() {
    local script="$1"
    ensure_resolve
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

cmd_cinematic() {
    echo "Applying cinematic grade..."
    apply_grade 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local cc = comp:AddTool("ColorCorrector")
    cc:SetAttrs({TOOLS_Name = "CinematicGrade"})
    cc.MasterRGBContrast = 1.15
    cc.MasterSaturation = 0.9
    cc.HighlightsRGBGain = {0.95, 0.98, 1.05}
    cc.ShadowsRGBGain = {1.08, 0.98, 0.92}
    cc.MasterRGBLift = 0.02
    comp:Unlock()
    print("✓ Cinematic grade applied")
end'
    echo "✓ Cinematic grade applied"
}

cmd_teal_orange() {
    echo "Applying teal & orange grade..."
    apply_grade 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local cc = comp:AddTool("ColorCorrector")
    cc:SetAttrs({TOOLS_Name = "TealOrangeGrade"})
    cc.MasterRGBContrast = 1.1
    cc.MasterSaturation = 1.1
    cc.HighlightsRGBGain = {1.1, 0.95, 0.85}
    cc.ShadowsRGBGain = {0.8, 0.95, 1.15}
    cc.MidtonesRGBGain = {1.0, 0.98, 0.95}
    comp:Unlock()
    print("✓ Teal & Orange grade applied")
end'
    echo "✓ Teal & orange grade applied"
}

cmd_vintage() {
    echo "Applying vintage grade..."
    apply_grade 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local cc = comp:AddTool("ColorCorrector")
    cc:SetAttrs({TOOLS_Name = "VintageGrade"})
    cc.MasterRGBContrast = 0.85
    cc.MasterSaturation = 0.7
    cc.MasterRGBGain = {1.05, 1.0, 0.9}
    cc.MasterRGBLift = 0.08
    local grain = comp:AddTool("FilmGrain")
    grain:SetAttrs({TOOLS_Name = "VintageGrain"})
    grain.Strength = 0.25
    comp:Unlock()
    print("✓ Vintage grade applied")
end'
    echo "✓ Vintage grade applied"
}

cmd_high_contrast() {
    echo "Applying high contrast grade..."
    apply_grade 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local cc = comp:AddTool("ColorCorrector")
    cc:SetAttrs({TOOLS_Name = "HighContrastGrade"})
    cc.MasterRGBContrast = 1.3
    cc.MasterSaturation = 1.2
    cc.MasterRGBGamma = 0.95
    local sharp = comp:AddTool("UnsharpMask")
    sharp:SetAttrs({TOOLS_Name = "ContrastSharpen"})
    sharp.Gain = 0.5
    comp:Unlock()
    print("✓ High contrast grade applied")
end'
    echo "✓ High contrast grade applied"
}

cmd_black_white() {
    echo "Applying B&W grade..."
    apply_grade 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local desat = comp:AddTool("ColorCorrector")
    desat:SetAttrs({TOOLS_Name = "BWGrade"})
    desat.MasterSaturation = 0
    desat.MasterRGBContrast = 1.2
    local cc = comp:AddTool("ColorCorrector")
    cc:SetAttrs({TOOLS_Name = "BWTone"})
    cc.MasterRGBGamma = 0.9
    cc.MasterRGBLift = 0.02
    comp:Unlock()
    print("✓ Black & White grade applied")
end'
    echo "✓ Black & white grade applied"
}

cmd_day_for_night() {
    echo "Applying day-for-night grade..."
    apply_grade 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local cc = comp:AddTool("ColorCorrector")
    cc:SetAttrs({TOOLS_Name = "DayForNight"})
    cc.MasterRGBGain = {0.5, 0.6, 0.9}
    cc.MasterRGBGamma = 0.7
    cc.MasterSaturation = 0.6
    cc.MasterRGBContrast = 1.2
    comp:Unlock()
    print("✓ Day-for-night grade applied")
end'
    echo "✓ Day-for-night grade applied"
}

cmd_warm() {
    echo "Applying warm grade..."
    apply_grade 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local cc = comp:AddTool("ColorCorrector")
    cc:SetAttrs({TOOLS_Name = "WarmGrade"})
    cc.MasterRGBGain = {1.1, 1.0, 0.85}
    cc.ShadowsRGBGain = {1.05, 0.98, 0.9}
    comp:Unlock()
    print("✓ Warm grade applied")
end'
    echo "✓ Warm grade applied"
}

cmd_cool() {
    echo "Applying cool grade..."
    apply_grade 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local cc = comp:AddTool("ColorCorrector")
    cc:SetAttrs({TOOLS_Name = "CoolGrade"})
    cc.MasterRGBGain = {0.9, 0.95, 1.1}
    cc.HighlightsRGBGain = {0.92, 0.98, 1.08}
    comp:Unlock()
    print("✓ Cool grade applied")
end'
    echo "✓ Cool grade applied"
}

cmd_bleach_bypass() {
    echo "Applying bleach bypass grade..."
    apply_grade 'local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local cc = comp:AddTool("ColorCorrector")
    cc:SetAttrs({TOOLS_Name = "BleachBypass"})
    cc.MasterSaturation = 0.5
    cc.MasterRGBContrast = 1.4
    cc.MasterRGBGamma = 0.85
    cc.HighlightsRGBGain = {1.1, 1.1, 1.1}
    comp:Unlock()
    print("✓ Bleach bypass grade applied")
end'
    echo "✓ Bleach bypass grade applied"
}

# Main
case "$1" in
    cinematic)      cmd_cinematic ;;
    teal-orange)    cmd_teal_orange ;;
    vintage)        cmd_vintage ;;
    high-contrast)  cmd_high_contrast ;;
    black-white|bw) cmd_black_white ;;
    day-for-night)  cmd_day_for_night ;;
    warm)           cmd_warm ;;
    cool)           cmd_cool ;;
    bleach-bypass)  cmd_bleach_bypass ;;
    help|--help|-h|"") show_help ;;
    *)              echo "Unknown preset: $1"; show_help; exit 1 ;;
esac
