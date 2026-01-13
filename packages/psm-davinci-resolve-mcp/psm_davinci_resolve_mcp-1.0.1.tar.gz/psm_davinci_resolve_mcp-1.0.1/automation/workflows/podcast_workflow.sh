#!/bin/bash
# Podcast Video Production Workflow
# Optimized for talking head / interview content

set -e

RESOLVE_CMD="$HOME/bin/resolve"

show_help() {
    echo "Podcast Video Production Workflow"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  new <video>           Start new podcast project"
    echo "  intro <show_name>     Add podcast intro"
    echo "  guest <name> <title>  Add guest lower third"
    echo "  chapter <title>       Add chapter marker graphic"
    echo "  highlight             Mark highlight clip"
    echo "  audiogram             Create square audiogram"
    echo "  outro                 Add outro/subscribe"
    echo "  full <video>          Full podcast workflow"
    echo ""
}

ensure_resolve() {
    if ! pgrep -x "Resolve" > /dev/null; then
        $RESOLVE_CMD launch
        sleep 5
    fi
}

cmd_new() {
    local video="$1"
    if [ -z "$video" ]; then
        echo "Usage: $0 new /path/to/podcast.mp4"
        exit 1
    fi

    echo "=== Creating New Podcast Project ==="
    ensure_resolve

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
        keystroke "$video"
        delay 0.3
        key code 36
        delay 0.5
        key code 36
    end tell
end tell
EOF

    sleep 2
    $RESOLVE_CMD edit
    sleep 1

    osascript << 'EOF'
tell application "System Events"
    tell process "Resolve"
        key code 111
    end tell
end tell
EOF

    echo "✓ Podcast project created"
}

cmd_intro() {
    local show_name="${1:-My Podcast}"

    echo "Adding podcast intro: $show_name"
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    cat << LUA | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Dark gradient background
    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "PodcastIntroBG"})
    bg.TopLeftRed = 0.08
    bg.TopLeftGreen = 0.08
    bg.TopLeftBlue = 0.12

    -- Show title
    local title = comp:AddTool("TextPlus")
    title:SetAttrs({TOOLS_Name = "ShowTitle"})
    title.StyledText = "$show_name"
    title.Font = "Arial Black"
    title.Size = 0.08
    title.Center = {0.5, 0.6}

    -- Episode indicator
    local ep = comp:AddTool("TextPlus")
    ep:SetAttrs({TOOLS_Name = "EpisodeNumber"})
    ep.StyledText = "EPISODE ##"
    ep.Font = "Arial"
    ep.Size = 0.03
    ep.Center = {0.5, 0.45}
    ep.Red1 = 0.7
    ep.Green1 = 0.7
    ep.Blue1 = 0.7

    comp:Unlock()
    print("✓ Podcast intro added - update episode number")
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

    echo "✓ Podcast intro added"
}

cmd_guest() {
    local name="${1:-Guest Name}"
    local title="${2:-Guest Title}"

    echo "Adding guest lower third: $name - $title"
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    cat << LUA | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Lower third background bar
    local bar = comp:AddTool("Background")
    bar:SetAttrs({TOOLS_Name = "GuestBar"})
    bar.TopLeftRed = 0.1
    bar.TopLeftGreen = 0.4
    bar.TopLeftBlue = 0.6
    bar.TopLeftAlpha = 0.9

    -- Guest name
    local nameText = comp:AddTool("TextPlus")
    nameText:SetAttrs({TOOLS_Name = "GuestName"})
    nameText.StyledText = "$name"
    nameText.Font = "Arial Bold"
    nameText.Size = 0.04
    nameText.Center = {0.25, 0.12}

    -- Guest title
    local titleText = comp:AddTool("TextPlus")
    titleText:SetAttrs({TOOLS_Name = "GuestTitle"})
    titleText.StyledText = "$title"
    titleText.Font = "Arial"
    titleText.Size = 0.025
    titleText.Center = {0.25, 0.07}
    titleText.Red1 = 0.9
    titleText.Green1 = 0.9
    titleText.Blue1 = 0.9

    comp:Unlock()
    print("✓ Guest lower third: $name")
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

    echo "✓ Guest lower third added"
}

cmd_chapter() {
    local title="${1:-Chapter Title}"

    echo "Adding chapter marker: $title"
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    cat << LUA | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Chapter card
    local card = comp:AddTool("Background")
    card:SetAttrs({TOOLS_Name = "ChapterCard"})
    card.TopLeftRed = 0.15
    card.TopLeftGreen = 0.15
    card.TopLeftBlue = 0.2
    card.TopLeftAlpha = 0.85

    -- Chapter title
    local text = comp:AddTool("TextPlus")
    text:SetAttrs({TOOLS_Name = "ChapterTitle"})
    text.StyledText = "$title"
    text.Font = "Arial Bold"
    text.Size = 0.05
    text.Center = {0.5, 0.5}

    comp:Unlock()
    print("✓ Chapter marker: $title")
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

    echo "✓ Chapter marker added"
}

cmd_highlight() {
    echo "Marking highlight clip..."
    ensure_resolve
    $RESOLVE_CMD edit
    sleep 0.5

    # Add marker at current position
    osascript << 'EOF'
tell application "System Events"
    tell process "Resolve"
        keystroke "m" using command down
    end tell
end tell
EOF

    echo "✓ Highlight marker added at playhead"
    echo "  Use these markers to create short clips later"
}

cmd_audiogram() {
    echo "Creating audiogram composition (1080x1080)..."
    ensure_resolve
    $RESOLVE_CMD fusion
    sleep 1
    $RESOLVE_CMD console
    sleep 0.5

    cat << 'LUA' | pbcopy
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Square background for social
    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "AudiogramBG"})
    bg.Width = 1080
    bg.Height = 1080
    bg.TopLeftRed = 0.1
    bg.TopLeftGreen = 0.1
    bg.TopLeftBlue = 0.15

    -- Waveform placeholder
    local wave = comp:AddTool("Background")
    wave:SetAttrs({TOOLS_Name = "WaveformArea"})
    wave.TopLeftRed = 0.2
    wave.TopLeftGreen = 0.5
    wave.TopLeftBlue = 0.7
    wave.TopLeftAlpha = 0.8

    -- Quote text area
    local quote = comp:AddTool("TextPlus")
    quote:SetAttrs({TOOLS_Name = "QuoteText"})
    quote.StyledText = "\"Add your best quote here\""
    quote.Font = "Arial"
    quote.Size = 0.06
    quote.Center = {0.5, 0.3}

    comp:Unlock()
    print("✓ Audiogram template created (1080x1080)")
    print("  Add audio waveform effect to WaveformArea")
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

    echo "✓ Audiogram template created"
}

cmd_outro() {
    echo "Adding podcast outro..."
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
    bg:SetAttrs({TOOLS_Name = "OutroBG"})
    bg.TopLeftRed = 0.05
    bg.TopLeftGreen = 0.05
    bg.TopLeftBlue = 0.08

    local thanks = comp:AddTool("TextPlus")
    thanks:SetAttrs({TOOLS_Name = "ThanksMessage"})
    thanks.StyledText = "Thanks for listening!"
    thanks.Font = "Arial Bold"
    thanks.Size = 0.06
    thanks.Center = {0.5, 0.65}

    local subscribe = comp:AddTool("TextPlus")
    subscribe:SetAttrs({TOOLS_Name = "SubscribeCTA"})
    subscribe.StyledText = "Subscribe • Rate • Review"
    subscribe.Font = "Arial"
    subscribe.Size = 0.035
    subscribe.Center = {0.5, 0.5}

    local social = comp:AddTool("TextPlus")
    social:SetAttrs({TOOLS_Name = "SocialHandles"})
    social.StyledText = "@yourhandle"
    social.Font = "Arial"
    social.Size = 0.03
    social.Center = {0.5, 0.35}
    social.Red1 = 0.6
    social.Green1 = 0.6
    social.Blue1 = 0.6

    comp:Unlock()
    print("✓ Podcast outro added")
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

    echo "✓ Podcast outro added"
}

cmd_full() {
    local video="$1"
    if [ -z "$video" ]; then
        echo "Usage: $0 full /path/to/podcast.mp4"
        exit 1
    fi

    echo "========================================="
    echo "  FULL PODCAST WORKFLOW AUTOMATION"
    echo "========================================="
    echo ""

    cmd_new "$video"
    sleep 1
    echo ""

    cmd_intro "My Podcast"
    sleep 1
    echo ""

    cmd_guest "Host Name" "Host & Creator"
    sleep 1
    echo ""

    cmd_outro

    echo ""
    echo "========================================="
    echo "  PODCAST WORKFLOW COMPLETE"
    echo "========================================="
    echo ""
    echo "Added:"
    echo "  ✓ Imported footage & timeline"
    echo "  ✓ Podcast intro"
    echo "  ✓ Host lower third"
    echo "  ✓ Outro with CTA"
    echo ""
    echo "Next steps:"
    echo "  - Add guest lower thirds: $0 guest 'Name' 'Title'"
    echo "  - Add chapter markers: $0 chapter 'Topic'"
    echo "  - Mark highlights: $0 highlight"
    echo "  - Create audiogram: $0 audiogram"
}

# Main
case "$1" in
    new)        cmd_new "$2" ;;
    intro)      cmd_intro "$2" ;;
    guest)      cmd_guest "$2" "$3" ;;
    chapter)    cmd_chapter "$2" ;;
    highlight)  cmd_highlight ;;
    audiogram)  cmd_audiogram ;;
    outro)      cmd_outro ;;
    full)       cmd_full "$2" ;;
    help|--help|-h|"") show_help ;;
    *)          echo "Unknown command: $1"; show_help; exit 1 ;;
esac
