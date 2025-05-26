from tkinter import Tk
from gui import NoteBookApp

def main():
    # 创建主窗口
    root = Tk()
    # 初始化应用
    app = NoteBookApp(root)
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()