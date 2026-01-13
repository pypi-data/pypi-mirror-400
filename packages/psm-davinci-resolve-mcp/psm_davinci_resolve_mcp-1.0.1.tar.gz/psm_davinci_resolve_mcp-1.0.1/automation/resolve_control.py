#!/usr/bin/env python3
"""
DaVinci Resolve Automation Controller
Controls Resolve via AppleScript for the FREE version (no Studio required)
"""
import subprocess
import time
import os

class ResolveController:
    """Control DaVinci Resolve via AppleScript automation."""

    def __init__(self):
        self.app_name = "DaVinci Resolve"

    def run_applescript(self, script: str) -> str:
        """Execute AppleScript and return output."""
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    def run_applescript_file(self, script: str) -> str:
        """Execute multi-line AppleScript."""
        result = subprocess.run(
            ["osascript", "-"],
            input=script,
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout.strip()

    # ========== Application Control ==========

    def launch(self):
        """Launch DaVinci Resolve."""
        self.run_applescript(f'tell application "{self.app_name}" to activate')
        time.sleep(2)
        return "Resolve launched"

    def quit(self):
        """Quit DaVinci Resolve."""
        self.run_applescript(f'tell application "{self.app_name}" to quit')
        return "Resolve quit"

    def is_running(self) -> bool:
        """Check if Resolve is running."""
        result = subprocess.run(["pgrep", "-x", "Resolve"], capture_output=True)
        return result.returncode == 0

    # ========== Page Navigation ==========

    def go_to_page(self, page: str):
        """
        Navigate to a specific page.
        Pages: media, cut, edit, fusion, color, fairlight, deliver
        """
        shortcuts = {
            "media": "2",
            "cut": "3",
            "edit": "4",
            "fusion": "5",
            "color": "6",
            "fairlight": "7",
            "deliver": "8"
        }

        if page.lower() not in shortcuts:
            return f"Unknown page: {page}"

        key = shortcuts[page.lower()]
        script = f'''
        tell application "{self.app_name}" to activate
        delay 0.5
        tell application "System Events"
            tell process "Resolve"
                keystroke "{key}" using shift down
            end tell
        end tell
        '''
        self.run_applescript_file(script)
        time.sleep(0.5)
        return f"Navigated to {page} page"

    # ========== Menu Actions ==========

    def click_menu(self, menu: str, item: str, submenu: str = None):
        """Click a menu item."""
        if submenu:
            script = f'''
            tell application "{self.app_name}" to activate
            delay 0.3
            tell application "System Events"
                tell process "Resolve"
                    click menu item "{submenu}" of menu "{item}" of menu item "{item}" of menu "{menu}" of menu bar 1
                end tell
            end tell
            '''
        else:
            script = f'''
            tell application "{self.app_name}" to activate
            delay 0.3
            tell application "System Events"
                tell process "Resolve"
                    click menu item "{item}" of menu "{menu}" of menu bar 1
                end tell
            end tell
            '''
        return self.run_applescript_file(script)

    def open_console(self):
        """Open the Fusion Console."""
        self.go_to_page("fusion")
        time.sleep(0.5)
        self.click_menu("Workspace", "Console")
        return "Console opened"

    def run_fusion_script(self, script_name: str):
        """Run a Fusion script from the Scripts menu."""
        self.go_to_page("fusion")
        time.sleep(0.5)

        script = f'''
        tell application "{self.app_name}" to activate
        delay 0.5
        tell application "System Events"
            tell process "Resolve"
                click menu bar item "Workspace" of menu bar 1
                delay 0.3
                click menu item "Scripts" of menu "Workspace" of menu bar 1
                delay 0.3
                click menu item "Comp" of menu "Scripts" of menu item "Scripts" of menu "Workspace" of menu bar 1
                delay 0.3
                click menu item "{script_name}" of menu "Comp" of menu item "Comp" of menu "Scripts" of menu item "Scripts" of menu "Workspace" of menu bar 1
            end tell
        end tell
        '''
        result = self.run_applescript_file(script)
        return f"Ran script: {script_name}"

    # ========== Keyboard Shortcuts ==========

    def press_key(self, key: str, modifiers: list = None):
        """Press a keyboard shortcut."""
        mod_str = ""
        if modifiers:
            mod_str = " using {" + ", ".join(f"{m} down" for m in modifiers) + "}"

        script = f'''
        tell application "{self.app_name}" to activate
        delay 0.2
        tell application "System Events"
            tell process "Resolve"
                keystroke "{key}"{mod_str}
            end tell
        end tell
        '''
        return self.run_applescript_file(script)

    def play_pause(self):
        """Toggle play/pause."""
        return self.press_key(" ")

    def mark_in(self):
        """Set in point."""
        return self.press_key("i")

    def mark_out(self):
        """Set out point."""
        return self.press_key("o")

    def cut(self):
        """Make a cut at playhead."""
        return self.press_key("b")

    def delete_selected(self):
        """Delete selected clip."""
        script = '''
        tell application "System Events"
            tell process "Resolve"
                key code 51
            end tell
        end tell
        '''
        return self.run_applescript_file(script)

    def undo(self):
        """Undo last action."""
        return self.press_key("z", ["command"])

    def redo(self):
        """Redo last action."""
        return self.press_key("z", ["command", "shift"])

    def save_project(self):
        """Save current project."""
        return self.press_key("s", ["command"])

    # ========== Timeline Navigation ==========

    def go_to_start(self):
        """Go to timeline start."""
        script = '''
        tell application "System Events"
            tell process "Resolve"
                key code 115
            end tell
        end tell
        '''
        return self.run_applescript_file(script)

    def go_to_end(self):
        """Go to timeline end."""
        script = '''
        tell application "System Events"
            tell process "Resolve"
                key code 119
            end tell
        end tell
        '''
        return self.run_applescript_file(script)

    def next_edit(self):
        """Go to next edit point."""
        script = '''
        tell application "System Events"
            tell process "Resolve"
                key code 125
            end tell
        end tell
        '''
        return self.run_applescript_file(script)

    def prev_edit(self):
        """Go to previous edit point."""
        script = '''
        tell application "System Events"
            tell process "Resolve"
                key code 126
            end tell
        end tell
        '''
        return self.run_applescript_file(script)

    def step_forward(self, frames: int = 1):
        """Step forward by frames."""
        script = '''
        tell application "System Events"
            tell process "Resolve"
                key code 124
            end tell
        end tell
        '''
        for _ in range(frames):
            self.run_applescript_file(script)
            time.sleep(0.05)
        return f"Stepped forward {frames} frames"

    def step_backward(self, frames: int = 1):
        """Step backward by frames."""
        script = '''
        tell application "System Events"
            tell process "Resolve"
                key code 123
            end tell
        end tell
        '''
        for _ in range(frames):
            self.run_applescript_file(script)
            time.sleep(0.05)
        return f"Stepped backward {frames} frames"

    # ========== Import/Export ==========

    def import_media(self, file_path: str):
        """Import media file via File menu."""
        # Use Cmd+I shortcut
        self.press_key("i", ["command"])
        time.sleep(1)

        # Type the file path in the dialog
        script = f'''
        tell application "System Events"
            keystroke "g" using {{command down, shift down}}
            delay 0.5
            keystroke "{file_path}"
            delay 0.2
            key code 36
            delay 0.5
            key code 36
        end tell
        '''
        self.run_applescript_file(script)
        return f"Imported: {file_path}"

    def start_render(self):
        """Start rendering (from Deliver page)."""
        self.go_to_page("deliver")
        time.sleep(0.5)
        return self.press_key("r", ["command", "shift"])

    # ========== Compound Actions ==========

    def add_text_overlay(self):
        """Add a text overlay using Fusion."""
        self.go_to_page("fusion")
        time.sleep(0.5)
        self.run_fusion_script("add_text")
        return "Added text overlay"

    def apply_color_correction(self):
        """Apply basic color correction."""
        self.go_to_page("fusion")
        time.sleep(0.5)
        self.run_fusion_script("color_correct")
        return "Applied color correction"

    def apply_cinematic_look(self):
        """Apply cinematic look template."""
        self.go_to_page("fusion")
        time.sleep(0.5)
        self.run_fusion_script("cinematic_lut")
        return "Applied cinematic look"

    def setup_green_screen(self):
        """Set up green screen keying."""
        self.go_to_page("fusion")
        time.sleep(0.5)
        self.run_fusion_script("green_screen")
        return "Green screen setup created"


# ========== CLI Interface ==========

def main():
    import argparse

    parser = argparse.ArgumentParser(description="DaVinci Resolve Automation")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Basic commands
    subparsers.add_parser("launch", help="Launch Resolve")
    subparsers.add_parser("quit", help="Quit Resolve")
    subparsers.add_parser("status", help="Check if Resolve is running")

    # Page navigation
    page_parser = subparsers.add_parser("page", help="Go to page")
    page_parser.add_argument("name", choices=["media", "cut", "edit", "fusion", "color", "fairlight", "deliver"])

    # Playback
    subparsers.add_parser("play", help="Play/Pause")
    subparsers.add_parser("in", help="Mark In")
    subparsers.add_parser("out", help="Mark Out")
    subparsers.add_parser("cut", help="Cut at playhead")
    subparsers.add_parser("undo", help="Undo")
    subparsers.add_parser("save", help="Save project")

    # Scripts
    script_parser = subparsers.add_parser("script", help="Run Fusion script")
    script_parser.add_argument("name", help="Script name (without .lua)")

    # Effects
    subparsers.add_parser("text", help="Add text overlay")
    subparsers.add_parser("color", help="Apply color correction")
    subparsers.add_parser("cinematic", help="Apply cinematic look")
    subparsers.add_parser("greenscreen", help="Setup green screen")
    subparsers.add_parser("console", help="Open Fusion console")

    args = parser.parse_args()

    ctrl = ResolveController()

    if args.command == "launch":
        print(ctrl.launch())
    elif args.command == "quit":
        print(ctrl.quit())
    elif args.command == "status":
        print("Running" if ctrl.is_running() else "Not running")
    elif args.command == "page":
        print(ctrl.go_to_page(args.name))
    elif args.command == "play":
        print(ctrl.play_pause())
    elif args.command == "in":
        print(ctrl.mark_in())
    elif args.command == "out":
        print(ctrl.mark_out())
    elif args.command == "cut":
        print(ctrl.cut())
    elif args.command == "undo":
        print(ctrl.undo())
    elif args.command == "save":
        print(ctrl.save_project())
    elif args.command == "script":
        print(ctrl.run_fusion_script(args.name))
    elif args.command == "text":
        print(ctrl.add_text_overlay())
    elif args.command == "color":
        print(ctrl.apply_color_correction())
    elif args.command == "cinematic":
        print(ctrl.apply_cinematic_look())
    elif args.command == "greenscreen":
        print(ctrl.setup_green_screen())
    elif args.command == "console":
        print(ctrl.open_console())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
