-- Countdown Timer / Clock
-- Animated countdown and timer displays

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- === COUNTDOWN NUMBER ===
    local countdown = comp:AddTool("TextPlus")
    countdown:SetAttrs({TOOLS_Name = "Timer_Countdown"})
    countdown.StyledText = "10"
    countdown.Font = "Arial Black"
    countdown.Size = 0.2
    countdown.Center = {0.5, 0.5}
    -- Animate StyledText: 10, 9, 8... or use expression

    -- === CIRCULAR PROGRESS ===
    local progressBG = comp:AddTool("EllipseMask")
    progressBG:SetAttrs({TOOLS_Name = "Timer_ProgressBG"})
    progressBG.Width = 0.4
    progressBG.Height = 0.4
    progressBG.Center = {0.5, 0.5}
    progressBG.SoftEdge = 0

    local progressRing = comp:AddTool("EllipseMask")
    progressRing:SetAttrs({TOOLS_Name = "Timer_ProgressRing"})
    progressRing.Width = 0.38
    progressRing.Height = 0.38
    progressRing.Center = {0.5, 0.5}
    progressRing.StartAngle = 0
    progressRing.EndAngle = 360  -- Animate 360 → 0

    -- === DIGITAL CLOCK ===
    local clock = comp:AddTool("TextPlus")
    clock:SetAttrs({TOOLS_Name = "Timer_Clock"})
    clock.StyledText = "00:00:00"
    clock.Font = "Courier"
    clock.Size = 0.08
    clock.Center = {0.5, 0.5}

    -- === PROGRESS BAR ===
    local barBG = comp:AddTool("Background")
    barBG:SetAttrs({TOOLS_Name = "Timer_BarBG"})
    barBG.TopLeftRed = 0.2
    barBG.TopLeftGreen = 0.2
    barBG.TopLeftBlue = 0.2

    local barMask = comp:AddTool("RectangleMask")
    barMask:SetAttrs({TOOLS_Name = "Timer_BarMask"})
    barMask.Width = 0.6
    barMask.Height = 0.02
    barMask.Center = {0.5, 0.2}

    local barFill = comp:AddTool("Background")
    barFill:SetAttrs({TOOLS_Name = "Timer_BarFill"})
    barFill.TopLeftRed = 0.2
    barFill.TopLeftGreen = 0.8
    barFill.TopLeftBlue = 0.2

    local barFillMask = comp:AddTool("RectangleMask")
    barFillMask:SetAttrs({TOOLS_Name = "Timer_BarFillMask"})
    barFillMask.Width = 0.6  -- Animate 0 → 0.6
    barFillMask.Height = 0.02
    barFillMask.Center = {0.2, 0.2}  -- Adjust for left align

    -- === SECONDS TICK ===
    local tick = comp:AddTool("TextPlus")
    tick:SetAttrs({TOOLS_Name = "Timer_Tick"})
    tick.StyledText = "●"
    tick.Size = 0.05
    tick.Center = {0.5, 0.3}
    -- Animate scale for pulse effect

    comp:Unlock()

    print("✓ Countdown timer elements added")
    print("")
    print("Elements:")
    print("  Timer_Countdown - Large number display")
    print("  Timer_ProgressRing - Circular progress")
    print("  Timer_Clock - Digital HH:MM:SS")
    print("  Timer_Bar* - Progress bar")
    print("  Timer_Tick - Pulsing indicator")
    print("")
    print("For animated countdown, use expressions or")
    print("manually keyframe text at each second")
else
    print("Error: No composition found")
end
