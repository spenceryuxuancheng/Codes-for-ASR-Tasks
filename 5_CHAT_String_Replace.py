import re
from pathlib import Path
from difflib import SequenceMatcher

def find_closest_match(target_name, mp3_names):
    """找到与目标名称最接近的MP3文件名"""
    best_match = None
    best_ratio = 0
    
    for mp3_name in mp3_names:
        # 先尝试简单清理和标准化
        target_clean = target_name.lower().replace('_', '').replace('-', '')
        mp3_clean = mp3_name.lower().replace('_', '').replace('-', '')
        
        # 使用SequenceMatcher计算相似度
        ratio = SequenceMatcher(None, target_clean, mp3_clean).ratio()
        
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = mp3_name
            
        # 如果完全匹配（忽略大小写和下划线）
        if target_clean == mp3_clean:
            return mp3_name  # 立即返回完全匹配
    
    # 如果相似度超过阈值，返回最佳匹配
    if best_ratio > 0.6:  # 60%相似度阈值
        return best_match
    
    return None

def update_chat_files(folder_path):
    """批量修改指定文件夹中所有子文件夹的CHAT文件的前10行"""
    folder = Path(folder_path)
    
    # 遍历文件夹中的所有子文件夹
    for subfolder in folder.iterdir():
        if not subfolder.is_dir():
            continue  # 跳过非文件夹项
            
        print(f"\n处理文件夹: {subfolder.name}")
        
        # 查找当前子文件夹中的所有MP3文件
        mp3_names = []
        for mp3_file in subfolder.glob("*.mp3"):
            mp3_names.append(mp3_file.stem)
        
        if not mp3_names:
            print(f"  警告: 在 {subfolder.name} 中未找到MP3文件")
            continue
        
        print(f"  找到MP3文件: {', '.join(mp3_names)}")
        
        # 遍历当前子文件夹中的所有CHAT文件
        chat_updated = 0
        for chat_file in subfolder.glob("*.cha"):
            # 读取文件内容
            try:
                with open(chat_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"  无法读取文件: {chat_file.name} - {e}")
                continue
            
            modified = False
            
            # 只处理前10行
            for i in range(min(10, len(lines))):
                # 查找包含@Media: 的行
                if "@Media:" in lines[i]:
                    # 提取@Media: 和, audio之间的所有内容
                    pattern = r'@Media:\s*(.+?),\s*audio'
                    match = re.search(pattern, lines[i])
                    
                    if match:
                        original_name = match.group(1).strip()
                        
                        # 找到最匹配的MP3文件名
                        closest_mp3 = find_closest_match(original_name, mp3_names)
                        
                        if closest_mp3:
                            # 构建新的字符串
                            new_line = re.sub(
                                r'(@Media:\s*).+?(\s*,\s*audio)',
                                rf'\g<1>{closest_mp3}\g<2>',
                                lines[i]
                            )
                            
                            lines[i] = new_line
                            modified = True
                            print(f"  {chat_file.name}: 将 '{original_name}' 替换为 '{closest_mp3}'")
                            break  # 找到并修改后跳出循环
                        else:
                            print(f"  {chat_file.name}: 未找到匹配的MP3文件（原值: '{original_name}'）")
                            break
            
            # 如果有修改，写回文件
            if modified:
                try:
                    with open(chat_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    chat_updated += 1
                except Exception as e:
                    print(f"  无法写入文件: {chat_file.name} - {e}")
        
        print(f"  完成: 在 {subfolder.name} 中更新了 {chat_updated} 个CHAT文件")

# 使用示例
if __name__ == "__main__":
    # 替换为你的文件夹路径
    folder_path = "/Users/SSSPR/Documents/Angel_Chan/NLM_English/Alignment_Input"
    update_chat_files(folder_path)