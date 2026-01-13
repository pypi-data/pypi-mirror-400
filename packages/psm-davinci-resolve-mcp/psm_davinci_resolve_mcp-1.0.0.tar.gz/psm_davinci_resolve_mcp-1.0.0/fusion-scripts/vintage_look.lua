-- Vintage Film Look
-- Complete vintage/retro film emulation

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Desaturate slightly
    local desat = comp:AddTool("ColorCorrector")
    desat:SetAttrs({TOOLS_Name = "VintageSaturation"})
    desat.MasterSaturation = 0.7

    -- Add warm tint
    local tint = comp:AddTool("ColorCorrector")
    tint:SetAttrs({TOOLS_Name = "WarmTint"})
    tint.MasterRGBGain = {1.05, 1.0, 0.9}  -- Warm highlights
    tint.ShadowsRGBGain = {0.95, 0.95, 1.05}  -- Cool shadows

    -- Lift blacks (faded look)
    local lift = comp:AddTool("ColorCorrector")
    lift:SetAttrs({TOOLS_Name = "LiftedBlacks"})
    lift.MasterRGBLift = 0.05

    -- Soft contrast curve
    local contrast = comp:AddTool("ColorCurves")
    contrast:SetAttrs({TOOLS_Name = "SoftContrast"})

    -- Add film grain
    local grain = comp:AddTool("FilmGrain")
    grain:SetAttrs({TOOLS_Name = "VintageGrain"})
    grain.Size = 1.5
    grain.Strength = 0.3
    grain.Softness = 0.5

    -- Vignette
    local ellipse = comp:AddTool("EllipseMask")
    ellipse:SetAttrs({TOOLS_Name = "VignetteMask"})
    ellipse.SoftEdge = 0.4
    ellipse.Width = 1.8
    ellipse.Height = 1.4

    local vignette = comp:AddTool("Background")
    vignette:SetAttrs({TOOLS_Name = "VignetteOverlay"})
    vignette.TopLeftRed = 0
    vignette.TopLeftGreen = 0
    vignette.TopLeftBlue = 0
    vignette.TopLeftAlpha = 0.4

    comp:Unlock()

    print("✓ Vintage film look applied")
    print("  - Desaturated colors")
    print("  - Warm highlights / Cool shadows")
    print("  - Lifted blacks (faded)")
    print("  - Film grain")
    print("  - Vignette")
else
    print("Error: No composition found")
end
