#!/bin/bash
# Project Backup & Archive
# Backup projects, media, and render files

set -e

RESOLVE_CMD="$HOME/bin/resolve"
BACKUP_DIR="$HOME/ColorGrading/Backups"
ARCHIVE_DIR="$HOME/ColorGrading/Archives"

mkdir -p "$BACKUP_DIR" "$ARCHIVE_DIR"

show_help() {
    echo "Project Backup & Archive"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  backup <project>     Quick backup of project database"
    echo "  archive <project>    Full archive with media"
    echo "  export <project>     Export project file (.drp)"
    echo "  list                 List all backups"
    echo "  restore <backup>     Restore from backup"
    echo "  clean                Remove old backups (keep 5)"
    echo "  cloud                Sync backups to cloud"
    echo "  verify <backup>      Verify backup integrity"
    echo ""
    echo "Examples:"
    echo "  $0 backup \"My Project\""
    echo "  $0 archive \"Finished Film\""
    echo "  $0 cloud"
    echo ""
}

ensure_resolve() {
    if ! pgrep -x "Resolve" > /dev/null; then
        $RESOLVE_CMD launch
        sleep 5
    fi
}

cmd_backup() {
    local project="$1"
    if [ -z "$project" ]; then
        echo "Error: Project name required"
        exit 1
    fi

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_name="${project// /_}_$timestamp"
    local backup_path="$BACKUP_DIR/$backup_name"

    mkdir -p "$backup_path"

    echo "=== Backing Up: $project ==="
    echo ""

    ensure_resolve

    # Export project file
    echo "Exporting project file..."
    $RESOLVE_CMD project open "$project"
    sleep 2

    # Use keyboard shortcut to export (File > Export Project)
    osascript << EOF
tell application "System Events"
    tell process "Resolve"
        keystroke "e" using {command down, shift down}
        delay 1
        keystroke "$backup_path/$project.drp"
        delay 0.5
        key code 36
    end tell
end tell
EOF

    sleep 2

    # Copy project settings
    echo "Saving project info..."
    cat > "$backup_path/info.txt" << EOF
Project: $project
Backup Date: $(date)
Resolve Version: $($RESOLVE_CMD version 2>/dev/null || echo "Unknown")
Computer: $(hostname)
User: $(whoami)
EOF

    # Create manifest
    echo "Creating manifest..."
    ls -la "$backup_path" > "$backup_path/manifest.txt"

    echo ""
    echo "✓ Backup complete: $backup_path"
    echo "  Size: $(du -sh "$backup_path" | cut -f1)"
}

cmd_archive() {
    local project="$1"
    if [ -z "$project" ]; then
        echo "Error: Project name required"
        exit 1
    fi

    local timestamp=$(date +%Y%m%d)
    local archive_name="${project// /_}_ARCHIVE_$timestamp"
    local archive_path="$ARCHIVE_DIR/$archive_name"

    mkdir -p "$archive_path"/{Project,Media,Renders,Cache,Stills}

    echo "=== Creating Full Archive: $project ==="
    echo ""
    echo "This will archive:"
    echo "  - Project file"
    echo "  - Source media"
    echo "  - Renders"
    echo "  - Cache files"
    echo "  - Stills/thumbnails"
    echo ""

    # Step 1: Backup project
    echo "[1/5] Backing up project..."
    ensure_resolve
    $RESOLVE_CMD project open "$project"
    sleep 2

    # Export via File menu
    osascript << EOF
tell application "System Events"
    tell process "Resolve"
        keystroke "e" using {command down, shift down}
        delay 1
    end tell
end tell
EOF
    sleep 1
    echo "  Save project file to: $archive_path/Project/"

    # Step 2: Media consolidation
    echo ""
    echo "[2/5] Consolidating media..."
    echo "  In Resolve: File > Media Management"
    echo "  Select: Copy media to new location"
    echo "  Destination: $archive_path/Media/"
    echo ""
    echo "  Press Enter when media copy is complete..."
    read

    # Step 3: Copy renders
    echo "[3/5] Finding renders..."
    local export_dir="$HOME/ColorGrading/Exports"
    if [ -d "$export_dir" ]; then
        # Look for project-related exports
        find "$export_dir" -name "*${project}*" -type f 2>/dev/null | while read f; do
            cp "$f" "$archive_path/Renders/"
            echo "  Copied: $(basename "$f")"
        done
    fi

    # Step 4: Cache files
    echo "[4/5] Cache files..."
    local cache_dir="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/CacheClip"
    if [ -d "$cache_dir" ]; then
        echo "  Cache location: $cache_dir"
        echo "  (Optional: manually copy relevant cache files)"
    fi

    # Step 5: Create archive info
    echo "[5/5] Creating archive manifest..."
    cat > "$archive_path/ARCHIVE_INFO.txt" << EOF
=====================================
PROJECT ARCHIVE
=====================================

Project: $project
Archive Date: $(date)
Archive Type: Full (project + media)

Contents:
- Project/     DaVinci Resolve project file
- Media/       Consolidated source media
- Renders/     Exported video files
- Cache/       Optimized media cache
- Stills/      Gallery stills and thumbnails

Restore Instructions:
1. Open DaVinci Resolve
2. File > Import Project Archive
3. Select this folder
4. Relink media if needed

=====================================
EOF

    # Calculate size
    local size=$(du -sh "$archive_path" | cut -f1)

    echo ""
    echo "=== Archive Complete ==="
    echo "Location: $archive_path"
    echo "Size: $size"
    echo ""

    # Optional: Compress
    read -p "Compress archive to .zip? (y/n) " compress
    if [ "$compress" = "y" ]; then
        echo "Compressing..."
        cd "$ARCHIVE_DIR"
        zip -r "${archive_name}.zip" "$archive_name"
        echo "✓ Created: ${archive_name}.zip"
    fi
}

cmd_export() {
    local project="$1"
    if [ -z "$project" ]; then
        echo "Error: Project name required"
        exit 1
    fi

    ensure_resolve
    $RESOLVE_CMD project open "$project"
    sleep 2

    echo "Exporting project file..."
    echo ""
    echo "In DaVinci Resolve:"
    echo "  File > Export Project..."
    echo ""
    echo "Save to: $BACKUP_DIR/"
    echo ""

    # Open export dialog
    osascript << 'EOF'
tell application "System Events"
    tell process "Resolve"
        keystroke "e" using {command down, shift down}
    end tell
end tell
EOF
}

cmd_list() {
    echo "=== Backups ==="
    echo ""
    ls -lt "$BACKUP_DIR" 2>/dev/null | head -20 || echo "  No backups found"
    echo ""

    echo "=== Archives ==="
    echo ""
    ls -lt "$ARCHIVE_DIR" 2>/dev/null | head -10 || echo "  No archives found"
    echo ""
}

cmd_restore() {
    local backup="$1"

    echo "=== Restore Project ==="
    echo ""

    if [ -z "$backup" ]; then
        echo "Available backups:"
        ls -1 "$BACKUP_DIR" 2>/dev/null
        echo ""
        echo "Usage: $0 restore <backup_folder>"
        exit 0
    fi

    local backup_path="$BACKUP_DIR/$backup"
    if [ ! -d "$backup_path" ]; then
        echo "Backup not found: $backup"
        exit 1
    fi

    ensure_resolve

    echo "Restoring from: $backup_path"
    echo ""
    echo "In DaVinci Resolve:"
    echo "  File > Import Project..."
    echo "  Select: $backup_path/*.drp"
    echo ""

    # Open Resolve file browser
    open "$backup_path"
}

cmd_clean() {
    echo "=== Cleaning Old Backups ==="
    echo ""

    # Keep only last 5 backups per project
    local projects=$(ls -1 "$BACKUP_DIR" 2>/dev/null | sed 's/_[0-9]*_[0-9]*$//' | sort -u)

    for project in $projects; do
        local backups=$(ls -1t "$BACKUP_DIR" | grep "^${project}_" | tail -n +6)
        for old in $backups; do
            echo "Removing: $old"
            rm -rf "$BACKUP_DIR/$old"
        done
    done

    echo ""
    echo "✓ Cleanup complete"
    echo "Remaining: $(ls -1 "$BACKUP_DIR" 2>/dev/null | wc -l | tr -d ' ') backups"
}

cmd_cloud() {
    echo "=== Cloud Sync ==="
    echo ""

    # Check for common cloud providers
    local cloud_paths=(
        "$HOME/Library/CloudStorage/iCloud Drive"
        "$HOME/Library/CloudStorage/Dropbox"
        "$HOME/Library/CloudStorage/OneDrive"
        "$HOME/Library/CloudStorage/GoogleDrive"
        "$HOME/MEGA"
    )

    local found_cloud=""
    for path in "${cloud_paths[@]}"; do
        if [ -d "$path" ]; then
            echo "Found: $path"
            found_cloud="$path"
        fi
    done

    if [ -z "$found_cloud" ]; then
        echo "No cloud storage found"
        exit 1
    fi

    echo ""
    read -p "Sync backups to $found_cloud? (y/n) " confirm
    if [ "$confirm" = "y" ]; then
        local cloud_backup="$found_cloud/Resolve_Backups"
        mkdir -p "$cloud_backup"

        echo "Syncing..."
        rsync -av --progress "$BACKUP_DIR/" "$cloud_backup/"

        echo ""
        echo "✓ Synced to: $cloud_backup"
    fi
}

cmd_verify() {
    local backup="$1"

    if [ -z "$backup" ]; then
        echo "Usage: $0 verify <backup_folder>"
        exit 1
    fi

    local backup_path="$BACKUP_DIR/$backup"
    if [ ! -d "$backup_path" ]; then
        backup_path="$ARCHIVE_DIR/$backup"
    fi

    if [ ! -d "$backup_path" ]; then
        echo "Backup not found: $backup"
        exit 1
    fi

    echo "=== Verifying: $backup ==="
    echo ""

    # Check for required files
    local valid=true

    if [ -f "$backup_path"/*.drp ]; then
        echo "✓ Project file found"
    else
        echo "✗ Missing project file"
        valid=false
    fi

    if [ -f "$backup_path/info.txt" ]; then
        echo "✓ Info file found"
        cat "$backup_path/info.txt"
    fi

    if [ -f "$backup_path/manifest.txt" ]; then
        echo "✓ Manifest found"
    fi

    echo ""
    if [ "$valid" = true ]; then
        echo "Backup verified OK"
    else
        echo "Backup may be incomplete"
    fi
}

# Main
case "$1" in
    backup)     cmd_backup "$2" ;;
    archive)    cmd_archive "$2" ;;
    export)     cmd_export "$2" ;;
    list)       cmd_list ;;
    restore)    cmd_restore "$2" ;;
    clean)      cmd_clean ;;
    cloud)      cmd_cloud ;;
    verify)     cmd_verify "$2" ;;
    help|--help|-h|"") show_help ;;
    *)          echo "Unknown: $1"; show_help; exit 1 ;;
esac
