-- Add camera shake effect
-- Run from: Fusion page > Console
local comp = fusion:GetCurrentComp()
if comp then
    comp:Lock()

    -- Transform for shake
    local shake = comp:AddTool("Transform")
    shake:SetAttrs({TOOLS_Name = "CameraShake"})

    -- Scale up slightly to hide edges during shake
    shake.Size = 1.05

    -- Add expressions for random shake
    -- Note: In Fusion, we use modifiers for animation
    local xShake = comp:AddModifier("CameraShake.Center", "PerlinNoiseModifier")
    local yShake = comp:AddModifier("CameraShake.Angle", "PerlinNoiseModifier")

    comp:Unlock()
    print("✓ Camera shake effect created")
    print("")
    print("Manual shake setup:")
    print("  1. Connect footage to CameraShake input")
    print("  2. Right-click Center.X > Modify With > Perlin Noise")
    print("  3. Set Scale = 0.01, Strength = 0.005, Speed = 5")
    print("  4. Repeat for Center.Y")
    print("  5. For rotation shake, add to Angle (Scale = 0.5)")
    print("")
    print("Intensity guide:")
    print("  Subtle: Strength 0.002, Speed 3")
    print("  Medium: Strength 0.005, Speed 5")
    print("  Heavy:  Strength 0.01, Speed 8")
end
