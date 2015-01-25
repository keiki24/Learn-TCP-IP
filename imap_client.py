#!/usr/bin/env python
# -*- coding:utf-8 -*-

import smtplib
import email
import quopri
from email.parser import HeaderParser
from email.header import decode_header
from imaplib import IMAP4_SSL, IMAP4

from config import ConfigIMAP
conf = ConfigIMAP()

# Config
USER_ACCOUNT = conf.user
HOST = conf.host
PASSWORD = conf.pw
PORT_IMAP = conf.imap_port
MAILBOX = conf.mailbox

def get_email_bysubject(from_addr):
    Parser = HeaderParser()
    try:
        conn = IMAP4_SSL(HOST, PORT_IMAP)
        while True:
            conn.login(USER_ACCOUNT, PASSWORD)
            conn.select(MAILBOX)
            # SEARCHコマンドで指定したメールアドレスのみを取得
            typ, ids = conn.search(None, '(FROM "%s")' % from_addr)

            for email_id in ids[0].split():
                # 対象idのメールの全体をを解析せずに返す
                typ, raw_email = conn.fetch(email_id, '(RFC822)')
                msg = Parser.parsestr(raw_email[0][1])
                # Subjectを取得する
                subject, encoding = decode_header(msg.get('Subject'))[0]
                subject = subject.decode(encoding)
                # Bodyを取得する
                charset = msg.get_content_charset()
                body = unicode(msg.get_payload(decode=True), str(charset), "ignore").encode("utf-8", "replace")
                print body
    except IMAP4.error, e:
        print e
    finally:
        conn.close()
        conn.logout()

if __name__ == '__main__':
    # 取得したいメールのメールアドレスを指定する
    get_email_bysubject('whatyouwant@mail.co.com')
