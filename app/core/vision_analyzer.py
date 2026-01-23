"""
Computer Vision Analysis for Vanta
Profile image and visual content analysis using OpenCV and PIL
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageStat
import requests
from typing import Dict, Any, Optional, List
import logging
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

class VisionAnalysisError(Exception):
    """Vision analysis related errors"""
    pass

class VisionAnalyzer:
    """Computer vision analyzer for profile images and visual content"""
    
    def __init__(self):
        # Initialize face detection cascade
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
            logger.info("OpenCV cascades loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load OpenCV cascades: {e}")
            self.face_cascade = None
            self.eye_cascade = None
            self.smile_cascade = None
    
    def download_image(self, url: str) -> Optional[np.ndarray]:
        """Download image from URL and convert to OpenCV format"""
        try:
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Convert to PIL Image
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to OpenCV format (BGR)
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            return opencv_image, image
            
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return None, None
    
    def analyze_profile_image(self, image_url: str) -> Dict[str, Any]:
        """Comprehensive profile image analysis"""
        if not image_url:
            return {"error": "No image URL provided"}
        
        # Download image
        opencv_img, pil_img = self.download_image(image_url)
        if opencv_img is None:
            return {"error": "Failed to download image"}
        
        analysis = {
            "image_url": image_url,
            "image_properties": {},
            "face_analysis": {},
            "visual_features": {},
            "authenticity_indicators": {},
            "professional_assessment": {}
        }
        
        try:
            # Basic image properties
            analysis["image_properties"] = self._analyze_image_properties(pil_img)
            
            # Face detection and analysis
            if self.face_cascade is not None:
                analysis["face_analysis"] = self._analyze_faces(opencv_img)
            
            # Visual features
            analysis["visual_features"] = self._analyze_visual_features(opencv_img, pil_img)
            
            # Authenticity indicators
            analysis["authenticity_indicators"] = self._analyze_authenticity(opencv_img, pil_img)
            
            # Professional assessment
            analysis["professional_assessment"] = self._assess_professionalism(opencv_img, pil_img)
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            analysis["error"] = f"Analysis failed: {str(e)}"
        
        return analysis
    
    def _analyze_image_properties(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze basic image properties"""
        stats = ImageStat.Stat(image)
        
        return {
            "dimensions": {
                "width": image.width,
                "height": image.height,
                "aspect_ratio": round(image.width / image.height, 2)
            },
            "format": image.format or "Unknown",
            "mode": image.mode,
            "file_size_estimate": len(image.tobytes()),
            "color_statistics": {
                "mean_rgb": [round(mean, 1) for mean in stats.mean],
                "stddev_rgb": [round(std, 1) for std in stats.stddev],
                "median": [round(med, 1) for med in stats.median] if hasattr(stats, 'median') else None
            },
            "is_square": image.width == image.height,
            "is_landscape": image.width > image.height,
            "is_portrait": image.height > image.width
        }
    
    def _analyze_faces(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect and analyze faces in the image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        face_analysis = {
            "faces_detected": len(faces),
            "faces": []
        }
        
        for i, (x, y, w, h) in enumerate(faces):
            face_roi = gray[y:y+h, x:x+w]
            face_roi_color = image[y:y+h, x:x+w]
            
            face_info = {
                "face_id": i,
                "position": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "size_relative": round((w * h) / (image.shape[0] * image.shape[1]), 3),
                "center_position": {
                    "x": round((x + w/2) / image.shape[1], 2),
                    "y": round((y + h/2) / image.shape[0], 2)
                }
            }
            
            # Detect eyes in face
            if self.eye_cascade is not None:
                eyes = self.eye_cascade.detectMultiScale(face_roi)
                face_info["eyes_detected"] = len(eyes)
            
            # Detect smile
            if self.smile_cascade is not None:
                smiles = self.smile_cascade.detectMultiScale(face_roi, 1.8, 20)
                face_info["smile_detected"] = len(smiles) > 0
            
            # Face quality assessment
            face_info["quality"] = self._assess_face_quality(face_roi)
            
            face_analysis["faces"].append(face_info)
        
        # Overall face analysis
        if len(faces) > 0:
            largest_face = max(face_analysis["faces"], key=lambda f: f["size_relative"])
            face_analysis["primary_face"] = largest_face
            face_analysis["multiple_faces"] = len(faces) > 1
            face_analysis["face_centered"] = abs(largest_face["center_position"]["x"] - 0.5) < 0.2
        
        return face_analysis
    
    def _assess_face_quality(self, face_roi: np.ndarray) -> Dict[str, Any]:
        """Assess the quality of detected face"""
        # Calculate sharpness using Laplacian variance
        sharpness = cv2.Laplacian(face_roi, cv2.CV_64F).var()
        
        # Calculate brightness
        brightness = np.mean(face_roi)
        
        # Calculate contrast
        contrast = face_roi.std()
        
        return {
            "sharpness": round(sharpness, 2),
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "quality_score": round(min(sharpness / 100, 1.0), 2)  # Normalize to 0-1
        }
    
    def _analyze_visual_features(self, opencv_img: np.ndarray, pil_img: Image.Image) -> Dict[str, Any]:
        """Analyze visual features of the image"""
        # Color analysis
        mean_color = np.mean(opencv_img, axis=(0, 1))
        dominant_color = self._get_dominant_color(opencv_img)
        
        # Edge detection for complexity
        gray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Histogram analysis
        hist_b = cv2.calcHist([opencv_img], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([opencv_img], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([opencv_img], [2], None, [256], [0, 256])
        
        return {
            "color_analysis": {
                "mean_bgr": [round(float(c), 1) for c in mean_color],
                "dominant_color_bgr": [int(c) for c in dominant_color],
                "color_variety": self._calculate_color_variety(opencv_img)
            },
            "complexity": {
                "edge_density": round(edge_density, 4),
                "complexity_score": round(min(edge_density * 10, 1.0), 2)
            },
            "composition": {
                "brightness_distribution": self._analyze_brightness_distribution(gray),
                "contrast_level": round(gray.std() / 255, 2),
                "histogram_peaks": {
                    "blue": int(np.argmax(hist_b)),
                    "green": int(np.argmax(hist_g)),
                    "red": int(np.argmax(hist_r))
                }
            }
        }
    
    def _get_dominant_color(self, image: np.ndarray) -> np.ndarray:
        """Extract dominant color using k-means clustering"""
        try:
            # Reshape image to be a list of pixels
            pixels = image.reshape((-1, 3))
            pixels = np.float32(pixels)
            
            # Apply k-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(pixels, 3, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Get the dominant color (most frequent cluster center)
            dominant_color = centers[np.argmax(np.bincount(labels.flatten()))]
            
            return dominant_color
        except:
            # Fallback to mean color
            return np.mean(image, axis=(0, 1))
    
    def _calculate_color_variety(self, image: np.ndarray) -> float:
        """Calculate color variety in the image"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Calculate histogram for hue channel
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        
        # Calculate entropy as a measure of color variety
        hist_norm = hist / np.sum(hist)
        hist_norm = hist_norm[hist_norm > 0]  # Remove zeros
        entropy = -np.sum(hist_norm * np.log2(hist_norm))
        
        # Normalize to 0-1 range
        max_entropy = np.log2(180)
        return round(entropy / max_entropy, 3)
    
    def _analyze_brightness_distribution(self, gray: np.ndarray) -> Dict[str, float]:
        """Analyze brightness distribution"""
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        # Calculate distribution in brightness ranges
        dark = np.sum(hist[:85]) / np.sum(hist)  # 0-85
        medium = np.sum(hist[85:170]) / np.sum(hist)  # 85-170
        bright = np.sum(hist[170:]) / np.sum(hist)  # 170-255
        
        return {
            "dark_pixels": round(dark, 3),
            "medium_pixels": round(medium, 3),
            "bright_pixels": round(bright, 3)
        }
    
    def _analyze_authenticity(self, opencv_img: np.ndarray, pil_img: Image.Image) -> Dict[str, Any]:
        """Analyze image for authenticity indicators"""
        # Check for common signs of manipulation
        gray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
        
        # Calculate image noise
        noise = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Check for JPEG artifacts (simplified)
        # This would be more complex in a real implementation
        jpeg_quality_estimate = min(noise / 1000, 1.0)
        
        # Check for unnatural smoothness (possible AI generation)
        blur_detection = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return {
            "noise_level": round(noise, 2),
            "jpeg_quality_estimate": round(jpeg_quality_estimate, 2),
            "blur_score": round(blur_detection, 2),
            "potential_manipulation": {
                "high_smoothness": blur_detection < 100,
                "unusual_noise": noise < 50 or noise > 2000,
                "suspicious_patterns": False  # Placeholder for more advanced detection
            },
            "authenticity_score": round(min(max(noise / 500, 0.1), 1.0), 2)
        }
    
    def _assess_professionalism(self, opencv_img: np.ndarray, pil_img: Image.Image) -> Dict[str, Any]:
        """Assess professionalism of profile image"""
        # Basic professionalism indicators
        height, width = opencv_img.shape[:2]
        
        # Check if image is high resolution
        is_high_res = width >= 400 and height >= 400
        
        # Check aspect ratio (professional photos are often 1:1 or standard ratios)
        aspect_ratio = width / height
        standard_ratio = abs(aspect_ratio - 1.0) < 0.1 or abs(aspect_ratio - 1.5) < 0.1
        
        # Check if image is centered (faces should be centered for professional look)
        face_analysis = self._analyze_faces(opencv_img)
        is_centered = face_analysis.get("face_centered", False)
        
        # Check lighting quality
        gray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
        lighting_quality = gray.std() / 255  # Good lighting has moderate contrast
        
        professional_score = 0
        if is_high_res:
            professional_score += 0.3
        if standard_ratio:
            professional_score += 0.2
        if is_centered:
            professional_score += 0.3
        if 0.2 < lighting_quality < 0.8:
            professional_score += 0.2
        
        return {
            "is_high_resolution": is_high_res,
            "standard_aspect_ratio": standard_ratio,
            "face_centered": is_centered,
            "lighting_quality": round(lighting_quality, 2),
            "professional_score": round(professional_score, 2),
            "recommendations": self._get_professional_recommendations(
                is_high_res, standard_ratio, is_centered, lighting_quality
            )
        }
    
    def _get_professional_recommendations(self, is_high_res: bool, standard_ratio: bool, 
                                        is_centered: bool, lighting_quality: float) -> List[str]:
        """Get recommendations for improving professionalism"""
        recommendations = []
        
        if not is_high_res:
            recommendations.append("Use a higher resolution image (at least 400x400 pixels)")
        if not standard_ratio:
            recommendations.append("Consider using a square (1:1) aspect ratio for social media")
        if not is_centered:
            recommendations.append("Center your face in the frame")
        if lighting_quality < 0.2:
            recommendations.append("Improve lighting - the image appears too dark or flat")
        if lighting_quality > 0.8:
            recommendations.append("Reduce harsh lighting or shadows")
        
        if not recommendations:
            recommendations.append("Professional-looking profile image!")
        
        return recommendations

# Create singleton instance
vision_analyzer = VisionAnalyzer()