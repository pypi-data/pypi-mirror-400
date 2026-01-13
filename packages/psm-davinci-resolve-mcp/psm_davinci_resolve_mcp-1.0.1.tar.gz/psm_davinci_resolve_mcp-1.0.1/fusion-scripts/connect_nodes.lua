-- Connect two nodes by name
-- Edit the node names below, then run from Console

local sourceName = "MediaIn1"  -- Change to your source node
local targetName = "MediaOut1" -- Change to your target node
local inputName = "Input"      -- Usually "Input" or "Background"

local comp = fusion:GetCurrentComp()
if comp then
    local source = comp:FindTool(sourceName)
    local target = comp:FindTool(targetName)

    if source and target then
        target[inputName] = source.Output
        print(string.format("Connected %s -> %s.%s", sourceName, targetName, inputName))
    else
        if not source then print("Source not found: " .. sourceName) end
        if not target then print("Target not found: " .. targetName) end
    end
else
    print("No composition open")
end
