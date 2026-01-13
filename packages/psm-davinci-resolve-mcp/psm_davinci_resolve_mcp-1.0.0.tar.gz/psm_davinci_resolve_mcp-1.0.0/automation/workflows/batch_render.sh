#!/bin/bash
# Batch Render Manager
# Queue and manage multiple render jobs

set -e

RESOLVE_CMD="$HOME/bin/resolve"
QUEUE_DIR="$HOME/.resolve_queue"
LOG_DIR="$HOME/ColorGrading/RenderLogs"

mkdir -p "$QUEUE_DIR" "$LOG_DIR"

show_help() {
    echo "Batch Render Manager"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  add <project>        Add project to render queue"
    echo "  list                 Show current queue"
    echo "  clear                Clear the queue"
    echo "  start                Start batch rendering"
    echo "  status               Check render status"
    echo "  logs                 View render logs"
    echo "  overnight            Setup overnight render"
    echo "  priority <project>   Move project to front of queue"
    echo ""
    echo "Examples:"
    echo "  $0 add \"My Project\""
    echo "  $0 start"
    echo "  $0 overnight"
    echo ""
}

ensure_resolve() {
    if ! pgrep -x "Resolve" > /dev/null; then
        $RESOLVE_CMD launch
        sleep 5
    fi
}

cmd_add() {
    local project="$1"
    if [ -z "$project" ]; then
        echo "Error: Project name required"
        exit 1
    fi

    local timestamp=$(date +%s)
    echo "$project" > "$QUEUE_DIR/$timestamp.job"

    echo "✓ Added to queue: $project"
    echo "  Queue position: $(ls "$QUEUE_DIR"/*.job 2>/dev/null | wc -l | tr -d ' ')"
}

cmd_list() {
    echo "=== Render Queue ==="
    echo ""

    local count=1
    for job in $(ls "$QUEUE_DIR"/*.job 2>/dev/null | sort); do
        local project=$(cat "$job")
        echo "  $count. $project"
        ((count++))
    done

    if [ $count -eq 1 ]; then
        echo "  (Queue is empty)"
    fi
    echo ""
}

cmd_clear() {
    rm -f "$QUEUE_DIR"/*.job
    echo "✓ Queue cleared"
}

cmd_start() {
    local jobs=$(ls "$QUEUE_DIR"/*.job 2>/dev/null | sort)
    local total=$(echo "$jobs" | grep -c . || echo 0)

    if [ "$total" -eq 0 ]; then
        echo "Queue is empty. Add projects first:"
        echo "  $0 add \"Project Name\""
        exit 0
    fi

    echo "=== Starting Batch Render ==="
    echo "Projects in queue: $total"
    echo ""

    ensure_resolve

    local current=1
    for job in $jobs; do
        local project=$(cat "$job")
        local log_file="$LOG_DIR/$(date +%Y%m%d_%H%M%S)_${project// /_}.log"

        echo "[$current/$total] Rendering: $project"
        echo "  Log: $log_file"

        # Open project
        $RESOLVE_CMD project open "$project" 2>&1 | tee -a "$log_file"
        sleep 3

        # Go to deliver page
        $RESOLVE_CMD deliver 2>&1 | tee -a "$log_file"
        sleep 2

        # Start render (Cmd+Shift+R)
        osascript << 'EOF' 2>&1 | tee -a "$log_file"
tell application "System Events"
    tell process "Resolve"
        keystroke "r" using {command down, shift down}
    end tell
end tell
EOF

        echo "  Started at $(date)"
        echo ""

        # Wait for render to complete (check every 30 seconds)
        echo "  Waiting for render..."
        while true; do
            sleep 30
            # Check if render dialog is gone
            local is_rendering=$(osascript -e 'tell application "System Events" to tell process "Resolve" to count of windows' 2>/dev/null || echo "1")
            if [ "$is_rendering" -le 1 ]; then
                break
            fi
        done

        echo "  Completed at $(date)" | tee -a "$log_file"

        # Remove from queue
        rm -f "$job"
        ((current++))
    done

    echo ""
    echo "=== Batch Render Complete ==="
    echo "Rendered $total projects"

    # Notification
    osascript -e 'display notification "All projects rendered" with title "Batch Render Complete"'
}

cmd_status() {
    echo "=== Render Status ==="
    echo ""

    # Check if Resolve is running
    if pgrep -x "Resolve" > /dev/null; then
        echo "DaVinci Resolve: Running"

        # Try to get current project
        local current=$($RESOLVE_CMD project current 2>/dev/null || echo "Unknown")
        echo "Current Project: $current"
    else
        echo "DaVinci Resolve: Not running"
    fi

    echo ""
    echo "Queue: $(ls "$QUEUE_DIR"/*.job 2>/dev/null | wc -l | tr -d ' ') projects waiting"
    echo ""
}

cmd_logs() {
    echo "=== Recent Render Logs ==="
    echo ""

    ls -lt "$LOG_DIR"/*.log 2>/dev/null | head -10 | while read line; do
        echo "  $line"
    done

    if [ ! -f "$LOG_DIR"/*.log 2>/dev/null ]; then
        echo "  No logs found"
    fi

    echo ""
    echo "View full log:"
    echo "  cat $LOG_DIR/<logfile>"
}

cmd_overnight() {
    local jobs=$(ls "$QUEUE_DIR"/*.job 2>/dev/null | wc -l | tr -d ' ')

    echo "=== Overnight Render Setup ==="
    echo ""
    echo "Projects queued: $jobs"
    echo ""

    if [ "$jobs" -eq 0 ]; then
        echo "Add projects to queue first:"
        echo "  $0 add \"Project 1\""
        echo "  $0 add \"Project 2\""
        echo ""
        exit 0
    fi

    echo "Overnight render will:"
    echo "  1. Render all $jobs projects"
    echo "  2. Log progress to $LOG_DIR"
    echo "  3. Notify when complete"
    echo "  4. Optionally sleep computer when done"
    echo ""

    read -p "Start overnight render? (y/n) " confirm
    if [ "$confirm" = "y" ]; then
        echo ""
        echo "Starting overnight render..."
        echo "Safe to leave computer running."
        echo ""

        # Start render in background
        nohup $0 start > "$LOG_DIR/overnight_$(date +%Y%m%d).log" 2>&1 &

        echo "Render started in background"
        echo "Log: $LOG_DIR/overnight_$(date +%Y%m%d).log"
        echo ""
        echo "Monitor progress:"
        echo "  tail -f $LOG_DIR/overnight_$(date +%Y%m%d).log"
    fi
}

cmd_priority() {
    local project="$1"
    if [ -z "$project" ]; then
        echo "Error: Project name required"
        exit 1
    fi

    # Find and move to front (timestamp = 0)
    for job in "$QUEUE_DIR"/*.job; do
        if [ -f "$job" ] && grep -q "$project" "$job"; then
            mv "$job" "$QUEUE_DIR/0.job"
            echo "✓ Moved to front: $project"
            return
        fi
    done

    echo "Project not found in queue: $project"
}

# Main
case "$1" in
    add)        cmd_add "$2" ;;
    list)       cmd_list ;;
    clear)      cmd_clear ;;
    start)      cmd_start ;;
    status)     cmd_status ;;
    logs)       cmd_logs ;;
    overnight)  cmd_overnight ;;
    priority)   cmd_priority "$2" ;;
    help|--help|-h|"") show_help ;;
    *)          echo "Unknown: $1"; show_help; exit 1 ;;
esac
