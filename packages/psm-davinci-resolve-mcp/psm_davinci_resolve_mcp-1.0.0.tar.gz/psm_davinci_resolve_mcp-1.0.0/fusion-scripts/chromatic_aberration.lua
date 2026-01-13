-- Chromatic Aberration Effect
-- Adds RGB channel separation for vintage/stylized look

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Split into RGB channels
    local channelR = comp:AddTool("ChannelBoolean")
    channelR:SetAttrs({TOOLS_Name = "RedChannel"})
    channelR.ToRed = 1
    channelR.ToGreen = 0
    channelR.ToBlue = 0

    local channelG = comp:AddTool("ChannelBoolean")
    channelG:SetAttrs({TOOLS_Name = "GreenChannel"})
    channelG.ToRed = 0
    channelG.ToGreen = 1
    channelG.ToBlue = 0

    local channelB = comp:AddTool("ChannelBoolean")
    channelB:SetAttrs({TOOLS_Name = "BlueChannel"})
    channelB.ToRed = 0
    channelB.ToGreen = 0
    channelB.ToBlue = 1

    -- Transform each channel slightly
    local transformR = comp:AddTool("Transform")
    transformR:SetAttrs({TOOLS_Name = "RedOffset"})
    transformR.Center = {0.502, 0.5}  -- Slight right offset
    transformR.Size = 1.005

    local transformB = comp:AddTool("Transform")
    transformB:SetAttrs({TOOLS_Name = "BlueOffset"})
    transformB.Center = {0.498, 0.5}  -- Slight left offset
    transformB.Size = 0.995

    -- Merge channels back
    local merge1 = comp:AddTool("Merge")
    merge1:SetAttrs({TOOLS_Name = "RGMerge"})
    merge1.ApplyMode = "Screen"

    local merge2 = comp:AddTool("Merge")
    merge2:SetAttrs({TOOLS_Name = "RGBMerge"})
    merge2.ApplyMode = "Screen"

    comp:Unlock()

    print("✓ Chromatic aberration effect added")
    print("  Adjust RedOffset/BlueOffset transforms for intensity")
    print("  Connect: Input → Channels → Transforms → Merges → Output")
else
    print("Error: No composition found")
end
