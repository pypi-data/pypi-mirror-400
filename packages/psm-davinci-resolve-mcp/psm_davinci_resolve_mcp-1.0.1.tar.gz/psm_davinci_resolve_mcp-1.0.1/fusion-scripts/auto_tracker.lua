-- Add a planar tracker for motion tracking
-- Run from: Fusion page > Console
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Add Planar Tracker
    local tracker = comp:AddTool("PlanarTracker")
    tracker:SetAttrs({TOOLS_Name = "AutoTracker"})

    -- Add a transform to apply tracking data
    local transform = comp:AddTool("Transform")
    transform:SetAttrs({TOOLS_Name = "TrackedTransform"})

    comp:Unlock()
    print("✓ Added PlanarTracker and Transform nodes")
    print("  1. Connect your footage to PlanarTracker input")
    print("  2. Draw a pattern to track in the viewer")
    print("  3. Press Track Forward button")
    print("  4. Connect tracker output to transform")
else
    print("✗ No composition open")
end
