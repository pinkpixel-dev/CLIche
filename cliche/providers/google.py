"""
Google provider implementation
"""
import os
from typing import Dict, List, Tuple
import google.generativeai as genai
from .base import LLMBase

class GoogleProvider(LLMBase):
    def __init__(self, config):
        # Check if config is a Config object or a dictionary
        if hasattr(config, 'get_provider_config'):
            # Config object
            provider_config = config.get_provider_config('google')
        else:
            # Dictionary
            provider_config = config
            
        # Initialize with the provider config
        super().__init__(provider_config)
        
        # Configure Google API with the provider config
        api_key = provider_config.get('api_key') or os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)

    async def ask(self, message, system_prompt=None, include_sys_info=False, professional_mode=False):
        """Ask the LLM a question and get a response.
        This method is called by CLIche's ask_llm and ask_with_memory methods.
        """
        return await self.generate_response(message, include_sys_info, professional_mode)

    async def generate_response(self, query: str, include_sys_info: bool = False, professional_mode: bool = False) -> str:
        try:
            model_name = self.config.get('model', 'gemini-pro')
            model = genai.GenerativeModel(model_name)
            
            # Get system context
            system_context = self.get_system_context(include_sys_info, professional_mode)
            
            # Create content with proper format
            response = model.generate_content(
                contents=[
                    {"role": "user", "parts": [{"text": f"System: {system_context}\n\nUser: {query}"}]}
                ]
            )
            return response.text
        except Exception as e:
            return f"Google Error: {str(e)}"

    async def list_models(self) -> List[Tuple[str, str]]:
        """List available Google models."""
        try:
            models = [
                ("gemini-2.0-pro", "Most capable model, best for complex tasks"),
                ("gemini-2.0-vision", "Vision and text model"),
                ("gemini-2.0-pro-latest", "Latest Pro model (auto-updates)"),
                ("gemini-2.0-vision-latest", "Latest Vision model (auto-updates)"),
                ("gemini-2.0-flash", "Fast and efficient model"),
                ("gemini-2.0-flash-latest", "Latest Flash model (auto-updates)")
            ]
            return models
        except Exception as e:
            return [("Error", f"Failed to fetch models: {str(e)}")]
