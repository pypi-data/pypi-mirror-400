-- Gradient Backgrounds
-- Various gradient generators for backgrounds

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Linear gradient (top to bottom)
    local linearBG = comp:AddTool("Background")
    linearBG:SetAttrs({TOOLS_Name = "Gradient_Linear"})
    linearBG.Type = "Gradient"
    linearBG.TopLeftRed = 0.2
    linearBG.TopLeftGreen = 0.4
    linearBG.TopLeftBlue = 0.8
    linearBG.BottomRightRed = 0.1
    linearBG.BottomRightGreen = 0.1
    linearBG.BottomRightBlue = 0.3

    -- Radial gradient (center glow)
    local radialBG = comp:AddTool("Background")
    radialBG:SetAttrs({TOOLS_Name = "Gradient_Radial"})
    radialBG.Type = "Gradient"
    radialBG.GradientType = 1  -- Radial
    radialBG.TopLeftRed = 0.3
    radialBG.TopLeftGreen = 0.3
    radialBG.TopLeftBlue = 0.4
    radialBG.BottomRightRed = 0.05
    radialBG.BottomRightGreen = 0.05
    radialBG.BottomRightBlue = 0.08

    -- Sunset gradient
    local sunset = comp:AddTool("Background")
    sunset:SetAttrs({TOOLS_Name = "Gradient_Sunset"})
    sunset.Type = "Gradient"
    sunset.TopLeftRed = 1.0
    sunset.TopLeftGreen = 0.6
    sunset.TopLeftBlue = 0.2
    sunset.BottomRightRed = 0.4
    sunset.BottomRightGreen = 0.1
    sunset.BottomRightBlue = 0.3

    -- Cool blue gradient
    local coolBlue = comp:AddTool("Background")
    coolBlue:SetAttrs({TOOLS_Name = "Gradient_CoolBlue"})
    coolBlue.Type = "Gradient"
    coolBlue.TopLeftRed = 0.1
    coolBlue.TopLeftGreen = 0.3
    coolBlue.TopLeftBlue = 0.5
    coolBlue.BottomRightRed = 0.02
    coolBlue.BottomRightGreen = 0.05
    coolBlue.BottomRightBlue = 0.15

    -- Dark vignette overlay
    local vignette = comp:AddTool("Background")
    vignette:SetAttrs({TOOLS_Name = "Gradient_Vignette"})
    vignette.Type = "Gradient"
    vignette.GradientType = 1  -- Radial
    vignette.TopLeftRed = 0
    vignette.TopLeftGreen = 0
    vignette.TopLeftBlue = 0
    vignette.TopLeftAlpha = 0
    vignette.BottomRightRed = 0
    vignette.BottomRightGreen = 0
    vignette.BottomRightBlue = 0
    vignette.BottomRightAlpha = 0.7

    comp:Unlock()

    print("✓ Gradient backgrounds added")
    print("")
    print("Available gradients:")
    print("  Gradient_Linear - Blue top to dark bottom")
    print("  Gradient_Radial - Center glow")
    print("  Gradient_Sunset - Warm orange to purple")
    print("  Gradient_CoolBlue - Professional blue")
    print("  Gradient_Vignette - Dark edge overlay")
else
    print("Error: No composition found")
end
