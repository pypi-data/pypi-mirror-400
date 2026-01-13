-- Create a glitch/distortion effect
-- Run from: Fusion page > Console
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Channel offset for RGB split
    local channelShift = comp:AddTool("ChannelBooleans")
    channelShift:SetAttrs({TOOLS_Name = "RGBSplit"})

    -- Displace for distortion
    local displace = comp:AddTool("Displace")
    displace:SetAttrs({TOOLS_Name = "GlitchDisplace"})
    displace.XRefraction = 10
    displace.YRefraction = 0

    -- Fast noise for displacement map
    local noise = comp:AddTool("FastNoise")
    noise:SetAttrs({TOOLS_Name = "GlitchNoise"})
    noise.Detail = 1
    noise.Contrast = 3
    noise.XScale = 100
    noise.YScale = 5
    noise.SeetheRate = 1

    -- Horizontal lines
    local lines = comp:AddTool("FastNoise")
    lines:SetAttrs({TOOLS_Name = "ScanLines"})
    lines.Detail = 0
    lines.XScale = 10000
    lines.YScale = 2
    lines.Contrast = 5

    -- Merge for compositing
    local merge = comp:AddTool("Merge")
    merge:SetAttrs({TOOLS_Name = "GlitchMerge"})
    merge.Blend = 0.3

    comp:Unlock()
    print("✓ Glitch effect nodes created")
    print("")
    print("Setup connections:")
    print("  1. Footage > RGBSplit")
    print("  2. GlitchNoise > GlitchDisplace.Input2")
    print("  3. Footage > GlitchDisplace.Input1")
    print("  4. Layer ScanLines over result")
    print("")
    print("For animated glitch:")
    print("  - Animate GlitchDisplace.XRefraction with random keyframes")
    print("  - Keyframe RGBSplit blend on/off")
end
