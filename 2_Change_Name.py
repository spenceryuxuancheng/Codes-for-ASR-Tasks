import os

print("🎵 音频文件重命名工具")
print("=" * 50)

# 显示当前目录
current_dir = os.path.join(os.getcwd(),"Alignment_Input")
print(f"工作目录: {current_dir}")
print()

# 统计变量
total_files = 0
renamed_files = 0

# 遍历当前目录下的所有项目
for item in os.listdir(current_dir):
    item_path = os.path.join(current_dir, item)
    
    # 只处理文件夹
    if os.path.isdir(item_path):
        print(f"📁 处理: {item}/")
        
        # 处理文件夹中的文件
        for filename in os.listdir(item_path):
            # 处理  文件
            if filename.lower().endswith('.cha') or filename.lower().endswith('.mp3'):
                total_files += 1
                
                # 检查是否包含空格
                if 'ENGNLM' in filename:
                    # 创建新文件名
                    new_name = filename.replace('ENGNLM', 'Eng_NLM')
                    
                    # 完整路径
                    old_path = os.path.join(item_path, filename)
                    new_path = os.path.join(item_path, new_name)
                    
                    # 重命名文件
                    try:
                        os.rename(old_path, new_path)
                        renamed_files += 1
                        print(f"  ✓ {filename} → {new_name}")
                    except Exception as e:
                        print(f"  ✗ 错误: {filename} - {e}")
        
        print()  # 空行分隔不同的文件夹

print("=" * 50)
print(f"📊 统计:")
print(f"  找到的文件: {total_files}")
print(f"  重命名的文件: {renamed_files}")
print()

if renamed_files == 0 and total_files > 0:
    print("✅ 所有文件名都已符合要求")
elif renamed_files > 0:
    print(f"✅ 成功重命名 {renamed_files} 个文件")
else:
    print("ℹ️  没有找到文件")
