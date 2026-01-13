-- Noise/Texture Generators
-- Film grain, static, organic textures

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Film grain overlay
    local filmGrain = comp:AddTool("FilmGrain")
    filmGrain:SetAttrs({TOOLS_Name = "Gen_FilmGrain"})
    filmGrain.Size = 1.5
    filmGrain.Strength = 0.25
    filmGrain.Softness = 0.5
    filmGrain.Monochromatic = true

    -- TV static/noise
    local static = comp:AddTool("FastNoise")
    static:SetAttrs({TOOLS_Name = "Gen_Static"})
    static.Detail = 10
    static.Contrast = 0.5
    static.Brightness = -0.2
    static.XScale = 1000
    static.YScale = 1000
    static.SeetheRate = 10  -- Fast animation

    -- Organic perlin noise
    local perlin = comp:AddTool("FastNoise")
    perlin:SetAttrs({TOOLS_Name = "Gen_Perlin"})
    perlin.Detail = 5
    perlin.Contrast = 1
    perlin.XScale = 0.5
    perlin.YScale = 0.5
    perlin.SeetheRate = 0.02

    -- Cloud/smoke texture
    local clouds = comp:AddTool("FastNoise")
    clouds:SetAttrs({TOOLS_Name = "Gen_Clouds"})
    clouds.Detail = 8
    clouds.Contrast = 0.8
    clouds.Brightness = 0.1
    clouds.XScale = 0.3
    clouds.YScale = 0.2
    clouds.SeetheRate = 0.01

    -- Scratches/damage
    local scratches = comp:AddTool("FastNoise")
    scratches:SetAttrs({TOOLS_Name = "Gen_Scratches"})
    scratches.Detail = 1
    scratches.Contrast = 8
    scratches.Brightness = -0.9
    scratches.XScale = 0.01
    scratches.YScale = 5
    scratches.SeetheRate = 5

    -- Paper texture
    local paper = comp:AddTool("FastNoise")
    paper:SetAttrs({TOOLS_Name = "Gen_Paper"})
    paper.Detail = 6
    paper.Contrast = 0.3
    paper.Brightness = 0.8
    paper.XScale = 2
    paper.YScale = 2

    comp:Unlock()

    print("✓ Noise/texture generators added")
    print("")
    print("Available textures:")
    print("  Gen_FilmGrain - Classic film grain")
    print("  Gen_Static - TV static noise")
    print("  Gen_Perlin - Organic noise")
    print("  Gen_Clouds - Cloud/smoke")
    print("  Gen_Scratches - Film damage")
    print("  Gen_Paper - Paper texture")
    print("")
    print("Blend modes: Screen, Overlay, Soft Light")
else
    print("Error: No composition found")
end
