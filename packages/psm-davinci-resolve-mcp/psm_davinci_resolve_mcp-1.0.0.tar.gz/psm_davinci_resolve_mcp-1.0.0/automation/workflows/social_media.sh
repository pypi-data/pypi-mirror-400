#!/bin/bash
# Social Media Multi-Platform Export Workflow
# Creates optimized exports for YouTube, Instagram, TikTok, Twitter

set -e

RESOLVE_CMD="$HOME/bin/resolve"

show_help() {
    echo "Social Media Multi-Platform Export"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  setup                  Set up timeline for multi-platform"
    echo "  youtube               Export YouTube optimized (1920x1080)"
    echo "  instagram-feed        Export Instagram feed (1080x1080)"
    echo "  instagram-story       Export Instagram story (1080x1920)"
    echo "  tiktok                Export TikTok (1080x1920)"
    echo "  twitter               Export Twitter (1280x720)"
    echo "  all                   Export all platforms"
    echo ""
    echo "Example:"
    echo "  $0 all                # Export for all platforms"
}

ensure_resolve() {
    if ! pgrep -x "Resolve" > /dev/null; then
        echo "Starting DaVinci Resolve..."
        $RESOLVE_CMD launch
        sleep 5
    fi
}

create_vertical_comp() {
    local name="$1"
    local width="$2"
    local height="$3"

    cat << LUA | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Create background for aspect ratio
    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "${name}_BG"})
    bg.Width = $width
    bg.Height = $height
    bg.TopLeftRed = 0
    bg.TopLeftGreen = 0
    bg.TopLeftBlue = 0

    -- Add resize transform
    local resize = comp:AddTool("Transform")
    resize:SetAttrs({TOOLS_Name = "${name}_Resize"})
    resize.Size = 0.5625  -- 9:16 from 16:9

    comp:Unlock()
    print("✓ Created ${name} composition ($width x $height)")
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
}

cmd_setup() {
    echo "Setting up multi-platform timeline..."
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    cat << 'LUA' | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Add merge for compositing layers
    local merge = comp:AddTool("Merge")
    merge:SetAttrs({TOOLS_Name = "SocialMerge"})

    -- Safe zone guide for vertical crops
    local guide = comp:AddTool("Background")
    guide:SetAttrs({TOOLS_Name = "SafeZoneGuide"})
    guide.Width = 1080
    guide.Height = 1920
    guide.TopLeftAlpha = 0.3
    guide.TopLeftRed = 0.2
    guide.TopLeftGreen = 0.5
    guide.TopLeftBlue = 0.2

    comp:Unlock()
    print("✓ Multi-platform setup complete")
    print("  Keep important content in center for vertical crops")
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
    echo "✓ Multi-platform setup complete"
}

cmd_youtube() {
    echo "Setting up YouTube export (1920x1080)..."
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1

    echo "YouTube Settings:"
    echo "  Resolution: 1920x1080"
    echo "  Codec: H.264"
    echo "  Bitrate: 20-50 Mbps"
    echo "  Audio: AAC 320kbps"
    echo "✓ Ready for YouTube export"
}

cmd_instagram_feed() {
    echo "Setting up Instagram Feed export (1080x1080)..."
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    create_vertical_comp "InstagramFeed" 1080 1080

    sleep 1
    $RESOLVE_CMD deliver
    sleep 1

    echo "Instagram Feed Settings:"
    echo "  Resolution: 1080x1080"
    echo "  Max Duration: 60 seconds"
    echo "  Codec: H.264"
    echo "✓ Ready for Instagram feed export"
}

cmd_instagram_story() {
    echo "Setting up Instagram Story export (1080x1920)..."
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    create_vertical_comp "InstagramStory" 1080 1920

    sleep 1
    $RESOLVE_CMD deliver
    sleep 1

    echo "Instagram Story Settings:"
    echo "  Resolution: 1080x1920 (9:16)"
    echo "  Max Duration: 15 seconds per story"
    echo "  Codec: H.264"
    echo "✓ Ready for Instagram story export"
}

cmd_tiktok() {
    echo "Setting up TikTok export (1080x1920)..."
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    create_vertical_comp "TikTok" 1080 1920

    sleep 1
    $RESOLVE_CMD deliver
    sleep 1

    echo "TikTok Settings:"
    echo "  Resolution: 1080x1920 (9:16)"
    echo "  Duration: 15s - 10min"
    echo "  Codec: H.264"
    echo "✓ Ready for TikTok export"
}

cmd_twitter() {
    echo "Setting up Twitter export (1280x720)..."
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1

    echo "Twitter/X Settings:"
    echo "  Resolution: 1280x720"
    echo "  Max Duration: 2:20 (140 seconds)"
    echo "  Max Size: 512MB"
    echo "  Codec: H.264"
    echo "✓ Ready for Twitter export"
}

cmd_all() {
    echo "========================================="
    echo "  MULTI-PLATFORM SOCIAL MEDIA EXPORT"
    echo "========================================="
    echo ""

    cmd_setup
    echo ""
    sleep 1

    echo "Platform configurations ready:"
    echo "  - YouTube: 1920x1080 (16:9)"
    echo "  - Instagram Feed: 1080x1080 (1:1)"
    echo "  - Instagram Story: 1080x1920 (9:16)"
    echo "  - TikTok: 1080x1920 (9:16)"
    echo "  - Twitter: 1280x720 (16:9)"
    echo ""
    echo "Use individual commands to set up each export,"
    echo "or manually configure in Deliver page."
    echo ""
    echo "✓ Multi-platform setup complete"
}

# Main
case "$1" in
    setup)           cmd_setup ;;
    youtube)         cmd_youtube ;;
    instagram-feed)  cmd_instagram_feed ;;
    instagram-story) cmd_instagram_story ;;
    tiktok)          cmd_tiktok ;;
    twitter)         cmd_twitter ;;
    all)             cmd_all ;;
    help|--help|-h|"") show_help ;;
    *)               echo "Unknown command: $1"; show_help; exit 1 ;;
esac
