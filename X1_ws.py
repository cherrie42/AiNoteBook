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

# 更新API凭据
APPID = "2fb081ac"
APISecret = "YWRmODg3YzE1MDQ4YWRhMDkyNWNlYjll"
APIKey = "a333dae3b265d577d4f2ac430e6ed782"
Spark_url = "wss://spark-api.xf-yun.com/v1/x1"

class Ws_Param:
    def __init__(self):
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

def get_answer(message):
    answer = ""
    isFirstContent = True
    
    def on_message(ws, message):
        nonlocal answer, isFirstContent
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
                isFirstContent = True
            if('content' in text and text['content']):
                content = text["content"]
                if isFirstContent:
                    print("\n*******************以上为思维链内容，模型回复内容如下********************\n")
                    isFirstContent = False
                print(content, end="")
                answer += content
            if status == 2:
                ws.close()

    def on_error(ws, error):
        print("### error:", error)

    def on_close(ws, close_status_code, close_msg):
        print("")

    def on_open(ws):
        data = {
            "header": {
                "app_id": APPID
            },
            "parameter": {
                "chat": {
                    "domain": "x1",
                    "temperature": 0.5,
                    "max_tokens": 4096
                }
            },
            "payload": {
                "message": {
                    "text": message
                }
            }
        }
        ws.send(json.dumps(data))

    wsParam = Ws_Param()
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(
        wsUrl,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return answer


# 管理对话历史，按序编为列表
def getText(text,role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

# 获取对话中的所有角色的content长度
def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

# 判断长度是否超长，当前限制8K tokens
def checklen(text):
    while (getlength(text) > 11000):
        del text[0]
    return text


#主程序入口
if __name__ =='__main__':
    # Remove the placeholder credentials and use the actual ones
    chatHistory = []
    while (1):
        Input = input("\n" + "我:")
        question = checklen(getText(chatHistory,"user", Input))
        print("星火:", end="")
        getText(chatHistory,"assistant", get_answer(question))


