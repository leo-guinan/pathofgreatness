"""OpenRouter API client."""
import os
import json
import asyncio
from typing import Dict, Optional
import httpx
from models import calculate_cost


class OpenRouterClient:
    """Client for OpenRouter API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY must be set")

        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku")

    async def chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        max_retries: int = 3
    ) -> Dict:
        """Make a chat completion request to OpenRouter with retry logic."""
        model = model or self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://greatness-path.app",
            "X-Title": "The Greatness Path"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        last_error = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()

                # Extract response
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                })

                # Calculate cost
                cost = calculate_cost(usage, model)

                return {
                    "content": content,
                    "usage": usage,
                    "cost": cost,
                    "model": model
                }

            except (httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectError,
                    httpx.ReadError, ConnectionError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                    print(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"API call failed after {max_retries} attempts: {e}")
                    raise Exception(f"OpenRouter API failed after {max_retries} retries: {str(e)}")

            except Exception as e:
                # For other errors (like HTTP 500), don't retry
                print(f"API call failed with non-retryable error: {e}")
                raise

        # Should never reach here, but just in case
        raise Exception(f"OpenRouter API failed: {str(last_error)}")

    async def analyze_person(self, person: str, prompts: dict) -> Dict:
        """Analyze an admired person to determine Order."""
        messages = [
            {"role": "system", "content": prompts["system"]},
            {"role": "user", "content": prompts["user"]}
        ]

        response = await self.chat_completion(
            messages=messages,
            temperature=prompts["temperature"],
            max_tokens=1000
        )

        # Parse JSON response
        try:
            content = response["content"].strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nContent: {response['content']}")

        return {
            "order": data.get("order"),
            "archetypes": data.get("archetypes", []),
            "explanation": data.get("explanation", ""),
            "traits": data.get("admired_person_traits", []),
            "usage": response["usage"],
            "cost": response["cost"],
            "model": response["model"]
        }

    async def attempt_trial(self, prompts: dict) -> Dict:
        """AI attempts a trial."""
        messages = [
            {"role": "system", "content": prompts["system"]},
            {"role": "user", "content": prompts["user"]}
        ]

        response = await self.chat_completion(
            messages=messages,
            temperature=prompts["temperature"],
            max_tokens=3000
        )

        return {
            "submission": response["content"],
            "usage": response["usage"],
            "cost": response["cost"],
            "model": response["model"]
        }

    async def evaluate_trial(self, prompts: dict) -> Dict:
        """Evaluate a trial submission."""
        messages = [
            {"role": "system", "content": prompts["system"]},
            {"role": "user", "content": prompts["user"]}
        ]

        response = await self.chat_completion(
            messages=messages,
            temperature=prompts["temperature"],
            max_tokens=1500
        )

        # Parse JSON response
        try:
            content = response["content"].strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nContent: {response['content']}")

        return {
            "evaluation": data,
            "usage": response["usage"],
            "cost": response["cost"],
            "model": response["model"]
        }

    async def provide_feedback(self, prompts: dict) -> Dict:
        """Provide feedback on a trial attempt."""
        messages = [
            {"role": "system", "content": prompts["system"]},
            {"role": "user", "content": prompts["user"]}
        ]

        response = await self.chat_completion(
            messages=messages,
            temperature=prompts["temperature"],
            max_tokens=1000
        )

        return {
            "feedback": response["content"],
            "usage": response["usage"],
            "cost": response["cost"],
            "model": response["model"]
        }

    async def generate_narrative(self, prompts: dict, max_tokens: int = 500) -> Dict:
        """Generate narrative text (chapter intro, transformation, timeline)."""
        messages = [
            {"role": "system", "content": prompts["system"]},
            {"role": "user", "content": prompts["user"]}
        ]

        response = await self.chat_completion(
            messages=messages,
            temperature=prompts["temperature"],
            max_tokens=max_tokens
        )

        return {
            "narrative": response["content"],
            "usage": response["usage"],
            "cost": response["cost"],
            "model": response["model"]
        }
