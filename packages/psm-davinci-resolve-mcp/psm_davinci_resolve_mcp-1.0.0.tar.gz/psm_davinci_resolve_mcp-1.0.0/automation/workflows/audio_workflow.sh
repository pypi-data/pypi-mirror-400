#!/bin/bash
# Audio Workflow Tools
# Audio processing, mixing, and enhancement

set -e

RESOLVE_CMD="$HOME/bin/resolve"

show_help() {
    echo "Audio Workflow Tools"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  fairlight             Open Fairlight audio page"
    echo "  normalize             Normalize audio levels"
    echo "  voice-enhance         Enhance dialogue/voice"
    echo "  music-duck            Setup music ducking"
    echo "  noise-reduce          Reduce background noise"
    echo "  eq-voice              EQ preset for voice"
    echo "  eq-music              EQ preset for music"
    echo "  compress              Add compression"
    echo "  limiter               Add limiter for broadcast"
    echo "  stereo-enhance        Widen stereo field"
    echo "  audio-sync            Manual sync tools"
    echo "  export-audio          Export audio only"
    echo ""
}

ensure_resolve() {
    if ! pgrep -x "Resolve" > /dev/null; then
        $RESOLVE_CMD launch
        sleep 5
    fi
}

cmd_fairlight() {
    echo "Opening Fairlight audio page..."
    ensure_resolve
    $RESOLVE_CMD fairlight
    sleep 1
    echo "✓ Fairlight page opened"
    echo ""
    echo "Key shortcuts:"
    echo "  M - Mute track"
    echo "  S - Solo track"
    echo "  R - Record enable"
    echo "  Cmd+L - Link/unlink audio"
    echo "  Alt+S - Add fade"
}

cmd_normalize() {
    echo "Audio Normalization Guide"
    echo "========================="
    ensure_resolve
    $RESOLVE_CMD fairlight
    sleep 1
    echo ""
    echo "Steps to normalize:"
    echo "  1. Select clip(s) in timeline"
    echo "  2. Right-click → Normalize Audio Levels"
    echo "  3. Choose target:"
    echo "     - YouTube: -14 LUFS"
    echo "     - Podcast: -16 LUFS"
    echo "     - Broadcast: -24 LUFS"
    echo "     - Streaming: -14 to -16 LUFS"
    echo ""
    echo "✓ Fairlight ready for normalization"
}

cmd_voice_enhance() {
    echo "Voice Enhancement Setup"
    echo "======================="
    ensure_resolve
    $RESOLVE_CMD fairlight
    sleep 1
    echo ""
    echo "Recommended effect chain for voice:"
    echo ""
    echo "1. NOISE GATE"
    echo "   Threshold: -40 to -50 dB"
    echo "   Attack: 1ms"
    echo "   Release: 100ms"
    echo ""
    echo "2. EQ (Voice)"
    echo "   High-pass: 80-100 Hz"
    echo "   Cut: 200-400 Hz (mud)"
    echo "   Boost: 2-4 kHz (presence)"
    echo "   Boost: 8-12 kHz (air)"
    echo ""
    echo "3. COMPRESSOR"
    echo "   Ratio: 3:1 to 4:1"
    echo "   Threshold: -20 dB"
    echo "   Attack: 10ms"
    echo "   Release: 100ms"
    echo ""
    echo "4. DE-ESSER (if needed)"
    echo "   Frequency: 5-8 kHz"
    echo ""
    echo "Effects → Audio FX → Add to track"
}

cmd_music_duck() {
    echo "Music Ducking Setup"
    echo "==================="
    ensure_resolve
    $RESOLVE_CMD fairlight
    sleep 1
    echo ""
    echo "Fairlight Auto-Ducking:"
    echo "  1. Select music track"
    echo "  2. Mixer → Track → Dynamics"
    echo "  3. Enable Sidechain/Ducker"
    echo "  4. Set voice track as sidechain source"
    echo ""
    echo "Settings:"
    echo "  Duck Amount: -10 to -15 dB"
    echo "  Attack: 50ms"
    echo "  Hold: 100ms"
    echo "  Release: 500ms"
    echo ""
    echo "Manual ducking:"
    echo "  Use volume automation on music track"
    echo "  -10 to -15 dB during dialogue"
}

cmd_noise_reduce() {
    echo "Noise Reduction"
    echo "==============="
    ensure_resolve
    $RESOLVE_CMD fairlight
    sleep 1
    echo ""
    echo "Built-in Noise Reduction:"
    echo "  1. Select clip"
    echo "  2. Effects Library → Audio FX"
    echo "  3. Fairlight FX → Noise Reduction"
    echo ""
    echo "Settings:"
    echo "  - Learn noise profile from quiet section"
    echo "  - Reduction: Start at 10-15 dB"
    echo "  - Don't over-process (artifacts)"
    echo ""
    echo "Alternative: Use DaVinci Neural Engine"
    echo "  Right-click clip → Voice Isolation"
}

cmd_eq_voice() {
    echo "Voice EQ Preset"
    echo "==============="
    echo ""
    echo "Parametric EQ settings for voice:"
    echo ""
    echo "Band 1: High-pass filter"
    echo "  Type: HP 12dB/oct"
    echo "  Freq: 80 Hz"
    echo ""
    echo "Band 2: Cut mud"
    echo "  Type: Bell"
    echo "  Freq: 250 Hz"
    echo "  Gain: -3 dB"
    echo "  Q: 1.5"
    echo ""
    echo "Band 3: Add presence"
    echo "  Type: Bell"
    echo "  Freq: 3 kHz"
    echo "  Gain: +2 dB"
    echo "  Q: 2.0"
    echo ""
    echo "Band 4: Add air"
    echo "  Type: High shelf"
    echo "  Freq: 10 kHz"
    echo "  Gain: +2 dB"
}

cmd_eq_music() {
    echo "Music EQ Preset"
    echo "==============="
    echo ""
    echo "Parametric EQ for background music:"
    echo ""
    echo "Band 1: Sub bass control"
    echo "  Type: HP 6dB/oct"
    echo "  Freq: 40 Hz"
    echo ""
    echo "Band 2: Reduce voice frequencies"
    echo "  Type: Bell"
    echo "  Freq: 2.5 kHz"
    echo "  Gain: -4 dB"
    echo "  Q: 1.0"
    echo ""
    echo "This helps music sit behind voice"
}

cmd_compress() {
    echo "Compression Settings"
    echo "===================="
    echo ""
    echo "Voice/Dialogue:"
    echo "  Ratio: 3:1 to 4:1"
    echo "  Threshold: -20 dB"
    echo "  Attack: 10-20 ms"
    echo "  Release: 100-150 ms"
    echo "  Makeup gain: +3 dB"
    echo ""
    echo "Music:"
    echo "  Ratio: 2:1 to 3:1"
    echo "  Threshold: -15 dB"
    echo "  Attack: 30 ms"
    echo "  Release: 200 ms"
    echo ""
    echo "Effects → Audio FX → Dynamics"
}

cmd_limiter() {
    echo "Limiter for Broadcast"
    echo "====================="
    echo ""
    echo "Output limiter settings:"
    echo ""
    echo "YouTube/Streaming:"
    echo "  Ceiling: -1 dB"
    echo "  Target: -14 LUFS"
    echo ""
    echo "Broadcast TV:"
    echo "  Ceiling: -2 dB"
    echo "  Target: -24 LUFS"
    echo ""
    echo "Podcast:"
    echo "  Ceiling: -1 dB"
    echo "  Target: -16 LUFS"
    echo ""
    echo "Apply to Master bus in Fairlight"
}

cmd_stereo_enhance() {
    echo "Stereo Enhancement"
    echo "=================="
    echo ""
    echo "For wider stereo image:"
    echo ""
    echo "1. Mid-Side Processing:"
    echo "   Boost sides +2-3 dB"
    echo ""
    echo "2. Stereo Delay:"
    echo "   L: 0ms, R: 10-20ms"
    echo "   Very subtle effect"
    echo ""
    echo "3. Use with caution on voice"
    echo "   Best for music/ambience"
    echo ""
    echo "Check in mono for phase issues!"
}

cmd_audio_sync() {
    echo "Audio Sync Tools"
    echo "================"
    ensure_resolve
    $RESOLVE_CMD edit
    sleep 1
    echo ""
    echo "Auto-sync methods:"
    echo "  1. Select video + audio clips"
    echo "  2. Right-click → Auto Sync Audio"
    echo "  3. Choose: Based on Waveform"
    echo ""
    echo "Manual sync:"
    echo "  1. Find clap/sync point"
    echo "  2. Mark with 'M'"
    echo "  3. Align markers"
    echo "  4. Link clips: Cmd+L"
    echo ""
    echo "Slip audio (fine tune):"
    echo "  Hold Cmd+Option and drag"
}

cmd_export_audio() {
    echo "Export Audio Only"
    echo "================="
    ensure_resolve
    $RESOLVE_CMD deliver
    sleep 1
    echo ""
    echo "Audio-only export:"
    echo "  Format: Audio Only"
    echo "  Codec: AAC / MP3 / WAV"
    echo ""
    echo "Recommended settings:"
    echo "  Podcast: MP3 128-192 kbps"
    echo "  Music: WAV 24-bit / FLAC"
    echo "  Video audio: AAC 320 kbps"
    echo ""
    echo "✓ Deliver page ready"
}

# Main
case "$1" in
    fairlight)       cmd_fairlight ;;
    normalize)       cmd_normalize ;;
    voice-enhance)   cmd_voice_enhance ;;
    music-duck)      cmd_music_duck ;;
    noise-reduce)    cmd_noise_reduce ;;
    eq-voice)        cmd_eq_voice ;;
    eq-music)        cmd_eq_music ;;
    compress)        cmd_compress ;;
    limiter)         cmd_limiter ;;
    stereo-enhance)  cmd_stereo_enhance ;;
    audio-sync)      cmd_audio_sync ;;
    export-audio)    cmd_export_audio ;;
    help|--help|-h|"") show_help ;;
    *)               echo "Unknown: $1"; show_help; exit 1 ;;
esac
