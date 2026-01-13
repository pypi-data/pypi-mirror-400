#!/bin/bash
# Proxy Workflow Automation
# Create, manage, and relink proxy media

set -e

RESOLVE_CMD="$HOME/bin/resolve"

show_help() {
    echo "Proxy Workflow Automation"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  create <folder>        Create proxies for folder"
    echo "  status                 Show proxy status"
    echo "  enable                 Enable proxy mode"
    echo "  disable                Disable proxy mode (full res)"
    echo "  relink                 Relink to original media"
    echo "  settings               Show proxy settings"
    echo "  optimize               Optimize playback settings"
    echo ""
    echo "Proxy Codecs:"
    echo "  - ProRes Proxy (Mac) - Best quality/size"
    echo "  - DNxHR LB (Windows) - Good quality"
    echo "  - H.264 (Universal) - Smaller files"
    echo ""
}

ensure_resolve() {
    if ! pgrep -x "Resolve" > /dev/null; then
        $RESOLVE_CMD launch
        sleep 5
    fi
}

cmd_create() {
    local folder="$1"

    echo "=== Creating Proxy Media ==="
    echo "Source: $folder"
    ensure_resolve

    $RESOLVE_CMD media
    sleep 1

    echo ""
    echo "Steps to create proxies:"
    echo "  1. Select clips in Media Pool"
    echo "  2. Right-click → Generate Proxy Media"
    echo "  3. Choose resolution: 1/2 or 1/4"
    echo "  4. Choose codec: ProRes Proxy (Mac) or DNxHR LB"
    echo ""
    echo "Proxy location: Same folder as original or custom"
    echo ""
    echo "For batch creation:"
    echo "  Project Settings → Master Settings → Proxy Generation"

    # Open project settings
    osascript << 'EOF'
tell application "DaVinci Resolve" to activate
delay 0.5
tell application "System Events"
    tell process "Resolve"
        keystroke "," using {command down, shift down}
    end tell
end tell
EOF

    echo "✓ Project settings opened"
}

cmd_status() {
    echo "=== Proxy Status ==="
    ensure_resolve

    echo ""
    echo "Check proxy status:"
    echo "  1. Look at Media Pool thumbnails"
    echo "  2. Proxy clips show 'P' indicator"
    echo "  3. Playback → Proxy Mode shows current state"
    echo ""
    echo "Timeline indicator:"
    echo "  - 'Proxy' badge in viewer = using proxies"
    echo "  - No badge = using original media"
    echo ""

    $RESOLVE_CMD edit
}

cmd_enable() {
    echo "Enabling Proxy Mode..."
    ensure_resolve
    $RESOLVE_CMD edit
    sleep 0.5

    # Playback menu → Use Proxy
    osascript << 'EOF'
tell application "DaVinci Resolve" to activate
delay 0.3
tell application "System Events"
    tell process "Resolve"
        click menu item "Prefer Proxies" of menu "Proxy" of menu item "Proxy" of menu "Playback" of menu bar 1
    end tell
end tell
EOF

    echo "✓ Proxy mode enabled"
    echo "  Using proxy media for playback"
}

cmd_disable() {
    echo "Disabling Proxy Mode (Full Resolution)..."
    ensure_resolve
    $RESOLVE_CMD edit
    sleep 0.5

    osascript << 'EOF'
tell application "DaVinci Resolve" to activate
delay 0.3
tell application "System Events"
    tell process "Resolve"
        click menu item "Prefer Camera Originals" of menu "Proxy" of menu item "Proxy" of menu "Playback" of menu bar 1
    end tell
end tell
EOF

    echo "✓ Full resolution mode enabled"
    echo "  Using original media"
}

cmd_relink() {
    echo "=== Relink Media ==="
    ensure_resolve
    $RESOLVE_CMD media
    sleep 1

    echo ""
    echo "To relink media:"
    echo "  1. Select offline clips (red icon)"
    echo "  2. Right-click → Relink Selected Clips"
    echo "  3. Navigate to new location"
    echo "  4. Click 'Relink'"
    echo ""
    echo "Batch relink:"
    echo "  File → Relink Clips for Selected Bins"
    echo ""
    echo "✓ Media page ready for relinking"
}

cmd_settings() {
    echo "=== Proxy Settings Guide ==="
    echo ""
    echo "Recommended Proxy Settings:"
    echo ""
    echo "Resolution:"
    echo "  4K source → 1/4 (1080p proxy)"
    echo "  1080p source → 1/2 (540p proxy)"
    echo "  8K source → 1/8 (1080p proxy)"
    echo ""
    echo "Codecs (by platform):"
    echo "  Mac: ProRes Proxy (best)"
    echo "  Windows: DNxHR LB"
    echo "  Universal: H.264 (smaller files)"
    echo ""
    echo "Storage estimate (per hour):"
    echo "  ProRes Proxy 1080p: ~15 GB/hr"
    echo "  DNxHR LB 1080p: ~12 GB/hr"
    echo "  H.264 1080p: ~4 GB/hr"
    echo ""
    echo "Project Settings → Master Settings → Proxy Generation"
}

cmd_optimize() {
    echo "=== Optimizing Playback ==="
    ensure_resolve

    echo ""
    echo "Playback optimization settings:"
    echo ""
    echo "1. Timeline Resolution:"
    echo "   Playback → Timeline Proxy Mode → Half/Quarter"
    echo ""
    echo "2. Render Cache:"
    echo "   Playback → Render Cache → Smart"
    echo ""
    echo "3. Optimized Media:"
    echo "   Right-click clips → Generate Optimized Media"
    echo ""
    echo "4. Reduce Playback Quality:"
    echo "   Playback → Proxy Mode → Half Resolution"
    echo ""

    # Open playback menu
    osascript << 'EOF'
tell application "DaVinci Resolve" to activate
delay 0.3
tell application "System Events"
    tell process "Resolve"
        click menu "Playback" of menu bar 1
    end tell
end tell
EOF

    echo "✓ Playback menu opened"
}

# Main
case "$1" in
    create)     cmd_create "$2" ;;
    status)     cmd_status ;;
    enable)     cmd_enable ;;
    disable)    cmd_disable ;;
    relink)     cmd_relink ;;
    settings)   cmd_settings ;;
    optimize)   cmd_optimize ;;
    help|--help|-h|"") show_help ;;
    *)          echo "Unknown: $1"; show_help; exit 1 ;;
esac
