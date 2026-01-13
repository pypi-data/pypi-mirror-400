-- Batch rename all selected tools with a prefix
-- Select tools in Fusion, then run from Console

local prefix = "Shot01_"  -- Change this prefix

local comp = fusion:GetCurrentComp()
if comp then
    local selected = comp:GetToolList(true)  -- true = selected only

    if #selected > 0 then
        comp:Lock()
        for i, tool in ipairs(selected) do
            local oldName = tool.Name
            local newName = prefix .. oldName
            tool:SetAttrs({TOOLS_Name = newName})
            print(string.format("Renamed: %s -> %s", oldName, newName))
        end
        comp:Unlock()
        print(string.format("\nRenamed %d tools", #selected))
    else
        print("No tools selected. Select tools first, then run script.")
    end
else
    print("No composition open")
end
