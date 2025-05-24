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
        
    def generate_structured_note(self, content, content_type="text"):
        """生成结构化笔记"""
        prompt = f"""请将以下{content_type}内容整理成结构化的学习笔记，包含以下部分：
1. 主要知识点概述
2. 关键概念解释
3. 重点内容详解
4. 知识点之间的关系
5. 相关标签
内容如下：
{content}"""
        
        messages = [{"role": "user", "content": prompt}]
        return self.spark_api.ask_question(messages)
        
    def extract_tags(self, content):
        """提取内容标签"""
        prompt = """请为以下内容提取5-8个关键标签，用逗号分隔：
        
        内容：
        {content}"""
        
        messages = [{"role": "user", "content": prompt}]
        return self.spark_api.ask_question(messages)