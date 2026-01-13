"""Pricing information for various AI providers."""
from typing import Optional, Tuple

import requests

from . import getLogger
from .config import baseConf

logger = getLogger.getLogger(__name__, debug=baseConf.get("debug", False))

# Cache for OpenRouter pricing to avoid repeated API calls
_openrouter_pricing_cache = {}


def get_openrouter_pricing(model_id: str) -> Optional[dict]:
    """
    Fetch pricing for an OpenRouter model.

    Args:
        model_id: The model identifier (e.g., "anthropic/claude-sonnet-4.5")

    Returns:
        Dictionary with 'prompt' and 'completion' pricing per token, or None
    """
    # Check cache first
    if model_id in _openrouter_pricing_cache:
        return _openrouter_pricing_cache[model_id]

    api_key = baseConf.get('openrouter_api', '')
    if not api_key:
        logger.debug("No OpenRouter API key found")
        return None

    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        models_data = response.json()

        for model in models_data.get("data", []):
            if model["id"] == model_id:
                pricing = model.get("pricing", {})
                result = {
                    'prompt': float(pricing.get('prompt', 0)),
                    'completion': float(pricing.get('completion', 0)),
                    'request': float(pricing.get('request', 0))
                }
                # Cache it!
                _openrouter_pricing_cache[model_id] = result
                return result

        logger.debug(f"Model '{model_id}' not found in OpenRouter")
        return None

    except Exception as e:
        logger.debug(f"Failed to fetch OpenRouter pricing: {e}")
        return None


def get_model_pricing(model: str, provider: str = "") -> Tuple[float, float]:
    """
    Get pricing for a model (input cost per token, output cost per token).

    Args:
        model: Model identifier
        provider: Provider name (openai, openrouter, etc.)

    Returns:
        Tuple of (input_price_per_token, output_price_per_token)
    """
    per_k = 1000
    per_m = 1000 * per_k

    # Strip provider prefix if present in model name
    # This handles cases like "openrouter:anthropic/claude-sonnet-4.5"
    clean_model = model
    if ':' in model:
        clean_model = ':'.join(model.split(':')[1:])

    # OpenRouter pricing (dynamic)
    if provider == "openrouter":
        pricing = get_openrouter_pricing(clean_model)
        if pricing:
            return (pricing['prompt'], pricing['completion'])

    # Static pricing table (existing models)
    ppt_table = {
        '00:gpt-4o': (5 / per_m, 15 / per_m),
        '01:gpt-3': (0.5 / per_m, 1.5 / per_m),
        '02:gpt-4-turbo': (10 / per_m, 30 / per_m),
        '03:gpt-4-32k': (60 / per_m, 120 / per_m),
        '04:gpt-4-': (30 / per_m, 60 / per_m),
        '05:open-mistral-7b': (0.25 / per_m, 0.25 / per_m),
        '06:open-mixtral-8x7b': (0.7 / per_m, 0.7 / per_m),
        '07:open-mixtral-8x22b': (2 / per_m, 6 / per_m),
        '08:mistral-small': (1 / per_m, 3 / per_m),
        '09:mistral-medium': (2.7 / per_m, 8.1 / per_m),
        '10:mistral-large': (4 / per_m, 12 / per_m),
    }

    ppt_indexes_sorted = list(sorted(ppt_table.keys()))
    for index in ppt_indexes_sorted:
        model_start = ':'.join(index.split(':')[1:])
        if clean_model.startswith(model_start):
            return ppt_table[index]

    return (0.0, 0.0)
