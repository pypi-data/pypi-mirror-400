-- Create a split screen layout (2, 3, or 4 way)
-- Edit splitCount before running
local splitCount = 2  -- Options: 2, 3, or 4

local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    if splitCount == 2 then
        -- Two-way horizontal split
        local left = comp:AddTool("Transform")
        left:SetAttrs({TOOLS_Name = "Left"})
        left.Center = {0.25, 0.5}
        left.Size = 0.5

        local right = comp:AddTool("Transform")
        right:SetAttrs({TOOLS_Name = "Right"})
        right.Center = {0.75, 0.5}
        right.Size = 0.5

        local merge = comp:AddTool("Merge")
        merge:SetAttrs({TOOLS_Name = "SplitMerge"})

        print("✓ 2-way split screen created")
        print("  Connect clip 1 to 'Left', clip 2 to 'Right'")

    elseif splitCount == 3 then
        -- Three-way split
        local pos1 = comp:AddTool("Transform")
        pos1:SetAttrs({TOOLS_Name = "TopLeft"})
        pos1.Center = {0.25, 0.75}
        pos1.Size = 0.5

        local pos2 = comp:AddTool("Transform")
        pos2:SetAttrs({TOOLS_Name = "TopRight"})
        pos2.Center = {0.75, 0.75}
        pos2.Size = 0.5

        local pos3 = comp:AddTool("Transform")
        pos3:SetAttrs({TOOLS_Name = "Bottom"})
        pos3.Center = {0.5, 0.25}
        pos3.Size = 0.5

        print("✓ 3-way split screen created")
        print("  Connect clips to TopLeft, TopRight, Bottom")

    elseif splitCount == 4 then
        -- Four-way grid
        local positions = {
            {name = "TopLeft", x = 0.25, y = 0.75},
            {name = "TopRight", x = 0.75, y = 0.75},
            {name = "BottomLeft", x = 0.25, y = 0.25},
            {name = "BottomRight", x = 0.75, y = 0.25},
        }

        for i, pos in ipairs(positions) do
            local t = comp:AddTool("Transform")
            t:SetAttrs({TOOLS_Name = pos.name})
            t.Center = {pos.x, pos.y}
            t.Size = 0.5
        end

        print("✓ 4-way split screen created")
        print("  Connect clips to TopLeft, TopRight, BottomLeft, BottomRight")
    end

    -- Add background
    local bg = comp:AddTool("Background")
    bg:SetAttrs({TOOLS_Name = "SplitBG"})
    bg.TopLeftRed = 0
    bg.TopLeftGreen = 0
    bg.TopLeftBlue = 0

    comp:Unlock()
    print("  Use Merge nodes to combine all splits")
else
    print("✗ No composition open")
end
