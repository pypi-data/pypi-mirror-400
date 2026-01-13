-- Cinematic Look Template
-- Creates a film-like color grade without LUTs
-- Run from: Fusion page > Console

local comp = fusion:GetCurrentComp()
if not comp then
    print("✗ No composition open")
    return
end

comp:Lock()

print("=== Creating Cinematic Look ===")

-- 1. Lift/Gamma/Gain - S-curve contrast
local lgg = comp:AddTool("ColorCorrector")
lgg:SetAttrs({TOOLS_Name = "01_LiftGammaGain"})
-- Lift shadows slightly blue
lgg.ShadowsRed = -0.02
lgg.ShadowsGreen = -0.01
lgg.ShadowsBlue = 0.02
-- Gamma (mids)
lgg.MidtonesRed = 1.0
lgg.MidtonesGreen = 0.98
lgg.MidtonesBlue = 0.95
-- Highlights warm
lgg.HighlightsRed = 1.02
lgg.HighlightsGreen = 1.0
lgg.HighlightsBlue = 0.96

-- 2. Saturation - slightly desaturate
local sat = comp:AddTool("ColorCorrector")
sat:SetAttrs({TOOLS_Name = "02_Saturation"})
sat.MasterSaturation = 0.85

-- 3. Contrast curve
local contrast = comp:AddTool("ColorCurves")
contrast:SetAttrs({TOOLS_Name = "03_Contrast"})

-- 4. Film grain
local grain = comp:AddTool("FilmGrain")
grain:SetAttrs({TOOLS_Name = "04_FilmGrain"})
grain.Size = 1.2
grain.Strength = 0.08
grain.Power = 1.5

-- 5. Subtle vignette
local vignette = comp:AddTool("Vignette")
vignette:SetAttrs({TOOLS_Name = "05_Vignette"})
vignette.Amount = 0.3
vignette.Size = 1.2
vignette.Softness = 0.8

-- 6. Glow for highlights
local glow = comp:AddTool("SoftGlow")
glow:SetAttrs({TOOLS_Name = "06_HighlightGlow"})
glow.Gain = 0.15
glow.Threshold = 0.75

comp:Unlock()

print("✓ Cinematic look nodes created!")
print("")
print("Connect in order:")
print("  Footage → 01_LiftGammaGain → 02_Saturation → 03_Contrast")
print("         → 04_FilmGrain → 05_Vignette → 06_HighlightGlow → Output")
print("")
print("Adjustments:")
print("  - 01: Tweak color balance (blue shadows, warm highlights)")
print("  - 02: Reduce saturation more for bleach bypass look")
print("  - 03: Adjust S-curve in ColorCurves")
print("  - 04: Increase grain for more film look")
print("  - 05: Increase vignette for moodier look")
