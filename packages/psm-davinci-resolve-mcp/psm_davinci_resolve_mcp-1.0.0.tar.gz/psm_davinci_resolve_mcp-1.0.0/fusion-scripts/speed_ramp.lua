-- Create a speed ramp / time remap setup
-- Run from: Fusion page > Console
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Time Speed node for ramping
    local timeSpeed = comp:AddTool("TimeSpeed")
    timeSpeed:SetAttrs({TOOLS_Name = "SpeedRamp"})
    timeSpeed.Speed = 1.0
    timeSpeed.InterpolationMode = 2  -- Optical flow

    -- Add keyframes info
    print("✓ Speed Ramp node created")
    print("")
    print("To create a speed ramp:")
    print("  1. Connect footage to SpeedRamp input")
    print("  2. Right-click Speed parameter > Animate")
    print("  3. At normal speed sections: Speed = 1.0")
    print("  4. At slow-mo sections: Speed = 0.25 (or lower)")
    print("  5. Use bezier curves in spline editor for smooth ramps")
    print("")
    print("Interpolation modes:")
    print("  0 = Nearest (choppy)")
    print("  1 = Linear (basic)")
    print("  2 = Optical Flow (smoothest, slower)")

    comp:Unlock()
else
    print("✗ No composition open")
end
