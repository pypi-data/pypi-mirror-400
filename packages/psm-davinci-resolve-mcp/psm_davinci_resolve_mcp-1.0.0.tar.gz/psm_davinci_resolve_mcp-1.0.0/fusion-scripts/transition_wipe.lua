-- Wipe Transitions
-- Various wipe styles for scene transitions

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Linear wipe (left to right)
    local wipeL = comp:AddTool("RectangleMask")
    wipeL:SetAttrs({TOOLS_Name = "Wipe_LeftRight"})
    wipeL.Width = 2
    wipeL.Height = 2
    wipeL.Center = {-0.5, 0.5}  -- Animate X: -0.5 → 1.5
    wipeL.SoftEdge = 0.02

    -- Vertical wipe (top to bottom)
    local wipeV = comp:AddTool("RectangleMask")
    wipeV:SetAttrs({TOOLS_Name = "Wipe_TopDown"})
    wipeV.Width = 2
    wipeV.Height = 2
    wipeV.Center = {0.5, 1.5}  -- Animate Y: 1.5 → -0.5
    wipeV.SoftEdge = 0.02

    -- Diagonal wipe
    local wipeD = comp:AddTool("RectangleMask")
    wipeD:SetAttrs({TOOLS_Name = "Wipe_Diagonal"})
    wipeD.Width = 3
    wipeD.Height = 3
    wipeD.Angle = 45
    wipeD.Center = {-0.5, 1.5}  -- Animate to {1.5, -0.5}
    wipeD.SoftEdge = 0.03

    -- Iris wipe (circle)
    local iris = comp:AddTool("EllipseMask")
    iris:SetAttrs({TOOLS_Name = "Wipe_Iris"})
    iris.Width = 0  -- Animate 0 → 2.5
    iris.Height = 0  -- Animate 0 → 2.5
    iris.Center = {0.5, 0.5}
    iris.SoftEdge = 0.02

    -- Clock wipe
    local clock = comp:AddTool("EllipseMask")
    clock:SetAttrs({TOOLS_Name = "Wipe_Clock"})
    clock.Width = 3
    clock.Height = 3
    clock.StartAngle = 0  -- Animate 0 → 360
    clock.EndAngle = 0

    comp:Unlock()

    print("✓ Wipe transitions added")
    print("")
    print("Usage (animate over ~15-30 frames):")
    print("  Wipe_LeftRight: Center.X -0.5 → 1.5")
    print("  Wipe_TopDown: Center.Y 1.5 → -0.5")
    print("  Wipe_Diagonal: Center {-0.5, 1.5} → {1.5, -0.5}")
    print("  Wipe_Iris: Width/Height 0 → 2.5")
    print("  Wipe_Clock: StartAngle 0 → 360")
else
    print("Error: No composition found")
end
