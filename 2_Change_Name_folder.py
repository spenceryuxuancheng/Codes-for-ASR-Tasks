import os

print("📁 資料夾重命名工具")
print("=" * 50)

# 顯示當前目錄
current_dir = os.path.join(os.getcwd(), "Recordings_mp3")
print(f"工作目錄: {current_dir}")
print()

# 統計變數
total_folders = 0
renamed_folders = 0

# 獲取所有項目並排序，避免處理改名後的衝突
items = os.listdir(current_dir)
items.sort(reverse=True)  # 倒序處理，避免名稱衝突

# 遍歷當前目錄下的所有項目
for item in items:
    item_path = os.path.join(current_dir, item)
    
    # 只處理資料夾
    if os.path.isdir(item_path):
        total_folders += 1
        
        # 檢查資料夾名稱是否包含 "_Aligned"
        if '_Aligned' in item:
            # 創建新資料夾名稱
            new_name = item.replace('_Aligned', '')
            
            # 完整路徑
            old_path = item_path
            new_path = os.path.join(current_dir, new_name)
            
            # 檢查新名稱是否已存在
            if os.path.exists(new_path):
                print(f"  ⚠️  跳過: {item} → {new_name} (目標資料夾已存在)")
                continue
            
            # 重命名資料夾
            try:
                os.rename(old_path, new_path)
                renamed_folders += 1
                print(f"  ✓ {item} → {new_name}")
            except Exception as e:
                print(f"  ✗ 錯誤: {item} - {e}")
        else:
            print(f"  • {item} (無需修改)")

print("=" * 50)
print(f"📊 統計:")
print(f"  找到的資料夾: {total_folders}")
print(f"  重命名的資料夾: {renamed_folders}")
print()

if renamed_folders == 0 and total_folders > 0:
    print("✅ 所有資料夾名稱都已符合要求")
elif renamed_folders > 0:
    print(f"✅ 成功重命名 {renamed_folders} 個資料夾")
else:
    print("ℹ️  沒有找到資料夾")