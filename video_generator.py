import os
import pandas as pd
from pathlib import Path
import subprocess
import time
from datetime import datetime

def download_video(url, output_folder, cookie_file="cookies.txt"):
    """Download video in 1440p quality"""
    try:
        # Check if cookie file exists
        if not os.path.exists(cookie_file):
            print(f"ERROR: Cookie file '{cookie_file}' not found!")
            return False
        
        # Build command for 1440p download
        cmd = [
            'yt-dlp',
            '--cookies', cookie_file,
            '-f', 'bestvideo[height=1440][ext=mkv]+bestaudio[ext=m4a]/bestvideo[height<=1440]+bestaudio/best',
            '--merge-output-format', 'mkv',
            '-o', f'{output_folder}/%(title)s.%(ext)s',
            '--embed-thumbnail',
            '--embed-metadata',
            '--no-warnings',
            url
        ]
        
        print("Downloading in 1440p quality...")
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def get_video_info(url, cookie_file="cookies.txt"):
    """Get available formats for a video"""
    try:
        cmd = [
            'yt-dlp',
            '--cookies', cookie_file,
            '-F',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except:
        return None

def main():
    excel_file = "Youtube URLs.xlsx"
    output_folder = "Downloaded_Videos"
    cookie_file = "cookies.txt"
    
    # Create output folder
    Path(output_folder).mkdir(exist_ok=True)
    
    # Check cookie file
    if not os.path.exists(cookie_file):
        print("="*70)
        print("ERROR: cookies.txt not found!")
        print("="*70)
        print("\nPlease export cookies from YouTube using browser extension.")
        return
    
    print("="*70)
    print("YouTube Bulk Downloader - 1440p Quality")
    print("="*70)
    
    try:
        # Read Excel
        df = pd.read_excel(excel_file)
        
        # Normalize column names
        df.columns = [col.strip().lower() for col in df.columns]

         # Pick correct column
        if 'url' in df.columns:
             url_column = 'url'
        else:
             url_column = df.columns[0]  # fallback to first column

         # Clean URLs properly (remove blanks, spaces, etc.)
        urls = [
             str(u).strip()
             for u in df[url_column]
             if isinstance(u, str) and u.strip().lower() not in ["", "nan", "none"]
        ]

        print(f"✅ Total valid URLs found: {len(urls)}")

        
        print(f"\nFound {len(urls)} videos to download")
        print("Quality: 1440p (or highest available)\n")
        
        successful = 0
        failed = 0
        failed_urls = []
        
        for idx, url in enumerate(urls, 1):
            print(f"\n{'='*70}")
            print(f"[{idx}/{len(urls)}] Processing Video")
            print(f"{'='*70}")
            print(f"URL: {url}\n")
            
            # Show available formats (optional - comment out if too verbose)
            # print("Checking available formats...")
            # formats = get_video_info(url, cookie_file)
            # if formats:
            #     print(formats)
            
            if download_video(url, output_folder, cookie_file):
                successful += 1
                print("\n✓ Successfully downloaded in 1440p!")
            else:
                failed += 1
                failed_urls.append(url)
                print("\n✗ Download failed")
            
            print("-"*70)
            
            # Wait between downloads
            if idx < len(urls):
                wait_time = 3
                print(f"\nWaiting {wait_time} seconds before next download...\n")
                time.sleep(wait_time)
        
        # Summary
        print("\n" + "="*70)
        print("DOWNLOAD SUMMARY")
        print("="*70)
        print(f"Total Videos: {len(urls)}")
        print(f"Successfully Downloaded: {successful}")
        print(f"Failed: {failed}")
        print(f"Save Location: {os.path.abspath(output_folder)}")
        print("="*70)
        
        if failed_urls:
            log_file = f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(log_file, 'w') as f:
                f.write("Failed URLs:\n\n")
                for url in failed_urls:
                    f.write(f"{url}\n")
            print(f"\nFailed URLs saved to: {log_file}")
        
    except FileNotFoundError:
        print(f"ERROR: '{excel_file}' not found!")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()