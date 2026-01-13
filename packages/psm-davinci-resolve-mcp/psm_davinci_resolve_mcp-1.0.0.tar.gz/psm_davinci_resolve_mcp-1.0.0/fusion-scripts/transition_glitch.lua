-- Glitch Transition
-- Digital distortion transition between clips

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- RGB split for glitch
    local splitR = comp:AddTool("Transform")
    splitR:SetAttrs({TOOLS_Name = "GlitchTrans_R"})
    splitR.Center = {0.51, 0.5}  -- Animate offset

    local splitB = comp:AddTool("Transform")
    splitB:SetAttrs({TOOLS_Name = "GlitchTrans_B"})
    splitB.Center = {0.49, 0.5}

    -- Horizontal displacement
    local displace = comp:AddTool("Displace")
    displace:SetAttrs({TOOLS_Name = "GlitchTrans_Displace"})
    displace.XOffset = 0  -- Animate 0 → 0.1 → 0
    displace.Type = 0  -- Horizontal

    -- Block glitch using noise
    local blocks = comp:AddTool("FastNoise")
    blocks:SetAttrs({TOOLS_Name = "GlitchTrans_Blocks"})
    blocks.Detail = 0
    blocks.Contrast = 10
    blocks.XScale = 0.1
    blocks.YScale = 3
    blocks.Seethe = 1  -- Animate for randomness

    -- Scan line interference
    local scanlines = comp:AddTool("FastNoise")
    scanlines:SetAttrs({TOOLS_Name = "GlitchTrans_Scan"})
    scanlines.Detail = 0
    scanlines.Contrast = 5
    scanlines.XScale = 500
    scanlines.YScale = 1
    scanlines.Brightness = -0.5

    -- Dissolve control
    local dissolve = comp:AddTool("Dissolve")
    dissolve:SetAttrs({TOOLS_Name = "GlitchTrans_Mix"})
    dissolve.Mix = 0.5

    comp:Unlock()

    print("✓ Glitch transition added")
    print("")
    print("Animation (over ~10-20 frames):")
    print("  Frame 0: Clean clip A")
    print("  Frame 5-15: Animate glitch intensity up/down")
    print("  Frame 20: Clean clip B")
    print("")
    print("Animate Seethe for random block movement")
else
    print("Error: No composition found")
end
