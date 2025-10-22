"""
Process Review Meeting Result - Extract API Design Guidelines

This script processes the JSON output from the review_meeting_processor analyzer
and converts it into a reusable API/SDK Design Guidelines document.

The output is designed to be used by:
1. LLMs for automated API/SDK review
2. Developers creating new APIs/SDKs
3. API design documentation and training

Analyzer Structure (review_meeting_processor.json):
- Segments (array) - Major topics/stages of the meeting
  - SegmentId (string)
  - SegmentTopic (string) - High-level meeting stage or agenda item
  - Knowledges (array) - Reusable design guidelines extracted from this segment
    - StartTimestamp (string)
    - EndTimestamp (string)
    - KeyFrameTimestamp (string)
    - Title (string) - Concise title for the design guideline
    - Problem (string) - API design problem or anti-pattern
    - RecommendedSolution (string) - Recommended approach and best practice pattern
"""

import logging
import json
from pathlib import Path
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO)

# Path to the raw result file
RAW_RESULT_PATH = Path("output/archboard_review_meeting_raw_result.json")
VIDEO_FILE_NAME = "AzureSDKReviewMeetingRecording.mp4"
VIDEO_FILE_PATH = Path("data") / VIDEO_FILE_NAME
KEYFRAMES_DIR = Path("output/keyframes")

def extract_frame_as_file(video_path, timestamp_str, output_path):
    """Extract a frame at the given timestamp and save it as an image file.
    
    Returns:
        Path to the saved image file, or None if extraction failed.
    """
    try:
        if not video_path.exists():
            logging.error(f"Video file not found: {video_path}")
            return None
            
        # Convert timestamp string (HH:MM:SS.mmm) to seconds
        time_parts = timestamp_str.split(':')
        seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])
        
        logging.info(f"Extracting frame at {timestamp_str} ({seconds}s) from {video_path.name}")
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use ffmpeg to extract frame to file
        cmd = [
            'ffmpeg', '-ss', str(seconds), '-i', str(video_path),
            '-vframes', '1', '-y', str(output_path)
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logging.info(f"Successfully extracted frame to {output_path}")
        return output_path
    except FileNotFoundError as e:
        logging.error(f"ffmpeg not found. Please install ffmpeg to enable frame extraction.")
        logging.error(f"Install ffmpeg: https://ffmpeg.org/download.html")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"ffmpeg failed to extract frame at {timestamp_str}: {e}")
        return None
    except Exception as e:
        logging.warning(f"Failed to extract frame at {timestamp_str}: {e}")
        return None

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

def format_segment(segment, segment_index):
    """Format a segment with its knowledge items into markdown.
    
    Args:
        segment: The segment data dictionary
        segment_index: The 1-based index of the segment (for naming keyframe files)
    """
    segment_id = segment.get("SegmentId", "Unknown")
    segment_topic = segment.get("SegmentTopic", "Unknown Topic")
    segment_summary = segment.get("SegmentSummary", "")
    knowledges_raw = segment.get("Knowledges", [])
    
    # Parse knowledge items
    knowledges = []
    for knowledge_obj in knowledges_raw:
        parsed_knowledge = {}
        knowledge_value = extract_value(knowledge_obj)
        for key, value in knowledge_value.items():
            parsed_knowledge[key] = extract_value(value)
        knowledges.append(parsed_knowledge)
    
    # Get time range from first and last knowledge item
    begin = knowledges[0].get("StartTimestamp", "-") if knowledges else "-"
    end = knowledges[-1].get("EndTimestamp", "-") if knowledges else "-"
    
    output = [
        f"## Segment {segment_id}: {segment_topic}",
        f"**Time Range:** {begin} - {end}",
        f"**Total Knowledge Items:** {len(knowledges)}",
        ""
    ]
    
    if segment_summary:
        output.append(f"**Summary:** {segment_summary}")
        output.append("")
    
    for idx, knowledge in enumerate(knowledges, 1):
        start = knowledge.get("StartTimestamp", "-")
        end_time = knowledge.get("EndTimestamp", "-")
        key_frame = knowledge.get("KeyFrameTimestamp", "")
        title = knowledge.get("Title", "")
        problem = knowledge.get("Problem", "")
        best_practice = knowledge.get("RecommendedSolution", "")
        
        # Use title in the heading if available
        heading = f"### Design Guideline {idx}"
        if title:
            heading += f": {title}"
        output.append(heading)
        output.append(f"**Source Discussion Time:** {start} - {end_time}")
        
        if key_frame:
            output.append(f"**Reference Frame:** {key_frame}")
            # Extract frame image and save as file
            # Use sanitized timestamp for filename (replace : with -)
            timestamp_safe = key_frame.replace(":", "-").replace(".", "-")
            image_filename = f"segment_{segment_index}_guideline_{idx}_{timestamp_safe}.png"
            image_path = KEYFRAMES_DIR / image_filename
            
            extracted_path = extract_frame_as_file(VIDEO_FILE_PATH, key_frame, image_path)
            if extracted_path:
                # Use relative path from output directory
                relative_path = f"keyframes/{image_filename}"
                output.append(f'<img src="{relative_path}" alt="Key Frame at {key_frame}" width="600"/>')
        
        output.append("")
        
        if problem:
            output.append(f"**Problem:**")
            output.append(problem)
            output.append("")
        
        if best_practice:
            output.append(f"**Best Practice:**")
            output.append(best_practice)
            output.append("")
    
    return '\n'.join(output)

# Extract segments from the nested structure
logging.info("Extracting segments from result...")
contents = result_json.get("result", {}).get("contents", [])
if contents:
    content = contents[0]
    fields = content.get("fields", {})
    segments_data = fields.get("Segments", {})
    segments_raw = segments_data.get("valueArray", [])
    
    # Extract additional video analysis results
    markdown_transcript = content.get("markdown", "")
    key_frame_times_ms = content.get("KeyFrameTimesMs", [])
    transcript_phrases = content.get("transcriptPhrases", [])
    
    # Parse all segments
    segments = [parse_segment(seg) for seg in segments_raw]
else:
    segments = []
    markdown_transcript = ""
    key_frame_times_ms = []
    transcript_phrases = []

logging.info(f"Found {len(segments)} segments")

# Count total knowledge items across all segments
total_knowledges = sum(len(seg.get("Knowledges", [])) for seg in segments)

# Generate markdown output
markdown_output = [
    "# API/SDK Design Guidelines",
    f"**Extracted from:** {VIDEO_FILE_NAME}",
    "",
    "> This document contains reusable API/SDK design principles and best practices extracted from technical review meetings.",
    "> These guidelines can be used by developers and LLMs to review APIs or design better SDKs.",
    "",
    f"**Total Topics:** {len(segments)}",
    f"**Total Design Guidelines:** {total_knowledges}",
    "",
    "---",
    ""
]

for idx, segment in enumerate(segments, 1):
    markdown_output.append(format_segment(segment, idx))
    markdown_output.append("---")
    markdown_output.append("")

# Write summary to markdown file
summary_path = Path("output/archboard_review_meeting_summary.md")
summary_path.parent.mkdir(exist_ok=True)
with open(summary_path, "w", encoding="utf-8") as f:
    f.write('\n'.join(markdown_output))

logging.info(f"✅ API Design Guidelines written to {summary_path}")
logging.info(f"📊 Extracted {len(segments)} topics with {total_knowledges} design guidelines successfully!")
