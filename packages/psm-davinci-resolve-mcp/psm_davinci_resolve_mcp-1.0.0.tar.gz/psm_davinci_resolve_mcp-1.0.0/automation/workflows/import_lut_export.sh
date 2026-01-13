#!/bin/bash
# Auto Import → Apply LUT → Export Workflow
# Usage: ./import_lut_export.sh /path/to/video.mp4 [lut_name]

set -e

VIDEO_PATH="$1"
LUT_NAME="${2:-cinematic_lut}"
RESOLVE_CMD="$HOME/bin/resolve"

if [ -z "$VIDEO_PATH" ]; then
    echo "Usage: $0 /path/to/video.mp4 [lut_name]"
    echo ""
    echo "Available LUTs: cinematic_lut, color_correct, film_grain"
    exit 1
fi

if [ ! -f "$VIDEO_PATH" ]; then
    echo "Error: File not found: $VIDEO_PATH"
    exit 1
fi

echo "=== Auto Import → LUT → Export Workflow ==="
echo "Video: $VIDEO_PATH"
echo "LUT: $LUT_NAME"
echo ""

# Step 1: Ensure Resolve is running
echo "1. Checking DaVinci Resolve..."
if ! pgrep -x "Resolve" > /dev/null; then
    echo "   Starting Resolve..."
    $RESOLVE_CMD launch
    sleep 5
fi
echo "   ✓ Resolve running"

# Step 2: Go to Media page and import
echo "2. Importing media..."
$RESOLVE_CMD media
sleep 1

# Use Cmd+I to open import dialog
osascript << EOF
tell application "DaVinci Resolve" to activate
delay 0.5
tell application "System Events"
    tell process "Resolve"
        keystroke "i" using command down
        delay 1
        keystroke "g" using {command down, shift down}
        delay 0.5
        keystroke "$VIDEO_PATH"
        delay 0.3
        key code 36
        delay 0.5
        key code 36
    end tell
end tell
EOF
sleep 2
echo "   ✓ Media imported"

# Step 3: Go to Edit page and add to timeline
echo "3. Adding to timeline..."
$RESOLVE_CMD edit
sleep 1

# Select clip in media pool and add to timeline (F12 or drag)
osascript << 'EOF'
tell application "System Events"
    tell process "Resolve"
        -- Press F12 to append to timeline
        key code 111
    end tell
end tell
EOF
sleep 1
echo "   ✓ Added to timeline"

# Step 4: Go to Fusion and apply LUT
echo "4. Applying $LUT_NAME..."
$RESOLVE_CMD fusion
sleep 1
$RESOLVE_CMD console
sleep 0.5

# Run the LUT script
LUT_SCRIPT="dofile([[/Users/matthewkarsten/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/${LUT_NAME}.lua]])"
echo "$LUT_SCRIPT" | pbcopy
osascript << 'EOF'
tell application "System Events"
    tell process "Resolve"
        keystroke "v" using command down
        delay 0.2
        key code 36
    end tell
end tell
EOF
sleep 2
echo "   ✓ LUT applied"

# Step 5: Go to Deliver page and set up export
echo "5. Setting up export..."
$RESOLVE_CMD deliver
sleep 1

echo "   ✓ Ready to render"
echo ""
echo "=== Workflow Complete ==="
echo "Click 'Add to Render Queue' then 'Render All' to export"
