import logging
import json
import os
import sys
import uuid
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
    logging.info(f"Analyzing video: {VIDEO_FILE_PATH.name}")
    try:
        analyze_response = client.begin_analyze(analyzer_id, file_location=VIDEO_FILE_PATH)
        result_json = client.poll_result(analyze_response, timeout_seconds=3600, polling_interval_seconds=10)
        logging.info("✅ Analysis complete.")
        
        # Save the raw API response to a JSON file for later processing
        # (output_dir and safe_name already defined above for skip check)
        with open(raw_result_path, "w", encoding="utf-8") as f:
            json.dump(result_json, f, indent=2, ensure_ascii=False)
        logging.info(f"📁 Raw API response saved to {raw_result_path}")
        
    except RuntimeError as exc:
        logging.error(f"Video analysis failed: {exc}")
        logging.error(f"⚠️  Skipping video: {VIDEO_FILE_PATH.name} (likely exceeds size/length limits)")
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
