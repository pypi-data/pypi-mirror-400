-- Logo Reveal Animations
-- Various logo animation templates

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- === FADE IN ===
    local fadeIn = comp:AddTool("Dissolve")
    fadeIn:SetAttrs({TOOLS_Name = "Logo_FadeIn"})
    fadeIn.Mix = 0  -- Animate 0 → 1

    -- === SCALE POP ===
    local scalePop = comp:AddTool("Transform")
    scalePop:SetAttrs({TOOLS_Name = "Logo_ScalePop"})
    scalePop.Size = 0  -- Animate 0 → 1.2 → 1
    scalePop.Center = {0.5, 0.5}

    -- === SLIDE IN ===
    local slideIn = comp:AddTool("Transform")
    slideIn:SetAttrs({TOOLS_Name = "Logo_SlideIn"})
    slideIn.Center = {-0.5, 0.5}  -- Animate X: -0.5 → 0.5

    -- === BLUR REVEAL ===
    local blurReveal = comp:AddTool("Blur")
    blurReveal:SetAttrs({TOOLS_Name = "Logo_BlurReveal"})
    blurReveal.XBlurSize = 50  -- Animate 50 → 0
    blurReveal.YBlurSize = 50

    -- === GLITCH REVEAL ===
    local glitchReveal = comp:AddTool("Transform")
    glitchReveal:SetAttrs({TOOLS_Name = "Logo_GlitchReveal"})
    -- Animate with random offsets then settle

    -- === PARTICLE BUILD ===
    local particleBuild = comp:AddTool("pEmitter")
    particleBuild:SetAttrs({TOOLS_Name = "Logo_ParticleBuild"})
    particleBuild.Number = 200
    particleBuild.Lifespan = 50
    -- Use logo as particle target

    -- === SHINE/GLINT ===
    local shine = comp:AddTool("FastNoise")
    shine:SetAttrs({TOOLS_Name = "Logo_Shine"})
    shine.Detail = 0
    shine.Contrast = 5
    shine.XScale = 0.05
    shine.YScale = 2
    shine.Center = {-0.5, 0.5}  -- Animate X across logo

    local shineMerge = comp:AddTool("Merge")
    shineMerge:SetAttrs({TOOLS_Name = "Logo_ShineMerge"})
    shineMerge.ApplyMode = "Screen"
    shineMerge.Blend = 0.5

    -- === 3D FLIP ===
    local flip3D = comp:AddTool("Transform")
    flip3D:SetAttrs({TOOLS_Name = "Logo_3DFlip"})
    flip3D.Angle = 0  -- Animate for flip effect
    flip3D.Size = 1

    -- === TYPEWRITER (for text logos) ===
    local typewriter = comp:AddTool("TextPlus")
    typewriter:SetAttrs({TOOLS_Name = "Logo_Typewriter"})
    typewriter.StyledText = "YOUR LOGO"
    typewriter.Font = "Arial Black"
    typewriter.Size = 0.1
    typewriter.Center = {0.5, 0.5}
    -- Animate WriteOn parameter 0 → 1

    comp:Unlock()

    print("✓ Logo reveal animations added")
    print("")
    print("Animations (animate over 20-40 frames):")
    print("  Logo_FadeIn: Mix 0→1")
    print("  Logo_ScalePop: Size 0→1.2→1 (overshoot)")
    print("  Logo_SlideIn: Center.X -0.5→0.5")
    print("  Logo_BlurReveal: BlurSize 50→0")
    print("  Logo_Shine: Center.X -0.5→1.5")
    print("  Logo_Typewriter: WriteOn 0→1")
else
    print("Error: No composition found")
end
