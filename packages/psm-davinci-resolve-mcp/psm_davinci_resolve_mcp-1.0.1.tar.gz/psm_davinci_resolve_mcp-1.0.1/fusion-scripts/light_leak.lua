-- Light Leak / Film Burn Effect
-- Adds organic light leaks for vintage/dreamy look

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Create animated light leak
    local leak1 = comp:AddTool("FastNoise")
    leak1:SetAttrs({TOOLS_Name = "LightLeak1"})
    leak1.Detail = 2
    leak1.Contrast = 3
    leak1.Brightness = 0.2
    leak1.XScale = 0.3
    leak1.SeetheRate = 0.02  -- Animate over time

    -- Color the leak warm orange/red
    local leakColor = comp:AddTool("ColorCorrector")
    leakColor:SetAttrs({TOOLS_Name = "LeakColor"})
    leakColor.MasterRGBGain = {1.5, 0.6, 0.2}  -- Orange tint

    -- Second leak for variety
    local leak2 = comp:AddTool("FastNoise")
    leak2:SetAttrs({TOOLS_Name = "LightLeak2"})
    leak2.Detail = 1
    leak2.Contrast = 4
    leak2.Brightness = 0.1
    leak2.XScale = 0.5
    leak2.Seethe = 0.3

    local leak2Color = comp:AddTool("ColorCorrector")
    leak2Color:SetAttrs({TOOLS_Name = "Leak2Color"})
    leak2Color.MasterRGBGain = {1.2, 1.0, 0.3}  -- Yellow tint

    -- Merge with screen blend
    local merge = comp:AddTool("Merge")
    merge:SetAttrs({TOOLS_Name = "LeakMerge"})
    merge.ApplyMode = "Screen"
    merge.Blend = 0.4

    -- Glow for soft edges
    local glow = comp:AddTool("SoftGlow")
    glow:SetAttrs({TOOLS_Name = "LeakGlow"})
    glow.Threshold = 0.5
    glow.Gain = 0.5
    glow.XGlowSize = 50

    comp:Unlock()

    print("✓ Light leak effect added")
    print("  SeetheRate animates leak movement")
    print("  Adjust Blend for intensity")
    print("  Screen blend mode for natural look")
else
    print("Error: No composition found")
end
