#!/usr/bin/python
# -*- encoding: utf-8 -*-
import boto3
from boto3.session import Session
import os
import commands
import logging

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# linkchecker settings 
check_protocol = os.environ['CHECK_PROTOCOL']
check_url = os.environ['CHECK_URL']
check_option = os.environ['CHECK_OPTION']
target_url = check_protocol + "://" + check_url
upload_file = check_url + "/index.html"

# s3 settings
s3 = boto3.resource('s3')
bucket_name = os.environ['BUCKET_NAME']
obj = s3.Object(bucket_name,upload_file)

topic = os.environ['SNS_ARN']

# mail settings 
from_mail = os.environ['FROM_MAIL']
to_mail = os.environ['TO_MAIL']
smtp_host = os.environ['SMTP_HOST']
smtp_user = os.environ['SMTP_USER']
smtp_pass = os.environ['SMTP_PASS']

def handler():
	try:
		data = commands.getoutput("linkchecker -o html " + target_url + " " + check_option)
		response = obj.put(Body = data,
			ContentType='text/html',
			ACL='public-read')
		logger.info(response)

		index = data.find("0 warnings found. 0 errors found.")
		if index != -1:
			logger.info("Successful! Error was not found!")
		else:
			logger.info("http://" + bucket_name + ".s3-website-ap-northeast-1.amazonaws.com/" + check_url + "/")
			subject = '[WARN] ' +'サイトリンク切れ通知 [' + check_url + ']'
			header =   'サイトリンク切れを検知しました' + '\n\n' + '下記URLより結果を確認してください'   + '\n' 
			body =   "http://" + bucket_name + ".s3-website-ap-northeast-1.amazonaws.com/" + check_url + "/"
			footer = '\n\n'
			message = header + body + footer
			send_mail(subject, message)	

	except Exception, e:
		subject = '[ERROR] ' + check_url
		message = str(e)
		sns_publish(subject, message)

	logger.info("Complete!!")

def sns_publish(subject, message):
	sns = boto3.client('sns')
	response = sns.publish(
		TopicArn=topic,
		Message=message,
		Subject=subject
	)
	return

def send_mail(subject, message):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = from_mail
	msg['To'] = to_mail
	body_text = message
	msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

	s = smtplib.SMTP_SSL(smtp_host, 465)
	s.login(smtp_user, smtp_pass)
	s.sendmail( from_mail, [to_mail], msg.as_string() )
	s.close()
	return


handler()