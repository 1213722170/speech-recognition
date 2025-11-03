@echo off
echo 正在启动语音助手（已禁用代理）...
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
python voice_assistant.py
pause
