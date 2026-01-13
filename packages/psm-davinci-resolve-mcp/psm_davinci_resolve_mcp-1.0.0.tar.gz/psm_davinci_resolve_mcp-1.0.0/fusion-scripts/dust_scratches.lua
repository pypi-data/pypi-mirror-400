-- Film Dust & Scratches
-- Add film damage overlay effects

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- === DUST PARTICLES ===
    local dustNoise = comp:AddTool("FastNoise")
    dustNoise:SetAttrs({TOOLS_Name = "Film_DustNoise"})
    dustNoise.Detail = 10
    dustNoise.Contrast = 5
    dustNoise.Brightness = -0.95
    dustNoise.XScale = 50
    dustNoise.YScale = 50
    dustNoise.SeetheRate = 0.5

    local dustThreshold = comp:AddTool("ColorCorrector")
    dustThreshold:SetAttrs({TOOLS_Name = "Film_DustThreshold"})
    dustThreshold.MasterRGBGain = 0.1
    dustThreshold.MasterRGBGamma = 0.3

    -- === SCRATCHES (Vertical Lines) ===
    local scratchNoise = comp:AddTool("FastNoise")
    scratchNoise:SetAttrs({TOOLS_Name = "Film_ScratchNoise"})
    scratchNoise.Detail = 1
    scratchNoise.Contrast = 10
    scratchNoise.Brightness = -0.98
    scratchNoise.XScale = 500
    scratchNoise.YScale = 1
    scratchNoise.SeetheRate = 2

    -- Motion blur for scratches
    local scratchBlur = comp:AddTool("DirectionalBlur")
    scratchBlur:SetAttrs({TOOLS_Name = "Film_ScratchBlur"})
    scratchBlur.Length = 0.05
    scratchBlur.Angle = 90  -- Vertical

    -- === HAIR/FIBER ===
    local hairEmit = comp:AddTool("pEmitter")
    hairEmit:SetAttrs({TOOLS_Name = "Film_HairEmitter"})
    hairEmit.Number = 3
    hairEmit.Lifespan = 30
    hairEmit.Velocity = 0
    hairEmit.SizeControls = {0.001, 0.003}

    local hairRender = comp:AddTool("pRender")
    hairRender:SetAttrs({TOOLS_Name = "Film_HairRender"})

    -- === LIGHT FLICKER ===
    local flicker = comp:AddTool("BrightnessContrast")
    flicker:SetAttrs({TOOLS_Name = "Film_Flicker"})
    flicker.Gain = 1.0
    -- Animate Gain with expression: 1 + (random() * 0.05)

    -- === GATE WEAVE (Subtle Position Shake) ===
    local gateWeave = comp:AddTool("Transform")
    gateWeave:SetAttrs({TOOLS_Name = "Film_GateWeave"})
    gateWeave.Size = 1.02  -- Slight zoom for wiggle room
    -- Animate Center with expression for subtle movement

    -- === VIGNETTE FLICKER ===
    local vigFlicker = comp:AddTool("Vignette")
    vigFlicker:SetAttrs({TOOLS_Name = "Film_VignetteFlicker"})
    vigFlicker.Softness = 0.5
    vigFlicker.Size = 0.8
    -- Animate size for breathing effect

    -- Merge all damage
    local damageMerge = comp:AddTool("Merge")
    damageMerge:SetAttrs({TOOLS_Name = "Film_DamageMerge"})
    damageMerge.ApplyMode = "Screen"
    damageMerge.Blend = 0.3

    comp:Unlock()

    print("✓ Film dust & scratches added")
    print("")
    print("Elements:")
    print("  Film_DustNoise - Random dust spots")
    print("  Film_ScratchNoise - Vertical scratches")
    print("  Film_HairEmitter - Stray hairs/fibers")
    print("  Film_Flicker - Brightness variation")
    print("  Film_GateWeave - Position instability")
    print("")
    print("Merge with Screen mode at 20-40% blend")
else
    print("Error: No composition found")
end
