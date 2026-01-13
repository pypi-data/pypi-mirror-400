-- Watermark Tools
-- Add text or logo watermarks

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- === TEXT WATERMARK ===
    local textWM = comp:AddTool("TextPlus")
    textWM:SetAttrs({TOOLS_Name = "Watermark_Text"})
    textWM.StyledText = "© Your Name"
    textWM.Font = "Arial"
    textWM.Size = 0.025
    textWM.Center = {0.9, 0.05}  -- Bottom right
    textWM.Red1 = 1
    textWM.Green1 = 1
    textWM.Blue1 = 1

    -- Opacity control
    local textWMMerge = comp:AddTool("Merge")
    textWMMerge:SetAttrs({TOOLS_Name = "Watermark_TextMerge"})
    textWMMerge.Blend = 0.5  -- 50% opacity

    -- === LOGO WATERMARK ===
    -- (Import your logo PNG with alpha)
    local logoTransform = comp:AddTool("Transform")
    logoTransform:SetAttrs({TOOLS_Name = "Watermark_LogoTransform"})
    logoTransform.Size = 0.1
    logoTransform.Center = {0.1, 0.9}  -- Top left

    local logoMerge = comp:AddTool("Merge")
    logoMerge:SetAttrs({TOOLS_Name = "Watermark_LogoMerge"})
    logoMerge.Blend = 0.3  -- Semi-transparent

    -- === FULL SCREEN WATERMARK ===
    local fullWM = comp:AddTool("TextPlus")
    fullWM:SetAttrs({TOOLS_Name = "Watermark_Full"})
    fullWM.StyledText = "PREVIEW"
    fullWM.Font = "Arial Bold"
    fullWM.Size = 0.15
    fullWM.Center = {0.5, 0.5}
    fullWM.Angle = -30  -- Diagonal
    fullWM.Red1 = 1
    fullWM.Green1 = 1
    fullWM.Blue1 = 1

    local fullWMMerge = comp:AddTool("Merge")
    fullWMMerge:SetAttrs({TOOLS_Name = "Watermark_FullMerge"})
    fullWMMerge.Blend = 0.15  -- Very subtle
    fullWMMerge.ApplyMode = "Normal"

    -- === TIMECODE BURN-IN ===
    local timecode = comp:AddTool("TextPlus")
    timecode:SetAttrs({TOOLS_Name = "Watermark_Timecode"})
    timecode.StyledText = "00:00:00:00"  -- Use TimeCode expression
    timecode.Font = "Courier"
    timecode.Size = 0.025
    timecode.Center = {0.1, 0.05}
    timecode.Red1 = 1
    timecode.Green1 = 1
    timecode.Blue1 = 1

    comp:Unlock()

    print("✓ Watermark tools added")
    print("")
    print("Types:")
    print("  Watermark_Text - Simple text (bottom right)")
    print("  Watermark_Logo* - Logo placement (top left)")
    print("  Watermark_Full - Diagonal PREVIEW stamp")
    print("  Watermark_Timecode - Timecode burn-in")
    print("")
    print("Adjust Blend for opacity (0.3-0.5 typical)")
else
    print("Error: No composition found")
end
