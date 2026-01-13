-- Parallax Scroll Effect
-- Creates depth with multi-layer scrolling

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Background layer (slowest)
    local bgLayer = comp:AddTool("Transform")
    bgLayer:SetAttrs({TOOLS_Name = "BackgroundLayer"})
    bgLayer.Size = 1.1  -- Slightly larger for movement room
    -- Animate Center.X slowly: e.g., 0.5 → 0.52 over 100 frames

    -- Midground layer (medium speed)
    local midLayer = comp:AddTool("Transform")
    midLayer:SetAttrs({TOOLS_Name = "MidgroundLayer"})
    midLayer.Size = 1.05
    -- Animate Center.X: 0.5 → 0.55 over 100 frames

    -- Foreground layer (fastest)
    local fgLayer = comp:AddTool("Transform")
    fgLayer:SetAttrs({TOOLS_Name = "ForegroundLayer"})
    fgLayer.Size = 1.0
    -- Animate Center.X: 0.5 → 0.6 over 100 frames

    -- Blur background for depth
    local bgBlur = comp:AddTool("Blur")
    bgBlur:SetAttrs({TOOLS_Name = "BackgroundBlur"})
    bgBlur.XBlurSize = 3
    bgBlur.YBlurSize = 3

    -- Merge layers
    local merge1 = comp:AddTool("Merge")
    merge1:SetAttrs({TOOLS_Name = "BG_Mid_Merge"})

    local merge2 = comp:AddTool("Merge")
    merge2:SetAttrs({TOOLS_Name = "Final_Merge"})

    comp:Unlock()

    print("✓ Parallax scroll setup created")
    print("")
    print("Layer speed guide (per 100 frames):")
    print("  Background: move 0.02 (slowest)")
    print("  Midground:  move 0.05 (medium)")
    print("  Foreground: move 0.10 (fastest)")
    print("")
    print("Connect your layers:")
    print("  BG image → BackgroundBlur → BackgroundLayer")
    print("  Mid image → MidgroundLayer")
    print("  FG image → ForegroundLayer")
else
    print("Error: No composition found")
end
