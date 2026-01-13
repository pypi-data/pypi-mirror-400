-- Animated Text Reveal
-- Creates text with animated reveal/wipe effect

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Main text
    local text = comp:AddTool("TextPlus")
    text:SetAttrs({TOOLS_Name = "RevealText"})
    text.StyledText = "YOUR TEXT HERE"
    text.Font = "Arial Black"
    text.Size = 0.08
    text.Center = {0.5, 0.5}

    -- Write-on effect using mask
    local writeMask = comp:AddTool("RectangleMask")
    writeMask:SetAttrs({TOOLS_Name = "RevealMask"})
    writeMask.Width = 2.0
    writeMask.Height = 0.2
    writeMask.Center = {-0.5, 0.5}  -- Start off-screen left
    writeMask.SoftEdge = 0.05

    -- Animate mask center from {-0.5, 0.5} to {1.5, 0.5}
    -- This creates left-to-right reveal

    -- Glow for text pop
    local glow = comp:AddTool("SoftGlow")
    glow:SetAttrs({TOOLS_Name = "TextGlow"})
    glow.Threshold = 0.9
    glow.Gain = 0.2
    glow.XGlowSize = 5
    glow.YGlowSize = 5

    -- Drop shadow
    local shadow = comp:AddTool("DropShadow")
    shadow:SetAttrs({TOOLS_Name = "TextShadow"})
    shadow.ShadowOffset = {0.003, -0.003}
    shadow.Softness = 5
    shadow.ShadowDensity = 0.7

    comp:Unlock()

    print("✓ Text reveal setup created")
    print("")
    print("To animate the reveal:")
    print("  1. Select RevealMask")
    print("  2. Go to frame 0, set Center.X = -0.5")
    print("  3. Right-click Center → Animate")
    print("  4. Go to frame 30, set Center.X = 1.5")
    print("")
    print("For typewriter effect, use Text+ Write On parameter")
else
    print("Error: No composition found")
end
