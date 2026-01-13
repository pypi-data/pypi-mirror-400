-- Animated Backgrounds
-- Moving gradients, particles, and patterns

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- === ANIMATED GRADIENT ===
    local gradNoise = comp:AddTool("FastNoise")
    gradNoise:SetAttrs({TOOLS_Name = "AnimBG_GradientNoise"})
    gradNoise.Detail = 1
    gradNoise.Contrast = 0.5
    gradNoise.Brightness = 0.3
    gradNoise.XScale = 0.2
    gradNoise.YScale = 0.5
    gradNoise.SeetheRate = 0.02  -- Slow animation

    local gradColor = comp:AddTool("ColorCorrector")
    gradColor:SetAttrs({TOOLS_Name = "AnimBG_GradientColor"})
    gradColor.MasterRGBGain = {0.3, 0.5, 0.8}  -- Blue tint

    -- === FLOATING PARTICLES ===
    local particleEmit = comp:AddTool("pEmitter")
    particleEmit:SetAttrs({TOOLS_Name = "AnimBG_Particles"})
    particleEmit.Number = 30
    particleEmit.Lifespan = 300
    particleEmit.SizeControls = {0.005, 0.015}
    particleEmit.Velocity = 0.001

    local particleRender = comp:AddTool("pRender")
    particleRender:SetAttrs({TOOLS_Name = "AnimBG_ParticlesRender"})

    local particleGlow = comp:AddTool("SoftGlow")
    particleGlow:SetAttrs({TOOLS_Name = "AnimBG_ParticlesGlow"})
    particleGlow.Threshold = 0.1
    particleGlow.Gain = 0.5

    -- === GRID PATTERN ===
    local grid = comp:AddTool("FastNoise")
    grid:SetAttrs({TOOLS_Name = "AnimBG_Grid"})
    grid.Detail = 0
    grid.Contrast = 10
    grid.XScale = 20
    grid.YScale = 20
    grid.Brightness = -0.9

    local gridMove = comp:AddTool("Transform")
    gridMove:SetAttrs({TOOLS_Name = "AnimBG_GridMove"})
    -- Animate Center.X and Center.Y for movement

    -- === WAVE PATTERN ===
    local wave = comp:AddTool("FastNoise")
    wave:SetAttrs({TOOLS_Name = "AnimBG_Wave"})
    wave.Detail = 2
    wave.Contrast = 2
    wave.XScale = 0.1
    wave.YScale = 0.5
    wave.SeetheRate = 0.05
    wave.Brightness = 0.2

    -- === BOKEH LIGHTS ===
    local bokehEmit = comp:AddTool("pEmitter")
    bokehEmit:SetAttrs({TOOLS_Name = "AnimBG_Bokeh"})
    bokehEmit.Number = 15
    bokehEmit.Lifespan = 400
    bokehEmit.SizeControls = {0.03, 0.1}
    bokehEmit.Velocity = 0.0003

    local bokehRender = comp:AddTool("pRender")
    bokehRender:SetAttrs({TOOLS_Name = "AnimBG_BokehRender"})

    local bokehBlur = comp:AddTool("Blur")
    bokehBlur:SetAttrs({TOOLS_Name = "AnimBG_BokehBlur"})
    bokehBlur.XBlurSize = 20
    bokehBlur.YBlurSize = 20

    -- === NOISE TEXTURE ===
    local noiseBG = comp:AddTool("FastNoise")
    noiseBG:SetAttrs({TOOLS_Name = "AnimBG_Noise"})
    noiseBG.Detail = 5
    noiseBG.Contrast = 0.3
    noiseBG.XScale = 1
    noiseBG.YScale = 1
    noiseBG.SeetheRate = 0.1  -- Subtle movement

    comp:Unlock()

    print("✓ Animated backgrounds added")
    print("")
    print("Backgrounds:")
    print("  AnimBG_Gradient* - Slow moving gradient")
    print("  AnimBG_Particles* - Floating dust/orbs")
    print("  AnimBG_Grid* - Moving grid pattern")
    print("  AnimBG_Wave* - Wave pattern")
    print("  AnimBG_Bokeh* - Out of focus lights")
    print("  AnimBG_Noise* - Animated texture")
    print("")
    print("SeetheRate controls animation speed")
else
    print("Error: No composition found")
end
