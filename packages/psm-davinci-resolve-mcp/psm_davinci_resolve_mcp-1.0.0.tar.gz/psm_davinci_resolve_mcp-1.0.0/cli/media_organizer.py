#!/usr/bin/env python3
"""
Media Organizer for DaVinci Resolve Projects
Organizes media files into a structure optimized for Resolve.
"""
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import json

def get_video_metadata(file_path: str) -> dict:
    """Extract metadata using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(file_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    except:
        return {}

def organize_for_resolve(source_dir: str, project_name: str = "Project"):
    """
    Organize media files into a DaVinci Resolve-friendly structure:
    ProjectName/
    ├── 01_FOOTAGE/
    │   ├── A_CAM/
    │   ├── B_CAM/
    │   └── BROLL/
    ├── 02_AUDIO/
    │   ├── MUSIC/
    │   ├── SFX/
    │   └── VO/
    ├── 03_GRAPHICS/
    ├── 04_EXPORTS/
    └── 05_PROJECT_FILES/
    """
    source = Path(source_dir)
    base = source.parent / project_name

    # Create folder structure
    folders = [
        "01_FOOTAGE/A_CAM",
        "01_FOOTAGE/B_CAM",
        "01_FOOTAGE/BROLL",
        "02_AUDIO/MUSIC",
        "02_AUDIO/SFX",
        "02_AUDIO/VO",
        "03_GRAPHICS",
        "04_EXPORTS",
        "05_PROJECT_FILES",
    ]

    for folder in folders:
        (base / folder).mkdir(parents=True, exist_ok=True)

    # File type mappings
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".mxf", ".r3d", ".braw"}
    audio_exts = {".wav", ".mp3", ".aiff", ".aac", ".m4a"}
    image_exts = {".jpg", ".jpeg", ".png", ".tiff", ".psd", ".ai", ".eps"}

    # Organize files
    for f in source.rglob("*"):
        if f.is_file():
            ext = f.suffix.lower()

            if ext in video_exts:
                dest = base / "01_FOOTAGE/BROLL" / f.name
            elif ext in audio_exts:
                # Try to categorize audio
                name_lower = f.stem.lower()
                if any(x in name_lower for x in ["music", "song", "track"]):
                    dest = base / "02_AUDIO/MUSIC" / f.name
                elif any(x in name_lower for x in ["sfx", "sound", "effect"]):
                    dest = base / "02_AUDIO/SFX" / f.name
                else:
                    dest = base / "02_AUDIO/VO" / f.name
            elif ext in image_exts:
                dest = base / "03_GRAPHICS" / f.name
            else:
                continue

            if not dest.exists():
                print(f"Moving: {f.name} -> {dest.parent.name}/")
                shutil.copy2(f, dest)

    print(f"\nProject structure created at: {base}")
    print("\nFolder structure:")
    for folder in folders:
        print(f"  {folder}")

def create_daily_folder(base_dir: str):
    """Create a dated folder for today's shoot."""
    today = datetime.now().strftime("%Y-%m-%d")
    folder = Path(base_dir) / f"SHOOT_{today}"

    subfolders = ["A_CAM", "B_CAM", "AUDIO", "STILLS"]
    for sub in subfolders:
        (folder / sub).mkdir(parents=True, exist_ok=True)

    print(f"Created daily shoot folder: {folder}")
    return str(folder)

def generate_media_report(directory: str):
    """Generate a report of all media files."""
    path = Path(directory)

    report = {
        "videos": [],
        "audio": [],
        "images": [],
        "total_size_gb": 0
    }

    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".mxf"}
    audio_exts = {".wav", ".mp3", ".aiff"}
    image_exts = {".jpg", ".png", ".tiff"}

    total_size = 0

    for f in path.rglob("*"):
        if f.is_file():
            size = f.stat().st_size
            total_size += size
            ext = f.suffix.lower()

            info = {
                "name": f.name,
                "path": str(f),
                "size_mb": round(size / (1024*1024), 2)
            }

            if ext in video_exts:
                meta = get_video_metadata(str(f))
                if meta.get("streams"):
                    for stream in meta["streams"]:
                        if stream.get("codec_type") == "video":
                            info["resolution"] = f"{stream.get('width')}x{stream.get('height')}"
                            info["codec"] = stream.get("codec_name")
                            info["fps"] = stream.get("r_frame_rate")
                report["videos"].append(info)
            elif ext in audio_exts:
                report["audio"].append(info)
            elif ext in image_exts:
                report["images"].append(info)

    report["total_size_gb"] = round(total_size / (1024**3), 2)

    # Print report
    print("\n=== MEDIA REPORT ===")
    print(f"Total size: {report['total_size_gb']} GB")
    print(f"\nVideos ({len(report['videos'])}):")
    for v in report["videos"][:10]:
        print(f"  {v['name']} - {v.get('resolution', 'N/A')} - {v['size_mb']}MB")
    if len(report["videos"]) > 10:
        print(f"  ... and {len(report['videos'])-10} more")

    print(f"\nAudio ({len(report['audio'])}):")
    for a in report["audio"][:5]:
        print(f"  {a['name']} - {a['size_mb']}MB")

    print(f"\nImages ({len(report['images'])})")

    return report

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python media_organizer.py organize <source_dir> [project_name]")
        print("  python media_organizer.py daily <base_dir>")
        print("  python media_organizer.py report <directory>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "organize" and len(sys.argv) >= 3:
        project = sys.argv[3] if len(sys.argv) > 3 else "Project"
        organize_for_resolve(sys.argv[2], project)
    elif cmd == "daily" and len(sys.argv) >= 3:
        create_daily_folder(sys.argv[2])
    elif cmd == "report" and len(sys.argv) >= 3:
        generate_media_report(sys.argv[2])
    else:
        print("Invalid command")
