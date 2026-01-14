# The main Terminal will eventually run the Hot Reloading

# Start Up Shell
osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
osascript -e 'tell application "Terminal" to do script "cd project_path && source venv/bin/activate" in front window'
osascript -e 'tell application "Terminal" to do script "flask shell" in front window'

# Start Up Flask Server
osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
osascript -e 'tell application "Terminal" to do script "cd project_path && source venv/bin/activate" in front window'
osascript -e 'tell application "Terminal" to do script "flask run --debug" in front window'

# Building your tailwind.css file
osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
osascript -e 'tell application "Terminal" to do script "cd project_path && npm run watch:css" in front window'

# Building your tailwind.min.css file
osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
osascript -e 'tell application "Terminal" to do script "cd project_path && npm run build:css" in front window'

# Open up VS code Text
osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
osascript -e 'tell application "Terminal" to do script "cd project_path && code ." in front window'

sleep 5

# Open Safari and navigate to http://127.0.0.1:5000
open -a "Safari" "http://127.0.0.1:5000"


#!/bin/bash

# Define the folder to watch
WATCH_FOLDER_TEMPLATES="$(pwd)/app/templates"
WATCH_FOLDER_CONTROLLER="$(pwd)/app/controllers"
WATCH_FOLDER_FORMS="$(pwd)/app/forms"
WATCH_FOLDER_MODELS="$(pwd)/app/models"
WATCH_FOLDER_ROUTES="$(pwd)/app/routes"

# Function to refresh Chrome
refresh_safari() {
    osascript <<EOF
tell application "Safari"
    repeat with w in windows
        repeat with t in tabs of w
            if (URL of t contains "http://127.0.0.1:5000/") then
                tell t to do JavaScript "window.location.reload();"
            end if
        end repeat
    end repeat
end tell
EOF
}


# Watch for file changes in the folder and its subfolders
fswatch -0 "$WATCH_FOLDER_TEMPLATES" "$WATCH_FOLDER_CONTROLLER" "$WATCH_FOLDER_FORMS" "$WATCH_FOLDER_MODELS" "$WATCH_FOLDER_ROUTES" | while read -d "" event

do
    echo "Change detected: $event"

    # Call the function to refresh Chrome
    refresh_safari
done
