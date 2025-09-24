#!/usr/bin/env python3
"""
Perplexity API Client
Lightweight wrapper for Perplexity API with retry logic and error handling.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PerplexityAPIError(Exception):
    """Custom exception for Perplexity API errors"""
    pass


class PerplexityAPIClient:
    """Client for Perplexity API with retry logic and error handling"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Perplexity API client
        
        Args:
            api_key: Perplexity API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key or self.api_key == "your_perplexity_api_key_here":
            raise ValueError("Perplexity API key is required. Set PERPLEXITY_API_KEY environment variable or pass api_key parameter.")
        
        self.endpoint = "https://api.perplexity.ai/chat/completions"
        self.model = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def generate_content(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate content using Perplexity API
        
        Args:
            prompt: The prompt to send to the API
            model: Model to use (defaults to configured model)
            
        Returns:
            Generated content as string
            
        Raises:
            PerplexityAPIError: If API request fails
        """
        model = model or self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system", 
                    "content": "Be precise, concise, and provide actionable steps. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.1  # Low temperature for consistent, structured output
        }
        
        try:
            response = self.session.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            if "choices" not in data or not data["choices"]:
                raise PerplexityAPIError("No choices in API response")
            
            content = data["choices"][0]["message"]["content"]
            
            if not content:
                raise PerplexityAPIError("Empty content in API response")
            
            return content.strip()
            
        except requests.exceptions.RequestException as e:
            raise PerplexityAPIError(f"Network error: {e}")
        except json.JSONDecodeError as e:
            raise PerplexityAPIError(f"Invalid JSON response: {e}")
        except KeyError as e:
            raise PerplexityAPIError(f"Unexpected response structure: {e}")
        except Exception as e:
            raise PerplexityAPIError(f"Unexpected error: {e}")
    
    def query(self, query_text: str, model: str = None, max_tokens: int = 2048, temperature: float = 0.1) -> Dict[str, Any]:
        """
        Query method matching the provided API structure
        
        Args:
            query_text: The query text to send
            model: Model to use (defaults to configured model)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            API response as dictionary
        """
        model = model or self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Be precise, concise, and provide actionable steps."},
                {"role": "user", "content": query_text}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = self.session.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            return {"error": f"HTTP error occurred: {http_err}", "status_code": response.status_code}
        except Exception as err:
            return {"error": f"An error occurred: {err}"}
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get client information for debugging"""
        return {
            "client_type": "PerplexityAPIClient",
            "api_available": bool(self.api_key),
            "model": self.model,
            "endpoint": self.endpoint
        } 