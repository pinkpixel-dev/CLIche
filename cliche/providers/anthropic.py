"""
Anthropic provider implementation
"""
import os
from typing import Dict, List, Tuple
import anthropic
from .base import LLMBase

class AnthropicProvider(LLMBase):
    def __init__(self, config):
        # Check if config is a Config object or a dictionary
        if hasattr(config, 'get_provider_config'):
            # Config object
            provider_config = config.get_provider_config('anthropic')
        else:
            # Dictionary
            provider_config = config
            
        # Initialize with the provider config
        super().__init__(provider_config)
        
        # Initialize Anthropic client
        api_key = provider_config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # Set default model if not specified
        if 'model' not in self.config:
            self.config['model'] = 'claude-3-opus-20240229'

    async def ask(self, message, system_prompt=None, include_sys_info=False, professional_mode=False):
        """Ask the LLM a question and get a response.
        This method is called by CLIche's ask_llm and ask_with_memory methods.
        """
        return await self.generate_response(message, include_sys_info, professional_mode)

    async def generate_response(self, query: str, include_sys_info: bool = False, professional_mode: bool = False) -> str:
        try:
            # Get system context
            system_context = self.get_system_context(include_sys_info, professional_mode)
            
            response = self.client.messages.create(
                model=self.config['model'],
                system=system_context,  # Anthropic uses a separate system parameter
                messages=[
                    {"role": "user", "content": query}
                ],
                max_tokens=self.config.get('max_tokens', 1000)  # Use our new default
            )
            return response.content[0].text
        except Exception as e:
            return f"Anthropic Error: {str(e)}"

    async def list_models(self) -> List[Tuple[str, str]]:
        """List available Anthropic models."""
        # Anthropic doesn't have a models list API, so we hardcode the latest models
        models = [
            ("claude-3.5-sonnet-20240307", "Most capable model, best for complex tasks"),
            ("claude-3.5-haiku-20240307", "Fast and efficient model"),
            ("claude-3.5-opus-20240307", "Research and academic writing model"),
            ("claude-3.5-sonnet-latest", "Latest Sonnet model (auto-updates)"),
            ("claude-3.5-haiku-latest", "Latest Haiku model (auto-updates)"),
            ("claude-3.5-opus-latest", "Latest Opus model (auto-updates)")
        ]
        return models
