"""
AI Integration for API-ARM using GitHub Marketplace Models.
"""

import os
import json
from typing import Optional, Any
from openai import OpenAI

from ..models.endpoint import Endpoint, HTTPMethod
from .config import ConfigManager

class AIModel:
    """Supported GitHub Marketplace Models."""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    PHI_3_5_MINI = "Phi-3.5-mini-instruct"
    MISTRAL_LARGE = "Mistral-large"


class AIAnalyzer:
    """
    AI-powered API analysis using GitHub Marketplace Models.
    Requires GITHUB_TOKEN environment variable or local config.
    """
    
    BASE_URL = "https://models.inference.ai.azure.com"
    
    def __init__(self, token: Optional[str] = None, model: str = AIModel.GPT_4O_MINI):
        self._config = ConfigManager()
        self.token = token or os.environ.get("GITHUB_TOKEN") or self._config.github_token
        self.model = model
        
        if not self.token:
            raise ValueError(
                "GitHub Token is required for AI features. "
                "Please run 'apiarm setup' to configure it, "
                "or set the GITHUB_TOKEN environment variable."
            )
            
        self.client = OpenAI(
            base_url=self.BASE_URL,
            api_key=self.token,
        )

    def discover_endpoints(self, base_url: str, content: str) -> list[Endpoint]:
        """
        Use AI to discover endpoints from raw content (HTML/JSON).
        """
        prompt = f"""
        Analyze the following API response or documentation fragment from {base_url} 
        and extract any API endpoints, methods, and parameters you can infer.
        
        Guidelines:
        1. If the content is an OpenAPI/Swagger spec or HTML documentation, extract all listed endpoints.
        2. If the content is a JSON response from a successful API call, include the current path ({base_url}) as an endpoint and describe its purpose based on the data.
        3. If the content reflects a specific category (e.g., 'breeds', 'users'), infer common CRUD or list endpoints.
        4. If the content is an error message, infer the required parameters or correct endpoint structure.
        
        Return ONLY a raw JSON object with this structure:
        {{
            "endpoints": [
                {{
                    "path": "/path",
                    "method": "GET",
                    "description": "...",
                    "parameters": {{
                        "query": [{{ "name": "param", "required": true }}],
                        "body": null
                    }}
                }}
            ]
        }}
        
        Content:
        {content[:4000]}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert API analyzer."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            
            result_json = response.choices[0].message.content
            if not result_json:
                return []
                
            data = json.loads(result_json)
            endpoints = []
            
            for ep_data in data.get("endpoints", []):
                try:
                    # Validate method
                    method_str = ep_data.get("method", "GET").upper()
                    try:
                        method = HTTPMethod(method_str) 
                    except ValueError:
                        method = HTTPMethod.GET
                        
                    endpoint = Endpoint(
                        path=ep_data.get("path", "/"),
                        methods=[method],
                        description=ep_data.get("description", "AI inferred endpoint"),
                        parameters=ep_data.get("parameters", {}),
                        requires_auth=False # Assume public unless evidence otherwise
                    )
                    endpoints.append(endpoint)
                except Exception:
                    continue
                    
            return endpoints
            
        except Exception as e:
            print(f"AI Analysis failed: {e}")
            return []
