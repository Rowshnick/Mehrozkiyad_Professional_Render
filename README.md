Mehrozkiyad Professional - Render-ready

نحوه اجرا محلی:
pip install -r requirements.txt
export TG_BOT_TOKEN="YOUR_TOKEN"    # یا روی ویندوز: set TG_BOT_TOKEN=...
python bot_app.py

نحوه دیپلوی روی Render:
1. آپلود فایل‌ها به GitHub (همان ساختار)
2. ساخت Web Service در Render و اتصال به GitHub repo
3. قرار دادن TG_BOT_TOKEN در Environment variables
4. Deploy — Render مقدار RENDER_EXTERNAL_URL را قرار می‌دهد؛ سپس ربات در حالت webhook اجرا می‌شود.
