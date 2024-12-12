import imaplib
import email
import re
import time
import datetime
import pytz
from email.utils import parsedate_to_datetime

def get_code(login, password, imap_url):
    for i in range(3):
        try:
            imap = imaplib.IMAP4_SSL(imap_url, timeout=60)
            imap.login(login, password)
        except:
            time.sleep(5)
    try:
        imap.select("inbox")
    except:
        return 0

    try:

        status, messages = imap.search(None, '(OR FROM "noreply@mailer2.okx.com" FROM "noreply@mailer1.okx.com")')
        messages = messages[0].split(b' ')

        messages = messages[-1:]

        code = 0

        for msg_num in messages:
            _, msg_data = imap.fetch(msg_num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            date_str = msg.get("Date")
            if date_str:
                email_date = parsedate_to_datetime(date_str)
                email_date = email_date.astimezone(pytz.utc)
                current_date = datetime.datetime.now(pytz.utc)
                diff = (current_date - email_date).total_seconds()
                if diff < 1200:
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/html":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    code_pattern = re.compile(r'(\d{6})<\/div>')
                    match = code_pattern.search(body)
                    if match:
                        code = match.group(1)
                        break
                    else:
                        pass
    except:
        try:
            code = get_code_again(login, password, imap_url)
        except:
            code = 0

    imap.close()
    imap.logout()

    return code


def get_code_again(login, password, imap_url):
    for i in range(3):
        try:
            imap = imaplib.IMAP4_SSL(imap_url, timeout=60)
            imap.login(login, password)
            break  # Exit the loop if login is successful
        except:
            time.sleep(5)

    try:
        imap.select("inbox")
    except:
        return 0

    status, messages = imap.search(None, 'ALL')
    messages = messages[0].split(b' ')

    messages = messages[-1:]
    code = 0

    for msg_num in messages:
        try:
            res, msg_data = imap.fetch(msg_num, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            date_str = msg.get("Date")
            FROM_STR = msg.get("From")
            if FROM_STR not in ["OKX <noreply@mailer2.okx.com>", "OKX <noreply@mailer1.okx.com>", "OKX <noreply@mailer.okx.com>"]:
                continue
            if date_str:
                email_date = parsedate_to_datetime(date_str)
                email_date = email_date.astimezone(pytz.utc)
                current_date = datetime.datetime.now(pytz.utc)
                diff = (current_date - email_date).total_seconds()
                if diff < 1200:
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/html":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    code_pattern = re.compile(r'(\d{6})<\/div>')
                    match = code_pattern.search(body)
                    if match:
                        code = match.group(1)
                        break
        except:
            pass

    imap.close()
    imap.logout()

    return code