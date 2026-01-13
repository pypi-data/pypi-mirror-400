-- Add cinematic letterbox bars (2.35:1 aspect ratio)
-- Run from: Fusion page > Console
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Create black bars
    local bars = comp:AddTool("Background")
    bars:SetAttrs({TOOLS_Name = "CinematicBars"})
    bars.TopLeftRed = 0
    bars.TopLeftGreen = 0
    bars.TopLeftBlue = 0
    bars.TopLeftAlpha = 1

    -- Create mask for letterbox
    local rect = comp:AddTool("RectangleMask")
    rect:SetAttrs({TOOLS_Name = "LetterboxMask"})
    rect.Width = 1.0
    rect.Height = 0.12  -- Adjust for different ratios
    rect.Center = {0.5, 0.94}  -- Top bar
    rect.SoftEdge = 0

    -- Duplicate for bottom bar
    local rect2 = comp:AddTool("RectangleMask")
    rect2:SetAttrs({TOOLS_Name = "LetterboxMask2"})
    rect2.Width = 1.0
    rect2.Height = 0.12
    rect2.Center = {0.5, 0.06}  -- Bottom bar
    rect2.SoftEdge = 0

    -- Merge node to composite bars
    local merge = comp:AddTool("Merge")
    merge:SetAttrs({TOOLS_Name = "BarsOverlay"})

    comp:Unlock()
    print("✓ Cinematic bars created (2.35:1 ratio)")
    print("  Connect your footage to BarsOverlay.Background")
    print("  Adjust LetterboxMask Height for different ratios:")
    print("    0.12 = 2.35:1 (Cinemascope)")
    print("    0.06 = 1.85:1 (Standard widescreen)")
end
