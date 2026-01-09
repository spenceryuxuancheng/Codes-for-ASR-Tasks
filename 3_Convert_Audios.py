import os
import time
import subprocess

input_folder_name = "MAIN_Narrative"  # 輸入文件夾名稱
output_folder_name = "MAIN_Narrative_mp3"  # 輸出文件夾名稱

# 設置當前目錄
current_dir = os.path.join(os.getcwd(), input_folder_name)

# 1. 定義要處理的文件夾列表 - 掃描當前目錄下的所有子文件夾
input_folder_name_list = [f for f in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, f))]

# 顯示找到的文件夾
print(f"掃描到 {len(input_folder_name_list)} 個文件夾: {input_folder_name_list}")

# 2. 創建輸出根目錄
output_root = os.path.join(os.getcwd(), output_folder_name)
os.makedirs(output_root, exist_ok=True)  # 確保輸出文件夾存在

# 統計轉換數量
total_converted = 0
total_skipped = 0
total_failed = 0

# 支持的音頻格式列表
AUDIO_EXTENSIONS = [
    '.m4a', '.wav', '.aac', '.flac', '.ogg', '.wma',
    '.mp3', '.aiff', '.alac', '.opus', '.amr', '.mka'
]

def convert_audio_to_mp3(input_path, output_path):
    """使用 ffmpeg 將音頻文件轉換為 MP3 格式"""
    try:
        # 獲取文件擴展名
        file_ext = os.path.splitext(input_path)[1].lower()
        
        # 設置不同的轉換參數
        if file_ext in ['.wav', '.aiff', '.flac']:
            # 無損格式轉換，使用較高質量
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-codec:a', 'libmp3lame',
                '-qscale:a', '0',  # 最高質量
                '-loglevel', 'error',
                '-y',  # 覆蓋輸出文件
                output_path
            ]
            
        elif file_ext in ['.m4a', '.mp4', '.aac']:
            # 有損格式轉換，保持較好質量
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-codec:a', 'libmp3lame',
                '-b:a', '192k',  # 192kbps 比特率
                '-loglevel', 'error',
                '-y',
                output_path
            ]
            
        elif file_ext in ['.ogg', '.opus']:
            # OGG/Opus 格式轉換
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-codec:a', 'libmp3lame',
                '-qscale:a', '2',  # 較高質量
                '-loglevel', 'error',
                '-y',
                output_path
            ]
            
        elif file_ext == '.mp3':
            # 如果是 mp3 文件，直接複製（不重新編碼）
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-codec:a', 'copy',  # 直接複製
                '-loglevel', 'error',
                '-y',
                output_path
            ]
            
        else:
            # 通用處理方法
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-codec:a', 'libmp3lame',
                '-b:a', '160k',  # 默認比特率
                '-loglevel', 'error',
                '-y',
                output_path
            ]
        
        # 執行轉換命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  FFmpeg 錯誤: {e.stderr if e.stderr else str(e)}")
        return False
    except Exception as e:
        print(f"  音頻轉換失敗: {e}")
        return False

def get_audio_info(input_path):
    """獲取音頻文件信息"""
    try:
        # 使用 ffprobe 獲取詳細信息
        probe_cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name,channels,sample_rate,duration,bit_rate,tags:format=format_name',
            '-of', 'json',
            input_path
        ]
        
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            
            if 'streams' in data and len(data['streams']) > 0:
                stream = data['streams'][0]
                info = {
                    'codec': stream.get('codec_name', '未知').upper(),
                    'channels': stream.get('channels', '未知'),
                    'sample_rate': f"{stream.get('sample_rate', '未知')} Hz",
                    'duration': float(stream.get('duration', 0)),
                    'bitrate': int(stream.get('bit_rate', 0)) // 1000 if stream.get('bit_rate') else 0
                }
                return info
                
    except Exception as e:
        # 如果 ffprobe 失敗，使用簡單方法
        try:
            # 獲取基本文件信息
            file_ext = os.path.splitext(input_path)[1][1:].upper()
            info = {
                'codec': file_ext,
                'channels': '未知',
                'sample_rate': '未知',
                'duration': 0,
                'bitrate': 0
            }
            return info
        except:
            pass
    
    return None

def format_duration(seconds):
    """格式化時間顯示"""
    if seconds <= 0:
        return "未知"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def format_size(bytes_size):
    """格式化文件大小顯示"""
    if bytes_size <= 0:
        return "未知"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def clean_filename(filename):
    """清理文件名中的特殊字符"""
    # 保留基本字符，其他替換為下劃線
    clean = ''.join(c if c.isalnum() or c in (' ', '_', '-', '.') else '_' for c in filename)
    # 替換多個空格為單個下劃線
    clean = clean.replace(' ', '_').replace('__', '_').replace('..', '.')
    # 移除開頭和結尾的下劃線
    return clean.strip('_')

# 檢查 ffmpeg/ffprobe 是否可用
def check_ffmpeg():
    """檢查系統是否安裝了 ffmpeg 和 ffprobe"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
        return True
    except:
        return False

# 檢查依賴
print("檢查 FFmpeg 依賴...")
if not check_ffmpeg():
    print("❌ FFmpeg 未安裝或不在 PATH 中")
    print("請安裝 FFmpeg：")
    print("- Windows: 從 https://ffmpeg.org/download.html 下載並添加到 PATH")
    print("- Mac: brew install ffmpeg")
    print("- Linux: sudo apt-get install ffmpeg")
    exit(1)
else:
    print("✅ FFmpeg 檢查通過")

# 3. 遍歷每個文件夾進行處理
for folder in input_folder_name_list:
    folder_path = os.path.join(current_dir, folder)
    
    # 檢查文件夾是否存在
    if not os.path.exists(folder_path):
        print(f"⚠️  文件夾不存在: {folder}")
        continue
    
    # 跳過輸出文件夾本身，避免重複處理
    if folder == output_folder_name:
        print(f"⏭️  跳過輸出文件夾: {folder}")
        continue
    
    # 在新輸出目錄下創建對應的子文件夾
    output_subfolder = os.path.join(output_root, folder)
    os.makedirs(output_subfolder, exist_ok=True)
    
    # 查找所有音頻文件
    audio_files = []
    for file in os.listdir(folder_path):
        file_lower = file.lower()
        if any(file_lower.endswith(ext) for ext in AUDIO_EXTENSIONS):
            audio_files.append(file)
    
    if not audio_files:
        print(f"📁 文件夾中沒有音頻文件: {folder}")
        continue
    
    print(f"\n{'='*60}")
    print(f"正在處理文件夾: {folder} (找到 {len(audio_files)} 個音頻文件)")
    print(f"{'='*60}")
    
    folder_converted = 0
    folder_skipped = 0
    folder_failed = 0
    
    # 4. 轉換當前文件夾中的每個音頻文件
    for audio_file in audio_files:
        input_path = os.path.join(folder_path, audio_file)
        
        # 獲取輸入文件信息
        input_size = os.path.getsize(input_path) if os.path.exists(input_path) else 0
        
        # 生成輸出文件名
        base_name = os.path.splitext(audio_file)[0]
        clean_name = clean_filename(base_name)
        
        # 檢查原文件是否已經是 MP3
        if audio_file.lower().endswith('.mp3'):
            mp3_file = clean_name + '_converted.mp3'  # 避免覆蓋原文件
        else:
            mp3_file = clean_name + '.mp3'
        
        output_path = os.path.join(output_subfolder, mp3_file)
        
        # 檢查是否已存在
        if os.path.exists(output_path):
            output_size = os.path.getsize(output_path)
            print(f"  ⏭️  已存在，跳過: {mp3_file} ({format_size(output_size)})")
            folder_skipped += 1
            total_skipped += 1
            continue
        
        try:
            # 顯示轉換信息
            print(f"\n  🎵 處理文件: {audio_file}")
            print(f"    大小: {format_size(input_size)}")
            
            # 獲取音頻信息
            audio_info = get_audio_info(input_path)
            if audio_info:
                print(f"    編碼: {audio_info['codec']}")
                print(f"    聲道: {audio_info['channels']}")
                print(f"    採樣率: {audio_info['sample_rate']}")
                if audio_info['duration'] > 0:
                    print(f"    時長: {format_duration(audio_info['duration'])}")
                if audio_info['bitrate'] > 0:
                    print(f"    碼率: {audio_info['bitrate']} kbps")
            
            print(f"  🔄 正在轉換為: {mp3_file}")
            
            # 使用 ffmpeg 進行轉換
            start_time = time.time()
            
            if convert_audio_to_mp3(input_path, output_path):
                # 計算轉換時間
                conversion_time = time.time() - start_time
                
                # 獲取輸出文件信息
                output_size = os.path.getsize(output_path)
                size_ratio = (output_size / input_size * 100) if input_size > 0 else 0
                
                folder_converted += 1
                total_converted += 1
                
                print(f"  ✅ 轉換成功!")
                print(f"    輸出大小: {format_size(output_size)} ({size_ratio:.1f}% 原始大小)")
                print(f"    轉換時間: {conversion_time:.1f} 秒")
                
                # 顯示壓縮效果
                if size_ratio > 0 and size_ratio < 100:
                    print(f"    📉 壓縮率: {(100-size_ratio):.1f}% 節省空間")
                    
            else:
                print(f"  ❌ 轉換失敗: {audio_file}")
                folder_failed += 1
                total_failed += 1
                
        except Exception as e:
            print(f"  ❌ 處理文件 {audio_file} 時出錯: {e}")
            folder_failed += 1
            total_failed += 1
    
    # 顯示文件夾轉換總結
    if folder_converted > 0 or folder_failed > 0 or folder_skipped > 0:
        print(f"\n  📊 文件夾 {folder} 轉換總結:")
        if folder_converted > 0:
            print(f"    ✅ 成功轉換: {folder_converted} 個文件")
        if folder_skipped > 0:
            print(f"    ⏭️  已跳過: {folder_skipped} 個文件")
        if folder_failed > 0:
            print(f"    ❌ 失敗: {folder_failed} 個文件")
    
    print(f"完成處理文件夾: {folder}")

# 5. 輸出總結信息
print(f"\n{'='*60}")
print("音頻轉換任務完成!")
print(f"{'='*60}")

if total_converted > 0 or total_skipped > 0 or total_failed > 0:
    print(f"\n📊 總計統計:")
    print(f"  ✅ 成功轉換: {total_converted} 個音頻文件")
    print(f"  ⏭️  已跳過: {total_skipped} 個文件 (已存在)")
    print(f"  ❌ 轉換失敗: {total_failed} 個文件")
    
    if total_converted > 0:
        print(f"\n🎉 轉換完成!")
        print(f"所有 MP3 文件已保存至: {output_root}")
        
        # 顯示轉換後的文件結構
        print(f"\n📁 轉換結果文件夾結構:")
        for folder in input_folder_name_list:
            if folder != output_folder_name:
                output_subfolder = os.path.join(output_root, folder)
                if os.path.exists(output_subfolder):
                    mp3_files = [f for f in os.listdir(output_subfolder) 
                               if f.lower().endswith('.mp3')]
                    if mp3_files:
                        total_size = sum(os.path.getsize(os.path.join(output_subfolder, f)) 
                                       for f in mp3_files)
                        print(f"  📂 {folder}: {len(mp3_files)} 個 MP3 文件 ({format_size(total_size)})")
        
        print(f"\n💾 輸出目錄: {output_root}")
else:
    print("沒有需要轉換的音頻文件")

print(f"\n{'='*60}")