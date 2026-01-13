-- Export still frames from composition
-- Edit frame numbers below before running
local framesToExport = {1, 30, 60, 90}  -- Add your frame numbers
local outputPath = os.getenv("HOME") .. "/Desktop/stills/"

local comp = fusion:GetCurrentComp()
if comp then
    -- Create output directory
    os.execute("mkdir -p '" .. outputPath .. "'")

    -- Add a saver for export
    local saver = comp:AddTool("Saver")
    saver:SetAttrs({TOOLS_Name = "StillExporter"})
    saver.Clip = outputPath .. "frame_.png"

    print("✓ Saver node created")
    print("  Output folder: " .. outputPath)
    print("")
    print("To export stills manually:")
    print("  1. Connect your final output to StillExporter")
    print("  2. Move playhead to desired frame")
    print("  3. In Saver, enable 'Save Current Frame Only'")
    print("  4. Click Render or press the Render button")
    print("")
    print("For batch export, render these frames: ")
    for i, frame in ipairs(framesToExport) do
        print("  Frame " .. frame)
    end
else
    print("✗ No composition open")
end
