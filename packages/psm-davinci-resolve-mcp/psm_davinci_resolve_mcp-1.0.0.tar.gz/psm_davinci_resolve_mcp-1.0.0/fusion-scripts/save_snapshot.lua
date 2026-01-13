-- Save a snapshot/screenshot of the current viewer
-- Run from: Fusion page > Console (Shift+0)

local comp = fusion:GetCurrentComp()
if comp then
    local path = os.getenv("HOME") .. "/Desktop/fusion_snapshot.png"

    -- Get the current time
    local currentTime = comp.CurrentTime

    -- Find a saver or create output
    local saver = comp:FindTool("Saver1")
    if not saver then
        comp:Lock()
        saver = comp:AddTool("Saver")
        saver.Clip = path
        comp:Unlock()
    end

    print("Snapshot would be saved to: " .. path)
    print("(Full saver functionality requires connecting to output)")
else
    print("No composition open")
end
