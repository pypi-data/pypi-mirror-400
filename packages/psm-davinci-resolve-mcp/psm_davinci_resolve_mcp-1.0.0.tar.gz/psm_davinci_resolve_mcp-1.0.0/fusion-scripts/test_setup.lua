-- Test script to verify Fusion scripting is working
-- Run from: Fusion page > Console (press `)
print("========================================")
print("   DaVinci Resolve Scripting Test")
print("========================================")

-- Check if we can access Fusion
if fusion then
    print("✓ Fusion object available")
else
    print("✗ Cannot access Fusion object")
    return
end

-- Check for current composition
local comp = fusion:GetCurrentComp()
if comp then
    print("✓ Composition accessible")
    local attrs = comp:GetAttrs()
    print("  Name: " .. (attrs.COMPS_Name or "Untitled"))
    print("  Frames: " .. attrs.COMPN_GlobalStart .. " - " .. attrs.COMPN_GlobalEnd)

    -- Count tools
    local tools = comp:GetToolList()
    print("  Tools: " .. #tools)
else
    print("⚠ No composition open (create one first)")
end

-- Check Resolve access (Studio only)
if resolve then
    print("✓ Resolve API available (Studio)")
    local projectManager = resolve:GetProjectManager()
    if projectManager then
        local project = projectManager:GetCurrentProject()
        if project then
            print("  Project: " .. project:GetName())
        end
    end
else
    print("○ Resolve API not available (Free version - normal)")
end

print("========================================")
print("  All basic checks passed!")
print("  Scripts are ready to use.")
print("========================================")
