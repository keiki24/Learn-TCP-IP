#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
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

class IMAPP():

    def __init__(self, host, port=993):
        self.conn = IMAP4_SSL(host, port)
        self.parser = HeaderParser()

    # ログインする
    # メールボックスを選択する
    def login_select(self, account, password, mailbox):
        self.conn.login(account, password)
        self.conn.select(mailbox)

    # idを取得する
    def get_ids(self, query):
        # query = '(From "whoamailaddress")'
        typ, ids = self.conn.search(None, '(%s)' % query)

        return ids

    # 一つのidからメールを取得する
    def get_message(self, email_id):
        typ, raw_email = self.conn.fetch(email_id, '(RFC822)')
        msg = self.parser.parsestr(raw_email[0][1])

        return msg

    # Subjectを取得する
    def get_subject(self, msg):
        subject, encoding = decode_header(msg.get('Subject'))[0]
        subject = subject.decode(encoding)

        return subject

    def get_body(self, msg):
        default_charset = "iso-2022-jp"
        charset = msg.get_content_charset()
        if charset == None:
            charset = default_charset
        body = unicode(msg.get_payload(decode=True), str(charset), "ignore").encode("utf-8", "replace")

        return body

    # 対象のメールを取得する
    # メールからSubjectとbodyを抽出する
    def get_email_by_subject(self, from_addr):
        try:
            self.login_select(USER_ACCOUNT, PASSWORD, MAILBOX)
            ids = self.get_ids('FROM "%s"' % from_addr)

            email_body = []
            for email_id in ids[0].split():
                # 対象idのメールの全体をを解析せずに返す
                message = self.get_message(email_id)
                # Subjectを取得する
                subject = self.get_subject(message)
                # Bodyを取得する
                body = self.get_body(message)
                email_body.append(body)
            return email_body
        except IMAP4.error, e:
            print e
        finally:
            pass
            self.conn.close()
            self.conn.logout()

    # 未読メールを取得する
    def get_email_unseen(self):
        try:
            self.login_select(USER_ACCOUNT, PASSWORD, MAILBOX)
            ids = self.get_ids('UNSEEN')
            if len(ids[0]) == 0:
                print "There is no Unread email."
                return

            email_body = []
            for email_id in ids[0].split():
                message = self.get_message(email_id)
                # Subjectを取得する
                subject = self.get_subject(message)
                # Bodyを取得する
                body = self.get_body(message)
                email_body.append(body)
            return email_body
        except IMAP4.error, e:
            print e
        finally:
            self.conn.close()
            self.conn.logout()

    # 指定した日付以降のメールを取得する
    # e.g. get_email_since(25-Jan-2015)
    def get_email_since(self, date_since):
        try:
            self.login_select(USER_ACCOUNT, PASSWORD, MAILBOX)
            # SEARCHコマンドで指定した日付以降のメールを取得する
            query = '(SINCE %s)' % date_since
            ids = self.get_ids(query)
            if len(ids[0]) == 0:
                print "There is no email since %s." % date_since
                return

            email_body = []
            for email_id in ids[0].split():
                message = self.get_message(email_id)
                # Subjectを取得する
                subject = self.get_subject(message)
                # Bodyを取得する
                body = self.get_body(message)
                #print body
                email_body.append(body)
            return email_body
        except IMAP4.error, e:
            print e
        finally:
            self.conn.close()
            self.conn.logout()

if __name__ == '__main__':
    imap = IMAPP(HOST, PORT_IMAP)
    body = imap.get_email_by_subject('whatyouwant@mail.co.com')
    #body = imap.get_email_unseen()
    #body = imap.get_email_since("25-Jan-2015")
    if body is None:
        sys.exit(0)

    for b in body:
        print ".".join(body)
