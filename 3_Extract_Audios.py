import os
import subprocess
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class AudioExtractionResult:
    """Data class for audio extraction results"""
    input_file: str
    output_file: str
    success: bool
    duration: float = 0.0
    error: Optional[str] = None

class AudioExtractor:
    """Elegant audio extractor for MP4 files"""
    
    # Constants
    SUPPORTED_FORMATS = {'.mp4', '.m4v', '.mov'}
    BITRATES = {
        'high': '320k',
        'medium': '192k', 
        'low': '128k'
    }
    
    def __init__(self, input_folder: str, output_folder: str, bitrate: str = 'medium'):
        """
        Initialize the audio extractor
        
        Args:
            input_folder: Input folder containing MP4 files
            output_folder: Output folder for MP3 files
            bitrate: Audio quality ('high', 'medium', 'low')
        """
        self.input_root = Path(input_folder)
        self.output_root = Path(output_folder)
        self.bitrate = self.BITRATES.get(bitrate, self.BITRATES['medium'])
        
        # Create output directory
        self.output_root.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.results: List[AudioExtractionResult] = []
    
    def find_mp4_files(self) -> List[Path]:
        """Recursively find all MP4 files in input directory"""
        mp4_files = []
        
        for file_path in self.input_root.rglob('*'):
            if file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                mp4_files.append(file_path)
        
        return sorted(mp4_files)
    
    def get_audio_info(self, input_path: Path) -> dict:
        """Extract audio information from MP4 file"""
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_format', '-show_streams', str(input_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Simple parsing - look for audio stream and duration
            output = result.stdout
            if 'codec_type=audio' in output:
                return {'duration': 0}  # Successfully detected audio
        except Exception:
            pass
        return {}
    
    def generate_output_path(self, input_path: Path) -> Path:
        """Generate output MP3 file path"""
        # Preserve directory structure relative to input root
        relative_path = input_path.relative_to(self.input_root)
        
        # Change extension to .mp3
        output_path = self.output_root / relative_path.with_suffix('.mp3')
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        return output_path
    
    def extract_audio(self, input_path: Path) -> AudioExtractionResult:
        """Extract audio from a single MP4 file"""
        output_path = self.generate_output_path(input_path)
        
        # Skip if already exists
        if output_path.exists():
            return AudioExtractionResult(
                input_file=str(input_path),
                output_file=str(output_path),
                success=True,
                duration=0.0
            )
        
        try:
            # Get audio info first
            audio_info = self.get_audio_info(input_path)
            
            # Extract audio using ffmpeg
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-q:a', '0',  # Best quality
                '-map', 'a',  # Extract audio only
                '-acodec', 'libmp3lame',
                '-b:a', self.bitrate,
                '-ac', '2',  # Stereo
                '-ar', '44100',  # Sample rate
                '-y',  # Overwrite
                str(output_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Verify the output file
            if output_path.exists() and output_path.stat().st_size > 0:
                return AudioExtractionResult(
                    input_file=str(input_path),
                    output_file=str(output_path),
                    success=True,
                    duration=audio_info.get('duration', 0)
                )
            else:
                return AudioExtractionResult(
                    input_file=str(input_path),
                    output_file=str(output_path),
                    success=False,
                    error="Output file empty or not created"
                )
                
        except subprocess.TimeoutExpired:
            return AudioExtractionResult(
                input_file=str(input_path),
                output_file=str(output_path),
                success=False,
                error="Conversion timed out"
            )
        except Exception as e:
            return AudioExtractionResult(
                input_file=str(input_path),
                output_file=str(output_path),
                success=False,
                error=str(e)
            )
    
    def format_duration(self, seconds: float) -> str:
        """Format duration in HH:MM:SS"""
        if seconds <= 0:
            return "Unknown"
        
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    
    def format_size(self, bytes_size: int) -> str:
        """Format file size in human-readable format"""
        if bytes_size <= 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB']
        size = float(bytes_size)
        
        for unit in units:
            if size < 1024.0 or unit == units[-1]:
                return f"{size:.1f} {unit}"
            size /= 1024.0
    
    def process_all(self) -> None:
        """Process all MP4 files found"""
        mp4_files = self.find_mp4_files()
        
        if not mp4_files:
            print(f"❌ No MP4 files found in: {self.input_root}")
            return
        
        print(f"🎵 Found {len(mp4_files)} MP4 file(s) to process")
        print(f"📁 Output directory: {self.output_root}")
        print("-" * 50)
        
        for i, mp4_file in enumerate(mp4_files, 1):
            # Show progress
            relative_path = mp4_file.relative_to(self.input_root)
            print(f"[{i}/{len(mp4_files)}] Processing: {relative_path}")
            
            # Extract audio
            result = self.extract_audio(mp4_file)
            self.results.append(result)
            
            # Show result
            if result.success:
                if result.duration > 0:
                    print(f"   ✅ Extracted: {self.format_duration(result.duration)} audio")
                else:
                    print(f"   ✅ Already exists, skipping")
            else:
                print(f"   ❌ Failed: {result.error}")
        
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print extraction summary"""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        skipped = [r for r in successful if r.duration == 0]
        
        print("\n" + "=" * 50)
        print("🎧 EXTRACTION SUMMARY")
        print("=" * 50)
        
        print(f"📊 Total processed: {len(self.results)} file(s)")
        
        if successful:
            print(f"✅ Successfully extracted: {len(successful) - len(skipped)} file(s)")
        
        if skipped:
            print(f"⏭️  Skipped (already exist): {len(skipped)} file(s)")
        
        if failed:
            print(f"❌ Failed: {len(failed)} file(s)")
            
            # Show failed files
            print("\nFailed files:")
            for result in failed:
                rel_path = Path(result.input_file).relative_to(self.input_root)
                print(f"  • {rel_path}: {result.error}")

# Main execution
if __name__ == "__main__":
    # Configuration
    INPUT_FOLDER = "/Users/SSSPR/Documents/Zhang_Caicai/2_MAIN_Narrative/MAIN_Narrative_mp3:4_Backup/MAIN_Narrative_mp4_Backup"
    OUTPUT_FOLDER = "/Users/SSSPR/Documents/Zhang_Caicai/2_MAIN_Narrative/MAIN_Narrative_mp3:4_Backup/MAIN_Narrative_output_mp4-mp3"
    
    # Create and run extractor
    extractor = AudioExtractor(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        bitrate='medium'  # Options: 'high', 'medium', 'low'
    )
    
    # Process all files
    extractor.process_all()