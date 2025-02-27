import hashlib
import secrets
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from env.env import CATEGORIES_MAPPING
import sys
import os
import datetime



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.env import SENDER_ADDRESS,PASSWORD

def get_category_id(label, categories_mapping=CATEGORIES_MAPPING):
    for category_id, category_label in categories_mapping.items():
        if category_label == label:
            return category_id
    return None  

def increment_hour(current_hour, increment):
    
    next_hour = (current_hour + increment) % 24
    return next_hour


def encrypt_password(password):
    password = password.encode('utf-8')  
    encrypted_passwd = hashlib.sha256(password).hexdigest()
    return encrypted_passwd

def is_empty(text):
    return text==None or text==''

def generate_otp():
    code = secrets.randbelow(900000) + 100000
    return code

def send_email(receiver_addr,subject,body):
    print('Hello guy')
    try:
        connection=SMTP('smtp.gmail.com',587)
        connection.starttls()
        
        msg = MIMEMultipart()
        msg['From'] = SENDER_ADDRESS
        msg['To'] = receiver_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        connection.login(user=SENDER_ADDRESS,password=PASSWORD)
        
        connection.sendmail(SENDER_ADDRESS, receiver_addr, msg.as_string())
        sent=True
    except Exception as e:
        print(e)
        sent=False
    finally:
        connection.quit()

    return sent

def format_source(name,author):
    if (name is None and author is None) or name is None:
        return "Source Unkown"
    
    if author is None:
        return name
    return f"{name} | {author}"
def format_duration(timestamp):
    if timestamp is None:
        return "(Time unknown)"    
    dt_object = datetime.datetime.fromtimestamp(timestamp)

    current_time = datetime.datetime.now()

    duration = current_time - dt_object

    days = duration.total_seconds() // 86400
    hours = (duration.total_seconds() % 86400) // 3600
    minutes = (duration.total_seconds() % 3600) // 60
    seconds = duration.total_seconds() % 60

    if days >= 1:
        formatted_duration = f"{int(days)}d"
    elif hours >= 1:
        formatted_duration = f"{int(hours)}h"
    elif minutes >= 1:
        formatted_duration = f"{int(minutes)}m"
    else:
        formatted_duration = f"{int(seconds)}s"

    return formatted_duration

if __name__=="__main__":
    pass
   
