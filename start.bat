@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
streamlit run scripts/chat_ui.py
pause
