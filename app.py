from flask import Flask, request, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from linebot import LineBotApi
from linebot.models import MessageEvent, TextMessage, TextSendMessage , ImageMessage, ImageSendMessage
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ImageMessage,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
)

import os
import tempfile
import cv2
import numpy as np
from ultralytics import YOLO
from yolo_predictions import SHARK



# Replace with your LINE Bot credentials
channel_secret = "xxxxxxxx"
channel_access_token = xxxxxxxxxxx"

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

model = SHARK('best.pt')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

@app.route("/webhook", methods=["GET", "POST"])
def home():
    try:
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)
        handler.handle(body, signature)
    except:
        pass

    return "Hello Line Chatbot"


@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    print("ได้รับข้อความรูปภาพจาก LINE")

    # ดึงข้อมูลรูปภาพ
    try:
        message_content = line_bot_api.get_message_content(event.message.id)
        print("ดึงภาพสมเร็จ")
    except Exception as e:
        print(f"ดึงข้อมูลภาพไม่สำเร็จ: {e}")
        return

    # บันทึกรูปภาพ
    static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp').replace("\\","/")
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='jpg' + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name
    dist_path = tempfile_path + '.jpg'  # เติมนามสกุลเข้าไปในชื่อไฟล์เป็น jpg-xxxxxx.jpg
    os.rename(tempfile_path, dist_path) # เปลี่ยนชื่อไฟล์ภาพเดิมที่ยังไม่มีนามสกุลให้เป็น jpg-xxxxxx.jpg

    filename_image = os.path.basename(dist_path) # ชื่อไฟล์ภาพ output (ชื่อเดียวกับ input)
    filename_fullpath = dist_path.replace("\\","/")   # เปลี่ยนเครื่องหมาย \ เป็น / ใน path เต็ม

    print("บันทึกรูปภาพ:", filename_fullpath)
    # ประมวลผลภาพ
    img = cv2.imread(filename_fullpath)
    model(filename_fullpath,img)
  

    # ส่งรูปภาพกลับไปยังผู้ใช้
    dip_url = request.host_url + os.path.join('static', 'tmp', filename_image).replace("\\","/")
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text='ประมวลผลภาพเรียบร้อยแล้ว'),
            ImageSendMessage(dip_url, dip_url)
        ]
    )
    
    

@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)

if __name__ == "__main__":          
    app.run()

