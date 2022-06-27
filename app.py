import base64
from flask import Flask, send_file, jsonify
from voice_recognition import VoiceRecognition

# class OverlayServer:
#     def __init__(self, img_path):
#         self.img_path = img_path
#         self.

popup_flag = False
app = Flask(__name__)
# vr = VoiceRecognition('Microphone (NVIDIA Broadcast)', grammar="[\"test\", \"[unk]\"]")

img = 'vaultboy.png'
@app.route('/' + img)
def serve_img():
    return send_file(img, mimetype='image/png')

@app.route('/')
def main_page():
    with open('frontend.html') as f:
        return f.read()

@app.route('/popup')
def serve_flag():
    global popup_flag
    if popup_flag:
        popup_flag = False
        return "true"
    return "false"

@app.route('/trigger')
def change_flag():
    global popup_flag
    popup_flag = True
    return ''
        
if __name__ == '__main__':
    # OverlayServer('vaultboy.png').run()
    app.run(host='0.0.0.0', port=5000)