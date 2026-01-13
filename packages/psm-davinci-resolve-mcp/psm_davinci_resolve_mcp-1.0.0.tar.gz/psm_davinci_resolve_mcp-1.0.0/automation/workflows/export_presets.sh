#!/bin/bash
# Export Preset Manager
# Quick export configurations for different platforms

set -e

RESOLVE_CMD="$HOME/bin/resolve"

show_help() {
    echo "Export Preset Manager"
    echo ""
    echo "Usage: $0 <preset>"
    echo ""
    echo "Video Presets:"
    echo "  youtube-4k          YouTube 4K (3840x2160, 50Mbps)"
    echo "  youtube-1080        YouTube 1080p (1920x1080, 20Mbps)"
    echo "  youtube-shorts      YouTube Shorts (1080x1920, 15Mbps)"
    echo "  instagram-feed      Instagram Feed (1080x1080)"
    echo "  instagram-reels     Instagram Reels (1080x1920)"
    echo "  tiktok              TikTok (1080x1920)"
    echo "  twitter             Twitter/X (1280x720)"
    echo "  vimeo               Vimeo (1080p, high quality)"
    echo "  broadcast           Broadcast TV (1080i, ProRes)"
    echo "  cinema              Cinema DCP (4K, high bitrate)"
    echo ""
    echo "Audio Presets:"
    echo "  podcast             Podcast (MP3 192kbps)"
    echo "  audiobook           Audiobook (MP3 64kbps mono)"
    echo "  music               Music (WAV 24-bit)"
    echo ""
    echo "Archive:"
    echo "  master              Master file (ProRes 422 HQ)"
    echo "  archive             Archive (ProRes 4444)"
    echo ""
}

ensure_resolve() {
    if ! pgrep -x "Resolve" > /dev/null; then
        $RESOLVE_CMD launch
        sleep 5
    fi
}

show_preset() {
    local name="$1"
    local res="$2"
    local codec="$3"
    local bitrate="$4"
    local audio="$5"
    local notes="$6"

    echo "═══════════════════════════════════════════"
    echo "  $name"
    echo "═══════════════════════════════════════════"
    echo ""
    echo "Resolution:    $res"
    echo "Codec:         $codec"
    echo "Bitrate:       $bitrate"
    echo "Audio:         $audio"
    [ -n "$notes" ] && echo "Notes:         $notes"
    echo ""
}

cmd_youtube_4k() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "YouTube 4K" \
        "3840 x 2160 (16:9)" \
        "H.264 / H.265" \
        "40-80 Mbps (H.264) or 20-40 Mbps (H.265)" \
        "AAC 320kbps, 48kHz" \
        "Upload takes time. H.265 recommended for smaller files."
}

cmd_youtube_1080() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "YouTube 1080p" \
        "1920 x 1080 (16:9)" \
        "H.264" \
        "15-25 Mbps" \
        "AAC 320kbps, 48kHz" \
        "Standard quality for most content."
}

cmd_youtube_shorts() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "YouTube Shorts" \
        "1080 x 1920 (9:16 vertical)" \
        "H.264" \
        "10-15 Mbps" \
        "AAC 256kbps" \
        "Max 60 seconds. Keep text in safe zone."
}

cmd_instagram_feed() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Instagram Feed" \
        "1080 x 1080 (1:1 square)" \
        "H.264" \
        "5-10 Mbps" \
        "AAC 256kbps" \
        "Max 60 seconds for feed posts."
}

cmd_instagram_reels() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Instagram Reels" \
        "1080 x 1920 (9:16 vertical)" \
        "H.264" \
        "10-15 Mbps" \
        "AAC 256kbps" \
        "Max 90 seconds. Recommended: 15-30 sec."
}

cmd_tiktok() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "TikTok" \
        "1080 x 1920 (9:16 vertical)" \
        "H.264" \
        "10-15 Mbps" \
        "AAC 256kbps" \
        "Max 10 minutes. Best: 15-60 seconds."
}

cmd_twitter() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Twitter/X" \
        "1280 x 720 (16:9)" \
        "H.264" \
        "5-10 Mbps" \
        "AAC 256kbps" \
        "Max 2:20 (140 sec). Max file: 512MB."
}

cmd_vimeo() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Vimeo" \
        "1920 x 1080 (or 4K)" \
        "H.264 High Profile" \
        "20-30 Mbps" \
        "AAC 320kbps, 48kHz" \
        "Higher bitrate OK. Vimeo transcodes well."
}

cmd_broadcast() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Broadcast TV" \
        "1920 x 1080i (interlaced)" \
        "ProRes 422 or DNxHR HQ" \
        "~220 Mbps (ProRes 422)" \
        "PCM 24-bit, 48kHz" \
        "Check with broadcaster for exact specs."
}

cmd_cinema() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Cinema DCP" \
        "4096 x 2160 (DCI 4K) or 2048 x 1080" \
        "JPEG2000" \
        "250 Mbps max" \
        "PCM 24-bit, 48kHz (5.1 or 7.1)" \
        "Use DCP format in Deliver page."
}

cmd_podcast() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Podcast Audio" \
        "Audio Only" \
        "MP3" \
        "192 kbps (stereo) or 96 kbps (mono)" \
        "MP3, 44.1kHz" \
        "Normalize to -16 LUFS."
}

cmd_audiobook() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Audiobook" \
        "Audio Only" \
        "MP3" \
        "64 kbps (mono)" \
        "MP3, 44.1kHz, Mono" \
        "ACX specs. Normalize to -18 to -23 LUFS."
}

cmd_music() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Music Master" \
        "Audio Only" \
        "WAV or AIFF" \
        "Uncompressed" \
        "24-bit, 48kHz (or 96kHz)" \
        "For distribution, also export MP3 320kbps."
}

cmd_master() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Master File" \
        "Match source (1080p/4K)" \
        "ProRes 422 HQ" \
        "~330 Mbps (1080p) / ~1.3 Gbps (4K)" \
        "PCM 24-bit, 48kHz" \
        "High quality for future re-encoding."
}

cmd_archive() {
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    show_preset "Archive" \
        "Match source" \
        "ProRes 4444 (with alpha if needed)" \
        "~660 Mbps (1080p)" \
        "PCM 24-bit, 48kHz" \
        "Highest quality. Large files."
}

# Main
case "$1" in
    youtube-4k)       cmd_youtube_4k ;;
    youtube-1080)     cmd_youtube_1080 ;;
    youtube-shorts)   cmd_youtube_shorts ;;
    instagram-feed)   cmd_instagram_feed ;;
    instagram-reels)  cmd_instagram_reels ;;
    tiktok)           cmd_tiktok ;;
    twitter)          cmd_twitter ;;
    vimeo)            cmd_vimeo ;;
    broadcast)        cmd_broadcast ;;
    cinema)           cmd_cinema ;;
    podcast)          cmd_podcast ;;
    audiobook)        cmd_audiobook ;;
    music)            cmd_music ;;
    master)           cmd_master ;;
    archive)          cmd_archive ;;
    help|--help|-h|"") show_help ;;
    *)                echo "Unknown: $1"; show_help; exit 1 ;;
esac
