-- List all tools in the current Fusion composition
-- Run from: Fusion page > Console (Shift+0) > paste and press Enter

local comp = fusion:GetCurrentComp()
if comp then
    local tools = comp:GetToolList()
    print("=== Tools in Composition ===")
    for i, tool in ipairs(tools) do
        print(string.format("%d. %s (%s)", i, tool.Name, tool.ID))
    end
    print(string.format("\nTotal: %d tools", #tools))
else
    print("No composition open")
end
