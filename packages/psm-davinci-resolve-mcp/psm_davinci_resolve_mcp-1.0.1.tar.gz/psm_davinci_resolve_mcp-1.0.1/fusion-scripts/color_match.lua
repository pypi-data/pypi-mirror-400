-- Color Match / Shot Matching
-- Tools for matching color between shots

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Reference sampler (sample from reference shot)
    local refSample = comp:AddTool("ColorCorrector")
    refSample:SetAttrs({TOOLS_Name = "Match_Reference"})
    -- Use eyedropper on reference shot

    -- Target adjustment
    local targetCC = comp:AddTool("ColorCorrector")
    targetCC:SetAttrs({TOOLS_Name = "Match_Target"})

    -- Histogram matching
    local histMatch = comp:AddTool("ColorCorrector")
    histMatch:SetAttrs({TOOLS_Name = "Match_Histogram"})

    -- Exposure match
    local expMatch = comp:AddTool("BrightnessContrast")
    expMatch:SetAttrs({TOOLS_Name = "Match_Exposure"})
    expMatch.Gain = 1.0
    expMatch.Gamma = 1.0

    -- White balance match
    local wbMatch = comp:AddTool("WhiteBalance")
    wbMatch:SetAttrs({TOOLS_Name = "Match_WhiteBalance"})

    -- Saturation match
    local satMatch = comp:AddTool("ColorCorrector")
    satMatch:SetAttrs({TOOLS_Name = "Match_Saturation"})
    satMatch.MasterSaturation = 1.0

    comp:Unlock()

    print("✓ Color match tools added")
    print("")
    print("Workflow:")
    print("  1. Sample reference shot colors")
    print("  2. Adjust Match_Exposure for brightness")
    print("  3. Adjust Match_WhiteBalance for temp")
    print("  4. Adjust Match_Saturation")
    print("  5. Fine tune with Match_Target")
else
    print("Error: No composition found")
end
