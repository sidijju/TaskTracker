#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/Task Tracker.app" dist/dmg
# If the DMG already exists, delete it.
test -f "Task Tracker.dmg" && rm "Task Tracker.dmg"
create-dmg \
  --volname "Task Tracker" \
  --volicon "tasktracker.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "Task Tracker.app" 175 120 \
  --hide-extension "Task Tracker.app" \
  --app-drop-link 425 120 \
  "Task Tracker.dmg" \
  "dist/dmg/"