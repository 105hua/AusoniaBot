echo "BOT LINTING"

echo "BOT.PY"
pylint bot.py

echo "MODULES"
pylint modules

echo "EXTENSIONS"
pylint extensions

echo "API"

echo "SERVER.PY"
pylint api/server.py

echo "API MODULES"
pylint api/modules