---
type: how-to
title: Deploy with nginx and gunicorn
description: Deploying on a Linux server with gunicorn behind nginx as a reverse proxy
resource: "nginx/appseed-app.conf, gunicorn.conf.py, autorun.sh"
tags: [deploy, nginx, gunicorn]
timestamp: 2026-10-17
audience: human
authority: current
source: original readme
maintainer: Israel Holetz
---

# Deploy with nginx and gunicorn

`gunicorn.conf.py` listens on `0.0.0.0:8001` with 1 worker — keep a single worker: the state
of running automations lives in the dashboard process's memory.

```bash
# nginx as a proxy to 127.0.0.1:8001
sudo apt install nginx
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s "$PWD/nginx/appseed-app.conf" /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# application
uv sync
./autorun.sh      # activates .venv and execs gunicorn run:app; APP_DIR is optional
```

If Apache holds port 80: `sudo systemctl disable --now apache2`.

In production use `DEBUG=False`, your own `SECRET_KEY`, and HTTPS on nginx.
