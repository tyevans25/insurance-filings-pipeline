"""
LLM Client Abstraction Layer
Supports both Anthropic Claude and Ollama endpoints with unified interface
"""

import os
from typing import Optional
import anthropic
import requests


class LLMClient:
    """Unified LLM client supporting Claude and Ollama"""
    
    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize LLM client
        
        Args:
            provider: 'claude' or 'ollama' (defaults to LLM_PROVIDER env var)
            api_key: API key (defaults to ANTHROPIC_API_KEY or OLLAMA_API_KEY)
            base_url: Base URL for Ollama (defaults to OLLAMA_BASE_URL env var)
            model: Model name (defaults to OLLAMA_MODEL env var for Ollama)
        """
        self.provider = provider or os.getenv('LLM_PROVIDER', 'claude')
        
        if self.provider == 'claude':
            self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-sonnet-4-20250514"
            
        elif self.provider == 'ollama':
            self.api_key = api_key or os.getenv('OLLAMA_API_KEY')
            self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'https://gpu-01.insight.gsu.edu:11443')
            self.model = model or os.getenv('OLLAMA_MODEL', 'llama3.1')
            
            if not self.api_key:
                raise ValueError("OLLAMA_API_KEY not found")
                
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.0
    ) -> str:
        """
        Generate completion from LLM
        
        Args:
            system_prompt: System/instruction prompt
            user_prompt: User query/prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        if self.provider == 'claude':
            return self._generate_claude(system_prompt, user_prompt, max_tokens, temperature)
        elif self.provider == 'ollama':
            return self._generate_ollama(system_prompt, user_prompt, max_tokens, temperature)
    
    def _generate_claude(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Claude API"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def _generate_ollama(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Ollama endpoint"""
        try:
            url = f"{self.base_url}/api/generate"
            
            # Combine system and user prompts for Ollama
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            print(f"[Ollama] Calling {url} with model {self.model}")
            
            response = requests.post(
                url, 
                json=payload, 
                headers=headers, 
                verify=False,  # Disable SSL verification for self-signed certs
                timeout=120  # 2 minute timeout for long responses
            )
            
            print(f"[Ollama] Response status: {response.status_code}")
            
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.HTTPError as e:
            print(f"[Ollama] HTTP Error: {e}")
            print(f"[Ollama] Response content: {e.response.text if e.response else 'No response'}")
            raise Exception(f"Ollama API HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"[Ollama] Request Error: {e}")
            raise Exception(f"Ollama API request error: {e}")
        except Exception as e:
            print(f"[Ollama] General Error: {e}")
            raise Exception(f"Ollama API error: {str(e)}")
    
    def get_provider_info(self) -> dict:
        """Return information about current provider"""
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": getattr(self, 'base_url', 'anthropic.com')
        }