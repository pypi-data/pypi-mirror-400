-- Motion Blur Effect
-- Adds realistic motion blur to footage

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Vector motion blur using optical flow
    local blur = comp:AddTool("VectorMotionBlur")
    blur:SetAttrs({TOOLS_Name = "MotionBlur"})
    blur.Scale = 1.0
    blur.Angle = 180
    blur.Samples = 10
    blur.Quality = 4  -- High quality

    -- Alternative: Directional blur for stylized look
    local dirBlur = comp:AddTool("DirectionalBlur")
    dirBlur:SetAttrs({TOOLS_Name = "DirectionalBlur"})
    dirBlur.Length = 0.02
    dirBlur.Angle = 0
    dirBlur.Type = 0  -- Linear

    comp:Unlock()

    print("✓ Motion blur added")
    print("  MotionBlur - realistic optical flow blur")
    print("  DirectionalBlur - stylized directional blur")
    print("  Animate Length/Scale for speed ramping effects")
else
    print("Error: No composition found")
end
