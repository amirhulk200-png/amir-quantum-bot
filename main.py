import os
import json
import sqlite3
import asyncio
import logging
import aiohttp
import urllib.parse
from aiohttp import web

# ==========================================
# تنظیمات پیشرفته لاگ‌گیری
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger("EliteEnterpriseBot")

# ==========================================
# مشخصات ربات و کانال
# ==========================================
TELEGRAM_BOT_TOKEN = "8241260358:AAGwwsRQU1R0qiOdl0Rlcb21L5fhYzhXt20"
# یوزرنیم دقیق کانال عمومی شما
PUBLIC_CHANNEL_ID = "@AMIR_QUANTUM_SIGNALS"
ADMIN_USER_ID = 6506567538
ADMIN_USERNAME = "amir_trade_signal_bot"

# تعرفه لایسنس
BOT_PRICE_USD = 10.0

# ولت‌های پرداخت
CRYPTO_WALLETS = {
    "⚡ Bitcoin (BTC)": "bc1ql0xttzcmk3q22wdxswqttclz24mujgamz5t6lc",
    "🌐 Ethereum (ETH)": "0x8B6Bbbb498e782aB17959Fa54857Cf70A9535837",
    "☀️ Solana (SOL)": "FZgVeFzLFragJDFEoBPJhMF4pbF551gwhqV4m2quF6hj",
    "🔹 Litecoin (LTC)": "ltc1q87smxvqk2a70fdlkxnrvsyc9nd6gtrnct2yvx",
    "💎 TON Network": "UQBD5CSPchSbU9d50ZvEOgwFzwKc9_snBh4hH4l54USvzhjX"
}

# بازه زمانی ارسال سیگنال (هر 15 ثانیه)
INTERVAL_SECONDS = 15

# ==========================================
# مدیریت پایگاه داده (SQLite)
# ==========================================
def init_db():
    try:
        conn = sqlite3.connect("elite_enterprise.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                referred_by INTEGER,
                referral_count INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"DB Error: {e}")

def register_user(user_id, username, first_name, referred_by=None):
    try:
        conn = sqlite3.connect("elite_enterprise.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("""
                INSERT INTO users (user_id, username, first_name, referred_by)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, referred_by))
            conn.commit()
            
            if referred_by and referred_by != user_id:
                cursor.execute("""
                    UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?
                """, (referred_by,))
                conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"User registration error: {e}")

def get_user_stats(user_id):
    try:
        conn = sqlite3.connect("elite_enterprise.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT referral_count FROM users WHERE user_id = ?", (user_id,))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else 0
    except Exception:
        return 0

# ==========================================
# موتور تحلیل بازار و نمودار زنده QuickChart
# ==========================================
async def fetch_market_data():
    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "price": float(data.get("lastPrice", 0)),
                        "change": float(data.get("priceChangePercent", 0)),
                        "high": float(data.get("highPrice", 0)),
                        "low": float(data.get("lowPrice", 0))
                    }
        except Exception:
            pass
        return {"price": 85000.0, "change": 2.5, "high": 87000.0, "low": 83000.0}

async def generate_elite_chart(market):
    price = market["price"]
    chart_config = {
        "type": "line",
        "data": {
            "labels": ["T-3", "T-2", "T-1", "LIVE"],
            "datasets": [{
                "label": "ELITE QUANTUM v3.2",
                "data": [price*0.99, price*0.995, price*0.998, price],
                "borderColor": "#00FF66" if market["change"] >= 0 else "#FF3366",
                "backgroundColor": "rgba(0, 255, 102, 0.05)",
                "fill": True,
                "borderWidth": 3
            }]
        },
        "options": {
            "title": {"display": True, "text": f"ELITE QUANTUM TERMINAL | BTC: ${price:,.2f}", "fontColor": "#FFFFFF"}
        }
    }
    encoded = urllib.parse.quote(str(chart_config).replace("'", '"'))
    return f"https://quickchart.io/chart?bkg=0F172A&c={encoded}&w=900&h=500"

# ==========================================
# سیستم ارسال خودکار سیگنال به کانال
# ==========================================
async def broadcast_elite_signals():
    logger.info("Elite quantum signal broadcast engine active...")
    await asyncio.sleep(3)
    while True:
        try:
            market = await fetch_market_data()
            chart_url = await generate_elite_chart(market)
            
            global_copy = (
                f"🌐 *ELITE QUANTUM TRADING INTELLIGENCE* ⚡\n\n"
                f"📊 *Real-Time On-Chain Market Report:*\n"
                f"▪️ *Asset Class:* Bitcoin (BTC/USDT)\n"
                f"▪️ *Execution Price:* `${market['price']:,.2f}`\n"
                f"▪️ *24H Volatility Momentum:* `{market['change']}%`\n\n"
                f"💎 *Deploy Your Autonomous Enterprise Bot:*\n"
                f"Institutional-grade AI engine running 24/7.\n\n"
                f"🔥 *Global License Fee:* *{BOT_PRICE_USD}$* (Lifetime Access)\n"
            )
            
            wallets_block = "".join([f"{coin}:\n`{addr}`\n\n" for coin, addr in CRYPTO_WALLETS.items()])
            full_broadcast = (
                global_copy + 
                f"──────────────────────────────\n"
                f"💳 *Secure Multi-Currency Payment Vaults:*\n\n"
                f"{wallets_block}"
                f"💡 _After payment, forward your receipt here for instant automated processing._"
            )
            
            markup = {
                "inline_keyboard": [
                    [{"text": f"⚡ خرید ربات و دریافت لایسنس ({int(BOT_PRICE_USD)}$)", "url": f"https://t.me/{ADMIN_USERNAME}?start=buy"}],
                    [{"text": "🌟 سیستم کسب درآمد دلاری (رفرال)", "url": f"https://t.me/{ADMIN_USERNAME}?start=ref"}]
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(chart_url) as resp:
                    if resp.status == 200:
                        img_bytes = await resp.read()
                        
                        # ارسال عکس با استفاده از aiohttp formData
                        form = aiohttp.FormData()
                        form.add_field("chat_id", PUBLIC_CHANNEL_ID)
                        form.add_field("caption", full_broadcast)
                        form.add_field("parse_mode", "Markdown")
                        form.add_field("reply_markup", json.dumps(markup))
                        form.add_field("photo", img_bytes, filename="chart.jpg", content_type="image/jpeg")
                        
                        post_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
                        async with session.post(post_url, data=form) as p_resp:
                            res_json = await p_resp.json()
                            if res_json.get("ok"):
                                logger.info(">>> [SUCCESS] New elite broadcast posted to channel!")
                            else:
                                logger.error(f">>> [TELEGRAM ERROR] Failed to post: {res_json}")
        except Exception as e:
            logger.error(f">>> [BROADCAST ERROR] {e}")
            
        await asyncio.sleep(INTERVAL_SECONDS)

# ==========================================
# سیستم لیسنر چت و تایید فیش‌ها
# ==========================================
async def send_msg(session, chat_id, text, markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if markup:
        payload["reply_markup"] = json.dumps(markup)
    async with session.post(url, json=payload) as r:
        return await r.json()

async def run_elite_listener():
    logger.info("Elite interactive async listener online...")
    offset = 0
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}&timeout=25"
                async with session.get(url, timeout=30) as resp:
                    if resp.status != 200:
                        await asyncio.sleep(3)
                        continue
                    res = await resp.json()
                    
                for update in res.get("result", []):
                    offset = update["update_id"] + 1
                    
                    if "callback_query" in update:
                        cq = update["callback_query"]
                        data = cq["data"]
                        u_id = cq["from"]["id"]
                        if u_id == ADMIN_USER_ID:
                            if data.startswith("approve_"):
                                t_user = data.split("_")[1]
                                await send_msg(session, t_user, "🎉 *پرداخت تایید شد!*\nلینک سورس‌کد انحصاری:\n`https://github.com/example/elite-quantum-bot-source`")
                                await send_msg(session, ADMIN_USER_ID, "✅ تاییدیه انجام و سورس ارسال شد.")
                            elif data.startswith("reject_"):
                                t_user = data.split("_")[1]
                                await send_msg(session, t_user, "❌ فیش ارسالی توسط واحد مالی تایید نشد.")
                                await send_msg(session, ADMIN_USER_ID, "❌ تراکنش رد شد.")
                        continue

                    msg = update.get("message")
                    if not msg:
                        continue
                        
                    chat_id = msg["chat"]["id"]
                    first_name = msg["from"].get("first_name", "Elite Trader")
                    username = msg["from"].get("username", "")
                    text = msg.get("text", "")
                    
                    ref_id = None
                    if text.startswith("/start"):
                        parts = text.split()
                        if len(parts) > 1 and parts[1].isdigit():
                            ref_id = int(parts[1])
                            
                    register_user(chat_id, username, first_name, ref_id)

                    if text.startswith("/start") and "ref" in text:
                        ref_count = get_user_stats(chat_id)
                        ref_link = f"https://t.me/{ADMIN_USERNAME}?start={chat_id}"
                        ref_msg = (
                            f"🌐 *سیستم ارجاع و بازاریابی ویروسی (Affiliate)*\n\n"
                            f"🔗 *لینک دعوت اختصاصی شما:*\n`{ref_link}`\n\n"
                            f"👥 *تعداد دعوت‌شده‌ها:* `{ref_count}` نفر"
                        )
                        await send_msg(session, chat_id, ref_msg)
                        continue

                    if "photo" in msg:
                        photo_id = msg["photo"][-1]["file_id"]
                        caption = msg.get("caption", "بدون توضیحات")
                        
                        admin_markup = {
                            "inline_keyboard": [[
                                {"text": "✅ تایید پرداخت و ارسال سورس", "callback_data": f"approve_{chat_id}"},
                                {"text": "❌ رد فیش", "callback_data": f"reject_{chat_id}"}
                            ]]
                        }
                        form = aiohttp.FormData()
                        form.add_field("chat_id", str(ADMIN_USER_ID))
                        form.add_field("photo", photo_id)
                        form.add_field("caption", f"📥 *Elite Payment Proof!*\n👤 User: {first_name} (`{chat_id}`)\n💬 Note: {caption}")
                        form.add_field("parse_mode", "Markdown")
                        form.add_field("reply_markup", json.dumps(admin_markup))
                        
                        async with session.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto", data=form):
                            pass
                            
                        await send_msg(session, chat_id, "⏳ فیش واریز شما دریافت شد و در صف بررسی واحد مالی قرار گرفت.")
                        
                    elif text.startswith("/start"):
                        welcome_text = (
                            f"🌟 *خوش آمدید {first_name} به سامانه معاملاتی الیت!*\n\n"
                            f"💵 *هزینه لایسنس کامل سورس‌کد:* تنها `10$`\n\n"
                            f"👇 مبلغ را به ولت‌های کانال واریز کرده و اسکرین‌شات رسید را همین‌جا ارسال کنید."
                        )
                        await send_msg(session, chat_id, welcome_text)

            except Exception as e:
                logger.error(f"Listener error: {e}")
                await asyncio.sleep(5)

# ==========================================
# سرور وب Keep-Alive روی پورت 8080
# ==========================================
async def handle_ping(request):
    return web.Response(text="Elite Quantum Bot is active 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Keep-alive web server running on port {port}")

# ==========================================
# اجرای هسته مرکزی موازی
# ==========================================
async def main():
    init_db()
    logger.info("Elite system online. Running parallel loops & web server...")
    await asyncio.gather(
        start_web_server(),
        broadcast_elite_signals(),
        run_elite_listener()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System stopped safely.")
