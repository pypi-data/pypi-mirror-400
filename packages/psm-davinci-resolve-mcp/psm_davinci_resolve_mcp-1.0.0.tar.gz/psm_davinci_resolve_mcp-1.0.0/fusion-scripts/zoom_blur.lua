-- Zoom Blur / Radial Blur Effect
-- Creates dramatic zoom/radial blur for impact moments

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- Radial blur from center
    local zoom = comp:AddTool("ZoomBlur")
    zoom:SetAttrs({TOOLS_Name = "ZoomBlur"})
    zoom.Center = {0.5, 0.5}
    zoom.Length = 0.05
    zoom.XOffset = 0
    zoom.YOffset = 0
    zoom.Quality = 10  -- Higher = smoother

    -- Mask to keep center sharp
    local centerMask = comp:AddTool("EllipseMask")
    centerMask:SetAttrs({TOOLS_Name = "SharpCenter"})
    centerMask.Center = {0.5, 0.5}
    centerMask.Width = 0.4
    centerMask.Height = 0.3
    centerMask.SoftEdge = 0.3
    centerMask.Invert = true

    -- Optional: Directional version
    local dirZoom = comp:AddTool("DirectionalBlur")
    dirZoom:SetAttrs({TOOLS_Name = "DirectionalZoom"})
    dirZoom.Type = 1  -- Radial
    dirZoom.Length = 0.03
    dirZoom.Center = {0.5, 0.5}

    comp:Unlock()

    print("✓ Zoom blur effect added")
    print("  ZoomBlur - classic zoom effect")
    print("  DirectionalZoom - radial variant")
    print("  SharpCenter mask keeps subject clear")
    print("")
    print("Animate Length for impact transitions:")
    print("  0 → 0.1 = zoom in effect")
    print("  0.1 → 0 = zoom settle")
else
    print("Error: No composition found")
end
