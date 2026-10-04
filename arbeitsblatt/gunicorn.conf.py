"""Gunicorn-Konfiguration für Coolify/Docker.

Genau ein Worker: Präsenz, Flush-Acks und Socket-Räume liegen im Prozessspeicher (Standard §22).
gthread passt zu Flask-SocketIO im threading-Modus; mit simple-websocket läuft echtes WebSocket.
Dauerhafte Lernendenarbeit liegt nie nur im RAM – sie steht in SQLite unter /app/data.
"""

import os

bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = 1
worker_class = "gthread"
threads = 50
timeout = 180            # KI-Bildbewertungen und IServ-Abschluss dürfen länger dauern
graceful_timeout = 30
preload_app = False
accesslog = "-"
errorlog = "-"
