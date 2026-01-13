-- HDR / Dynamic Range Tools
-- Expand and compress dynamic range

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Shadow recovery
    local shadowLift = comp:AddTool("ColorCorrector")
    shadowLift:SetAttrs({TOOLS_Name = "HDR_ShadowRecovery"})
    shadowLift.ShadowsRGBGain = {1.3, 1.3, 1.3}
    shadowLift.ShadowsRGBGamma = 1.2

    -- Highlight recovery
    local hiRecovery = comp:AddTool("ColorCorrector")
    hiRecovery:SetAttrs({TOOLS_Name = "HDR_HighlightRecovery"})
    hiRecovery.HighlightsRGBGain = {0.85, 0.85, 0.85}

    -- Local contrast (clarity)
    local clarity = comp:AddTool("UnsharpMask")
    clarity:SetAttrs({TOOLS_Name = "HDR_Clarity"})
    clarity.Size = 50
    clarity.Gain = 0.3

    -- Tone mapping (HDR to SDR)
    local toneMap = comp:AddTool("ColorCorrector")
    toneMap:SetAttrs({TOOLS_Name = "HDR_ToneMap"})
    toneMap.MasterRGBContrast = 0.9
    toneMap.MasterRGBGamma = 1.1
    toneMap.HighlightsRGBGain = {0.8, 0.8, 0.8}

    -- Glow for HDR bloom effect
    local hdrBloom = comp:AddTool("SoftGlow")
    hdrBloom:SetAttrs({TOOLS_Name = "HDR_Bloom"})
    hdrBloom.Threshold = 0.8
    hdrBloom.Gain = 0.15
    hdrBloom.XGlowSize = 30

    -- Dynamic range expansion
    local expand = comp:AddTool("ColorCorrector")
    expand:SetAttrs({TOOLS_Name = "HDR_Expand"})
    expand.MasterRGBContrast = 1.2
    expand.MasterRGBGamma = 0.95

    comp:Unlock()

    print("✓ HDR tools added")
    print("")
    print("Tools:")
    print("  HDR_ShadowRecovery - Lift shadows")
    print("  HDR_HighlightRecovery - Recover highlights")
    print("  HDR_Clarity - Local contrast")
    print("  HDR_ToneMap - HDR to SDR conversion")
    print("  HDR_Bloom - Highlight glow")
    print("  HDR_Expand - Increase dynamic range")
else
    print("Error: No composition found")
end
