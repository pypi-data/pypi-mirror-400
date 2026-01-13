"""
DaVinci Resolve API wrapper module.
Handles connection to DaVinci Resolve's Python scripting API.
"""

import sys
import os
from typing import Optional, Any

# DaVinci Resolve scripting paths for different platforms
RESOLVE_SCRIPT_PATHS = {
    "darwin": [
        "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules",
        "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/",
    ],
    "win32": [
        os.path.join(os.environ.get("PROGRAMDATA", ""),
                     "Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting/Modules"),
    ],
    "linux": [
        "/opt/resolve/Developer/Scripting/Modules",
        "/opt/resolve/libs/Fusion/",
    ],
}


class ResolveConnection:
    """Manages connection to DaVinci Resolve application."""

    def __init__(self):
        self._resolve = None
        self._fusion = None
        self._project_manager = None
        self._setup_paths()

    def _setup_paths(self):
        """Add DaVinci Resolve scripting paths to sys.path."""
        platform = sys.platform
        paths = RESOLVE_SCRIPT_PATHS.get(platform, [])

        for path in paths:
            if os.path.exists(path) and path not in sys.path:
                sys.path.append(path)

    def connect(self) -> bool:
        """
        Connect to running DaVinci Resolve instance.
        Returns True if connection successful.
        """
        try:
            import DaVinciResolveScript as dvr
            self._resolve = dvr.scriptapp("Resolve")
            if self._resolve:
                self._fusion = self._resolve.Fusion()
                self._project_manager = self._resolve.GetProjectManager()
                return True
            return False
        except ImportError as e:
            print(f"Failed to import DaVinci Resolve Script: {e}")
            print("Make sure DaVinci Resolve is installed and paths are correct.")
            return False
        except Exception as e:
            print(f"Failed to connect to DaVinci Resolve: {e}")
            return False

    @property
    def resolve(self):
        """Get the Resolve object."""
        return self._resolve

    @property
    def fusion(self):
        """Get the Fusion object."""
        return self._fusion

    @property
    def project_manager(self):
        """Get the Project Manager object."""
        return self._project_manager

    @property
    def is_connected(self) -> bool:
        """Check if connected to Resolve."""
        return self._resolve is not None

    # ==================== Project Operations ====================

    def get_current_project(self):
        """Get the currently open project."""
        if not self._project_manager:
            return None
        return self._project_manager.GetCurrentProject()

    def get_project_name(self) -> Optional[str]:
        """Get current project name."""
        project = self.get_current_project()
        return project.GetName() if project else None

    def list_projects(self) -> list[str]:
        """List all projects in current database."""
        if not self._project_manager:
            return []
        return self._project_manager.GetProjectListInCurrentFolder() or []

    def create_project(self, name: str) -> bool:
        """Create a new project."""
        if not self._project_manager:
            return False
        project = self._project_manager.CreateProject(name)
        return project is not None

    def open_project(self, name: str) -> bool:
        """Open an existing project by name."""
        if not self._project_manager:
            return False
        project = self._project_manager.LoadProject(name)
        return project is not None

    def save_project(self) -> bool:
        """Save the current project."""
        project = self.get_current_project()
        if not project:
            return False
        return project.SaveProject()

    def close_project(self) -> bool:
        """Close the current project."""
        if not self._project_manager:
            return False
        return self._project_manager.CloseProject(self.get_current_project())

    # ==================== Timeline Operations ====================

    def get_current_timeline(self):
        """Get the current timeline."""
        project = self.get_current_project()
        return project.GetCurrentTimeline() if project else None

    def get_timeline_count(self) -> int:
        """Get number of timelines in current project."""
        project = self.get_current_project()
        return project.GetTimelineCount() if project else 0

    def list_timelines(self) -> list[dict]:
        """List all timelines in current project."""
        project = self.get_current_project()
        if not project:
            return []

        timelines = []
        count = project.GetTimelineCount()
        for i in range(1, count + 1):
            timeline = project.GetTimelineByIndex(i)
            if timeline:
                timelines.append({
                    "index": i,
                    "name": timeline.GetName(),
                    "duration": timeline.GetEndFrame() - timeline.GetStartFrame(),
                })
        return timelines

    def create_timeline(self, name: str) -> bool:
        """Create a new empty timeline."""
        project = self.get_current_project()
        if not project:
            return False
        media_pool = project.GetMediaPool()
        timeline = media_pool.CreateEmptyTimeline(name)
        return timeline is not None

    def set_current_timeline(self, name: str) -> bool:
        """Set the current timeline by name."""
        project = self.get_current_project()
        if not project:
            return False

        count = project.GetTimelineCount()
        for i in range(1, count + 1):
            timeline = project.GetTimelineByIndex(i)
            if timeline and timeline.GetName() == name:
                return project.SetCurrentTimeline(timeline)
        return False

    def get_timeline_info(self) -> Optional[dict]:
        """Get detailed info about current timeline."""
        timeline = self.get_current_timeline()
        if not timeline:
            return None

        return {
            "name": timeline.GetName(),
            "start_frame": timeline.GetStartFrame(),
            "end_frame": timeline.GetEndFrame(),
            "track_count": {
                "video": timeline.GetTrackCount("video"),
                "audio": timeline.GetTrackCount("audio"),
                "subtitle": timeline.GetTrackCount("subtitle"),
            },
            "current_timecode": timeline.GetCurrentTimecode(),
        }

    # ==================== Media Pool Operations ====================

    def get_media_pool(self):
        """Get the media pool."""
        project = self.get_current_project()
        return project.GetMediaPool() if project else None

    def import_media(self, file_paths: list[str]) -> list[dict]:
        """Import media files into the media pool."""
        media_pool = self.get_media_pool()
        if not media_pool:
            return []

        clips = media_pool.ImportMedia(file_paths)
        if not clips:
            return []

        return [{"name": clip.GetName(), "path": clip.GetClipProperty("File Path")}
                for clip in clips if clip]

    def list_media_pool_items(self) -> list[dict]:
        """List items in the root folder of media pool."""
        media_pool = self.get_media_pool()
        if not media_pool:
            return []

        root_folder = media_pool.GetRootFolder()
        if not root_folder:
            return []

        clips = root_folder.GetClipList()
        return [{"name": clip.GetName()} for clip in clips if clip]

    def create_bin(self, name: str) -> bool:
        """Create a new bin/folder in media pool."""
        media_pool = self.get_media_pool()
        if not media_pool:
            return False
        folder = media_pool.AddSubFolder(media_pool.GetCurrentFolder(), name)
        return folder is not None

    # ==================== Marker Operations ====================

    def add_marker(self, frame: int, color: str = "Blue",
                   name: str = "", note: str = "", duration: int = 1) -> bool:
        """Add a marker to the current timeline."""
        timeline = self.get_current_timeline()
        if not timeline:
            return False
        return timeline.AddMarker(frame, color, name, note, duration)

    def get_markers(self) -> dict:
        """Get all markers from current timeline."""
        timeline = self.get_current_timeline()
        if not timeline:
            return {}
        return timeline.GetMarkers()

    def delete_marker(self, frame: int) -> bool:
        """Delete marker at specified frame."""
        timeline = self.get_current_timeline()
        if not timeline:
            return False
        return timeline.DeleteMarkerAtFrame(frame)

    # ==================== Render Operations ====================

    def get_render_presets(self) -> list[str]:
        """Get list of available render presets."""
        project = self.get_current_project()
        if not project:
            return []
        return project.GetRenderPresetList() or []

    def set_render_preset(self, preset_name: str) -> bool:
        """Set the render preset."""
        project = self.get_current_project()
        if not project:
            return False
        return project.LoadRenderPreset(preset_name)

    def add_render_job(self) -> str:
        """Add current timeline to render queue."""
        project = self.get_current_project()
        if not project:
            return ""
        return project.AddRenderJob()

    def start_render(self) -> bool:
        """Start rendering all jobs in queue."""
        project = self.get_current_project()
        if not project:
            return False
        return project.StartRendering()

    def get_render_status(self) -> dict:
        """Get current render status."""
        project = self.get_current_project()
        if not project:
            return {}

        return {
            "is_rendering": project.IsRenderingInProgress(),
            "job_count": project.GetRenderJobCount(),
        }

    # ==================== Page Navigation ====================

    def open_page(self, page_name: str) -> bool:
        """
        Open a specific page in Resolve.
        Valid pages: media, cut, edit, fusion, color, fairlight, deliver
        """
        if not self._resolve:
            return False
        return self._resolve.OpenPage(page_name.lower())

    def get_current_page(self) -> str:
        """Get the currently open page."""
        if not self._resolve:
            return ""
        return self._resolve.GetCurrentPage()

    # ==================== Playback Control ====================

    def play(self) -> bool:
        """Start playback."""
        timeline = self.get_current_timeline()
        if not timeline:
            return False
        # Note: Playback control requires GUI interaction
        # This is a placeholder - actual implementation may vary
        return True

    def stop(self) -> bool:
        """Stop playback."""
        timeline = self.get_current_timeline()
        return timeline is not None

    def set_playhead_position(self, frame: int) -> bool:
        """Set playhead to specific frame."""
        timeline = self.get_current_timeline()
        if not timeline:
            return False
        return timeline.SetCurrentTimecode(str(frame))

    # ==================== Utility Methods ====================

    def get_version(self) -> str:
        """Get DaVinci Resolve version."""
        if not self._resolve:
            return "Not connected"
        version = self._resolve.GetVersion()
        if isinstance(version, list):
            return ".".join(str(v) for v in version)
        return str(version)

    def get_product_name(self) -> str:
        """Get product name (Resolve/Resolve Studio)."""
        if not self._resolve:
            return "Not connected"
        return self._resolve.GetProductName()


# Global connection instance
_connection: Optional[ResolveConnection] = None


def get_connection() -> ResolveConnection:
    """Get or create the global Resolve connection."""
    global _connection
    if _connection is None:
        _connection = ResolveConnection()
    return _connection
