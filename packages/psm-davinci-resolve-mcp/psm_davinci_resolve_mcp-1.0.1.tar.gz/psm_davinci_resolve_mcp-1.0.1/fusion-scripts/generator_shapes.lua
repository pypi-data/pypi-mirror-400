-- Shape Generators
-- Geometric shapes for motion graphics

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Circle
    local circle = comp:AddTool("EllipseMask")
    circle:SetAttrs({TOOLS_Name = "Shape_Circle"})
    circle.Width = 0.3
    circle.Height = 0.3
    circle.Center = {0.5, 0.5}
    circle.SoftEdge = 0

    local circleBG = comp:AddTool("Background")
    circleBG:SetAttrs({TOOLS_Name = "Shape_CircleFill"})
    circleBG.TopLeftRed = 1
    circleBG.TopLeftGreen = 0.3
    circleBG.TopLeftBlue = 0.3

    -- Rectangle
    local rect = comp:AddTool("RectangleMask")
    rect:SetAttrs({TOOLS_Name = "Shape_Rectangle"})
    rect.Width = 0.4
    rect.Height = 0.25
    rect.Center = {0.5, 0.5}
    rect.CornerRadius = 0.02

    local rectBG = comp:AddTool("Background")
    rectBG:SetAttrs({TOOLS_Name = "Shape_RectFill"})
    rectBG.TopLeftRed = 0.3
    rectBG.TopLeftGreen = 0.5
    rectBG.TopLeftBlue = 1

    -- Line
    local line = comp:AddTool("RectangleMask")
    line:SetAttrs({TOOLS_Name = "Shape_Line"})
    line.Width = 0.5
    line.Height = 0.005
    line.Center = {0.5, 0.5}

    local lineBG = comp:AddTool("Background")
    lineBG:SetAttrs({TOOLS_Name = "Shape_LineFill"})
    lineBG.TopLeftRed = 1
    lineBG.TopLeftGreen = 1
    lineBG.TopLeftBlue = 1

    -- Triangle (using polygon)
    local tri = comp:AddTool("PolylineMask")
    tri:SetAttrs({TOOLS_Name = "Shape_Triangle"})
    -- Note: Polyline requires manual point setup

    -- Ring/donut
    local ringOuter = comp:AddTool("EllipseMask")
    ringOuter:SetAttrs({TOOLS_Name = "Shape_RingOuter"})
    ringOuter.Width = 0.4
    ringOuter.Height = 0.4
    ringOuter.Center = {0.5, 0.5}

    local ringInner = comp:AddTool("EllipseMask")
    ringInner:SetAttrs({TOOLS_Name = "Shape_RingInner"})
    ringInner.Width = 0.3
    ringInner.Height = 0.3
    ringInner.Center = {0.5, 0.5}
    ringInner.Invert = true

    comp:Unlock()

    print("✓ Shape generators added")
    print("")
    print("Shapes available:")
    print("  Shape_Circle + Shape_CircleFill")
    print("  Shape_Rectangle + Shape_RectFill")
    print("  Shape_Line + Shape_LineFill")
    print("  Shape_RingOuter + Shape_RingInner (combine for ring)")
    print("")
    print("Animate Width/Height for scale")
    print("Animate Center for position")
    print("Animate Angle for rotation")
else
    print("Error: No composition found")
end
