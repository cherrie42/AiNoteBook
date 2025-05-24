import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread

class SpeechService:
    def __init__(self, app_id, api_key, api_secret):
        self.APPID = app_id
        self.APIKey = api_key
        self.APISecret = api_secret
        self.url = 'wss://ws-api.xfyun.cn/v2/iat'
        self.result_text = ""

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                               digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        return self.url + '?' + urlencode(v)

    def on_message(self, ws, message):
        try:
            result = json.loads(message)
            if result["code"] != 0:
                print(f"错误信息: {result['message']}")
                return
            
            data = result["data"]["result"]["ws"]
            for i in data:
                for w in i["cw"]:
                    self.result_text += w["w"]
            
        except Exception as e:
            print("解析消息异常:", str(e))

    def on_open(self, ws, audio_file):
        def run(*args):
            frameSize = 8000
            status = 0
            
            with open(audio_file, 'rb') as fp:
                while True:
                    buf = fp.read(frameSize)
                    if not buf:
                        status = 2
                    
                    if status == 0:
                        d = {
                            "common": {"app_id": self.APPID},
                            "business": {
                                "language": "zh_cn",
                                "domain": "iat",
                                "accent": "mandarin",
                                "vad_eos": 10000,
                                "dwa": "wpgs",        # 开启动态修正
                                "pd": "edu",          # 教育领域
                                "ptt": 0,             # 标点符号
                                "rlang": "zh-cn",     # 中文
                                "vinfo": 1            # 返回详细信息
                            },
                            "data": {
                                "status": 0,
                                "format": "audio/L16;rate=16000",
                                "encoding": "raw",
                                "audio": str(base64.b64encode(buf), 'utf-8')
                            }
                        }
                        ws.send(json.dumps(d))
                        status = 1
                    elif status == 1:
                        d = {
                            "data": {
                                "status": 1,
                                "format": "audio/L16;rate=16000",
                                "encoding": "raw",
                                "audio": str(base64.b64encode(buf), 'utf-8')
                            }
                        }
                        ws.send(json.dumps(d))
                    elif status == 2:
                        d = {
                            "data": {
                                "status": 2,
                                "format": "audio/L16;rate=16000",
                                "encoding": "raw",
                                "audio": str(base64.b64encode(buf), 'utf-8')
                            }
                        }
                        ws.send(json.dumps(d))
                        time.sleep(1)
                        break
                    time.sleep(0.04)
            ws.close()
        thread.start_new_thread(run, ())

    def on_error(self, ws, error):
        print("Error occurred:", error)
        self.result_text = ""

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed")

    def recognize_speech(self, audio_file):
        try:
            self.result_text = ""
            websocket.enableTrace(False)
            wsUrl = self.create_url()
            
            ws = websocket.WebSocketApp(
                wsUrl,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            ws.on_open = lambda ws: self.on_open(ws, audio_file)
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            return self.result_text if self.result_text else None
            
        except Exception as e:
            print("Speech recognition error:", str(e))
            return None