-- Zoom/Push Transitions
-- Smooth zoom and push transitions

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Zoom in transition (clip A zooms in and fades)
    local zoomIn = comp:AddTool("Transform")
    zoomIn:SetAttrs({TOOLS_Name = "Trans_ZoomIn"})
    zoomIn.Size = 1.0  -- Animate 1.0 → 3.0
    zoomIn.Center = {0.5, 0.5}

    local zoomInBlur = comp:AddTool("Blur")
    zoomInBlur:SetAttrs({TOOLS_Name = "Trans_ZoomInBlur"})
    zoomInBlur.XBlurSize = 0  -- Animate 0 → 20

    -- Zoom out transition (clip B zooms from large)
    local zoomOut = comp:AddTool("Transform")
    zoomOut:SetAttrs({TOOLS_Name = "Trans_ZoomOut"})
    zoomOut.Size = 3.0  -- Animate 3.0 → 1.0
    zoomOut.Center = {0.5, 0.5}

    -- Push left (A exits left, B enters from right)
    local pushALeft = comp:AddTool("Transform")
    pushALeft:SetAttrs({TOOLS_Name = "Trans_PushA_Left"})
    pushALeft.Center = {0.5, 0.5}  -- Animate X: 0.5 → -0.5

    local pushBLeft = comp:AddTool("Transform")
    pushBLeft:SetAttrs({TOOLS_Name = "Trans_PushB_Left"})
    pushBLeft.Center = {1.5, 0.5}  -- Animate X: 1.5 → 0.5

    -- Push up
    local pushAUp = comp:AddTool("Transform")
    pushAUp:SetAttrs({TOOLS_Name = "Trans_PushA_Up"})
    pushAUp.Center = {0.5, 0.5}  -- Animate Y: 0.5 → 1.5

    local pushBUp = comp:AddTool("Transform")
    pushBUp:SetAttrs({TOOLS_Name = "Trans_PushB_Up"})
    pushBUp.Center = {0.5, -0.5}  -- Animate Y: -0.5 → 0.5

    -- Whip pan (fast push with motion blur)
    local whip = comp:AddTool("Transform")
    whip:SetAttrs({TOOLS_Name = "Trans_WhipPan"})
    whip.Center = {0.5, 0.5}  -- Animate quickly
    whip.MotionBlur = 1
    whip.Quality = 10

    comp:Unlock()

    print("✓ Zoom/Push transitions added")
    print("")
    print("Zoom In: Size 1→3, Blur 0→20")
    print("Zoom Out: Size 3→1")
    print("Push Left: A.X 0.5→-0.5, B.X 1.5→0.5")
    print("Push Up: A.Y 0.5→1.5, B.Y -0.5→0.5")
    print("Whip Pan: Fast Center animation with MotionBlur")
else
    print("Error: No composition found")
end
