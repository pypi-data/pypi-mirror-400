-- Create a lower third title template
-- Edit the text below before running
local titleText = "John Smith"
local subtitleText = "Video Producer"

local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Background bar
    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "LowerThirdBG"})
    bg.TopLeftRed = 0.1
    bg.TopLeftGreen = 0.1
    bg.TopLeftBlue = 0.1
    bg.TopLeftAlpha = 0.8

    -- Crop to lower third area
    local crop = comp:AddTool("Crop")
    crop:SetAttrs({TOOLS_Name = "LowerThirdCrop"})
    crop.XOffset = 0.05
    crop.YOffset = 0.05
    crop.XSize = 0.4
    crop.YSize = 0.12

    -- Main title
    local title = comp:AddTool("TextPlus")
    title:SetAttrs({TOOLS_Name = "TitleText"})
    title.StyledText = titleText
    title.Font = "Arial Bold"
    title.Size = 0.06
    title.Center = {0.25, 0.12}

    -- Subtitle
    local subtitle = comp:AddTool("TextPlus")
    subtitle:SetAttrs({TOOLS_Name = "SubtitleText"})
    subtitle.StyledText = subtitleText
    subtitle.Font = "Arial"
    subtitle.Size = 0.035
    subtitle.Center = {0.25, 0.06}
    subtitle.Red1 = 0.7
    subtitle.Green1 = 0.7
    subtitle.Blue1 = 0.7

    comp:Unlock()
    print("✓ Created lower third template")
    print("  Edit TitleText and SubtitleText nodes to customize")
else
    print("✗ No composition open")
end
