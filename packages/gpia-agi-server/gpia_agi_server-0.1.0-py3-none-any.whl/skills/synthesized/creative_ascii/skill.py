"""
Creative ASCII Suite
====================

A comprehensive suite for generating ASCII art from text and images, 
implementing the capabilities of the original 'missingASCII Skills' JS library
within the Python GPIA ecosystem.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import io

# Optional imports handled gracefully
try:
    import pyfiglet
except ImportError:
    pyfiglet = None

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillMetadata,
    SkillResult,
    SkillLevel,
)

logger = logging.getLogger(__name__)

# Standard ASCII character ramp (dark to light)
ASCII_RAMP_STANDARD = "@%#*+=-:. "
ASCII_RAMP_COMPLEX = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

class CreativeAsciiSkill(Skill):
    """
    Implementation of the Creative ASCII Suite.
    Provides text-to-ascii, image-to-ascii, and decorative divider generation.
    """

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="creative/ascii",
            name="Creative ASCII Suite",
            description="Generates ASCII art from text and images, and creates dividers.",
            category=SkillCategory.CREATIVE,
            level=SkillLevel.INTERMEDIATE,
            tags=["ascii", "art", "image", "text"],
            author="Architect (GPIA)",
            version="1.0.0",
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string", 
                    "enum": ["text_to_ascii", "image_to_ascii", "create_divider", "list_fonts"],
                    "description": "The specific operation to perform."
                },
                "text": {"type": "string", "description": "Text to convert to ASCII art."},
                "font": {"type": "string", "description": "Font name for text generation (e.g., 'standard', 'slant')."},
                "width": {"type": "integer", "description": "Output width in characters."},
                "image_path": {"type": "string", "description": "Path to the image file for conversion."},
                "contrast": {"type": "integer", "description": "Contrast adjustment (0-200, default 100)."},
                "brightness": {"type": "integer", "description": "Brightness adjustment (0-200, default 100)."},
                "inverted": {"type": "boolean", "description": "Invert the output colors."}, 
                "style": {"type": "string", "description": "Style for dividers or specialized rendering."},
            },
            "required": ["action"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string", "description": "The generated ASCII art or data."},
                "fonts": {"type": "array", "items": {"type": "string"}, "description": "List of available fonts."}
            }
        }

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        action = input_data.get("action")
        
        try:
            if action == "text_to_ascii":
                return self._text_to_ascii(input_data)
            elif action == "image_to_ascii":
                return self._image_to_ascii(input_data)
            elif action == "create_divider":
                return self._create_divider(input_data)
            elif action == "list_fonts":
                return self._list_fonts()
            else:
                return SkillResult(
                    success=False, 
                    output=None, 
                    error=f"Unknown action: {action}",
                    skill_id=self.metadata().id
                )
        except Exception as e:
            logger.exception(f"Error executing CreativeAsciiSkill: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                skill_id=self.metadata().id
            )

    def _text_to_ascii(self, data: Dict[str, Any]) -> SkillResult:
        if not pyfiglet:
            return SkillResult(success=False, output="pyfiglet library not installed.", error="DependencyMissing")
        
        text = data.get("text", "Sample")
        font = data.get("font", "standard")
        width = data.get("width", 80)
        
        try:
            fig = pyfiglet.Figlet(font=font, width=width)
            result = fig.renderText(text)
            return SkillResult(success=True, output=result, skill_id=self.metadata().id)
        except pyfiglet.FontNotFound:
            return SkillResult(success=False, output=None, error=f"Font '{font}' not found.", skill_id=self.metadata().id)

    def _list_fonts(self) -> SkillResult:
        if not pyfiglet:
            return SkillResult(success=False, output="pyfiglet library not installed.", error="DependencyMissing")
        
        fonts = pyfiglet.FigletFont.getFonts()
        return SkillResult(success=True, output={"fonts": fonts}, skill_id=self.metadata().id)

    def _image_to_ascii(self, data: Dict[str, Any]) -> SkillResult:
        if not Image:
            return SkillResult(success=False, output="Pillow (PIL) library not installed.", error="DependencyMissing")

        image_path = data.get("image_path")
        if not image_path or not Path(image_path).exists():
             return SkillResult(success=False, output=None, error=f"Image path not found: {image_path}", skill_id=self.metadata().id)

        width = data.get("width", 100)
        contrast = data.get("contrast", 100)
        inverted = data.get("inverted", False)
        
        try:
            img = Image.open(image_path)
            
            # 1. Resize
            aspect_ratio = img.height / img.width
            # Terminal characters are roughly twice as tall as wide, so we correct aspect ratio
            char_aspect = 0.55 
            new_height = int(width * aspect_ratio * char_aspect)
            img = img.resize((width, new_height))
            
            # 2. Convert to grayscale
            img = img.convert("L")
            
            # 3. Apply contrast/brightness (Basic implementation)
            if inverted:
                img = ImageOps.invert(img)

            pixels = img.getdata()
            
            # 4. Map to ASCII
            chars = ASCII_RAMP_COMPLEX
            # Scale pixel value to index of chars array
            scale = (len(chars) - 1) / 255
            new_pixels = [chars[int(pixel * scale)] for pixel in pixels]
            
            new_pixels_str = "".join(new_pixels)
            
            # Split string into lines
            ascii_image = "\n".join([new_pixels_str[i:i+width] for i in range(0, len(new_pixels_str), width)])
            
            return SkillResult(success=True, output=ascii_image, skill_id=self.metadata().id)
            
        except Exception as e:
             return SkillResult(success=False, output=None, error=f"Image processing error: {e}", skill_id=self.metadata().id)

    def _create_divider(self, data: Dict[str, Any]) -> SkillResult:
        style = data.get("style", "simple")
        width = data.get("width", 40)
        
        # Define some basic divider styles (Start, Body, End)
        styles = {
            "simple": ("[", "-", "]"),
            "double": ("<<", "=", ">>"),
            "stars": ("*", "*", "*"),
            "waves": ("~", "~", "~"),
            "pipes": ("|", "-", "|"),
            "arrows": (">", "-", "<"),
        }
        
        s, b, e = styles.get(style, styles["simple"])
        
        # Calculate body length
        body_len = width - len(s) - len(e)
        if body_len < 0:
            body_len = 0
            
        # If body is multi-char, we need to handle repetition correctly
        result = f"{s}{b * body_len}{e}"
        
        return SkillResult(success=True, output=result, skill_id=self.metadata().id)
