-- Call-to-Action Graphics
-- Subscribe, like, comment, follow buttons

local comp = fusion:GetCurrentComp()

if comp then
    comp:Lock()

    -- === SUBSCRIBE BUTTON ===
    local subBG = comp:AddTool("Background")
    subBG:SetAttrs({TOOLS_Name = "CTA_SubscribeBG"})
    subBG.TopLeftRed = 0.8
    subBG.TopLeftGreen = 0.1
    subBG.TopLeftBlue = 0.1

    local subMask = comp:AddTool("RectangleMask")
    subMask:SetAttrs({TOOLS_Name = "CTA_SubscribeMask"})
    subMask.Width = 0.2
    subMask.Height = 0.06
    subMask.Center = {0.85, 0.1}
    subMask.CornerRadius = 0.01

    local subText = comp:AddTool("TextPlus")
    subText:SetAttrs({TOOLS_Name = "CTA_SubscribeText"})
    subText.StyledText = "SUBSCRIBE"
    subText.Font = "Arial Bold"
    subText.Size = 0.025
    subText.Center = {0.85, 0.1}

    -- === LIKE BUTTON ===
    local likeBG = comp:AddTool("Background")
    likeBG:SetAttrs({TOOLS_Name = "CTA_LikeBG"})
    likeBG.TopLeftRed = 0.2
    likeBG.TopLeftGreen = 0.5
    likeBG.TopLeftBlue = 0.9

    local likeText = comp:AddTool("TextPlus")
    likeText:SetAttrs({TOOLS_Name = "CTA_LikeText"})
    likeText.StyledText = "👍 LIKE"
    likeText.Font = "Arial Bold"
    likeText.Size = 0.03
    likeText.Center = {0.15, 0.1}

    -- === BELL NOTIFICATION ===
    local bell = comp:AddTool("TextPlus")
    bell:SetAttrs({TOOLS_Name = "CTA_Bell"})
    bell.StyledText = "🔔"
    bell.Size = 0.05
    bell.Center = {0.92, 0.1}

    -- === COMMENT REMINDER ===
    local comment = comp:AddTool("TextPlus")
    comment:SetAttrs({TOOLS_Name = "CTA_Comment"})
    comment.StyledText = "💬 Comment below!"
    comment.Font = "Arial"
    comment.Size = 0.03
    comment.Center = {0.5, 0.08}

    -- === SOCIAL FOLLOW ===
    local social = comp:AddTool("TextPlus")
    social:SetAttrs({TOOLS_Name = "CTA_Social"})
    social.StyledText = "Follow @yourhandle"
    social.Font = "Arial Bold"
    social.Size = 0.025
    social.Center = {0.5, 0.05}

    -- === ARROW POINTER ===
    local arrow = comp:AddTool("TextPlus")
    arrow:SetAttrs({TOOLS_Name = "CTA_Arrow"})
    arrow.StyledText = "👇"
    arrow.Size = 0.06
    arrow.Center = {0.5, 0.15}
    -- Animate Y position for bounce

    -- === SWIPE UP (Stories) ===
    local swipeUp = comp:AddTool("TextPlus")
    swipeUp:SetAttrs({TOOLS_Name = "CTA_SwipeUp"})
    swipeUp.StyledText = "⬆️ Swipe Up"
    swipeUp.Font = "Arial Bold"
    swipeUp.Size = 0.035
    swipeUp.Center = {0.5, 0.1}

    comp:Unlock()

    print("✓ Call-to-action graphics added")
    print("")
    print("Elements:")
    print("  CTA_Subscribe* - Red subscribe button")
    print("  CTA_Like* - Blue like button")
    print("  CTA_Bell - Notification bell")
    print("  CTA_Comment - Comment reminder")
    print("  CTA_Social - Follow handle")
    print("  CTA_Arrow - Animated pointer")
    print("  CTA_SwipeUp - Stories swipe CTA")
    print("")
    print("Animate for attention (scale pulse, bounce)")
else
    print("Error: No composition found")
end
