-- Skin Retouching Tools
-- Beauty/skin smoothing without losing detail

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Skin tone qualifier
    local skinQual = comp:AddTool("ColorCorrector")
    skinQual:SetAttrs({TOOLS_Name = "Skin_Qualifier"})
    -- Typical skin tone range
    -- Hue: 0-40 degrees (orange/red)
    -- Saturation: 20-70%

    -- Frequency separation - Low (color/tone)
    local lowFreq = comp:AddTool("Blur")
    lowFreq:SetAttrs({TOOLS_Name = "Skin_LowFreq"})
    lowFreq.XBlurSize = 15
    lowFreq.YBlurSize = 15

    -- Frequency separation - High (detail)
    local highFreq = comp:AddTool("CustomTool")
    highFreq:SetAttrs({TOOLS_Name = "Skin_HighFreq"})
    -- Subtract low from original to get detail

    -- Skin smoothing (controlled blur)
    local skinSmooth = comp:AddTool("Blur")
    skinSmooth:SetAttrs({TOOLS_Name = "Skin_Smooth"})
    skinSmooth.XBlurSize = 5
    skinSmooth.YBlurSize = 5

    -- Preserve detail mask
    local detailMask = comp:AddTool("LumaKeyer")
    detailMask:SetAttrs({TOOLS_Name = "Skin_DetailMask"})
    detailMask.Low = 0.1
    detailMask.High = 0.9

    -- Color correction for skin
    local skinCC = comp:AddTool("ColorCorrector")
    skinCC:SetAttrs({TOOLS_Name = "Skin_ColorCorrect"})
    skinCC.MasterSaturation = 0.95  -- Slight desat
    skinCC.MidtonesRGBGain = {1.02, 1.0, 0.98}  -- Warm

    -- Subtle glow for beauty look
    local beautyGlow = comp:AddTool("SoftGlow")
    beautyGlow:SetAttrs({TOOLS_Name = "Skin_BeautyGlow"})
    beautyGlow.Threshold = 0.6
    beautyGlow.Gain = 0.1
    beautyGlow.XGlowSize = 10

    comp:Unlock()

    print("✓ Skin retouch tools added")
    print("")
    print("Workflow:")
    print("  1. Use Skin_Qualifier to isolate skin")
    print("  2. Apply Skin_Smooth (masked)")
    print("  3. Use Skin_DetailMask to preserve edges")
    print("  4. Add Skin_BeautyGlow for soft look")
    print("")
    print("Tip: Keep it subtle! Over-smoothing looks fake")
else
    print("Error: No composition found")
end
