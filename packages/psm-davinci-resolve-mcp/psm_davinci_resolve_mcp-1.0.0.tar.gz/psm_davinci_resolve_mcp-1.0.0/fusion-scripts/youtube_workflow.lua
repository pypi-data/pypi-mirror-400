-- YouTube Video Production Template
-- Sets up a complete composition for YouTube content
-- Run from: Fusion page > Console

local comp = fusion:GetCurrentComp()
if not comp then
    print("✗ No composition open")
    return
end

comp:Lock()

print("=== Creating YouTube Video Template ===")

-- 1. Media inputs
local mediaIn = comp:AddTool("MediaIn")
mediaIn:SetAttrs({TOOLS_Name = "MainFootage"})

-- 2. Background for letterboxing/safety
local bg = comp:AddTool("Background")
bg:SetAttrs({TOOLS_Name = "SafeAreaBG"})
bg.TopLeftRed = 0.1
bg.TopLeftGreen = 0.1
bg.TopLeftBlue = 0.1

-- 3. Color correction chain
local lift = comp:AddTool("ColorCorrector")
lift:SetAttrs({TOOLS_Name = "01_Exposure"})

local contrast = comp:AddTool("ColorCorrector")
contrast:SetAttrs({TOOLS_Name = "02_Contrast"})

local sat = comp:AddTool("ColorCorrector")
sat:SetAttrs({TOOLS_Name = "03_Saturation"})
sat.MasterSaturation = 1.15  -- Slight boost for YouTube

-- 4. Sharpening
local sharpen = comp:AddTool("UnsharpMask")
sharpen:SetAttrs({TOOLS_Name = "04_Sharpen"})
sharpen.Size = 2.5
sharpen.Gain = 0.3

-- 5. Lower third
local lowerThird = comp:AddTool("TextPlus")
lowerThird:SetAttrs({TOOLS_Name = "LowerThird"})
lowerThird.StyledText = "Your Name Here"
lowerThird.Font = "Arial Bold"
lowerThird.Size = 0.05
lowerThird.Center = {0.15, 0.08}

-- 6. Subscribe reminder
local subscribe = comp:AddTool("TextPlus")
subscribe:SetAttrs({TOOLS_Name = "SubscribeReminder"})
subscribe.StyledText = "SUBSCRIBE"
subscribe.Font = "Arial Black"
subscribe.Size = 0.04
subscribe.Center = {0.88, 0.08}
subscribe.Red1 = 1
subscribe.Green1 = 0.2
subscribe.Blue1 = 0.2

-- 7. Final merge and output
local merge = comp:AddTool("Merge")
merge:SetAttrs({TOOLS_Name = "FinalComp"})

local mediaOut = comp:AddTool("MediaOut")
mediaOut:SetAttrs({TOOLS_Name = "Output"})

comp:Unlock()

print("✓ YouTube template created!")
print("")
print("Node chain:")
print("  MainFootage → 01_Exposure → 02_Contrast → 03_Saturation → 04_Sharpen")
print("  └→ FinalComp (merge with LowerThird, SubscribeReminder)")
print("  └→ Output")
print("")
print("Next steps:")
print("  1. Connect MainFootage to your source clip")
print("  2. Connect nodes in sequence")
print("  3. Adjust LowerThird text")
print("  4. Add keyframes for subscribe animation")
