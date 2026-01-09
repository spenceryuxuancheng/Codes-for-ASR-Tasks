#!/usr/bin/env python3
import os
import sys
from mutagen.mp3 import MP3

def main():
    # 指定文件夹路径
    folder = '/Users/SSSPR/Documents/Angel_Chan/NLM_English/Alignment_Input'
    
    if not os.path.exists(folder):
        print(f"错误: 文件夹不存在 {folder}")
        sys.exit(1)
    
    total = 0
    count = 0
    
    print("搜索音频文件...")
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(('.mp3', '.wav')):
                full_path = os.path.join(root, f)
                print(f"找到: {f}")
                
                try:
                    if f.lower().endswith('.mp3'):
                        audio = MP3(full_path)
                    else:
                        from mutagen.wave import WAVE
                        audio = WAVE(full_path)
                    
                    duration = audio.info.length
                    total += duration
                    count += 1
                    print(f"  时长: {duration:.1f}秒")
                    
                except Exception as e:
                    print(f"  读取失败: {e}")
    
    if count == 0:
        print("未找到任何音频文件！")
        print("支持的格式: .mp3, .wav")
    else:
        print(f"\n总计:")
        print(f"文件数量: {count}")
        print(f"总时长: {total:.2f}秒")
        print(f"总时长: {total/60:.2f}分钟")
        print(f"总时长: {total/3600:.2f}小时")

if __name__ == "__main__":
    main()