-- Ink/Liquid Transitions
-- Organic ink spread and liquid morph transitions

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Ink spread using noise
    local inkNoise = comp:AddTool("FastNoise")
    inkNoise:SetAttrs({TOOLS_Name = "InkTrans_Noise"})
    inkNoise.Detail = 5
    inkNoise.Contrast = 2
    inkNoise.Brightness = 0  -- Animate -1 → 1 for spread
    inkNoise.XScale = 0.3
    inkNoise.YScale = 0.3
    inkNoise.SeetheRate = 0.02

    -- Threshold to create hard ink edge
    local inkThresh = comp:AddTool("ColorCorrector")
    inkThresh:SetAttrs({TOOLS_Name = "InkTrans_Threshold"})
    inkThresh.MasterRGBContrast = 5
    inkThresh.MasterRGBGamma = 0.5  -- Animate for spread

    -- Blur edge slightly
    local inkBlur = comp:AddTool("Blur")
    inkBlur:SetAttrs({TOOLS_Name = "InkTrans_EdgeBlur"})
    inkBlur.XBlurSize = 3
    inkBlur.YBlurSize = 3

    -- Luma keyer to use as matte
    local inkMatte = comp:AddTool("LumaKeyer")
    inkMatte:SetAttrs({TOOLS_Name = "InkTrans_Matte"})
    inkMatte.Low = 0.4
    inkMatte.High = 0.6

    -- Merge with ink as matte
    local inkMerge = comp:AddTool("Merge")
    inkMerge:SetAttrs({TOOLS_Name = "InkTrans_Merge"})
    -- Connect: Foreground=ClipB, Background=ClipA, EffectMask=InkMatte

    -- Liquid morph using displacement
    local liquidDisp = comp:AddTool("Displace")
    liquidDisp:SetAttrs({TOOLS_Name = "LiquidTrans_Displace"})
    liquidDisp.XRefraction = 0.5
    liquidDisp.YRefraction = 0.5

    -- Ripple effect
    local ripple = comp:AddTool("Dent")
    ripple:SetAttrs({TOOLS_Name = "LiquidTrans_Ripple"})
    ripple.Size = 0.5
    ripple.Strength = 0  -- Animate 0 → 0.3 → 0

    comp:Unlock()

    print("✓ Ink/Liquid transitions added")
    print("")
    print("Ink Spread:")
    print("  Animate InkTrans_Noise.Brightness: -1 → 1")
    print("  Or animate InkTrans_Threshold.Gamma: 2 → 0.2")
    print("")
    print("Liquid Morph:")
    print("  Animate LiquidTrans_Ripple.Strength: 0 → 0.3 → 0")
else
    print("Error: No composition found")
end
