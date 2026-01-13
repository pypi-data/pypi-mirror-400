-- Social Media Frames
-- Platform-specific frames and safe zones

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- === INSTAGRAM STORY FRAME (9:16) ===
    local igStoryBG = comp:AddTool("Background")
    igStoryBG:SetAttrs({TOOLS_Name = "Social_IGStory_BG"})
    igStoryBG.Width = 1080
    igStoryBG.Height = 1920
    igStoryBG.TopLeftRed = 0.1
    igStoryBG.TopLeftGreen = 0.1
    igStoryBG.TopLeftBlue = 0.1

    -- Safe zone guides (avoid top/bottom 150px for UI)
    local igSafeTop = comp:AddTool("RectangleMask")
    igSafeTop:SetAttrs({TOOLS_Name = "Social_IGStory_SafeTop"})
    igSafeTop.Width = 1
    igSafeTop.Height = 0.08
    igSafeTop.Center = {0.5, 0.96}

    local igSafeBottom = comp:AddTool("RectangleMask")
    igSafeBottom:SetAttrs({TOOLS_Name = "Social_IGStory_SafeBottom"})
    igSafeBottom.Width = 1
    igSafeBottom.Height = 0.15
    igSafeBottom.Center = {0.5, 0.075}

    -- === YOUTUBE THUMBNAIL FRAME (16:9) ===
    local ytThumbBG = comp:AddTool("Background")
    ytThumbBG:SetAttrs({TOOLS_Name = "Social_YTThumb_BG"})
    ytThumbBG.Width = 1280
    ytThumbBG.Height = 720
    ytThumbBG.TopLeftRed = 0.15
    ytThumbBG.TopLeftGreen = 0.15
    ytThumbBG.TopLeftBlue = 0.15

    -- Duration badge area (bottom right)
    local ytDuration = comp:AddTool("RectangleMask")
    ytDuration:SetAttrs({TOOLS_Name = "Social_YTThumb_Duration"})
    ytDuration.Width = 0.12
    ytDuration.Height = 0.08
    ytDuration.Center = {0.92, 0.08}

    -- === TIKTOK FRAME (9:16) ===
    local tiktokBG = comp:AddTool("Background")
    tiktokBG:SetAttrs({TOOLS_Name = "Social_TikTok_BG"})
    tiktokBG.Width = 1080
    tiktokBG.Height = 1920
    tiktokBG.TopLeftRed = 0
    tiktokBG.TopLeftGreen = 0
    tiktokBG.TopLeftBlue = 0

    -- Right side buttons zone
    local tiktokButtons = comp:AddTool("RectangleMask")
    tiktokButtons:SetAttrs({TOOLS_Name = "Social_TikTok_Buttons"})
    tiktokButtons.Width = 0.15
    tiktokButtons.Height = 0.4
    tiktokButtons.Center = {0.92, 0.4}

    -- === SQUARE FRAME (1:1) ===
    local squareBG = comp:AddTool("Background")
    squareBG:SetAttrs({TOOLS_Name = "Social_Square_BG"})
    squareBG.Width = 1080
    squareBG.Height = 1080
    squareBG.TopLeftRed = 0.2
    squareBG.TopLeftGreen = 0.2
    squareBG.TopLeftBlue = 0.2

    -- === TWITTER FRAME (16:9) ===
    local twitterBG = comp:AddTool("Background")
    twitterBG:SetAttrs({TOOLS_Name = "Social_Twitter_BG"})
    twitterBG.Width = 1280
    twitterBG.Height = 720
    twitterBG.TopLeftRed = 0.1
    twitterBG.TopLeftGreen = 0.1
    twitterBG.TopLeftBlue = 0.1

    comp:Unlock()

    print("✓ Social media frames added")
    print("")
    print("Frames:")
    print("  Social_IGStory_* - 1080x1920 with safe zones")
    print("  Social_YTThumb_* - 1280x720 with duration area")
    print("  Social_TikTok_* - 1080x1920 with button zone")
    print("  Social_Square_* - 1080x1080")
    print("  Social_Twitter_* - 1280x720")
    print("")
    print("Safe zones show areas to avoid for platform UI")
else
    print("Error: No composition found")
end
