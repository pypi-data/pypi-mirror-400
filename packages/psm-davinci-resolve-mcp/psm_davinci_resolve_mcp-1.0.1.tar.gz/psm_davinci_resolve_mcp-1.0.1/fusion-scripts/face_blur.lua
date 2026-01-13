-- Face/Privacy Blur
-- Blur faces, license plates, or sensitive areas

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Ellipse mask for face blur
    local faceMask = comp:AddTool("EllipseMask")
    faceMask:SetAttrs({TOOLS_Name = "Privacy_FaceMask"})
    faceMask.Width = 0.15
    faceMask.Height = 0.2
    faceMask.Center = {0.5, 0.6}
    faceMask.SoftEdge = 0.02

    -- Blur effect
    local faceBlur = comp:AddTool("Blur")
    faceBlur:SetAttrs({TOOLS_Name = "Privacy_FaceBlur"})
    faceBlur.XBlurSize = 30
    faceBlur.YBlurSize = 30

    -- Rectangle mask for plates/signs
    local rectMask = comp:AddTool("RectangleMask")
    rectMask:SetAttrs({TOOLS_Name = "Privacy_RectMask"})
    rectMask.Width = 0.2
    rectMask.Height = 0.05
    rectMask.Center = {0.5, 0.3}
    rectMask.SoftEdge = 0.01

    -- Pixelate effect (alternative)
    local pixelate = comp:AddTool("Transform")
    pixelate:SetAttrs({TOOLS_Name = "Privacy_Pixelate"})
    pixelate.Size = 0.05  -- Scale down then up = pixelation

    local pixelateUp = comp:AddTool("Transform")
    pixelateUp:SetAttrs({TOOLS_Name = "Privacy_PixelateUp"})
    pixelateUp.Size = 20  -- Scale back up
    pixelateUp.FilterMethod = 0  -- Nearest neighbor

    -- Black bar (complete redaction)
    local blackBar = comp:AddTool("Background")
    blackBar:SetAttrs({TOOLS_Name = "Privacy_BlackBar"})
    blackBar.TopLeftRed = 0
    blackBar.TopLeftGreen = 0
    blackBar.TopLeftBlue = 0

    -- Tracker for moving blur
    local tracker = comp:AddTool("Tracker")
    tracker:SetAttrs({TOOLS_Name = "Privacy_Tracker"})
    -- Connect tracker output to mask center

    comp:Unlock()

    print("✓ Privacy blur tools added")
    print("")
    print("For static subjects:")
    print("  Position Privacy_FaceMask over face")
    print("  Connect mask to Privacy_FaceBlur")
    print("")
    print("For moving subjects:")
    print("  1. Use Privacy_Tracker to track face")
    print("  2. Connect tracker to mask Center")
    print("")
    print("Pixelation: Privacy_Pixelate → Privacy_PixelateUp")
else
    print("Error: No composition found")
end
