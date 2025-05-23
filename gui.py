import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from models.note import Note
from services.note_manager import NoteManager
from services.note_ai import NoteAI

class NoteBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI笔记助手")
        self.root.geometry("800x600")
        
        # 初始化API凭据
        self.appid = "2fb081ac"
        self.api_secret = "YWRmODg3YzE1MDQ4YWRhMDkyNWNlYjll"
        self.api_key = "a333dae3b265d577d4f2ac430e6ed782"
        
        # 初始化管理器
        self.note_manager = NoteManager()
        self.note_ai = NoteAI(self.note_manager, self.appid, self.api_key, self.api_secret)
        
        self.create_widgets()
        self.load_notes()

    def create_widgets(self):
        # 创建左右分栏
        left_frame = ttk.Frame(self.root, padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = ttk.Frame(self.root, padding="5")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 左侧笔记列表
        self.note_list = ttk.Treeview(left_frame, columns=("ID", "标题", "分类"), show="headings")
        self.note_list.heading("ID", text="ID")
        self.note_list.heading("标题", text="标题")
        self.note_list.heading("分类", text="分类")
        self.note_list.pack(fill=tk.BOTH, expand=True)
        self.note_list.bind("<<TreeviewSelect>>", self.on_select_note)
        
        # 右侧笔记详情和操作区
        note_frame = ttk.LabelFrame(right_frame, text="笔记详情", padding="5")
        note_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题输入
        ttk.Label(note_frame, text="标题:").pack(fill=tk.X)
        self.title_entry = ttk.Entry(note_frame)
        self.title_entry.pack(fill=tk.X)
        
        # 分类输入
        ttk.Label(note_frame, text="分类:").pack(fill=tk.X)
        self.category_entry = ttk.Entry(note_frame)
        self.category_entry.pack(fill=tk.X)
        
        # 内容输入
        ttk.Label(note_frame, text="内容:").pack(fill=tk.X)
        self.content_text = scrolledtext.ScrolledText(note_frame, height=10)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮区域
        button_frame = ttk.Frame(note_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="新建笔记", command=self.new_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存笔记", command=self.save_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="分析笔记", command=self.analyze_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="写作建议", command=self.get_suggestions).pack(side=tk.LEFT, padx=5)
        
        # AI分析结果显示区域
        ttk.Label(note_frame, text="AI分析结果:").pack(fill=tk.X)
        self.ai_result_text = scrolledtext.ScrolledText(note_frame, height=8)
        self.ai_result_text.pack(fill=tk.BOTH, expand=True)

    def load_notes(self):
        # 清空现有列表
        for item in self.note_list.get_children():
            self.note_list.delete(item)
        
        # 加载所有笔记
        notes = self.note_manager.get_all_notes()
        for note in notes:
            self.note_list.insert("", tk.END, values=(note[0], note[1], note[3]))

    def on_select_note(self, event):
        selection = self.note_list.selection()
        if selection:
            item = self.note_list.item(selection[0])
            note_id = item["values"][0]
            note = self.note_manager.get_note_by_id(note_id)
            if note:
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, note[1])
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(1.0, note[2])
                self.category_entry.delete(0, tk.END)
                self.category_entry.insert(0, note[3])

    def new_note(self):
        self.title_entry.delete(0, tk.END)
        self.content_text.delete(1.0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.ai_result_text.delete(1.0, tk.END)

    def save_note(self):
        title = self.title_entry.get()
        content = self.content_text.get(1.0, tk.END).strip()
        category = self.category_entry.get() or "默认"
        
        if not title or not content:
            messagebox.showwarning("警告", "标题和内容不能为空！")
            return
            
        note = Note(title, content, category)
        self.note_manager.add_note(note)
        self.load_notes()
        messagebox.showinfo("成功", "笔记保存成功！")

    def analyze_note(self):
        content = self.content_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "请先输入笔记内容！")
            return
            
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(1.0, "分析中...\n")
        self.root.update()
        
        analysis = self.note_ai.analyze_note(content)
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(1.0, analysis)

    def get_suggestions(self):
        content = self.content_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "请先输入笔记内容！")
            return
            
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(1.0, "生成建议中...\n")
        self.root.update()
        
        suggestions = self.note_ai.suggest_improvements(content)
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(1.0, suggestions)

def main():
    root = tk.Tk()
    app = NoteBookApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()