-- Particle Effects
-- Dust, snow, sparks, and floating particles

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Dust/floating particles
    local dustEmitter = comp:AddTool("pEmitter")
    dustEmitter:SetAttrs({TOOLS_Name = "Dust_Emitter"})
    dustEmitter.Number = 50
    dustEmitter.Lifespan = 200
    dustEmitter.SizeControls = {0.002, 0.005}
    dustEmitter.Velocity = 0.001
    dustEmitter.VelocityVariance = 0.002

    local dustRender = comp:AddTool("pRender")
    dustRender:SetAttrs({TOOLS_Name = "Dust_Render"})

    -- Snow effect
    local snowEmitter = comp:AddTool("pEmitter")
    snowEmitter:SetAttrs({TOOLS_Name = "Snow_Emitter"})
    snowEmitter.Number = 100
    snowEmitter.Lifespan = 150
    snowEmitter.SizeControls = {0.003, 0.008}
    snowEmitter.Velocity = 0.005
    snowEmitter.Angle = -90  -- Fall down

    local snowTurbulence = comp:AddTool("pTurbulence")
    snowTurbulence:SetAttrs({TOOLS_Name = "Snow_Turbulence"})
    snowTurbulence.XStrength = 0.01
    snowTurbulence.Density = 2

    local snowRender = comp:AddTool("pRender")
    snowRender:SetAttrs({TOOLS_Name = "Snow_Render"})

    -- Sparks/embers
    local sparkEmitter = comp:AddTool("pEmitter")
    sparkEmitter:SetAttrs({TOOLS_Name = "Sparks_Emitter"})
    sparkEmitter.Number = 30
    sparkEmitter.Lifespan = 80
    sparkEmitter.SizeControls = {0.001, 0.003}
    sparkEmitter.Velocity = 0.02
    sparkEmitter.Angle = 90  -- Rise up
    sparkEmitter.AngleVariance = 30

    local sparkRender = comp:AddTool("pRender")
    sparkRender:SetAttrs({TOOLS_Name = "Sparks_Render"})

    -- Bokeh/light orbs
    local bokehEmitter = comp:AddTool("pEmitter")
    bokehEmitter:SetAttrs({TOOLS_Name = "Bokeh_Emitter"})
    bokehEmitter.Number = 20
    bokehEmitter.Lifespan = 300
    bokehEmitter.SizeControls = {0.02, 0.08}
    bokehEmitter.Velocity = 0.0005

    local bokehRender = comp:AddTool("pRender")
    bokehRender:SetAttrs({TOOLS_Name = "Bokeh_Render"})

    local bokehGlow = comp:AddTool("SoftGlow")
    bokehGlow:SetAttrs({TOOLS_Name = "Bokeh_Glow"})
    bokehGlow.Threshold = 0.1
    bokehGlow.Gain = 1
    bokehGlow.XGlowSize = 20

    comp:Unlock()

    print("✓ Particle generators added")
    print("")
    print("Available particles:")
    print("  Dust - Slow floating particles")
    print("  Snow - Falling with turbulence")
    print("  Sparks - Rising embers")
    print("  Bokeh - Soft light orbs")
    print("")
    print("Connect: Emitter → (modifiers) → Render")
else
    print("Error: No composition found")
end
