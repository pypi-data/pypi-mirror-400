-- Lens Flare Effect
-- Adds cinematic lens flare

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Create lens flare
    local flare = comp:AddTool("LensFlare")
    flare:SetAttrs({TOOLS_Name = "CinematicFlare"})
    flare.Position = {0.7, 0.3}  -- Upper right
    flare.NumberOfRays = 8
    flare.RayLength = 2.0
    flare.StarBrightness = 0.5
    flare.Brightness = 0.8
    flare.Scale = 0.15

    -- Glow for extra bloom
    local glow = comp:AddTool("SoftGlow")
    glow:SetAttrs({TOOLS_Name = "FlareGlow"})
    glow.Threshold = 0.7
    glow.Gain = 0.3
    glow.XGlowSize = 15
    glow.YGlowSize = 15

    -- Merge flare with footage
    local merge = comp:AddTool("Merge")
    merge:SetAttrs({TOOLS_Name = "FlareMerge"})
    merge.ApplyMode = "Screen"
    merge.Blend = 0.7

    comp:Unlock()

    print("✓ Lens flare effect added")
    print("  Animate Position to follow light source")
    print("  Adjust Brightness for intensity")
else
    print("Error: No composition found")
end
