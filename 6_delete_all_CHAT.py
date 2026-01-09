import os

print("🗑️  刪除 .cha 檔案工具")
print("=" * 50)

# 設定工作目錄
current_dir = os.path.join(os.getcwd(), "Recordings_mp3")
print(f"工作目錄: {current_dir}")
print()

# 統計變數
total_folders = 0
deleted_files = 0
folders_with_cha = []

# 遍歷當前目錄下的所有項目
for item in os.listdir(current_dir):
    item_path = os.path.join(current_dir, item)
    
    # 只處理資料夾
    if os.path.isdir(item_path):
        total_folders += 1
        cha_found = False
        
        print(f"📁 掃描: {item}/")
        
        # 處理資料夾中的檔案
        for filename in os.listdir(item_path):
            # 檢查是否為 .cha 檔案
            if filename.lower().endswith('.cha'):
                cha_found = True
                file_path = os.path.join(item_path, filename)
                
                try:
                    os.remove(file_path)
                    deleted_files += 1
                    print(f"  ✓ 已刪除: {filename}")
                except Exception as e:
                    print(f"  ✗ 錯誤刪除 {filename}: {e}")
        
        if cha_found:
            folders_with_cha.append(item)
        
        print()  # 空行分隔不同的資料夾

print("=" * 50)
print(f"📊 統計:")
print(f"  掃描的資料夾: {total_folders}")
print(f"  包含 .cha 檔案的資料夾: {len(folders_with_cha)}")
print(f"  刪除的 .cha 檔案: {deleted_files}")
print()

if deleted_files > 0:
    print("✅ 刪除完成!")
    if folders_with_cha:
        print("包含 .cha 檔案的資料夾:")
        for folder in folders_with_cha:
            print(f"  • {folder}")
else:
    print("ℹ️  沒有找到 .cha 檔案")

# 安全確認版本（如果擔心誤刪）
print("\n" + "=" * 50)
print("⚠️  安全提示: 刪除的檔案無法復原!")
print("如果需要預覽而不實際刪除，請使用以下選項:")
