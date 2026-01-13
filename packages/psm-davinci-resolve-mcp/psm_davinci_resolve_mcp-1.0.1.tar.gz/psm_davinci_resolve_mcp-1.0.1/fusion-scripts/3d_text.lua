-- 3D Text Effect
-- Extruded text with lighting

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- === 3D TEXT ===
    local text3d = comp:AddTool("Text3D")
    text3d:SetAttrs({TOOLS_Name = "3D_Title"})
    text3d.StyledText = "YOUR TEXT"
    text3d.Font = "Arial Black"
    text3d.Size = 0.3
    text3d.ExtrusionDepth = 0.1
    text3d.BevelDepth = 0.02
    text3d.BevelWidth = 0.01

    -- Material
    local material = comp:AddTool("Blinn")
    material:SetAttrs({TOOLS_Name = "3D_Material"})
    material.Diffuse = {0.8, 0.8, 0.9}
    material.Specular = {1, 1, 1}
    material.SpecularExponent = 50

    -- Light 1 - Key light
    local keyLight = comp:AddTool("PointLight")
    keyLight:SetAttrs({TOOLS_Name = "3D_KeyLight"})
    keyLight.Intensity = 1.5
    keyLight.Color = {1, 0.95, 0.9}

    -- Light 2 - Fill light
    local fillLight = comp:AddTool("DirectionalLight")
    fillLight:SetAttrs({TOOLS_Name = "3D_FillLight"})
    fillLight.Intensity = 0.5
    fillLight.Color = {0.8, 0.85, 1}

    -- Light 3 - Rim light
    local rimLight = comp:AddTool("PointLight")
    rimLight:SetAttrs({TOOLS_Name = "3D_RimLight"})
    rimLight.Intensity = 0.8
    rimLight.Color = {0.9, 0.95, 1}

    -- Camera
    local camera = comp:AddTool("Camera3D")
    camera:SetAttrs({TOOLS_Name = "3D_Camera"})

    -- Renderer
    local renderer = comp:AddTool("Renderer3D")
    renderer:SetAttrs({TOOLS_Name = "3D_Renderer"})

    -- Shadow catcher
    local shadowPlane = comp:AddTool("ImagePlane3D")
    shadowPlane:SetAttrs({TOOLS_Name = "3D_ShadowPlane"})
    shadowPlane.ObjectID = "ShadowCatcher"

    -- Ambient occlusion
    local ssao = comp:AddTool("SSAO")
    ssao:SetAttrs({TOOLS_Name = "3D_AO"})
    ssao.Radius = 0.05
    ssao.Strength = 0.5

    comp:Unlock()

    print("✓ 3D text setup added")
    print("")
    print("Components:")
    print("  3D_Title - 3D extruded text")
    print("  3D_Material - Surface material")
    print("  3D_KeyLight/FillLight/RimLight - Lighting")
    print("  3D_Camera - Camera view")
    print("  3D_Renderer - Final render")
    print("")
    print("Animate camera for reveal effects")
else
    print("Error: No composition found")
end
