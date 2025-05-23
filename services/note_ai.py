from utils.spark_api import SparkAPI

class NoteAI:
    def __init__(self, note_manager, appid, api_key, api_secret):
        self.note_manager = note_manager
        self.spark_api = SparkAPI(appid, api_key, api_secret)

    def analyze_note(self, note_content):
        messages = [
            {"role": "user", "content": f"请分析并总结以下笔记内容：\n{note_content}"}
        ]
        return self.spark_api.ask_question(messages)

    def suggest_improvements(self, note_content):
        messages = [
            {"role": "user", "content": f"请为以下笔记内容提供改进建议：\n{note_content}"}
        ]
        return self.spark_api.ask_question(messages)