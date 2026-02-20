from openai import AsyncOpenAI
import json
import logging
from ..core.settings import settings

import random

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        # We will initialize the client dynamically per request to support rotation
        self.base_url = settings.GITHUB_MODELS_BASE_URL

    def _get_api_client(self, api_key: str):
        """Returns a fresh client for a specific key"""
        return AsyncOpenAI(
            base_url=self.base_url,
            api_key=api_key
        )

    async def generate_completion(self, prompt: str, system_prompt: str = "", model: str = settings.MODEL_NAME) -> str:
        keys = settings.api_keys_list
        logger.info(f"Initializaing rotation pool with {len(keys)} tokens.")
        # Shuffle keys to distribute load, but iterate through them on failure
        shuffled_keys = random.sample(keys, len(keys)) if keys else [settings.GITHUB_MODELS_API_KEY]
        
        last_error = None
        for attempt, key in enumerate(shuffled_keys):
            masked_key = f"{key[:7]}...{key[-4:]}" if key and len(key) > 11 else "***"
            logger.info(f"Attempt {attempt + 1}/{len(shuffled_keys)} using token: {masked_key}")
            try:
                client = self._get_api_client(key)
                response = await client.chat.completions.create(
                    messages=[ 
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model=model,
                    temperature=0.7,
                    max_tokens=2000,
                    top_p=1,
                    timeout=15.0
                )
                return response.choices[0].message.content
            except Exception as e:
                error_str = str(e)
                last_error = e
                logger.warning(f"Token {masked_key} failed: {error_str}")
                continue 
        
        # If we get here, all tokens in the pool have failed
        failure_msg = f"Error: All {len(shuffled_keys)} tokens in the rotation pool failed. Last error: {last_error}"
        logger.error(failure_msg)
        return failure_msg

    async def generate_json(self, prompt: str, system_prompt: str, model: str = settings.MODEL_NAME) -> dict:
        try:
            response_text = await self.generate_completion(prompt, system_prompt, model)
            # Try to strip markdown code blocks if present
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}, Response: {response_text}")
            return {"error": "Invalid JSON response from LLM", "raw_response": response_text}
        except Exception as e:
            logger.error(f"Error generating JSON: {e}")
            return {"error": str(e)}
