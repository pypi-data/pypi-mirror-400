-- Set up green screen / chroma key removal
-- Run from: Fusion page > Console
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Delta Keyer is the best for green screen
    local keyer = comp:AddTool("DeltaKeyer")
    keyer:SetAttrs({TOOLS_Name = "GreenScreenKey"})

    -- Pre-process with color correction
    local preCC = comp:AddTool("ColorCorrector")
    preCC:SetAttrs({TOOLS_Name = "PreKeyCC"})

    -- Clean up edges
    local erode = comp:AddTool("ErodeDilate")
    erode:SetAttrs({TOOLS_Name = "EdgeCleanup"})
    erode.Amount = -0.002  -- Slight edge erosion

    -- Blur the matte slightly
    local blur = comp:AddTool("Blur")
    blur:SetAttrs({TOOLS_Name = "MatteBlur"})
    blur.XBlurSize = 1.5

    -- Merge over background
    local merge = comp:AddTool("Merge")
    merge:SetAttrs({TOOLS_Name = "CompositeMerge"})

    comp:Unlock()
    print("✓ Green screen setup created:")
    print("  1. Connect footage to PreKeyCC")
    print("  2. Connect PreKeyCC to GreenScreenKey")
    print("  3. Use eyedropper on green area")
    print("  4. Connect key output through EdgeCleanup > MatteBlur")
    print("  5. Use CompositeMerge for final composite")
else
    print("✗ No composition open")
end
