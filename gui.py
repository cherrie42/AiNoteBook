import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
from models.note import Note
from services.note_manager import NoteManager
from services.note_ai import NoteAI
from tkinter import filedialog
from services.ocr_service import OCRService
from services.speech_service import SpeechService
from services.ppt_service import PPTService

class NoteBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI笔记助手")
        
        # 设置全屏
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.state('zoomed')  # Windows下设置最大化
        
        # 设置主题样式
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#2196f3")
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TLabelframe", background="#f5f5f5")
        style.configure("Treeview", rowheight=25, font=('Arial', 10))
        
        # 初始化API凭据
        self.appid = "2fb081ac"
        self.api_secret = "YWRmODg3YzE1MDQ4YWRhMDkyNWNlYjll"
        self.api_key = "a333dae3b265d577d4f2ac430e6ed782"
        
        # 初始化管理器
        self.note_manager = NoteManager()
        self.note_ai = NoteAI(self.note_manager, self.appid, self.api_key, self.api_secret)
        
        # 初始化OCR服务
        self.ocr_service = OCRService("2fb081ac", "819552254d36ebe8d6c0ed5ffbfd638a")
        
        # 初始化语音服务
        self.speech_service = SpeechService(self.appid, self.api_key, self.api_secret)
        
        # 初始化PPT服务
        self.ppt_service = PPTService()
        
        self.create_widgets()
        self.load_notes()

    def create_widgets(self):
        # 创建主分栏
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板
        left_frame = ttk.Frame(main_paned, padding="5")
        main_paned.add(left_frame, weight=1)
        
        # 搜索框
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_notes)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT, padx=5)
        
        # 笔记列表
        list_frame = ttk.LabelFrame(left_frame, text="笔记列表", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.note_list = ttk.Treeview(list_frame, columns=("ID", "标题", "分类", "时间"), show="headings")
        self.note_list.heading("ID", text="ID")
        self.note_list.heading("标题", text="标题")
        self.note_list.heading("分类", text="分类")
        self.note_list.heading("时间", text="创建时间")
        
        # 添加选择事件绑定
        self.note_list.bind("<<TreeviewSelect>>", self.on_select_note)
        # 设置列宽
        self.note_list.column("ID", width=50)
        self.note_list.column("标题", width=150)
        self.note_list.column("分类", width=100)
        self.note_list.column("时间", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.note_list.yview)
        self.note_list.configure(yscrollcommand=scrollbar.set)
        
        self.note_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右侧面板
        right_frame = ttk.Frame(main_paned, padding="5")
        main_paned.add(right_frame, weight=2)
        
        # 笔记详情区
        note_frame = ttk.LabelFrame(right_frame, text="笔记详情", padding="5")
        note_frame.pack(fill=tk.BOTH, expand=True)
        
        # 工具栏
        toolbar = ttk.Frame(note_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # 将按钮分组显示
        basic_tools = ttk.LabelFrame(toolbar, text="基本操作", padding="5")
        basic_tools.pack(side=tk.LEFT, fill=tk.X, padx=5)
        
        ttk.Button(basic_tools, text="📝 新建", command=self.new_note).pack(side=tk.LEFT, padx=2)
        ttk.Button(basic_tools, text="💾 保存", command=self.save_note).pack(side=tk.LEFT, padx=2)
        ttk.Button(basic_tools, text="🗑️ 删除", command=self.delete_note).pack(side=tk.LEFT, padx=2)
        
        ai_tools = ttk.LabelFrame(toolbar, text="AI功能", padding="5")
        ai_tools.pack(side=tk.LEFT, fill=tk.X, padx=5)
        
        ttk.Button(ai_tools, text="🤖 分析", command=self.analyze_note).pack(side=tk.LEFT, padx=2)
        ttk.Button(ai_tools, text="💡 建议", command=self.get_suggestions).pack(side=tk.LEFT, padx=2)
        ttk.Button(ai_tools, text="✨ 生成", command=self.generate_note).pack(side=tk.LEFT, padx=2)
        
        import_tools = ttk.LabelFrame(toolbar, text="导入工具", padding="5")
        import_tools.pack(side=tk.LEFT, fill=tk.X, padx=5)
        
        ttk.Button(import_tools, text="📷 识图", command=self.recognize_handwriting).pack(side=tk.LEFT, padx=2)
        ttk.Button(import_tools, text="🎤 语音", command=self.recognize_speech).pack(side=tk.LEFT, padx=2)
        ttk.Button(import_tools, text="📊 PPT", command=self.import_ppt).pack(side=tk.LEFT, padx=2)
        
        # 笔记信息区
        info_frame = ttk.Frame(note_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        # 标题和分类放在同一行
        title_frame = ttk.Frame(info_frame)
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="标题:").pack(side=tk.LEFT)
        self.title_entry = ttk.Entry(title_frame)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        
        ttk.Label(title_frame, text="分类:").pack(side=tk.LEFT)
        self.category_entry = ttk.Entry(title_frame, width=20)
        self.category_entry.pack(side=tk.LEFT, padx=5)
        
        # 内容区域
        content_frame = ttk.Frame(note_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 使用Notebook来组织内容和AI分析结果
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 内容页
        content_page = ttk.Frame(notebook)
        notebook.add(content_page, text="📝 笔记内容")
        
        self.content_text = scrolledtext.ScrolledText(content_page, wrap=tk.WORD, font=('Arial', 11))
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # AI分析页
        ai_page = ttk.Frame(notebook)
        notebook.add(ai_page, text="🤖 AI分析")
        
        self.ai_result_text = scrolledtext.ScrolledText(ai_page, wrap=tk.WORD, font=('Arial', 11))
        self.ai_result_text.pack(fill=tk.BOTH, expand=True)

    def filter_notes(self, *args):
        search_text = self.search_var.get().lower()
        self.load_notes(search_text)

    def load_notes(self, search_text=""):
        # 清空现有列表
        for item in self.note_list.get_children():
            self.note_list.delete(item)
        
        try:
            # 加载笔记
            notes = self.note_manager.get_all_notes()
            for note in notes:
                # 确保所有字段都存在
                note_id = note[0] if len(note) > 0 else ""
                title = note[1] if len(note) > 1 else ""
                category = note[3] if len(note) > 3 else "默认"
                created_time = note[4][:19] if len(note) > 4 and note[4] else ""
                
                # 搜索过滤
                if search_text.lower() in str(title).lower() or search_text.lower() in str(category).lower():
                    self.note_list.insert("", tk.END, values=(note_id, title, category, created_time))
        except Exception as e:
            messagebox.showerror("错误", f"加载笔记失败：{str(e)}")

    def on_select_note(self, event):
        try:
            selection = self.note_list.selection()
            if not selection:
                return
                
            item = self.note_list.item(selection[0])
            note_id = item["values"][0]
            
            # 获取笔记详情
            note = self.note_manager.get_note_by_id(note_id)
            if not note:
                messagebox.showwarning("警告", "未找到选中的笔记")
                return
                
            # 更新界面显示
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, note[1])  # 标题
            
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, note[2])  # 内容
            
            self.category_entry.delete(0, tk.END)
            self.category_entry.insert(0, note[3])  # 分类
            
            # 清空AI分析结果
            self.ai_result_text.delete(1.0, tk.END)
            
            # 切换到笔记内容标签页
            for child in self.root.winfo_children():
                if isinstance(child, ttk.PanedWindow):
                    for frame in child.winfo_children():
                        for widget in frame.winfo_children():
                            if isinstance(widget, ttk.LabelFrame):
                                for content_frame in widget.winfo_children():
                                    if isinstance(content_frame, ttk.Frame):
                                        for notebook in content_frame.winfo_children():
                                            if isinstance(notebook, ttk.Notebook):
                                                notebook.select(0)
                                                
        except Exception as e:
            messagebox.showerror("错误", f"加载笔记详情失败：{str(e)}")

    def new_note(self):
        # 清除当前选中的笔记
        for item in self.note_list.selection():
            self.note_list.selection_remove(item)
        
        # 清空输入框
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
        
        try:
            # 检查是否在编辑已有笔记
            selection = self.note_list.selection()
            if selection:
                item = self.note_list.item(selection[0])
                note_id = item["values"][0]
                # 更新已有笔记
                self.note_manager.update_note(note_id, title, content, category)
                message = "笔记更新成功！"
            else:
                # 创建新笔记
                note = Note(title, content, category)
                self.note_manager.add_note(note)
                message = "笔记保存成功！"
            
            self.load_notes()
            messagebox.showinfo("成功", message)
            
        except Exception as e:
            messagebox.showerror("错误", f"保存笔记失败：{str(e)}")

    def analyze_note(self):
        content = self.content_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "请先输入笔记内容！")
            return
            
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(1.0, "分析中...\n")
        self.root.update()
        
        # 创建分析线程
        import threading
        def analysis_thread():
            try:
                analysis = self.note_ai.analyze_note(content)
                # 使用 after 方法在主线程中更新 UI
                self.root.after(0, lambda: self.update_analysis_result(analysis))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"分析失败：{str(e)}"))
        
        thread = threading.Thread(target=analysis_thread)
        thread.daemon = True
        thread.start()

    def update_analysis_result(self, analysis):
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
        
        def suggestions_thread():
            try:
                suggestions = self.note_ai.suggest_improvements(content)
                self.root.after(0, lambda: self.update_analysis_result(suggestions))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"生成建议失败：{str(e)}"))
        
        thread = threading.Thread(target=suggestions_thread)
        thread.daemon = True
        thread.start()
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(1.0, suggestions)

    def recognize_handwriting(self):
        file_path = filedialog.askopenfilename(
            title="选择手写图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            self.ai_result_text.delete(1.0, tk.END)
            self.ai_result_text.insert(1.0, "正在识别中...\n")
            self.root.update()
            
            result = self.ocr_service.recognize_handwriting(file_path)
            
            if result:
                self.content_text.insert(tk.END, "\n" + result)
                self.ai_result_text.delete(1.0, tk.END)
                self.ai_result_text.insert(1.0, "识别完成！结果已添加到笔记内容中。")
            else:
                self.ai_result_text.delete(1.0, tk.END)
                self.ai_result_text.insert(1.0, "识别失败，请重试。")

    def recognize_speech(self):
        file_path = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[("音频文件", "*.wav")]
        )
        
        if file_path:
            self.ai_result_text.delete(1.0, tk.END)
            self.ai_result_text.insert(1.0, "正在识别语音...\n")
            self.root.update()
            
            result = self.speech_service.recognize_speech(file_path)
            
            if result:
                self.content_text.insert(tk.END, "\n" + result)
                self.ai_result_text.delete(1.0, tk.END)
                self.ai_result_text.insert(1.0, "语音识别完成！结果已添加到笔记内容中。")
            else:
                self.ai_result_text.delete(1.0, tk.END)
                self.ai_result_text.insert(1.0, "语音识别失败，请重试。")

    def import_ppt(self):
        file_path = filedialog.askopenfilename(
            title="选择PPT文件",
            filetypes=[("PPT文件", "*.pptx *.ppt")]
        )
        
        if file_path:
            self.ai_result_text.delete(1.0, tk.END)
            self.ai_result_text.insert(1.0, "正在解析PPT...\n")
            self.root.update()
            
            ppt_text = self.ppt_service.extract_text(file_path)
            if ppt_text:
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(1.0, ppt_text)
                self.ai_result_text.delete(1.0, tk.END)
                self.ai_result_text.insert(1.0, "PPT解析完成！")
            else:
                self.ai_result_text.delete(1.0, tk.END)
                self.ai_result_text.insert(1.0, "PPT解析失败，请重试。")

    def generate_note(self):
        content = self.content_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "请先输入或导入内容！")
            return
            
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(1.0, "正在生成笔记...\n")
        self.root.update()
        
        import threading
        def generation_thread():
            try:
                structured_note = self.note_ai.generate_structured_note(content)
                tags = self.note_ai.extract_tags(content)
                
                def update_ui():
                    if structured_note:
                        self.content_text.delete(1.0, tk.END)
                        self.content_text.insert(1.0, structured_note)
                        self.ai_result_text.delete(1.0, tk.END)
                        self.ai_result_text.insert(1.0, f"笔记生成完成！\n推荐标签：{tags}")
                    else:
                        self.ai_result_text.delete(1.0, tk.END)
                        self.ai_result_text.insert(1.0, "笔记生成失败，请重试。")
                
                self.root.after(0, update_ui)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"生成笔记失败：{str(e)}"))
        
        thread = threading.Thread(target=generation_thread)
        thread.daemon = True
        thread.start()

    def delete_note(self):
        selection = self.note_list.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的笔记！")
            return
            
        if not messagebox.askyesno("确认", "确定要删除选中的笔记吗？"):
            return
            
        try:
            item = self.note_list.item(selection[0])
            note_id = item["values"][0]
            
            # 删除笔记
            self.note_manager.delete_note(note_id)
            
            # 清空输入框
            self.new_note()
            
            # 刷新笔记列表
            self.load_notes()
            
            messagebox.showinfo("成功", "笔记删除成功！")
            
        except Exception as e:
            messagebox.showerror("错误", f"删除笔记失败：{str(e)}")