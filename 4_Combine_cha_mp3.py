import os
import shutil

Checked_Transcripts = os.path.join(os.getcwd(), "Checked_Transcripts")
Recordings_mp3 = os.path.join(os.getcwd(), "Recordings_mp3")
Alignment_Input = os.path.join(os.getcwd(), "Alignment_Input")

# 確保輸出目錄存在
if not os.path.exists(Alignment_Input):
    os.makedirs(Alignment_Input)

# 獲取兩個來源資料夾中的所有文件夾（只包含目錄）
checked_folders = [
    folder_name for folder_name in os.listdir(Checked_Transcripts)
    if os.path.isdir(os.path.join(Checked_Transcripts, folder_name))
]

recording_folders = [
    folder_name for folder_name in os.listdir(Recordings_mp3)
    if os.path.isdir(os.path.join(Recordings_mp3, folder_name))
]

# 找出兩個資料夾中都存在的子資料夾名稱（交集）
common_folders = set(checked_folders) & set(recording_folders)

print("找到的同名子資料夾:")
for folder in common_folders:
    print(f"  • {folder}")
print()

# 遍歷每個共同的轉錄文件夾
for folder_name in common_folders:
    checked_source = os.path.join(Checked_Transcripts, folder_name)
    recording_source = os.path.join(Recordings_mp3, folder_name)
    target_folder = os.path.join(Alignment_Input, folder_name)
    
    print(f"處理資料夾: {folder_name}")
    
    # 檢查目標資料夾是否存在，不存在則創建
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"  創建目標資料夾: {target_folder}")
    
    # 複製 Checked_Transcripts 中的文件
    checked_files_copied = 0
    if os.path.exists(checked_source):
        for file in os.listdir(checked_source):
            source_file = os.path.join(checked_source, file)
            if os.path.isfile(source_file):
                shutil.copy2(source_file, target_folder)
                checked_files_copied += 1
        print(f"  從 Checked_Transcripts 複製了 {checked_files_copied} 個文件")
    
    # 複製 Recordings_mp3 中的文件
    recording_files_copied = 0
    if os.path.exists(recording_source):
        for file in os.listdir(recording_source):
            source_file = os.path.join(recording_source, file)
            if os.path.isfile(source_file):
                shutil.copy2(source_file, target_folder)
                recording_files_copied += 1
        print(f"  從 Recordings_mp3 複製了 {recording_files_copied} 個文件")
    
    total_copied = checked_files_copied + recording_files_copied
    print(f"  總共複製了 {total_copied} 個文件到 {folder_name}")
    print()

print("=" * 50)
print("轉錄文件合併完成")
print(f"已處理 {len(common_folders)} 個共同子資料夾")

# 檢查只存在於一個資料夾中的子資料夾（可選的警告信息）
only_in_checked = set(checked_folders) - set(recording_folders)
only_in_recordings = set(recording_folders) - set(checked_folders)

if only_in_checked:
    print(f"\n⚠️  以下資料夾只在 Checked_Transcripts 中存在，未處理:")
    for folder in only_in_checked:
        print(f"  • {folder}")

if only_in_recordings:
    print(f"\n⚠️  以下資料夾只在 Recordings_mp3 中存在，未處理:")
    for folder in only_in_recordings:
        print(f"  • {folder}")