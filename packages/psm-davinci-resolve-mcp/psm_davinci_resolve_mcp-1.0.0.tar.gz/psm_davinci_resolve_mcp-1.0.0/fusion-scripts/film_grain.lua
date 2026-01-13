-- Add cinematic film grain effect
-- Run from: Fusion page > Console
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Film grain generator
    local grain = comp:AddTool("FilmGrain")
    grain:SetAttrs({TOOLS_Name = "CinematicGrain"})
    grain.Size = 1.5
    grain.Strength = 0.15
    grain.Softness = 0.3
    grain.Power = 1.2
    grain.SatResponse = 0.5  -- Less grain in saturated areas
    grain.LumResponse = 0.3  -- Less grain in highlights

    -- Optional: Add slight vignette
    local vignette = comp:AddTool("EllipseMask")
    vignette:SetAttrs({TOOLS_Name = "Vignette"})
    vignette.SoftEdge = 0.4
    vignette.Width = 1.8
    vignette.Height = 1.8

    local vigCC = comp:AddTool("ColorCorrector")
    vigCC:SetAttrs({TOOLS_Name = "VignetteCC"})
    vigCC.MasterRGBGain = 0.7

    comp:Unlock()
    print("✓ Film grain + vignette added")
    print("  Connect footage to CinematicGrain input")
    print("  Adjust Strength (0.1-0.3) for intensity")
end
