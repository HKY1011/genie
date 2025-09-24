import json
import os
import time
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors"""
    pass


class GeminiAPIClient:
    """Lightweight client wrapper for Google Gemini 2.0 Flash API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        """
        Initialize the Gemini API client
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY environment variable)
            base_url: Base URL for the Gemini API
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = base_url.rstrip('/')
        self.model = "models/gemini-2.0-flash"
        
        # Configure retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def generate_content(self, prompt: str, system_instruction: Optional[str] = None, 
                        temperature: float = 0.1, max_tokens: int = 4096) -> str:
        """
        Generate content using Gemini API
        
        Args:
            prompt: The main prompt to send to Gemini
            system_instruction: Optional system instruction
            temperature: Controls randomness (0.0 = deterministic, 1.0 = very random)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text content
            
        Raises:
            GeminiAPIError: If the API call fails
        """
        url = f"{self.base_url}/{self.model}:generateContent"
        
        # Prepare the request payload
        content_parts = []
        
        if system_instruction:
            content_parts.append({
                "text": system_instruction
            })
        
        content_parts.append({
            "text": prompt
        })
        
        payload = {
            "contents": [{
                "parts": content_parts
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }
        
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract the generated text
            if "candidates" in data and data["candidates"]:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
            
            raise GeminiAPIError("No content generated in response")
            
        except requests.exceptions.RequestException as e:
            raise GeminiAPIError(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise GeminiAPIError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            raise GeminiAPIError(f"Unexpected error: {str(e)}")
    
    def generate_json(self, prompt: str, system_instruction: Optional[str] = None, 
                     temperature: float = 0.1, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Generate JSON content using Gemini API
        
        Args:
            prompt: The main prompt to send to Gemini
            system_instruction: Optional system instruction
            temperature: Controls randomness
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Parsed JSON content as dictionary
            
        Raises:
            GeminiAPIError: If the API call fails or JSON is invalid
        """
        try:
            content = self.generate_content(prompt, system_instruction, temperature, max_tokens)
            
            # Try to extract JSON from the response
            # Look for JSON blocks marked with ```json or just try to parse the whole response
            if "```json" in content:
                # Extract JSON from code block
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end == -1:
                    end = len(content)
                json_str = content[start:end].strip()
            elif "```" in content:
                # Extract JSON from generic code block
                start = content.find("```") + 3
                end = content.find("```", start)
                if end == -1:
                    end = len(content)
                json_str = content[start:end].strip()
            else:
                # Try to parse the entire response as JSON
                json_str = content.strip()
            
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            raise GeminiAPIError(f"Failed to parse JSON response: {str(e)}\nContent: {content[:200]}...")
        except Exception as e:
            raise GeminiAPIError(f"Error generating JSON: {str(e)}")
    
    def health_check(self) -> bool:
        """
        Perform a health check on the API
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Simple test prompt
            response = self.generate_content("Respond with 'OK' if you can read this.")
            return "OK" in response or len(response.strip()) > 0
        except Exception:
            return False
    
    def get_client_info(self) -> Dict[str, Any]:
        """
        Get client information for debugging
        
        Returns:
            Dictionary with client information
        """
        return {
            "client_type": "GeminiAPIClient",
            "api_available": bool(self.api_key),
            "model": self.model,
            "base_url": self.base_url
        }


# Convenience function for quick API access
def get_gemini_client(api_key: Optional[str] = None) -> GeminiAPIClient:
    """
    Get a configured Gemini API client
    
    Args:
        api_key: Optional API key (defaults to environment variable)
        
    Returns:
        Configured GeminiAPIClient instance
    """
    return GeminiAPIClient(api_key=api_key) 