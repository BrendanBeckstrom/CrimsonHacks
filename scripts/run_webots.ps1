$WORLD_PATH = "webots/world/CrimsonMars.wbt"
# If Webots is not in PATH, set it here, e.g.:
# $env:Path += ";C:\\Program Files\\Webots"
webots --stdout --stderr --no-sandbox --mode=fast $WORLD_PATH