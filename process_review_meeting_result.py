import logging
import json
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)

# Path to the raw result file
RAW_RESULT_PATH = Path("output/archboard_review_meeting_raw_result.json")
VIDEO_FILE_NAME = "AzureSDKReviewMeetingRecording.mp4"

# Load the raw result
logging.info(f"Loading raw result from {RAW_RESULT_PATH}")
with open(RAW_RESULT_PATH, "r", encoding="utf-8") as f:
    result_json = json.load(f)

logging.info("Raw result loaded successfully")

# Extract and format results
def extract_value(field_obj):
    """Extract the actual value from a field object based on its type."""
    if not isinstance(field_obj, dict):
        return field_obj
    
    field_type = field_obj.get("type", "")
    if field_type == "string":
        return field_obj.get("valueString", "")
    elif field_type == "array":
        return field_obj.get("valueArray", [])
    elif field_type == "object":
        return field_obj.get("valueObject", {})
    return field_obj

def parse_segment(segment_obj):
    """Parse a segment object and extract all fields."""
    value_obj = extract_value(segment_obj)
    
    parsed = {}
    for key, value in value_obj.items():
        parsed[key] = extract_value(value)
    
    return parsed

def format_segment(segment):
    """Format a segment with its knowledge items into markdown."""
    segment_id = segment.get("SegmentId", "Unknown")
    segment_topic = segment.get("SegmentTopic", "Unknown Topic")
    knowledge_items_raw = segment.get("KnowledgeItems", [])
    
    # Parse knowledge items
    knowledge_items = []
    for item_obj in knowledge_items_raw:
        parsed_item = {}
        item_value = extract_value(item_obj)
        for key, value in item_value.items():
            parsed_item[key] = extract_value(value)
        knowledge_items.append(parsed_item)
    
    # Get time range from first and last knowledge item
    begin = knowledge_items[0].get("StartTimestamp", "-") if knowledge_items else "-"
    end = knowledge_items[-1].get("EndTimestamp", "-") if knowledge_items else "-"
    
    output = [
        f"# Segment: {segment_topic}",
        f"**Segment ID:** {segment_id}",
        f"**Time Range:** {begin} - {end}",
        f"**Total Knowledge Items:** {len(knowledge_items)}",
        ""
    ]
    
    for idx, item in enumerate(knowledge_items, 1):
        desc = item.get("Description", "")
        start = item.get("StartTimestamp", "-")
        end_time = item.get("EndTimestamp", "-")
        problem = item.get("APIProblem", "")
        decision = item.get("ReviewerDecision", "")
        
        output.append(f"## 📋 Knowledge Item {idx}")
        output.append(f"**⏱️ Time:** {start} - {end_time}")
        output.append("")
        
        if problem:
            output.append(f"**API Problem:**")
            output.append(f"{problem}")
            output.append("")
        
        if decision:
            output.append(f"**Reviewer Decision:**")
            output.append(f"{decision}")
            output.append("")
    
    return '\n'.join(output)

# Extract segments from the nested structure
logging.info("Extracting segments from result...")
contents = result_json.get("result", {}).get("contents", [])
if contents:
    fields = contents[0].get("fields", {})
    segments_data = fields.get("Segments", {})
    segments_raw = segments_data.get("valueArray", [])
    
    # Parse all segments
    segments = [parse_segment(seg) for seg in segments_raw]
else:
    segments = []

logging.info(f"Found {len(segments)} segments")

# Generate markdown output
markdown_output = [
    "# API/SDK Review Meeting Analysis",
    f"**Video:** {VIDEO_FILE_NAME}",
    f"**Total Segments:** {len(segments)}",
    "",
    "---",
    ""
]

for segment in segments:
    markdown_output.append(format_segment(segment))

# Write summary to markdown file
summary_path = Path("output/archboard_review_meeting_summary.md")
summary_path.parent.mkdir(exist_ok=True)
with open(summary_path, "w", encoding="utf-8") as f:
    f.write('\n\n'.join(markdown_output))

logging.info(f"✅ Summary written to {summary_path}")
logging.info(f"📊 Processed {len(segments)} segments successfully!")
