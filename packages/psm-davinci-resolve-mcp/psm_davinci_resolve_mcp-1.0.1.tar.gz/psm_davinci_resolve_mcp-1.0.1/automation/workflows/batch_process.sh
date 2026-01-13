#!/bin/bash
# Batch Process Multiple Clips
# Usage: ./batch_process.sh /path/to/folder [effect]

set -e

INPUT_DIR="$1"
EFFECT="${2:-color_correct}"
RESOLVE_CMD="$HOME/bin/resolve"
OUTPUT_DIR="${INPUT_DIR}/processed"

if [ -z "$INPUT_DIR" ]; then
    echo "Batch Video Processor for DaVinci Resolve"
    echo ""
    echo "Usage: $0 /path/to/video/folder [effect]"
    echo ""
    echo "Effects: color_correct, cinematic_lut, film_grain, cinematic_bars"
    echo ""
    echo "This will:"
    echo "  1. Import all videos from the folder"
    echo "  2. Apply the effect to each"
    echo "  3. Set up batch export"
    exit 1
fi

if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Directory not found: $INPUT_DIR"
    exit 1
fi

# Find video files
VIDEO_FILES=$(find "$INPUT_DIR" -maxdepth 1 -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.avi" -o -name "*.mkv" \) | head -20)
VIDEO_COUNT=$(echo "$VIDEO_FILES" | grep -c "." || echo "0")

if [ "$VIDEO_COUNT" -eq 0 ]; then
    echo "No video files found in $INPUT_DIR"
    exit 1
fi

echo "=== Batch Processing $VIDEO_COUNT Videos ==="
echo "Input: $INPUT_DIR"
echo "Effect: $EFFECT"
echo ""

# Ensure Resolve is running
echo "Starting DaVinci Resolve..."
if ! pgrep -x "Resolve" > /dev/null; then
    $RESOLVE_CMD launch
    sleep 5
fi

# Go to Media page
echo "Importing videos..."
$RESOLVE_CMD media
sleep 1

# Import all videos at once using Cmd+I
osascript << EOF
tell application "DaVinci Resolve" to activate
delay 0.5
tell application "System Events"
    tell process "Resolve"
        keystroke "i" using command down
        delay 1
        keystroke "g" using {command down, shift down}
        delay 0.5
        keystroke "$INPUT_DIR"
        delay 0.3
        key code 36
        delay 1
        -- Select all files (Cmd+A)
        keystroke "a" using command down
        delay 0.3
        key code 36
    end tell
end tell
EOF

sleep 3
echo "✓ Videos imported"

# Go to Edit page
echo "Creating timeline..."
$RESOLVE_CMD edit
sleep 1

# Add all clips to timeline
osascript << 'EOF'
tell application "System Events"
    tell process "Resolve"
        -- Select all in media pool
        keystroke "a" using command down
        delay 0.3
        -- Append to timeline
        key code 111
    end tell
end tell
EOF

sleep 2
echo "✓ Timeline created"

# Apply effect to each clip
echo "Applying $EFFECT to all clips..."

# Go to Fusion
$RESOLVE_CMD fusion
sleep 1

# Open console and apply effect
$RESOLVE_CMD console
sleep 0.5

EFFECT_SCRIPT="dofile([[/Users/matthewkarsten/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/${EFFECT}.lua]])"
echo "$EFFECT_SCRIPT" | pbcopy

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
echo "✓ Effect applied"

# Set up batch export
echo "Setting up export..."
$RESOLVE_CMD deliver
sleep 1

echo ""
echo "=== Batch Processing Complete ==="
echo ""
echo "Processed: $VIDEO_COUNT videos"
echo "Effect: $EFFECT"
echo ""
echo "To export:"
echo "  1. Configure render settings"
echo "  2. Set output folder: $OUTPUT_DIR"
echo "  3. Click 'Add to Render Queue'"
echo "  4. Click 'Render All'"
