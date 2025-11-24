import logging
import json
import os
import sys
import uuid
import subprocess
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from requests.exceptions import HTTPError, ConnectionError

# Load environment variables
load_dotenv(find_dotenv())
logging.basicConfig(level=logging.INFO)

# Azure configuration
AZURE_AI_ENDPOINT = os.getenv("AZURE_AI_ENDPOINT")
AZURE_AI_API_KEY = os.getenv("AZURE_AI_API_KEY")
AZURE_AI_API_VERSION = os.getenv("AZURE_AI_API_VERSION", "2025-05-01-preview")

# Add parent directory to path for shared modules
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))
from python.content_understanding_client import AzureContentUnderstandingClient
from python.video_splitter import VideoSplitter

# Authentication
credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

# Client setup
client = AzureContentUnderstandingClient(
    endpoint=AZURE_AI_ENDPOINT,
    api_version=AZURE_AI_API_VERSION,
    token_provider=token_provider,
    # subscription_key=AZURE_AI_API_KEY,
    x_ms_useragent="azure-ai-content-understanding-python/archboard_review_meeting_processor",
)

def get_video_metadata(video_path):
    """Get video metadata using ffprobe.
    
    Returns:
        dict: Video metadata including duration, fps, width, height
        None: If ffprobe is not available or fails
    """
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=duration,r_frame_rate,width,height',
            '-of', 'json',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        if 'streams' in data and len(data['streams']) > 0:
            stream = data['streams'][0]
            # Parse frame rate (format: "num/den")
            fps_str = stream.get('r_frame_rate', '0/1')
            num, den = map(int, fps_str.split('/'))
            fps = num / den if den != 0 else 0
            
            return {
                'duration': float(stream.get('duration', 0)),
                'fps': fps,
                'width': int(stream.get('width', 0)),
                'height': int(stream.get('height', 0))
            }
    except FileNotFoundError:
        logging.warning("ffprobe not found. Install ffmpeg to enable video validation.")
        return None
    except Exception as e:
        logging.warning(f"Failed to get video metadata: {e}")
        return None
    return None

def validate_video_for_service(video_path, max_duration=7200, max_fps=120, min_width=320, max_width=3840):
    """Validate video against Azure Content Understanding service limits.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    metadata = get_video_metadata(video_path)
    
    if metadata is None:
        # Cannot validate without metadata, proceed with caution
        return True, None
    
    issues = []
    
    if metadata['duration'] > max_duration:
        duration_hours = metadata['duration'] / 3600
        max_hours = max_duration / 3600
        issues.append(f"Duration {duration_hours:.2f}h exceeds limit of {max_hours:.2f}h")
    
    if metadata['fps'] > max_fps:
        issues.append(f"FPS {metadata['fps']:.1f} exceeds limit of {max_fps}")
    
    if metadata['width'] < min_width:
        issues.append(f"Width {metadata['width']}px is below minimum of {min_width}px")
    
    if metadata['width'] > max_width:
        issues.append(f"Width {metadata['width']}px exceeds maximum of {max_width}px")
    
    if issues:
        error_msg = f"Video validation failed:\n  - " + "\n  - ".join(issues)
        error_msg += f"\n\nVideo specs: {metadata['duration']:.1f}s, {metadata['fps']:.1f} fps, {metadata['width']}x{metadata['height']}px"
        return False, error_msg
    
    return True, None

# Find all video files in data folder
DATA_DIR = Path("data")
video_files = list(DATA_DIR.glob("*.mp4"))
logging.info(f"Found {len(video_files)} video files to analyze")

ANALYZER_TEMPLATE_PATH = Path("analyzer/review_meeting_processor.json")

# Load analyzer template
with open(ANALYZER_TEMPLATE_PATH, "r", encoding="utf-8") as f:
    analyzer_template = json.load(f)

# Process each video
for video_idx, VIDEO_FILE_PATH in enumerate(video_files, 1):
    logging.info(f"\n{'='*80}")
    logging.info(f"Processing video {video_idx}/{len(video_files)}: {VIDEO_FILE_PATH.name}")
    logging.info(f"{'='*80}\n")
    
    # Check if this video has already been processed
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    safe_name = VIDEO_FILE_PATH.stem.replace(" ", "_").replace("[", "").replace("]", "").replace("-", "_")
    raw_result_path = output_dir / f"{safe_name}_raw_result.json"
    
    if raw_result_path.exists():
        logging.info(f"⏭️  Skipping video (already processed): {VIDEO_FILE_PATH.name}")
        logging.info(f"   Output file exists: {raw_result_path}")
        logging.info(f"   To reprocess, delete: {raw_result_path}")
        continue
    
    # Check if video exceeds 2-hour limit and cut if needed
    duration = VideoSplitter.get_video_duration(VIDEO_FILE_PATH)
    video_to_process = VIDEO_FILE_PATH
    
    if duration and duration > 7200:  # 2 hours in seconds
        duration_hours = duration / 3600
        logging.warning(f"⚠️  Video exceeds 2-hour limit: {duration_hours:.2f}h")
        logging.warning(f"⚠️  Only the first 2 hours will be processed")
        logging.warning(f"⚠️  Remaining {duration_hours - 2:.2f}h will be skipped")
        
        # Create a 2-hour version
        try:
            chunks_dir = DATA_DIR / "chunks"
            chunks_dir.mkdir(exist_ok=True)
            
            truncated_path = chunks_dir / f"{VIDEO_FILE_PATH.stem}_first2h.mp4"
            
            if not truncated_path.exists():
                logging.info(f"🔪 Creating 2-hour version of video...")
                cmd = [
                    'ffmpeg',
                    '-i', str(VIDEO_FILE_PATH),
                    '-t', '7200',  # 2 hours
                    '-c', 'copy',
                    str(truncated_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                logging.info(f"✅ Created 2-hour version: {truncated_path.name}")
            else:
                logging.info(f"📁 Using existing 2-hour version: {truncated_path.name}")
            
            video_to_process = truncated_path
            
        except Exception as e:
            logging.error(f"❌ Failed to create 2-hour version: {e}")
            logging.error("💡 Please install ffmpeg: https://ffmpeg.org/download.html")
            logging.error("   Skipping this video.")
            continue
    
    # Validate the video to process
    is_valid, validation_error = validate_video_for_service(video_to_process)
    if not is_valid:
        logging.error(f"❌ Video validation failed for: {video_to_process.name}")
        logging.error(validation_error)
        continue
    
    # Create a unique analyzer for each video
    analyzer_id = f"review_meeting_{uuid.uuid4()}"
    logging.info(f"Creating analyzer: {analyzer_id}")
    try:
        create_response = client.begin_create_analyzer(
            analyzer_id,
            analyzer_template_path=str(ANALYZER_TEMPLATE_PATH),
        )
        client.poll_result(create_response)
        logging.info("Analyzer created successfully.")
    except HTTPError as exc:
        error_text = exc.response.text if exc.response is not None else str(exc)
        logging.error("Failed to create analyzer: %s", error_text)
        logging.error(f"Skipping video: {VIDEO_FILE_PATH.name}")
        continue

    # Analyze video
    logging.info(f"Analyzing video: {video_to_process.name}")
    try:
        analyze_response = client.begin_analyze(analyzer_id, file_location=video_to_process)
        result_json = client.poll_result(analyze_response, timeout_seconds=3600, polling_interval_seconds=10)
        logging.info("✅ Analysis complete.")
        
        # Save the raw API response to a JSON file for later processing
        # (output_dir and safe_name already defined above for skip check)
        with open(raw_result_path, "w", encoding="utf-8") as f:
            json.dump(result_json, f, indent=2, ensure_ascii=False)
        logging.info(f"📁 Raw API response saved to {raw_result_path}")
        
    except RuntimeError as exc:
        logging.error(f"Video analysis failed: {exc}")
        logging.error(f"⚠️  Skipping video: {VIDEO_FILE_PATH.name}")
        continue
    except (HTTPError, ConnectionError) as exc:
        error_text = exc.response.text if hasattr(exc, 'response') and exc.response is not None else str(exc)
        logging.error("Video analysis failed: %s", error_text)
        logging.error(f"⚠️  Skipping video: {VIDEO_FILE_PATH.name}")
        continue

logging.info(f"\n{'='*80}")
logging.info(f"✅ All videos processed!")
logging.info(f"💡 To process the results, run: python process_review_meeting_result.py")
logging.info(f"{'='*80}\n")
