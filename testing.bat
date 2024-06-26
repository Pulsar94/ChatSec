@echo off
start cmd /k "py ./main_server.py & pause"
powershell -command "Start-Sleep -Milliseconds 500"
start cmd /k "py ./main_client.py & pause"