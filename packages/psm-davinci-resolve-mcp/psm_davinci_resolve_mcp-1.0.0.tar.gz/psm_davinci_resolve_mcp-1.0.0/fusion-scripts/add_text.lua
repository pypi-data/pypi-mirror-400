-- Add a Text+ node to the current composition
-- Run from: Fusion page > Console (Shift+0)

local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()
    local text = comp:AddTool("TextPlus", -32768, -32768)
    text.StyledText = "Hello from Script!"
    text:SetAttrs({TOOLS_Name = "ScriptedText"})
    comp:Unlock()
    print("Added TextPlus node: " .. text.Name)
else
    print("No composition open")
end
