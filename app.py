import base64
from flask import Flask, send_file, jsonify
from flask_sock import Sock
from time import sleep
from voice_recognition import VoiceRecognition
from loguru import logger

popup_flag = False
app = Flask(__name__)
sock = Sock(app)

img = 'vaultboy.png'
@app.route('/' + img)
def serve_img():
    return send_file(img, mimetype='image/png')

@app.route('/')
def main_page():
    with open('frontend.html') as f:
        return f.read()

@sock.route('/popup')
def echo(sock):
    try:
        VoiceRecognition('Microphone (NVIDIA Broadcast)', 
            grammar=['test', 'archlinux', '[unk]']
            ).run(lambda: sock.send("true"))
    except Exception as e:
        logger.info('connection terminated: %s' % e)
        sock.close()

if __name__ == '__main__':
    logger.info("starting the webserver...")
    app.run(host='127.0.0.1', port=5000)