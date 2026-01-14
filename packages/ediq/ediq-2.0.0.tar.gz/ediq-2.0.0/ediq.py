"""
Ediq - AI Detection SDK
Official Python client for the Ediq AI detection API by Wyzcon

Supports two detection modes:
- Education: Essays, assignments, student work (with baselines)
- HR: Resumes, cover letters, LinkedIn profiles
"""

import requests
from typing import Optional, Dict, Any, Union, Literal
from pathlib import Path
from enum import Enum

__version__ = "2.0.0"


class EdiqError(Exception):
    """Base exception for Ediq SDK"""
    pass


class RateLimitError(EdiqError):
    """Raised when rate limit is exceeded"""
    pass


class AuthenticationError(EdiqError):
    """Raised when API key is invalid"""
    pass


class HRContextType(str, Enum):
    """Context types for HR detection"""
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    LINKEDIN = "linkedin_profile"
    OTHER = "other"


class Ediq:
    """
    Ediq AI Detection Client
    
    Supports two detection modes:
    - Education: For essays, assignments, student work
    - HR: For resumes, cover letters, LinkedIn profiles
    
    Simple usage:
        >>> from ediq import Ediq
        >>> client = Ediq("wyz_xxxxx")
        
        # Education detection
        >>> result = client.detect_edu("Essay text...")
        >>> print(result.probability)
        
        # HR detection  
        >>> result = client.detect_hr("Resume text...", context="resume")
        >>> print(result.probability)
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.wyzcon.com"):
        """
        Initialize Ediq client
        
        Args:
            api_key: Your Wyzcon API key (get from wyzcon.com)
            base_url: API base URL (default: https://api.wyzcon.com)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "User-Agent": f"ediq-python/{__version__}"
        })
    
    # =========================================================================
    # EDUCATION MODE - Essays, Assignments, Student Work
    # =========================================================================
    
    def detect_edu(
        self,
        text: str,
        *,
        student_id: Optional[str] = None,
        baseline: Optional[str] = None,
        include_report: bool = False,
        formal_mode: bool = False
    ) -> 'DetectionResult':
        """
        Detect AI-generated content in educational text (essays, assignments)
        
        Args:
            text: Text to analyze (minimum 50 characters)
            student_id: Optional student identifier for baseline comparison
            baseline: Optional baseline text for comparison
            include_report: Include comprehensive writing analysis
            formal_mode: Enable formal writing mode (reduces false positives)
            
        Returns:
            DetectionResult object with probability, assessment, etc.
            
        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            EdiqError: Other API errors
            
        Example:
            >>> result = client.detect_edu("Student essay text...")
            >>> print(f"AI: {result.probability}%")
            >>> print(f"Assessment: {result.assessment}")
        """
        payload = {
            "text": text,
            "mode": "education",
            "include_report": include_report,
            "formal_mode": formal_mode,
        }
        
        if student_id:
            payload["student_id"] = student_id
        if baseline:
            payload["student_baseline"] = baseline
        
        response = self._request("POST", "/detect/detect-ai/", json=payload)
        return DetectionResult(response)
    
    def detect_edu_file(
        self,
        file_path: Union[str, Path],
        *,
        student_id: Optional[str] = None,
        include_report: bool = False
    ) -> 'DetectionResult':
        """
        Detect AI content in an educational document file
        
        Args:
            file_path: Path to PDF, DOCX, or TXT file
            student_id: Optional student identifier
            include_report: Include comprehensive writing analysis
            
        Returns:
            DetectionResult object
            
        Example:
            >>> result = client.detect_edu_file("essay.pdf")
            >>> print(f"AI: {result.probability}%")
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f)}
            data = {'mode': 'education'}
            if student_id:
                data['student_id'] = student_id
            if include_report:
                data['include_report'] = 'true'
            
            response = self._request(
                "POST", 
                "/detect/detect-ai/",
                files=files,
                data=data,
                timeout=60
            )
        
        return DetectionResult(response)
    
    def detect_edu_image(
        self,
        image_path: Union[str, Path],
        *,
        student_id: Optional[str] = None,
        handwritten: bool = False
    ) -> 'DetectionResult':
        """
        Detect AI content in an educational image using OCR
        
        Args:
            image_path: Path to image file (JPG, PNG)
            student_id: Optional student identifier
            handwritten: True if image contains handwritten text
            
        Returns:
            DetectionResult object
            
        Example:
            >>> result = client.detect_edu_image("essay.jpg", handwritten=True)
            >>> print(f"AI: {result.probability}%")
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'image': (image_path.name, f)}
            data = {
                'mode': 'education',
                'input_type': 'handwritten' if handwritten else 'typed'
            }
            if student_id:
                data['student_id'] = student_id
            
            response = self._request(
                "POST",
                "/detect/detect-ai/",
                files=files,
                data=data,
                timeout=60
            )
        
        return DetectionResult(response)
    
    # =========================================================================
    # HR MODE - Resumes, Cover Letters, LinkedIn Profiles
    # =========================================================================
    
    def detect_hr(
        self,
        text: str,
        *,
        context: Union[str, HRContextType] = HRContextType.OTHER,
        include_report: bool = False
    ) -> 'DetectionResult':
        """
        Detect AI-generated content in HR documents (resumes, cover letters)
        
        Args:
            text: Text to analyze (minimum 50 characters)
            context: Document type - "resume", "cover_letter", "linkedin_profile", or "other"
            include_report: Include comprehensive writing analysis
            
        Returns:
            DetectionResult object with probability, assessment, etc.
            
        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            EdiqError: Other API errors
            
        Example:
            >>> result = client.detect_hr(resume_text, context="resume")
            >>> print(f"AI: {result.probability}%")
            >>> print(f"Assessment: {result.assessment}")
        """
        # Normalize context type
        if isinstance(context, HRContextType):
            context_str = context.value
        else:
            context_str = context.lower().replace(" ", "_")
        
        payload = {
            "text": text,
            "mode": "hr",
            "hr_context": context_str,
            "include_report": include_report,
        }
        
        response = self._request("POST", "/detect/detect-ai/", json=payload)
        return DetectionResult(response)
    
    def detect_hr_file(
        self,
        file_path: Union[str, Path],
        *,
        context: Union[str, HRContextType] = HRContextType.OTHER,
        include_report: bool = False
    ) -> 'DetectionResult':
        """
        Detect AI content in an HR document file
        
        Args:
            file_path: Path to PDF, DOCX, or TXT file (resume, cover letter, etc.)
            context: Document type - "resume", "cover_letter", "linkedin_profile", or "other"
            include_report: Include comprehensive writing analysis
            
        Returns:
            DetectionResult object
            
        Example:
            >>> result = client.detect_hr_file("resume.pdf", context="resume")
            >>> print(f"AI: {result.probability}%")
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Normalize context type
        if isinstance(context, HRContextType):
            context_str = context.value
        else:
            context_str = context.lower().replace(" ", "_")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f)}
            data = {
                'mode': 'hr',
                'hr_context': context_str,
            }
            if include_report:
                data['include_report'] = 'true'
            
            response = self._request(
                "POST", 
                "/detect/detect-ai/",
                files=files,
                data=data,
                timeout=60
            )
        
        return DetectionResult(response)
    
    # =========================================================================
    # BACKWARD COMPATIBLE METHODS (default to education mode)
    # =========================================================================
    
    def detect(
        self,
        text: str,
        *,
        student_id: Optional[str] = None,
        baseline: Optional[str] = None,
        include_report: bool = False,
        formal_mode: bool = False
    ) -> 'DetectionResult':
        """
        Detect AI-generated content in text (defaults to education mode)
        
        DEPRECATED: Use detect_edu() or detect_hr() instead for explicit mode selection.
        
        Args:
            text: Text to analyze (minimum 50 characters)
            student_id: Optional student identifier for baseline comparison
            baseline: Optional baseline text for comparison
            include_report: Include comprehensive writing analysis
            formal_mode: Enable formal writing mode (reduces false positives)
            
        Returns:
            DetectionResult object with probability, assessment, etc.
        """
        return self.detect_edu(
            text,
            student_id=student_id,
            baseline=baseline,
            include_report=include_report,
            formal_mode=formal_mode
        )
    
    def detect_file(
        self,
        file_path: Union[str, Path],
        *,
        student_id: Optional[str] = None,
        include_report: bool = False
    ) -> 'DetectionResult':
        """
        Detect AI content in a document file (defaults to education mode)
        
        DEPRECATED: Use detect_edu_file() or detect_hr_file() instead.
        """
        return self.detect_edu_file(
            file_path,
            student_id=student_id,
            include_report=include_report
        )
    
    def detect_image(
        self,
        image_path: Union[str, Path],
        *,
        student_id: Optional[str] = None,
        handwritten: bool = False
    ) -> 'DetectionResult':
        """
        Detect AI content in an image using OCR (education mode only)
        
        DEPRECATED: Use detect_edu_image() instead.
        """
        return self.detect_edu_image(
            image_path,
            student_id=student_id,
            handwritten=handwritten
        )
    
    # =========================================================================
    # USAGE & UTILITY
    # =========================================================================
    
    def usage(self) -> 'UsageInfo':
        """
        Get current API usage statistics
        
        Returns:
            UsageInfo object with scans used/limit
            
        Example:
            >>> usage = client.usage()
            >>> print(f"Used: {usage.used}/{usage.limit}")
        """
        response = self._request("GET", "/detect/usage/")
        return UsageInfo(response)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        timeout: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if 'files' in kwargs:
                # Don't set Content-Type for multipart
                headers = {k: v for k, v in self.session.headers.items() 
                          if k.lower() != 'content-type'}
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    timeout=timeout,
                    **kwargs
                )
            else:
                response = self.session.request(
                    method,
                    url,
                    timeout=timeout,
                    **kwargs
                )
            
            # Handle errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded. Please wait and try again.")
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    message = error_data.get('error', {}).get('message', 'Unknown error')
                    if isinstance(error_data.get('error'), str):
                        message = error_data.get('error')
                except:
                    message = response.text
                raise EdiqError(f"API error {response.status_code}: {message}")
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise EdiqError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise EdiqError("Connection failed")
        except requests.exceptions.RequestException as e:
            raise EdiqError(f"Request failed: {e}")


class DetectionResult:
    """Detection result object"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
    
    @property
    def probability(self) -> float:
        """AI probability (0-100)"""
        return self._data.get('probability', 0)
    
    @property
    def assessment(self) -> str:
        """Assessment category (likely_human, borderline, suspicious, likely_ai, highly_likely_ai)"""
        return self._data.get('assessment', 'unknown')
    
    @property
    def confidence(self) -> float:
        """Confidence score (0-100)"""
        return self._data.get('confidence', 0)
    
    @property
    def word_count(self) -> int:
        """Number of words analyzed"""
        return self._data.get('word_count', 0)
    
    @property
    def scan_id(self) -> Optional[int]:
        """Scan ID (if saved)"""
        return self._data.get('scan_id')
    
    @property
    def mode(self) -> str:
        """Detection mode used (education or hr)"""
        return self._data.get('mode', 'education')
    
    @property
    def report(self) -> Optional[Dict[str, Any]]:
        """Comprehensive writing report (if requested)"""
        return self._data.get('report')
    
    @property
    def layers(self) -> Dict[str, Any]:
        """Layer-by-layer detection breakdown"""
        return self._data.get('layer_summary', {})
    
    @property
    def baseline_similarity(self) -> Optional[float]:
        """Similarity to baseline (0-1, if baseline used) - Education mode only"""
        return self._data.get('similarity_score')
    
    @property
    def hr_context(self) -> Optional[str]:
        """HR document context type - HR mode only"""
        return self._data.get('hr_context')
    
    def __repr__(self):
        mode_str = f", mode='{self.mode}'" if self.mode else ""
        return f"DetectionResult(probability={self.probability}%, assessment='{self.assessment}'{mode_str})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Return raw response data"""
        return self._data


class UsageInfo:
    """Usage information object"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
    
    @property
    def used(self) -> int:
        """API scans used this period"""
        return self._data.get('usage', {}).get('api_scans_used', 0)
    
    @property
    def limit(self) -> int:
        """API scan limit for this period"""
        return self._data.get('usage', {}).get('api_scans_limit', 0)
    
    @property
    def remaining(self) -> int:
        """Remaining scans"""
        return max(0, self.limit - self.used)
    
    @property
    def period_start(self) -> str:
        """Period start date"""
        return self._data.get('usage', {}).get('period_start', '')
    
    @property
    def period_end(self) -> str:
        """Period end date"""
        return self._data.get('usage', {}).get('period_end', '')
    
    @property
    def tier(self) -> str:
        """Current API tier"""
        return self._data.get('api_tier_display', 'unknown')
    
    def __repr__(self):
        return f"UsageInfo(used={self.used}, limit={self.limit}, remaining={self.remaining}, tier='{self.tier}')"
