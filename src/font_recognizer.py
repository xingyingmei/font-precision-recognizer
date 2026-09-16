"""
Font Recognition Engine
Handles font identification from images using AI and computer vision
"""

import os
import base64
import io
from typing import List, Dict, Any, Optional
from PIL import Image
import cv2
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class FontRecognizer:
    """Main font recognition engine using Google Generative AI"""
    
    def __init__(self):
        """Initialize the font recognizer with API credentials"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.supported_formats = os.getenv('SUPPORTED_FORMATS', 'png,jpg,jpeg,gif,bmp,webp').split(',')
        self.max_image_size = int(os.getenv('MAX_IMAGE_SIZE', 10485760))
        self.font_sources = self._load_font_sources()
    
    def _load_font_sources(self) -> Dict[str, Dict[str, str]]:
        """Load available font sources from database"""
        return {
            'Google Fonts': {
                'url': 'https://fonts.google.com',
                'type': 'free',
                'search_pattern': 'https://fonts.google.com/?query={query}'
            },
            'MyFonts': {
                'url': 'https://www.myfonts.com',
                'type': 'commercial',
                'search_pattern': 'https://www.myfonts.com/search/{query}/'
            },
            'Font Squirrel': {
                'url': 'https://www.fontsquirrel.com',
                'type': 'free',
                'search_pattern': 'https://www.fontsquirrel.com/fonts?search={query}'
            },
            'DaFont': {
                'url': 'https://www.dafont.com',
                'type': 'free',
                'search_pattern': 'https://www.dafont.com/search.php?q={query}'
            },
            '1001 Fonts': {
                'url': 'https://www.1001fonts.com',
                'type': 'mixed',
                'search_pattern': 'https://www.1001fonts.com/search.html?search={query}'
            },
            'Font Space': {
                'url': 'https://www.fontspace.com',
                'type': 'free',
                'search_pattern': 'https://www.fontspace.com/search?q={query}'
            },
            'Creative Fabrica': {
                'url': 'https://www.creativefabrica.com',
                'type': 'subscription',
                'search_pattern': 'https://www.creativefabrica.com/search/?q={query}'
            },
            'Adobe Fonts': {
                'url': 'https://fonts.adobe.com',
                'type': 'commercial',
                'search_pattern': 'https://fonts.adobe.com/search?q={query}'
            },
            'YouWorkForThem': {
                'url': 'https://www.youworkforthem.com/fontlens',
                'type': 'commercial',
                'search_pattern': 'https://www.youworkforthem.com/fonts?search={query}'
            },
            'WhatFontIs': {
                'url': 'https://www.whatfontis.com',
                'type': 'free',
                'search_pattern': 'https://www.whatfontis.com/?s={query}'
            },
            'Global Fonts': {
                'url': 'https://globalfonts.pro',
                'type': 'commercial',
                'search_pattern': 'https://globalfonts.pro/search?q={query}'
            },
            'FontHub': {
                'url': 'https://fontshub.pro',
                'type': 'mixed',
                'search_pattern': 'https://fontshub.pro/search/?q={query}'
            },
            'Font Download': {
                'url': 'https://font.download',
                'type': 'free',
                'search_pattern': 'https://font.download/search/{query}'
            },
            'Font Park': {
                'url': 'https://fontpark.com',
                'type': 'mixed',
                'search_pattern': 'https://fontpark.com/en/search.html?q={query}'
            },
            'WebFont Free': {
                'url': 'https://webfontfree.com',
                'type': 'free',
                'search_pattern': 'https://webfontfree.com/?s={query}'
            },
            'Elements Envato': {
                'url': 'https://elements.envato.com/fonts',
                'type': 'commercial',
                'search_pattern': 'https://elements.envato.com/fonts/?search={query}'
            },
            'SandollCloud': {
                'url': 'https://www.sandollcloud.com',
                'type': 'commercial',
                'search_pattern': 'https://www.sandollcloud.com/?s={query}'
            }
        }
    
    def _validate_image(self, image_path: str) -> bool:
        """Validate image format and size"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        file_size = os.path.getsize(image_path)
        if file_size > self.max_image_size:
            raise ValueError(f"Image size exceeds maximum allowed size ({self.max_image_size} bytes)")
        
        ext = os.path.splitext(image_path)[1].lower().lstrip('.')
        if ext not in self.supported_formats:
            raise ValueError(f"Unsupported image format: {ext}. Supported: {', '.join(self.supported_formats)}")
        
        return True
    
    def _preprocess_image(self, image_path: str) -> Image.Image:
        """Preprocess image for better font recognition"""
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Enhance contrast and sharpness
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2)
        
        return img
    
    def _prepare_image_for_api(self, image: Image.Image) -> str:
        """Convert image to base64 for API submission"""
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def recognize_from_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Recognize fonts in an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of recognized fonts with confidence scores and sources
        """
        try:
            # Validate image
            self._validate_image(image_path)
            logger.info(f"Processing image: {image_path}")
            
            # Preprocess image
            processed_img = self._preprocess_image(image_path)
            
            # Prepare for API
            img_base64 = self._prepare_image_for_api(processed_img)
            
            # Use Google Generative AI if API key is available
            if self.api_key:
                results = self._analyze_with_generative_ai(img_base64)
            else:
                results = self._fallback_recognition(image_path)
            
            return results
            
        except Exception as e:
            logger.error(f"Error recognizing font: {str(e)}")
            return [{
                'name': 'Unknown',
                'confidence': 0,
                'error': str(e),
                'sources': []
            }]
    
    def _analyze_with_generative_ai(self, img_base64: str) -> List[Dict[str, Any]]:
        """Analyze image using Google Generative AI"""
        try:
            model = genai.GenerativeModel('gemini-pro-vision')
            
            prompt = """Analyze this image and identify the fonts used. For each font, provide:
            1. Font name (be specific)
            2. Font type (serif, sans-serif, script, etc.)
            3. Your confidence level (0-100)
            
            Format your response as JSON with this structure:
            {
                "fonts": [
                    {
                        "name": "Font Name",
                        "type": "font-type",
                        "confidence": 85
                    }
                ]
            }
            """
            
            response = model.generate_content([
                prompt,
                {'mime_type': 'image/jpeg', 'data': img_base64}
            ])
            
            # Parse response
            import json
            response_text = response.text
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            fonts_data = json.loads(json_str)
            results = []
            
            for font in fonts_data.get('fonts', []):
                font_result = self._create_font_result(
                    font.get('name', 'Unknown'),
                    font.get('type', 'unknown'),
                    font.get('confidence', 0) / 100.0
                )
                results.append(font_result)
            
            return results if results else self._create_default_result()
            
        except Exception as e:
            logger.error(f"Generative AI analysis failed: {str(e)}")
            return self._create_default_result()
    
    def _fallback_recognition(self, image_path: str) -> List[Dict[str, Any]]:
        """Fallback recognition using OpenCV features"""
        try:
            img = cv2.imread(image_path)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(img_gray, 100, 200)
            
            # Analyze image characteristics
            height, width = img_gray.shape
            aspect_ratio = width / height if height > 0 else 0
            
            # Determine font characteristics based on image analysis
            font_candidates = self._analyze_image_features(img_gray, edges)
            
            results = []
            for font_name, confidence in font_candidates:
                font_result = self._create_font_result(font_name, 'unknown', confidence)
                results.append(font_result)
            
            return results if results else self._create_default_result()
            
        except Exception as e:
            logger.error(f"Fallback recognition failed: {str(e)}")
            return self._create_default_result()
    
    def _analyze_image_features(self, img_gray, edges) -> List[tuple]:
        """Analyze image features to suggest fonts"""
        # This is a simplified analysis
        # In production, you would use more sophisticated feature extraction
        
        total_edges = np.sum(edges > 0)
        img_size = img_gray.shape[0] * img_gray.shape[1]
        edge_ratio = total_edges / img_size if img_size > 0 else 0
        
        candidates = []
        
        if edge_ratio > 0.15:
            candidates.append(('Bold Sans-Serif', 0.7))
            candidates.append(('Impact', 0.65))
        else:
            candidates.append(('Helvetica', 0.6))
            candidates.append(('Arial', 0.58))
        
        return candidates
    
    def _create_font_result(self, font_name: str, font_type: str, confidence: float) -> Dict[str, Any]:
        """Create a standardized font result object"""
        sources = self._find_font_sources(font_name)
        
        return {
            'name': font_name,
            'type': font_type,
            'confidence': min(confidence, 1.0),
            'sources': sources
        }
    
    def _create_default_result(self) -> List[Dict[str, Any]]:
        """Create default result when recognition fails"""
        return [{
            'name': 'Unable to determine',
            'type': 'unknown',
            'confidence': 0,
            'sources': []
        }]
    
    def _find_font_sources(self, font_name: str) -> List[Dict[str, str]]:
        """Find available sources for a font"""
        sources = []
        font_query = font_name.replace(' ', '+')
        
        for source_name, source_info in self.font_sources.items():
            search_url = source_info['search_pattern'].format(query=font_query)
            sources.append({
                'name': source_name,
                'url': search_url,
                'availability': source_info['type'],
                'baseUrl': source_info['url']
            })
        
        return sources
    
    def get_font_characteristics(self, font_name: str) -> Dict[str, Any]:
        """Get detailed characteristics of a font"""
        # This would connect to a font database
        return {
            'name': font_name,
            'description': 'Font description would go here',
            'type': 'unknown',
            'weights': [],
            'styles': [],
            'languages': []
        }
