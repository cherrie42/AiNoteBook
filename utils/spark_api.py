import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse, urlencode
import ssl
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import websocket

class Ws_Param:
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                               digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        return self.Spark_url + '?' + urlencode(v)

class SparkAPI:
    def __init__(self, appid, api_key, api_secret):
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.spark_url = "wss://spark-api.xf-yun.com/v1/x1"
        self.domain = "x1"
        self.answer = ""
        self.isFirstContent = True

    def on_message(self, ws, message):
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            text = choices['text'][0]
            if ('reasoning_content' in text and text['reasoning_content']):
                reasoning_content = text["reasoning_content"]
                print(reasoning_content, end="")
                self.isFirstContent = True
            if('content' in text and text['content']):
                content = text["content"]
                if self.isFirstContent:
                    print("\n*******************以上为思维链内容，模型回复内容如下********************\n")
                    self.isFirstContent = False
                print(content, end="")
                self.answer += content
            if status == 2:
                ws.close()

    def ask_question(self, messages):
        self.answer = ""
        wsParam = Ws_Param(self.appid, self.api_key, self.api_secret, self.spark_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(
            wsUrl,
            on_message=self.on_message,
            on_error=lambda ws, error: print("### error:", error),
            on_close=lambda ws, one, two: print(" "),
            on_open=lambda ws: thread.start_new_thread(
                lambda: ws.send(json.dumps({
                    "header": {
                        "app_id": self.appid
                    },
                    "parameter": {
                        "chat": {
                            "domain": self.domain,
                            "temperature": 0.5,
                            "max_tokens": 4096
                        }
                    },
                    "payload": {
                        "message": {
                            "text": messages
                        }
                    }
                })),
                ()
            )
        )
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return self.answer