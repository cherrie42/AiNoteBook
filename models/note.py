from datetime import datetime

class Note:
    def __init__(self, title, content, category="默认", created_at=None):
        self.title = title
        self.content = content
        self.category = category
        self.created_at = created_at or datetime.now()