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

# File to analyze
VIDEO_FILE_PATH = Path("data/AzureSDKReviewMeetingRecording.mp4")
ANALYZER_TEMPLATE_PATH = Path("analyzer_templates/review_meeting_processor.json")

# Load analyzer template
with open(ANALYZER_TEMPLATE_PATH, "r", encoding="utf-8") as f:
    analyzer_template = json.load(f)

# Create analyzer
analyzer_id = "archboard_review_meeting_" + str(uuid.uuid4())
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
    raise

# Analyze video
logging.info(f"Analyzing video: {VIDEO_FILE_PATH}")
try:
    analyze_response = client.begin_analyze(analyzer_id, file_location=VIDEO_FILE_PATH)
    result_json = client.poll_result(analyze_response, timeout_seconds=3600, polling_interval_seconds=10)
    logging.info("✅ Analysis complete.")
    
    # Save the raw API response to a JSON file for later processing
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    raw_result_path = output_dir / "archboard_review_meeting_raw_result.json"
    with open(raw_result_path, "w", encoding="utf-8") as f:
        json.dump(result_json, f, indent=2, ensure_ascii=False)
    logging.info(f"📁 Raw API response saved to {raw_result_path}")
    logging.info(f"💡 To process this result, run: python process_review_meeting_result.py")
    
except (HTTPError, ConnectionError) as exc:
    error_text = exc.response.text if hasattr(exc, 'response') and exc.response is not None else str(exc)
    logging.error("Video analysis failed: %s", error_text)
    logging.error("If you see connection errors, the analysis may still be running. Check Azure portal for operation status.")
    raise
finally:
    # Clean up analyzer
    try:
        client.delete_analyzer(analyzer_id)
        logging.info("🗑️  Analyzer deleted.")
    except Exception as e:
        logging.warning(f"Analyzer deletion failed: {e}")

logging.info("✅ Analysis process completed!")
