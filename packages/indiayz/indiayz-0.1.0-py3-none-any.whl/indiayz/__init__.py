"""
indiayz
Unified Open-Source AI Toolkit
"""

__title__ = "indiayz"
__version__ = "0.1.0"
__author__ = "indiayz"
__license__ = "Apache-2.0"

# Public API exports
from indiayz.image.generate import Image
from indiayz.audio.voice import Voice
from indiayz.llm.chat import Chat

__all__ = [
    "Image",
    "Voice",
    "Chat",
]
