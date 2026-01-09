import os
import subprocess
import time
import ffmpeg


input_folder_name = "MAIN_Narrative"# 輸入文件夾名稱
output_folder_name = "MAIN_Narrative_mp4"  # 輸出文件夾名稱

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

# 支持的視頻格式列表
VIDEO_EXTENSIONS = [
    '.mts', '.mov', '.avi', '.mpg', '.mpeg', '.mkv', 
    '.flv', '.wmv', '.mp4', '.m4v', '.3gp', '.vob',
    '.ts', '.m2ts', '.webm', '.ogv', '.divx', '.rmvb'
]

def convert_video_to_mp4(input_path, output_path):
    """將各種視頻文件轉換為 MP4 格式"""
    try:
        # 使用 ffmpeg-python 庫進行轉換
        (
            ffmpeg
            .input(input_path)
            .output(output_path, 
                   vcodec='libx264',      # H.264 視頻編碼
                   acodec='aac',          # AAC 音頻編碼
                   preset='fast',         # 編碼速度與質量平衡
                   crf=23,                # 質量參數 (18-28，越低質量越好)
                   pix_fmt='yuv420p',     # 兼容性更好的像素格式
                   movflags='+faststart') # 優化網絡播放
            .global_args('-loglevel', 'error')  # 只顯示錯誤信息
            .run(overwrite_output=True)
        )
        return True
    except ffmpeg.Error as e:
        print(f"  FFmpeg 錯誤: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        print(f"  轉換失敗: {e}")
        return False

def get_video_info(input_path):
    """獲取視頻文件信息"""
    try:
        probe = ffmpeg.probe(input_path)
        video_stream = next((stream for stream in probe['streams'] 
                            if stream['codec_type'] == 'video'), None)
        
        if video_stream:
            info = {
                'codec': video_stream.get('codec_name', '未知'),
                'width': video_stream.get('width', 0),
                'height': video_stream.get('height', 0),
                'duration': float(video_stream.get('duration', 0)),
                'bitrate': int(video_stream.get('bit_rate', 0)) // 1000 if 'bit_rate' in video_stream else 0,
                'fps': eval(video_stream.get('avg_frame_rate', '0/1')) if 'avg_frame_rate' in video_stream else 0
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
    
    # 查找所有視頻文件
    video_files = []
    for file in os.listdir(folder_path):
        file_lower = file.lower()
        if any(file_lower.endswith(ext) for ext in VIDEO_EXTENSIONS):
            video_files.append(file)
    
    if not video_files:
        print(f"📁 文件夾中沒有視頻文件: {folder}")
        continue
    
    print(f"\n{'='*60}")
    print(f"正在處理文件夾: {folder} (找到 {len(video_files)} 個視頻文件)")
    print(f"{'='*60}")
    
    folder_converted = 0
    folder_skipped = 0
    folder_failed = 0
    
    # 4. 轉換當前文件夾中的每個視頻文件
    for video_file in video_files:
        input_path = os.path.join(folder_path, video_file)
        
        # 獲取輸入文件信息
        input_size = os.path.getsize(input_path) if os.path.exists(input_path) else 0
        
        # 生成輸出文件名
        base_name = os.path.splitext(video_file)[0]
        # 清理文件名中的特殊字符
        clean_name = ''.join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in base_name)
        clean_name = clean_name.replace(' ', '_').replace('__', '_').strip('_')
        
        # 檢查原文件是否已經是 MP4
        if video_file.lower().endswith('.mp4'):
            mp4_file = clean_name + '_converted.mp4'  # 避免覆蓋原文件
        else:
            mp4_file = clean_name + '.mp4'
        
        output_path = os.path.join(output_subfolder, mp4_file)
        
        # 檢查是否已存在
        if os.path.exists(output_path):
            output_size = os.path.getsize(output_path)
            print(f"  ⏭️  已存在，跳過: {mp4_file} ({format_size(output_size)})")
            folder_skipped += 1
            total_skipped += 1
            continue
        
        try:
            # 顯示轉換信息
            print(f"\n  🎬 處理文件: {video_file}")
            print(f"    大小: {format_size(input_size)}")
            
            # 獲取視頻信息
            video_info = get_video_info(input_path)
            if video_info:
                print(f"    編碼: {video_info['codec']}")
                print(f"    分辨率: {video_info['width']}x{video_info['height']}")
                if video_info['duration'] > 0:
                    print(f"    時長: {format_duration(video_info['duration'])}")
                if video_info['fps'] > 0:
                    print(f"    幀率: {video_info['fps']:.1f} FPS")
                if video_info['bitrate'] > 0:
                    print(f"    碼率: {video_info['bitrate']} kbps")
            
            print(f"  🔄 正在轉換為: {mp4_file}")
            
            # 使用 ffmpeg 進行轉換
            start_time = time.time()
            
            if convert_video_to_mp4(input_path, output_path):
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
                print(f"  ❌ 轉換失敗: {video_file}")
                folder_failed += 1
                total_failed += 1
                
        except Exception as e:
            print(f"  ❌ 處理文件 {video_file} 時出錯: {e}")
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
print("轉換任務完成!")
print(f"{'='*60}")

if total_converted > 0 or total_skipped > 0 or total_failed > 0:
    print(f"\n📊 總計統計:")
    print(f"  ✅ 成功轉換: {total_converted} 個視頻文件")
    print(f"  ⏭️  已跳過: {total_skipped} 個文件 (已存在)")
    print(f"  ❌ 轉換失敗: {total_failed} 個文件")
    
    if total_converted > 0:
        print(f"\n🎉 轉換完成!")
        print(f"所有 MP4 文件已保存至: {output_root}")
        
        # 顯示轉換後的文件結構
        print(f"\n📁 轉換結果文件夾結構:")
        for folder in input_folder_name_list:
            if folder != output_folder_name:
                output_subfolder = os.path.join(output_root, folder)
                if os.path.exists(output_subfolder):
                    mp4_files = [f for f in os.listdir(output_subfolder) 
                               if f.lower().endswith('.mp4')]
                    if mp4_files:
                        total_size = sum(os.path.getsize(os.path.join(output_subfolder, f)) 
                                       for f in mp4_files)
                        print(f"  📂 {folder}: {len(mp4_files)} 個 MP4 文件 ({format_size(total_size)})")
        
        print(f"\n💾 輸出目錄: {output_root}")
else:
    print("沒有需要轉換的視頻文件")

print(f"\n{'='*60}")