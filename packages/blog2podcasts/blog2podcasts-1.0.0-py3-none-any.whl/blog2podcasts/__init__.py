"""
Blog2Podcasts - AI-powered blog to podcast converter

Convert any blog article into an engaging podcast audio file
with optional voice cloning from YouTube videos.
"""

__version__ = "1.0.0"
__author__ = "QuantBender"
__license__ = "MIT"

from blog2podcasts.scraper import BlogScraper, BlogContent
from blog2podcasts.summarizer import ContentSummarizer
from blog2podcasts.audio_generator import AudioGenerator, RECOMMENDED_VOICES
from blog2podcasts.voice_cloner import VoiceCloner, ClonedVoiceGenerator, VoiceProfile

__all__ = [
    "__version__",
    "BlogScraper",
    "BlogContent",
    "ContentSummarizer",
    "AudioGenerator",
    "RECOMMENDED_VOICES",
    "VoiceCloner",
    "ClonedVoiceGenerator",
    "VoiceProfile",
]
