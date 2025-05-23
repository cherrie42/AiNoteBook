from models.note import Note
from services.note_manager import NoteManager
from services.note_ai import NoteAI

def main():
    # 更新为你的API凭据
    appid = "2fb081ac"
    api_secret = "YWRmODg3YzE1MDQ4YWRhMDkyNWNlYjll"
    api_key = "a333dae3b265d577d4f2ac430e6ed782"
    
    note_manager = NoteManager()
    note_ai = NoteAI(note_manager, appid, api_key, api_secret)

    while True:
        print("\n=== AI笔记助手 ===")
        print("1. 创建新笔记")
        print("2. 查看所有笔记")
        print("3. 分析笔记")
        print("4. 获取写作建议")
        print("5. 退出")
        
        choice = input("\n请选择操作 (1-5): ")
        
        if choice == "1":
            title = input("请输入笔记标题: ")
            content = input("请输入笔记内容: ")
            category = input("请输入笔记分类(直接回车默认为'默认'): ") or "默认"
            note = Note(title, content, category)
            note_manager.add_note(note)
            print("笔记已保存！")
            
        elif choice == "2":
            try:
                notes = note_manager.get_all_notes()
                if not notes:
                    print("暂无笔记！")
                else:
                    print("\n=== 所有笔记 ===")
                    for note in notes:
                        print(f"\nID: {note[0]}")
                        print(f"标题: {note[1]}")
                        print(f"内容: {note[2][:50]}..." if len(note[2]) > 50 else note[2])
                        print(f"分类: {note[3]}")
                        print(f"创建时间: {note[4]}")
                        print("-" * 30)
            except Exception as e:
                print(f"查看笔记时出错: {e}")
                
        elif choice == "3":
            note_id = input("请输入要分析的笔记ID: ")
            note = note_manager.get_note_by_id(note_id)
            if note:
                print("\n分析结果：")
                analysis = note_ai.analyze_note(note[2])
                print(analysis)
            else:
                print("未找到该笔记！")
                
        elif choice == "4":
            note_id = input("请输入要获取建议的笔记ID: ")
            note = note_manager.get_note_by_id(note_id)
            if note:
                print("\n写作建议：")
                suggestions = note_ai.suggest_improvements(note[2])
                print(suggestions)
            else:
                print("未找到该笔记！")
                
        elif choice == "5":
            print("感谢使用！再见！")
            break

if __name__ == "__main__":
    main()