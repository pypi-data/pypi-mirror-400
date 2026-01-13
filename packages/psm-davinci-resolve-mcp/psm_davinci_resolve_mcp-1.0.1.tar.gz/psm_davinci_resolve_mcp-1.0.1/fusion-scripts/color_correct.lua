-- Apply basic color correction to selected clip
-- Run from: Fusion page > Console
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Add Color Corrector node
    local cc = comp:AddTool("ColorCorrector")
    cc:SetAttrs({TOOLS_Name = "BasicCC"})

    -- Set some default adjustments
    cc.MasterRGBGain = 1.1      -- Slight boost
    cc.MasterRGBGamma = 0.95    -- Slightly darker mids
    cc.MasterSaturation = 1.1   -- Boost saturation

    -- Add a soft glow
    local glow = comp:AddTool("SoftGlow")
    glow:SetAttrs({TOOLS_Name = "SubtleGlow"})
    glow.Gain = 0.3
    glow.Threshold = 0.7

    comp:Unlock()
    print("✓ Added ColorCorrector and SoftGlow nodes")
else
    print("✗ No composition open")
end
