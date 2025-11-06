import os
import json
import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime

def check_ffprobe_installed():
    """Check if FFprobe is installed and accessible"""
    try:
        result = subprocess.run(['ffprobe', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFprobe found: {version_line}")
            return True
    except FileNotFoundError:
        print("❌ FFprobe not found!")
        print("\n" + "="*70)
        print("INSTALLATION INSTRUCTIONS")
        print("="*70)
        print("\nWindows:")
        print("  1. Visit: https://www.gyan.dev/ffmpeg/builds/")
        print("  2. Download 'ffmpeg-release-essentials.zip'")
        print("  3. Extract and add the 'bin' folder to System PATH")
        print("  4. Restart terminal and run this script again")
        print("\nLinux/Ubuntu:")
        print("  sudo apt-get update")
        print("  sudo apt-get install ffmpeg")
        print("\nmacOS:")
        print("  brew install ffmpeg")
        print("\nAfter installation, verify with: ffprobe -version")
        print("="*70)
        return False
    return False

def extract_video_metadata(video_path):
    """Extract detailed metadata from a video file using FFprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        # Use utf-8 encoding and handle errors gracefully
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'  # Replace problematic characters instead of crashing
        )
        
        if result.returncode == 0 and result.stdout:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as je:
                print(f"   ❌ JSON decode error: {str(je)}")
                return None
        else:
            if result.stderr:
                print(f"   ❌ FFprobe error: {result.stderr[:200]}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def parse_metadata(raw_metadata, filepath):
    """Parse FFprobe output into structured data"""
    if not raw_metadata:
        return None
    
    parsed = {
        'filepath': filepath,
        'filename': os.path.basename(filepath),
        'file_size_bytes': 0,
        'file_size_mb': 0,
        'duration_seconds': 0,
        'format_name': '',
        'format_long_name': '',
        'bit_rate': 0,
        'video_codec': '',
        'video_codec_long': '',
        'resolution': '',
        'width': 0,
        'height': 0,
        'frame_rate': '',
        'aspect_ratio': '',
        'pixel_format': '',
        'video_bitrate': '',
        'audio_codec': '',
        'audio_codec_long': '',
        'audio_channels': 0,
        'audio_channel_layout': '',
        'audio_sample_rate': '',
        'audio_bitrate': '',
        'has_video': False,
        'has_audio': False,
        'has_subtitles': False,
        'subtitle_count': 0,
        'extraction_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Parse format information
    if 'format' in raw_metadata:
        fmt = raw_metadata['format']
        parsed['file_size_bytes'] = int(fmt.get('size', 0))
        parsed['file_size_mb'] = round(int(fmt.get('size', 0)) / (1024 * 1024), 2)
        parsed['duration_seconds'] = round(float(fmt.get('duration', 0)), 2)
        parsed['format_name'] = fmt.get('format_name', '')
        parsed['format_long_name'] = fmt.get('format_long_name', '')
        parsed['bit_rate'] = int(fmt.get('bit_rate', 0))
    
    # Parse streams
    if 'streams' in raw_metadata:
        video_streams = []
        audio_streams = []
        subtitle_count = 0
        
        for stream in raw_metadata['streams']:
            codec_type = stream.get('codec_type', '')
            
            if codec_type == 'video':
                video_streams.append(stream)
                parsed['has_video'] = True
            elif codec_type == 'audio':
                audio_streams.append(stream)
                parsed['has_audio'] = True
            elif codec_type == 'subtitle':
                subtitle_count += 1
                parsed['has_subtitles'] = True
        
        parsed['subtitle_count'] = subtitle_count
        
        # Get primary video stream info
        if video_streams:
            video = video_streams[0]
            parsed['video_codec'] = video.get('codec_name', '')
            parsed['video_codec_long'] = video.get('codec_long_name', '')
            parsed['width'] = video.get('width', 0)
            parsed['height'] = video.get('height', 0)
            parsed['resolution'] = f"{video.get('width', 0)}x{video.get('height', 0)}"
            parsed['frame_rate'] = video.get('r_frame_rate', '')
            parsed['aspect_ratio'] = video.get('display_aspect_ratio', '')
            parsed['pixel_format'] = video.get('pix_fmt', '')
            parsed['video_bitrate'] = video.get('bit_rate', 'N/A')
        
        # Get primary audio stream info
        if audio_streams:
            audio = audio_streams[0]
            parsed['audio_codec'] = audio.get('codec_name', '')
            parsed['audio_codec_long'] = audio.get('codec_long_name', '')
            parsed['audio_channels'] = audio.get('channels', 0)
            parsed['audio_channel_layout'] = audio.get('channel_layout', '')
            parsed['audio_sample_rate'] = audio.get('sample_rate', '')
            parsed['audio_bitrate'] = audio.get('bit_rate', 'N/A')
    
    return parsed

def scan_folder_for_videos(folder_path):
    """Scan folder for video files and remove duplicates"""
    video_extensions = ['.mkv', '.mp4', '.avi', '.mov', '.webm', '.flv', '.m4v', '.wmv']
    video_files = set()  # Use set to avoid duplicates
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        return []
    
    for ext in video_extensions:
        video_files.update(folder.glob(f'*{ext}'))
        video_files.update(folder.glob(f'*{ext.upper()}'))
    
    # Convert set back to sorted list
    return sorted(list(video_files))

def main():
    """Main function to extract metadata from downloaded videos"""
    
    print("="*70)
    print("VIDEO METADATA EXTRACTOR")
    print("="*70)
    print()
    
    # Check FFprobe installation
    if not check_ffprobe_installed():
        print("\n⚠️  Cannot proceed without FFprobe. Please install it first.")
        input("\nPress Enter to exit...")
        return
    
    print()
    
    # Default folder where videos are downloaded
    default_folder = "Downloaded_Videos"
    
    # Ask user for folder path
    print(f"Default video folder: {default_folder}")
    folder_input = input("Enter folder path (or press Enter for default): ").strip()
    
    if folder_input:
        video_folder = folder_input
    else:
        video_folder = default_folder
    
    print(f"\n📂 Scanning folder: {video_folder}")
    print()
    
    # Find all video files
    video_files = scan_folder_for_videos(video_folder)
    
    if not video_files:
        print(f"❌ No video files found in '{video_folder}'")
        print("\nSupported formats: .mkv, .mp4, .avi, .mov, .webm, .flv, .m4v, .wmv")
        input("\nPress Enter to exit...")
        return
    
    print(f"✅ Found {len(video_files)} video file(s)\n")
    print("="*70)
    print("EXTRACTING METADATA")
    print("="*70)
    print()
    
    # Extract metadata from each video
    all_metadata = []
    successful = 0
    failed = 0
    failed_files = []  # Track which files failed
    
    for idx, video_path in enumerate(video_files, 1):
        filename = video_path.name
        print(f"[{idx}/{len(video_files)}] {filename}")
        
        if not video_path.exists():
            print("   ⚠️  File not found, skipping...")
            failed += 1
            failed_files.append((filename, "File not found"))
            continue
        
        # Extract metadata
        raw_metadata = extract_video_metadata(str(video_path))
        
        if raw_metadata:
            parsed = parse_metadata(raw_metadata, str(video_path))
            
            if parsed:
                all_metadata.append(parsed)
                successful += 1
                
                # Display key info
                print(f"   ✅ Resolution: {parsed['resolution']}")
                print(f"   ✅ Duration: {parsed['duration_seconds']}s")
                print(f"   ✅ Size: {parsed['file_size_mb']} MB")
                print(f"   ✅ Video: {parsed['video_codec']} | Audio: {parsed['audio_codec']}")
            else:
                print("   ❌ Failed to parse metadata")
                failed += 1
                failed_files.append((filename, "Failed to parse metadata"))
        else:
            print("   ❌ Failed to extract metadata")
            failed += 1
            failed_files.append((filename, "Failed to extract metadata"))
        
        print()
    
    # Save results
    if all_metadata:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Save detailed JSON
        json_filename = f"video_metadata_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, indent=2, ensure_ascii=False)
        
        # 2. Create Excel summary
        excel_data = []
        for meta in all_metadata:
            excel_data.append({
                'Filename': meta['filename'],
                'Format': meta['format_long_name'],
                'Duration (seconds)': meta['duration_seconds'],
                'Size (MB)': meta['file_size_mb'],
                'Resolution': meta['resolution'],
                'Width': meta['width'],
                'Height': meta['height'],
                'Video Codec': meta['video_codec'],
                'Frame Rate': meta['frame_rate'],
                'Aspect Ratio': meta['aspect_ratio'],
                'Audio Codec': meta['audio_codec'],
                'Audio Channels': meta['audio_channels'],
                'Sample Rate': meta['audio_sample_rate'],
                'Has Subtitles': meta['has_subtitles'],
                'Subtitle Count': meta['subtitle_count'],
                'Extraction Time': meta['extraction_timestamp'],
                'File Path': meta['filepath']
            })
        
        df = pd.DataFrame(excel_data)
        excel_filename = f"video_metadata_summary_{timestamp}.xlsx"
        df.to_excel(excel_filename, index=False, sheet_name='Video Metadata')
        
        # Print summary
        print("="*70)
        print("EXTRACTION COMPLETE")
        print("="*70)
        print(f"✅ Successfully processed: {successful} video(s)")
        if failed > 0:
            print(f"❌ Failed: {failed} video(s)")
        print(f"\n📄 Output files created:")
        print(f"   1. {json_filename} (Detailed JSON)")
        print(f"   2. {excel_filename} (Excel Summary)")
        print(f"\n💾 Files saved in: {os.path.abspath('.')}")
        print("="*70)
        
        # Log failed files if any
        if failed_files:
            failed_log = f"failed_extractions_{timestamp}.txt"
            with open(failed_log, 'w', encoding='utf-8') as f:
                f.write("Failed Video Files\n")
                f.write("="*70 + "\n\n")
                for filename, reason in failed_files:
                    f.write(f"File: {filename}\n")
                    f.write(f"Reason: {reason}\n\n")
            print(f"\n⚠️  Failed files logged to: {failed_log}")
            print("="*70)
    else:
        print("="*70)
        print("❌ No metadata extracted")
        print("="*70)
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()