"""
Magpie Cloud - Create runtime workers and code sandboxes.
Visit https://magpiecloud.com for more information.
"""

import os
from typing import Optional, Dict, Any, List, Generator
from urllib.parse import urljoin

import requests
import json

from .exceptions import (
    AuthenticationError,
    JobNotFoundError,
    TemplateNotFoundError,
    APIError,
    ValidationError,
)
from .models import Job, JobRun, JobStatus, Template, LogEntry
from .resources import JobsResource, TemplatesResource


class Magpie:
    """
    Main client for interacting with Magpie Cloud API.

    Magpie Cloud helps you create runtime workers and code sandboxes.
    Visit https://magpiecloud.com for more information.

    Args:
        api_key: Your API key for authentication
        timeout: Request timeout in seconds (default: 30)
    """

    def __init__(
        self,
        api_key: str,
        timeout: int = 30
    ):
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = "https://api.magpiecloud.com"
        self.timeout = timeout
        
        # Initialize session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Magpie-SDK/0.1.0",
        })
        
        # Initialize resources
        self.jobs = JobsResource(self)
        self.templates = TemplatesResource(self)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
            )
            
            # Handle different response codes
            if response.status_code == 401:
                print(response)
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 404:
                if "job" in endpoint.lower():
                    raise JobNotFoundError(f"Job not found: {endpoint}")
                elif "template" in endpoint.lower():
                    raise TemplateNotFoundError(f"Template not found: {endpoint}")
                else:
                    raise APIError(f"Resource not found: {endpoint}")
            elif response.status_code == 422:
                error_data = self._safe_json(response)
                raise ValidationError(error_data.get("error", "Validation failed"))
            elif response.status_code >= 400:
                error_data = self._safe_json(response)
                raise APIError(
                    f"API error ({response.status_code}): {error_data.get('error', 'Unknown error')}"
                )
            
            data = self._safe_json(response)
            return data
        except requests.exceptions.Timeout:
            raise APIError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise APIError("Failed to connect to API")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
        except ValueError as e:
            raise APIError(f"Failed to decode response: {str(e)}")

    def _safe_json(self, response: requests.Response) -> Dict[str, Any]:
        if not response.text:
            return {}
        try:
            return response.json()
        except ValueError:
            return {}
    
    
    def test_connection(self) -> bool:
        """Test the connection and authentication."""
        try:
            self._make_request("GET", "/api/v1/health")
            return True
        except Exception:
            return False
