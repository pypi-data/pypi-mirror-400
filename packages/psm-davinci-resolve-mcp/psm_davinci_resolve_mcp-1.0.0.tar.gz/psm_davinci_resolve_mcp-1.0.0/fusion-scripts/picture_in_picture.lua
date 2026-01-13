-- Picture-in-Picture Setup
-- Creates PiP layout for tutorials, reactions, gaming

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Main video (full size background)
    local mainBG = comp:AddTool("Background")
    mainBG:SetAttrs({TOOLS_Name = "MainVideoBG"})
    mainBG.TopLeftRed = 0.1
    mainBG.TopLeftGreen = 0.1
    mainBG.TopLeftBlue = 0.1

    -- PiP transform (corner position)
    local pipTransform = comp:AddTool("Transform")
    pipTransform:SetAttrs({TOOLS_Name = "PiPTransform"})
    pipTransform.Size = 0.25  -- 25% size
    pipTransform.Center = {0.85, 0.15}  -- Bottom right corner

    -- PiP border
    local pipBorder = comp:AddTool("RectangleMask")
    pipBorder:SetAttrs({TOOLS_Name = "PiPBorder"})
    pipBorder.Width = 0.28
    pipBorder.Height = 0.20
    pipBorder.Center = {0.85, 0.15}
    pipBorder.BorderWidth = 0.003
    pipBorder.SoftEdge = 0

    local borderBG = comp:AddTool("Background")
    borderBG:SetAttrs({TOOLS_Name = "BorderColor"})
    borderBG.TopLeftRed = 1
    borderBG.TopLeftGreen = 1
    borderBG.TopLeftBlue = 1
    borderBG.TopLeftAlpha = 1

    -- Drop shadow for PiP
    local shadow = comp:AddTool("DropShadow")
    shadow:SetAttrs({TOOLS_Name = "PiPShadow"})
    shadow.ShadowOffset = {0.005, -0.005}
    shadow.Softness = 10
    shadow.ShadowDensity = 0.5

    -- Merge layers
    local merge = comp:AddTool("Merge")
    merge:SetAttrs({TOOLS_Name = "PiPMerge"})

    comp:Unlock()

    print("✓ Picture-in-Picture setup created")
    print("")
    print("Positions (adjust PiPTransform.Center):")
    print("  Bottom-right: {0.85, 0.15}")
    print("  Bottom-left:  {0.15, 0.15}")
    print("  Top-right:    {0.85, 0.85}")
    print("  Top-left:     {0.15, 0.85}")
    print("")
    print("Sizes (adjust PiPTransform.Size):")
    print("  Small:  0.20")
    print("  Medium: 0.25")
    print("  Large:  0.33")
else
    print("Error: No composition found")
end
