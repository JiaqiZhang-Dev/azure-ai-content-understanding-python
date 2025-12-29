"""
Video splitter utility for handling videos that exceed Content Understanding service limits.
"""
import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class VideoSplitter:
    """Handles splitting of long videos into chunks that meet service requirements."""
    
    # Maximum video duration in seconds (2 hours)
    MAX_DURATION_SECONDS = 7200
    
    @staticmethod
    def get_video_duration(video_path: str) -> Optional[float]:
        """
        Get the duration of a video file in seconds using ffprobe.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Duration in seconds, or None if it cannot be determined
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                str(video_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            logger.info(f"Video duration for {os.path.basename(video_path)}: {duration:.2f}s ({duration/3600:.2f}h)")
            return duration
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting video duration with ffprobe: {e}")
            logger.error(f"stderr: {e.stderr}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing ffprobe output: {e}")
            return None
        except FileNotFoundError:
            logger.warning("ffprobe not found. Install ffmpeg to enable video duration check.")
            return None
