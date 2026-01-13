# Troubleshooting Guide

Common issues and solutions for the DaVinci Resolve Automation Suite.

## DaVinci Resolve Not Responding

### Commands not executing

**Cause**: DaVinci Resolve not running or not focused.

**Solutions**:
1. Launch Resolve first: `resolve launch`
2. Wait for Resolve to fully load
3. Ensure Resolve window is not minimized

### AppleScript permission denied

**Cause**: macOS accessibility permissions not granted.

**Solutions**:
1. Go to **System Preferences > Security & Privacy > Privacy > Accessibility**
2. Add **Terminal** (or your terminal app)
3. Add **Script Editor**
4. Restart Terminal after adding permissions

### `osascript` errors

**Cause**: AppleScript syntax or permission issue.

**Solution**: Test AppleScript directly:
```bash
osascript -e 'tell application "DaVinci Resolve" to activate'
```

## Page Navigation Issues

### Wrong page selected

**Cause**: Keyboard shortcut conflict.

**Solutions**:
1. Reset Resolve keyboard shortcuts to default
2. Check no other app is capturing shortcuts
3. Use menu navigation instead of shortcuts

**Default page shortcuts**:
| Page | Shortcut |
|------|----------|
| Media | Shift+2 |
| Cut | Shift+3 |
| Edit | Shift+4 |
| Fusion | Shift+5 |
| Color | Shift+6 |
| Fairlight | Shift+7 |
| Deliver | Shift+8 |

### Page doesn't switch

**Cause**: Resolve still loading or dialog open.

**Solutions**:
1. Close any open dialogs
2. Wait for current operation to complete
3. Try again after a short delay

## Fusion Script Issues

### Script not found

**Cause**: Script not in correct location.

**Solution**: Verify script location:
```
macOS: ~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/
Windows: %APPDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\
```

### Script execution fails

**Cause**: Lua syntax error or API issue.

**Solutions**:
1. Open Fusion console to see errors: `resolve console`
2. Test script manually in Fusion console
3. Check Fusion API compatibility

**Common Lua errors**:
```lua
-- Wrong
comp.GetCurrentTime()  -- GetCurrentTime doesn't exist

-- Correct
comp:GetAttrs("COMPN_CurrentTime")
```

### No active composition

**Cause**: Fusion page not active or no comp.

**Solutions**:
1. Navigate to Fusion page: `resolve fusion`
2. Create or select a composition
3. Ensure timeline has Fusion clips

### `dofile` not working

**Cause**: Path or permission issue.

**Solution**: Use correct path format:
```lua
-- macOS
dofile("/Users/username/scripts/my_script.lua")

-- Windows (use forward slashes)
dofile("C:/Users/username/scripts/my_script.lua")
```

## Workflow Issues

### YouTube workflow fails

**Cause**: Step failed or Resolve not ready.

**Solutions**:
1. Run steps individually to find failure point
2. Ensure all required media is imported
3. Check timeline is selected

### Batch processing stops

**Cause**: File not found or format not supported.

**Solutions**:
1. Verify all files exist in source folder
2. Check file formats are supported by Resolve
3. Look for error messages in terminal output

### Export fails

**Cause**: Invalid render settings or disk full.

**Solutions**:
1. Check Deliver page settings
2. Verify destination path exists
3. Ensure enough disk space
4. Try different codec/format

## Color Grading Issues

### LUT not applying

**Cause**: LUT not installed or wrong path.

**Solutions**:
1. Install LUT to Resolve LUT folder:
   ```
   macOS: ~/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/
   ```
2. Refresh Resolve's LUT list (Project Settings > Color Management)
3. Check LUT format (.cube, .3dl supported)

### Color grade looks wrong

**Cause**: Color space or gamma mismatch.

**Solutions**:
1. Check Project Settings > Color Management
2. Ensure timeline color space matches footage
3. Apply color space transform if needed

## MCP Server Issues (Studio Only)

### `External scripting not enabled`

**Cause**: Resolve Studio scripting disabled.

**Solution**:
1. Open DaVinci Resolve **Studio**
2. Go to **Preferences > System > General**
3. Set **External scripting using** to "Local"
4. Restart Resolve
5. Restart Claude Code

### `Connection refused`

**Cause**: Resolve not running or wrong port.

**Solutions**:
1. Ensure Resolve Studio is running
2. Check no firewall blocking localhost
3. Verify scripting is enabled

### `Module not found`

**Cause**: Python dependencies missing.

**Solution**:
```bash
cd ~/davinci-resolve-mcp
pip install -r requirements.txt
# or
pip3 install DaVinciResolveScript
```

### `DaVinciResolveScript not found`

**Cause**: Resolve scripting module not in path.

**Solution** (macOS):
```bash
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
```

Add to `~/.zshrc` for persistence.

## Installation Issues

### Commands not found

**Cause**: Scripts not in PATH.

**Solution**:
```bash
# Add to PATH
export PATH="$PATH:$HOME/davinci-resolve-mcp/automation"

# Or create symlinks
ln -s ~/davinci-resolve-mcp/automation/resolve /usr/local/bin/resolve
```

### Permission denied

**Solution**:
```bash
chmod +x ~/davinci-resolve-mcp/automation/*
chmod +x ~/davinci-resolve-mcp/automation/workflows/*
```

## Performance Issues

### Scripts running slowly

**Solutions**:
1. Close unused Resolve windows/panels
2. Reduce timeline resolution for editing
3. Use proxy media for large files
4. Increase RAM allocation in Resolve preferences

### Resolve becoming unresponsive

**Solutions**:
1. Clear Resolve cache (Playback > Delete Render Cache > All)
2. Restart Resolve periodically
3. Reduce number of nodes in Fusion
4. Check GPU drivers are up to date

## Debugging

### Enable verbose output

```bash
# Add debug flag to scripts
resolve --debug status
```

### Test AppleScript separately

```bash
# Open Script Editor and test commands
osascript -e 'tell application "System Events"
  tell process "DaVinci Resolve"
    keystroke "5" using shift down
  end tell
end tell'
```

### Check Resolve logs

```
macOS: ~/Library/Logs/Blackmagic Design/DaVinci Resolve/
Windows: %APPDATA%\Blackmagic Design\DaVinci Resolve\logs\
```

### Verify Resolve version

```bash
resolve status
# Shows: DaVinci Resolve [version] - [Free/Studio]
```

## Getting Help

- [DaVinci Resolve Manual](https://www.blackmagicdesign.com/products/davinciresolve/training)
- [Fusion Scripting Guide](https://documents.blackmagicdesign.com/UserManuals/Fusion_Scripting_Guide.pdf)
- [Blackmagic Forum](https://forum.blackmagicdesign.com/viewforum.php?f=21)
- [GitHub Issues](https://github.com/PurpleSquirrelMedia/davinci-resolve-mcp/issues)
