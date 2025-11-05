import streamlit as st
import os
import pandas as pd
from pathlib import Path
import subprocess
import time
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="YouTube Bulk Downloader",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dynamic styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #FF0000;
        --secondary-color: #282828;
        --accent-color: #00D9FF;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Stats cards */
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
    }
    
    .stats-card h2 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .stats-card p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Success card */
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    /* Failed card */
    .failed-card {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    
    /* Progress styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    /* Download status */
    .download-item {
        background: rgba(102, 126, 234, 0.1);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Success status */
    .status-success {
        border-left-color: #38ef7d;
        background: rgba(56, 239, 125, 0.1);
    }
    
    /* Failed status */
    .status-failed {
        border-left-color: #f45c43;
        background: rgba(244, 92, 67, 0.1);
    }
    
    /* File uploader */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

def download_video(url, output_folder, cookie_file, progress_callback=None):
    """Download video using cookies with progress callback"""
    try:
        if not os.path.exists(cookie_file):
            return False, "Cookie file not found"
        
        cmd = [
            'yt-dlp',
            '--cookies', cookie_file,
            '-f', 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]',
            '--merge-output-format', 'mp4',
            '-o', f'{output_folder}/%(title)s.%(ext)s',
            '--no-warnings',
            '--progress',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, "Success"
        else:
            return False, result.stderr or "Unknown error"
            
    except Exception as e:
        return False, str(e)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎥 YouTube Bulk Downloader</h1>
        <p>Download multiple YouTube videos seamlessly with cookie authentication</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1384/1384060.png", width=100)
        st.title("⚙️ Settings")
        
        output_folder = st.text_input(
            "Output Folder",
            value="Downloaded_Videos",
            help="Folder where videos will be saved"
        )
        
        st.divider()
        
        st.subheader("📋 Instructions")
        st.markdown("""
        1. **Export Cookies:**
           - Install 'Get cookies.txt LOCALLY' Chrome extension
           - Go to YouTube.com and login
           - Click extension and export cookies
           
        2. **Upload Files:**
           - Upload your cookies.txt file
           - Upload Excel file with YouTube URLs
           
        3. **Start Download:**
           - Click 'Start Download' button
           - Monitor progress in real-time
        """)
        
        st.divider()
        
        st.info("💡 **Tip:** Use column named 'URL' or 'url' in your Excel file")
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Upload Cookie File")
        cookie_file = st.file_uploader(
            "Upload cookies.txt",
            type=['txt'],
            help="Export cookies from YouTube using browser extension"
        )
    
    with col2:
        st.subheader("📊 Upload Excel File")
        excel_file = st.file_uploader(
            "Upload Excel with URLs",
            type=['xlsx', 'xls'],
            help="Excel file containing YouTube URLs"
        )
    
    # Initialize session state
    if 'download_started' not in st.session_state:
        st.session_state.download_started = False
    if 'download_complete' not in st.session_state:
        st.session_state.download_complete = False
    
    # Process files
    if cookie_file and excel_file:
        st.success("✅ Both files uploaded successfully!")
        
        # Save cookie file temporarily
        cookie_path = "temp_cookies.txt"
        with open(cookie_path, 'wb') as f:
            f.write(cookie_file.getbuffer())
        
        # Read Excel file
        try:
            df = pd.read_excel(excel_file)
            
            # Find URL column
            if 'URL' in df.columns:
                urls = df['URL'].dropna().tolist()
            elif 'url' in df.columns:
                urls = df['url'].dropna().tolist()
            else:
                urls = df.iloc[:, 0].dropna().tolist()
            
            urls = [str(url).strip() for url in urls]
            
            st.info(f"📹 Found **{len(urls)}** videos to download")
            
            # Preview URLs
            with st.expander("🔍 Preview URLs"):
                preview_df = pd.DataFrame({'Video URLs': urls[:10]})
                st.dataframe(preview_df, use_container_width=True)
                if len(urls) > 10:
                    st.caption(f"Showing first 10 of {len(urls)} URLs")
            
            # Download button
            st.divider()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                start_download = st.button(
                    "🚀 Start Download",
                    type="primary",
                    use_container_width=True
                )
            
            if start_download:
                st.session_state.download_started = True
                st.session_state.download_complete = False
                
                # Create output folder
                Path(output_folder).mkdir(exist_ok=True)
                
                # Progress tracking
                st.markdown("---")
                st.subheader("📊 Download Progress")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                successful = 0
                failed = 0
                failed_urls = []
                
                # Download container
                download_container = st.container()
                
                for idx, url in enumerate(urls, 1):
                    with download_container:
                        status_text.text(f"Downloading {idx}/{len(urls)}: {url[:50]}...")
                        
                        success, message = download_video(url, output_folder, cookie_path)
                        
                        if success:
                            successful += 1
                            st.markdown(f"""
                            <div class="download-item status-success">
                                ✅ <strong>Video {idx}:</strong> Downloaded successfully<br>
                                <small>{url[:80]}...</small>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            failed += 1
                            failed_urls.append(url)
                            st.markdown(f"""
                            <div class="download-item status-failed">
                                ❌ <strong>Video {idx}:</strong> Failed<br>
                                <small>{url[:80]}...</small><br>
                                <small style="color: #f45c43;">Error: {message[:100]}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        progress_bar.progress(idx / len(urls))
                        
                        if idx < len(urls):
                            time.sleep(2)
                
                st.session_state.download_complete = True
                
                # Summary
                st.markdown("---")
                st.subheader("📈 Download Summary")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="stats-card">
                        <h2>{len(urls)}</h2>
                        <p>Total Videos</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="stats-card success-card">
                        <h2>{successful}</h2>
                        <p>Successful</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="stats-card failed-card">
                        <h2>{failed}</h2>
                        <p>Failed</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.success(f"✅ Downloads complete! Videos saved to: `{os.path.abspath(output_folder)}`")
                
                # Save failed URLs
                if failed_urls:
                    st.warning(f"⚠️ {len(failed_urls)} video(s) failed to download")
                    
                    failed_log = "\n".join(failed_urls)
                    st.download_button(
                        label="📥 Download Failed URLs",
                        data=failed_log,
                        file_name=f"failed_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                
                # Cleanup
                if os.path.exists(cookie_path):
                    os.remove(cookie_path)
                
                # Balloons for celebration
                if successful > 0:
                    st.balloons()
        
        except Exception as e:
            st.error(f"❌ Error processing Excel file: {str(e)}")
    
    else:
        st.info("👆 Please upload both cookie file and Excel file to begin")
        
        # Show example Excel format
        with st.expander("📄 Example Excel Format"):
            example_df = pd.DataFrame({
                'URL': [
                    'https://www.youtube.com/watch?v=example1',
                    'https://www.youtube.com/watch?v=example2',
                    'https://www.youtube.com/watch?v=example3'
                ]
            })
            st.dataframe(example_df, use_container_width=True)
            
            # Download example template
            buffer = io.BytesIO()
            example_df.to_excel(buffer, index=False)
            buffer.seek(0)
            
            st.download_button(
                label="📥 Download Example Template",
                data=buffer,
                file_name="youtube_urls_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>Made with ❤️ using Streamlit | Powered by yt-dlp</p>
        <p><small>⚠️ Please respect copyright and only download videos you have permission to download</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()