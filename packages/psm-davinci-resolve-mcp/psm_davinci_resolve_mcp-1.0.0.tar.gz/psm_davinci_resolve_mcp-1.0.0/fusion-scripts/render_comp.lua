-- Render the current Fusion composition
-- Run from: Fusion page > Console (Shift+0)

local comp = fusion:GetCurrentComp()
if comp then
    local attrs = comp:GetAttrs()
    local startFrame = attrs.COMPN_RenderStart
    local endFrame = attrs.COMPN_RenderEnd

    print(string.format("Rendering frames %d to %d...", startFrame, endFrame))
    comp:Render({Start = startFrame, End = endFrame, Wait = true})
    print("Render complete!")
else
    print("No composition open")
end
