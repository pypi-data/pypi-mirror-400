-- Mirror & Kaleidoscope Effects
-- Symmetry and reflection effects

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- === HORIZONTAL MIRROR ===
    local hMirror = comp:AddTool("Transform")
    hMirror:SetAttrs({TOOLS_Name = "Mirror_Horizontal"})
    hMirror.FlipHorizontal = true

    local hMirrorMask = comp:AddTool("RectangleMask")
    hMirrorMask:SetAttrs({TOOLS_Name = "Mirror_HMask"})
    hMirrorMask.Width = 0.5
    hMirrorMask.Height = 1
    hMirrorMask.Center = {0.75, 0.5}

    local hMerge = comp:AddTool("Merge")
    hMerge:SetAttrs({TOOLS_Name = "Mirror_HMerge"})

    -- === VERTICAL MIRROR ===
    local vMirror = comp:AddTool("Transform")
    vMirror:SetAttrs({TOOLS_Name = "Mirror_Vertical"})
    vMirror.FlipVertical = true

    local vMirrorMask = comp:AddTool("RectangleMask")
    vMirrorMask:SetAttrs({TOOLS_Name = "Mirror_VMask"})
    vMirrorMask.Width = 1
    vMirrorMask.Height = 0.5
    vMirrorMask.Center = {0.5, 0.25}

    local vMerge = comp:AddTool("Merge")
    vMerge:SetAttrs({TOOLS_Name = "Mirror_VMerge"})

    -- === QUAD MIRROR (4-way symmetry) ===
    local quad1 = comp:AddTool("Transform")
    quad1:SetAttrs({TOOLS_Name = "Mirror_Quad1"})
    quad1.FlipHorizontal = true

    local quad2 = comp:AddTool("Transform")
    quad2:SetAttrs({TOOLS_Name = "Mirror_Quad2"})
    quad2.FlipVertical = true

    local quad3 = comp:AddTool("Transform")
    quad3:SetAttrs({TOOLS_Name = "Mirror_Quad3"})
    quad3.FlipHorizontal = true
    quad3.FlipVertical = true

    -- === RADIAL MIRROR (Kaleidoscope) ===
    -- Create by rotating and merging copies
    local radialBase = comp:AddTool("Transform")
    radialBase:SetAttrs({TOOLS_Name = "Kaleidoscope_Base"})
    radialBase.Center = {0.5, 0.5}

    local radial1 = comp:AddTool("Transform")
    radial1:SetAttrs({TOOLS_Name = "Kaleidoscope_60"})
    radial1.Angle = 60
    radial1.Center = {0.5, 0.5}

    local radial2 = comp:AddTool("Transform")
    radial2:SetAttrs({TOOLS_Name = "Kaleidoscope_120"})
    radial2.Angle = 120
    radial2.Center = {0.5, 0.5}

    local radial3 = comp:AddTool("Transform")
    radial3:SetAttrs({TOOLS_Name = "Kaleidoscope_180"})
    radial3.Angle = 180
    radial3.Center = {0.5, 0.5}

    local radial4 = comp:AddTool("Transform")
    radial4:SetAttrs({TOOLS_Name = "Kaleidoscope_240"})
    radial4.Angle = 240
    radial4.Center = {0.5, 0.5}

    local radial5 = comp:AddTool("Transform")
    radial5:SetAttrs({TOOLS_Name = "Kaleidoscope_300"})
    radial5.Angle = 300
    radial5.Center = {0.5, 0.5}

    -- === REFLECTION (Water/Floor) ===
    local reflection = comp:AddTool("Transform")
    reflection:SetAttrs({TOOLS_Name = "Reflection_Transform"})
    reflection.FlipVertical = true
    reflection.Center = {0.5, 0.25}

    local reflectionFade = comp:AddTool("ColorCorrector")
    reflectionFade:SetAttrs({TOOLS_Name = "Reflection_Fade"})
    reflectionFade.MasterRGBGain = 0.5

    local reflectionBlur = comp:AddTool("Blur")
    reflectionBlur:SetAttrs({TOOLS_Name = "Reflection_Blur"})
    reflectionBlur.XBlurSize = 5
    reflectionBlur.YBlurSize = 10

    -- Gradient mask for reflection fade
    local reflectionMask = comp:AddTool("RectangleMask")
    reflectionMask:SetAttrs({TOOLS_Name = "Reflection_Mask"})
    reflectionMask.Width = 1
    reflectionMask.Height = 0.4
    reflectionMask.Center = {0.5, 0.1}
    reflectionMask.SoftEdge = 0.3

    comp:Unlock()

    print("✓ Mirror effects added")
    print("")
    print("Effects:")
    print("  Mirror_Horizontal - Left/right mirror")
    print("  Mirror_Vertical - Top/bottom mirror")
    print("  Mirror_Quad* - 4-way symmetry")
    print("  Kaleidoscope_* - 6-fold radial symmetry")
    print("  Reflection_* - Water/floor reflection")
    print("")
    print("Connect layers in order, merge with Add mode")
else
    print("Error: No composition found")
end
