lsof -t -i:1337 | xargs -r kill -9; gunicorn -w 1 -b 0.0.0.0:1337 main:app
