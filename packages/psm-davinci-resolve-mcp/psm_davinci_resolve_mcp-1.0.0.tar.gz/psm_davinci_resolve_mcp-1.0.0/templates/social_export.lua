-- Social Media Export Templates
-- Sets up compositions for different platforms
-- Run from: Fusion page > Console

-- Platform specifications
local platforms = {
    youtube = {width = 1920, height = 1080, fps = 30},
    instagram_feed = {width = 1080, height = 1080, fps = 30},
    instagram_story = {width = 1080, height = 1920, fps = 30},
    tiktok = {width = 1080, height = 1920, fps = 30},
    twitter = {width = 1280, height = 720, fps = 30},
    linkedin = {width = 1920, height = 1080, fps = 30},
}

-- Which platform to set up (change this)
local targetPlatform = "instagram_story"

local comp = fusion:GetCurrentComp()
if not comp then
    print("✗ No composition open")
    return
end

local spec = platforms[targetPlatform]
if not spec then
    print("✗ Unknown platform: " .. targetPlatform)
    print("Available: youtube, instagram_feed, instagram_story, tiktok, twitter, linkedin")
    return
end

comp:Lock()

print("=== Setting up for " .. targetPlatform .. " ===")
print(string.format("Resolution: %dx%d @ %dfps", spec.width, spec.height, spec.fps))

-- Set composition attributes
comp:SetAttrs({
    COMPN_Width = spec.width,
    COMPN_Height = spec.height,
    COMPN_FrameRate = spec.fps,
})

-- Background
local bg = comp:AddTool("Background")
bg:SetAttrs({TOOLS_Name = "PlatformBG"})
bg.Width = spec.width
bg.Height = spec.height

-- Transform for scaling footage
local transform = comp:AddTool("Transform")
transform:SetAttrs({TOOLS_Name = "FitFootage"})

-- Safe zones overlay (for Instagram/TikTok with UI overlays)
if targetPlatform == "instagram_story" or targetPlatform == "tiktok" then
    local safeTop = comp:AddTool("Background")
    safeTop:SetAttrs({TOOLS_Name = "TopSafeZone"})
    safeTop.TopLeftRed = 1
    safeTop.TopLeftGreen = 0
    safeTop.TopLeftBlue = 0
    safeTop.TopLeftAlpha = 0.3

    local safeBottom = comp:AddTool("Background")
    safeBottom:SetAttrs({TOOLS_Name = "BottomSafeZone"})
    safeBottom.TopLeftRed = 1
    safeBottom.TopLeftGreen = 0
    safeBottom.TopLeftBlue = 0
    safeBottom.TopLeftAlpha = 0.3

    print("")
    print("⚠ Safe zones added (red overlays)")
    print("  Keep important content away from top 10% and bottom 20%")
    print("  (Instagram/TikTok UI covers these areas)")
end

-- Output
local mediaOut = comp:AddTool("MediaOut")
mediaOut:SetAttrs({TOOLS_Name = "SocialOutput"})

comp:Unlock()

print("")
print("✓ Setup complete!")
print("")
print("Export settings in Deliver page:")
if targetPlatform == "youtube" then
    print("  Format: MP4, Codec: H.264, Bitrate: 20+ Mbps")
elseif targetPlatform:find("instagram") then
    print("  Format: MP4, Codec: H.264, Bitrate: 8-12 Mbps")
elseif targetPlatform == "tiktok" then
    print("  Format: MP4, Codec: H.264, Bitrate: 10+ Mbps, max 60s")
else
    print("  Format: MP4, Codec: H.264, Bitrate: 8-15 Mbps")
end
