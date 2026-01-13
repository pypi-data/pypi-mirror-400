#!/usr/bin/env python3
"""
DaVinci Resolve Render Helper CLI
Works with the free version via command-line rendering.
"""
import subprocess
import os
import sys
import argparse
from pathlib import Path

# Resolve application path
RESOLVE_APP = "/Applications/DaVinci Resolve/DaVinci Resolve.app"
RESOLVE_BIN = f"{RESOLVE_APP}/Contents/MacOS/Resolve"

def get_resolve_projects_path():
    """Get the path to Resolve projects database."""
    return Path.home() / "Library/Application Support/Blackmagic Design/DaVinci Resolve/Resolve Disk Database"

def list_projects():
    """List available projects (reads from filesystem)."""
    db_path = get_resolve_projects_path()
    if db_path.exists():
        print("Project database location:", db_path)
        # List .drp files
        for f in db_path.rglob("*.drp"):
            print(f"  - {f.stem}")
    else:
        print("No local project database found")
        print("Projects may be stored in PostgreSQL database")

def open_resolve():
    """Open DaVinci Resolve application."""
    subprocess.run(["open", RESOLVE_APP])
    print("Opening DaVinci Resolve...")

def export_frame(input_video: str, frame: int, output: str):
    """Export a single frame using ffmpeg."""
    cmd = [
        "ffmpeg", "-i", input_video,
        "-vf", f"select=eq(n\\,{frame})",
        "-vframes", "1",
        output, "-y"
    ]
    subprocess.run(cmd)
    print(f"Exported frame {frame} to {output}")

def create_proxy(input_video: str, output: str, resolution: str = "1280x720"):
    """Create a proxy/optimized media file."""
    cmd = [
        "ffmpeg", "-i", input_video,
        "-vf", f"scale={resolution}",
        "-c:v", "prores_ks", "-profile:v", "0",  # ProRes Proxy
        "-c:a", "pcm_s16le",
        output, "-y"
    ]
    print(f"Creating proxy: {input_video} -> {output}")
    subprocess.run(cmd)
    print("Done!")

def batch_transcode(input_dir: str, output_dir: str, codec: str = "prores"):
    """Batch transcode all videos in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".mxf"}

    for f in input_path.iterdir():
        if f.suffix.lower() in video_exts:
            output_file = output_path / f"{f.stem}_transcoded.mov"
            if codec == "prores":
                cmd = ["ffmpeg", "-i", str(f), "-c:v", "prores_ks", "-profile:v", "3",
                       "-c:a", "pcm_s16le", str(output_file), "-y"]
            elif codec == "dnxhd":
                cmd = ["ffmpeg", "-i", str(f), "-c:v", "dnxhd", "-b:v", "185M",
                       "-c:a", "pcm_s16le", str(output_file), "-y"]
            else:
                cmd = ["ffmpeg", "-i", str(f), "-c:v", "libx264", "-crf", "18",
                       str(output_file), "-y"]

            print(f"Transcoding: {f.name}")
            subprocess.run(cmd, capture_output=True)

    print(f"Batch transcode complete! Output: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="DaVinci Resolve Helper CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # open command
    subparsers.add_parser("open", help="Open DaVinci Resolve")

    # projects command
    subparsers.add_parser("projects", help="List available projects")

    # frame export
    frame_parser = subparsers.add_parser("frame", help="Export a frame from video")
    frame_parser.add_argument("input", help="Input video file")
    frame_parser.add_argument("frame", type=int, help="Frame number")
    frame_parser.add_argument("-o", "--output", default="frame.png", help="Output file")

    # proxy creation
    proxy_parser = subparsers.add_parser("proxy", help="Create proxy media")
    proxy_parser.add_argument("input", help="Input video file")
    proxy_parser.add_argument("-o", "--output", help="Output file")
    proxy_parser.add_argument("-r", "--resolution", default="1280x720", help="Resolution")

    # batch transcode
    batch_parser = subparsers.add_parser("batch", help="Batch transcode videos")
    batch_parser.add_argument("input_dir", help="Input directory")
    batch_parser.add_argument("output_dir", help="Output directory")
    batch_parser.add_argument("-c", "--codec", choices=["prores", "dnxhd", "h264"],
                              default="prores", help="Output codec")

    args = parser.parse_args()

    if args.command == "open":
        open_resolve()
    elif args.command == "projects":
        list_projects()
    elif args.command == "frame":
        export_frame(args.input, args.frame, args.output)
    elif args.command == "proxy":
        output = args.output or args.input.rsplit(".", 1)[0] + "_proxy.mov"
        create_proxy(args.input, output, args.resolution)
    elif args.command == "batch":
        batch_transcode(args.input_dir, args.output_dir, args.codec)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
