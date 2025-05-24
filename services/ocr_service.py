from urllib import parse
import base64
import hashlib
import time
import requests
import json

class OCRService:
    def __init__(self, app_id, api_key):
        self.app_id = app_id
        self.api_key = api_key
        self.url = "http://webapi.xfyun.cn/v1/service/v1/ocr/handwriting"
        self.language = "cn|en"
        self.location = "false"

    def get_header(self):
        cur_time = str(int(time.time()))
        param = {"language": self.language, "location": self.location}
        param_base64 = base64.b64encode(json.dumps(param).encode('utf-8'))
        
        str1 = self.api_key + cur_time + str(param_base64, 'utf-8')
        m2 = hashlib.md5()
        m2.update(str1.encode('utf-8'))
        check_sum = m2.hexdigest()
        
        header = {
            'X-CurTime': cur_time,
            'X-Param': param_base64,
            'X-Appid': self.app_id,
            'X-CheckSum': check_sum,
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        }
        return header

    def get_body(self, filepath):
        with open(filepath, 'rb') as f:
            imgfile = f.read()
        data = {'image': str(base64.b64encode(imgfile), 'utf-8')}
        return data

    def recognize_handwriting(self, image_path):
        try:
            response = requests.post(
                self.url, 
                headers=self.get_header(), 
                data=self.get_body(image_path)
            )
            
            result = response.json()
            if result.get('code') == '0' and 'data' in result:
                text_results = []
                for block in result['data']['block']:
                    line_text = []
                    for line in block['line']:
                        if isinstance(line['word'], dict):
                            line_text.append(line['word'].get('content', ''))
                        elif isinstance(line['word'], str):
                            line_text.append(line['word'])
                        elif isinstance(line['word'], list):
                            for word in line['word']:
                                if isinstance(word, dict):
                                    line_text.append(word.get('content', ''))
                                else:
                                    line_text.append(str(word))
                    if line_text:
                        text_results.append(' '.join(line_text))
                return '\n'.join(text_results) if text_results else "未识别到文字"
            else:
                return f"识别失败: {result.get('desc', '未知错误')}"
                
        except Exception as e:
            return f"识别出错: {str(e)}"