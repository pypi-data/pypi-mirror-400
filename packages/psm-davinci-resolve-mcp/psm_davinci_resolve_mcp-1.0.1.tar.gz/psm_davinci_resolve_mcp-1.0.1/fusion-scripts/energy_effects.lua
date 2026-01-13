-- Energy & Electric Effects
-- Lightning, plasma, energy trails

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- === LIGHTNING BOLT ===
    local lightning = comp:AddTool("FastNoise")
    lightning:SetAttrs({TOOLS_Name = "Energy_Lightning"})
    lightning.Detail = 3
    lightning.Contrast = 20
    lightning.Brightness = -0.5
    lightning.XScale = 200
    lightning.YScale = 5
    lightning.SeetheRate = 2  -- Fast animation

    local lightningGlow = comp:AddTool("SoftGlow")
    lightningGlow:SetAttrs({TOOLS_Name = "Energy_LightningGlow"})
    lightningGlow.Threshold = 0.5
    lightningGlow.Gain = 2
    lightningGlow.XGlowSize = 10
    lightningGlow.YGlowSize = 10

    local lightningColor = comp:AddTool("ColorCorrector")
    lightningColor:SetAttrs({TOOLS_Name = "Energy_LightningColor"})
    lightningColor.MasterRGBGain = {0.7, 0.8, 1}  -- Blue-white

    -- === PLASMA BALL ===
    local plasma = comp:AddTool("FastNoise")
    plasma:SetAttrs({TOOLS_Name = "Energy_Plasma"})
    plasma.Detail = 5
    plasma.Contrast = 3
    plasma.Brightness = 0.2
    plasma.XScale = 1
    plasma.YScale = 1
    plasma.SeetheRate = 0.3

    local plasmaMask = comp:AddTool("EllipseMask")
    plasmaMask:SetAttrs({TOOLS_Name = "Energy_PlasmaMask"})
    plasmaMask.Width = 0.3
    plasmaMask.Height = 0.3
    plasmaMask.SoftEdge = 0.1

    local plasmaGlow = comp:AddTool("SoftGlow")
    plasmaGlow:SetAttrs({TOOLS_Name = "Energy_PlasmaGlow"})
    plasmaGlow.Threshold = 0.3
    plasmaGlow.Gain = 1.5

    -- === ENERGY RING ===
    local ring = comp:AddTool("EllipseMask")
    ring:SetAttrs({TOOLS_Name = "Energy_Ring"})
    ring.Width = 0.5
    ring.Height = 0.5
    ring.SoftEdge = 0.02
    ring.BorderWidth = 0.02

    local ringGlow = comp:AddTool("SoftGlow")
    ringGlow:SetAttrs({TOOLS_Name = "Energy_RingGlow"})
    ringGlow.Threshold = 0.1
    ringGlow.Gain = 3
    ringGlow.XGlowSize = 30
    ringGlow.YGlowSize = 30

    -- === PARTICLE SPARKS ===
    local sparks = comp:AddTool("pEmitter")
    sparks:SetAttrs({TOOLS_Name = "Energy_Sparks"})
    sparks.Number = 50
    sparks.Lifespan = 30
    sparks.Velocity = 0.05
    sparks.VelocityVariation = 0.02
    sparks.SizeControls = {0.002, 0.01}

    local sparkForce = comp:AddTool("pDirectionalForce")
    sparkForce:SetAttrs({TOOLS_Name = "Energy_SparksGravity"})
    sparkForce.Direction = {0, -0.5, 0}

    local sparkRender = comp:AddTool("pRender")
    sparkRender:SetAttrs({TOOLS_Name = "Energy_SparksRender"})

    local sparkGlow = comp:AddTool("SoftGlow")
    sparkGlow:SetAttrs({TOOLS_Name = "Energy_SparksGlow"})
    sparkGlow.Threshold = 0.1
    sparkGlow.Gain = 2

    -- === ELECTRIC ARC ===
    local arc = comp:AddTool("FastNoise")
    arc:SetAttrs({TOOLS_Name = "Energy_Arc"})
    arc.Detail = 2
    arc.Contrast = 15
    arc.Brightness = -0.8
    arc.XScale = 100
    arc.YScale = 3
    arc.SeetheRate = 5  -- Very fast

    local arcDisplace = comp:AddTool("Displace")
    arcDisplace:SetAttrs({TOOLS_Name = "Energy_ArcDisplace"})
    arcDisplace.XRefraction = 0.1
    arcDisplace.YRefraction = 0.3

    -- === POWER SURGE ===
    local surge = comp:AddTool("BrightnessContrast")
    surge:SetAttrs({TOOLS_Name = "Energy_Surge"})
    surge.Gain = 2
    surge.Saturation = 1.5

    local surgeGlow = comp:AddTool("SoftGlow")
    surgeGlow:SetAttrs({TOOLS_Name = "Energy_SurgeGlow"})
    surgeGlow.Threshold = 0.6
    surgeGlow.Gain = 1
    surgeGlow.XGlowSize = 50
    surgeGlow.YGlowSize = 50

    comp:Unlock()

    print("✓ Energy effects added")
    print("")
    print("Effects:")
    print("  Energy_Lightning* - Electric bolt")
    print("  Energy_Plasma* - Glowing plasma ball")
    print("  Energy_Ring* - Expanding ring")
    print("  Energy_Sparks* - Flying particles")
    print("  Energy_Arc* - Electric arc")
    print("  Energy_Surge* - Power surge flash")
    print("")
    print("Use Add/Screen blend mode")
    print("Animate SeetheRate for electric movement")
else
    print("Error: No composition found")
end
