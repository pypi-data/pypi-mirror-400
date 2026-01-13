from enum import Enum

from pydantic import BaseModel, ConfigDict


class OpenAIModel(str, Enum):
    """OpenAI active models (as of late 2025)."""

    # GPT-5.2 Family (Agentic Flagships)
    GPT_5_2_PRO = "gpt-5.2-pro"
    GPT_5_2 = "gpt-5.2"
    GPT_5_2_MINI = "gpt-5.2-mini"
    GPT_5_2_NANO = "gpt-5.2-nano"

    # GPT-5.1 Family
    GPT_5_1 = "gpt-5.1"
    GPT_5_1_MINI = "gpt-5.1-mini"

    # GPT-4.5
    GPT_4_5 = "gpt-4.5"

    # o3/o4 Family (Reasoning)
    O3_PRO = "o3-pro"
    O3 = "o3"
    O3_MINI = "o3-mini"
    O4_MINI = "o4-mini"

    # o1 Family
    O1_PRO = "o1-pro"
    O1 = "o1"
    O1_MINI = "o1-mini"

    # GPT-4.1 Family
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"

    # GPT-4o Family
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"


class AnthropicModel(str, Enum):
    """Anthropic active models based on latest 2025 status."""

    # Claude 4.5 (The latest flagships)
    CLAUDE_4_5_OPUS = "claude-4.5-opus"
    CLAUDE_4_5_SONNET = "claude-4.5-sonnet"
    CLAUDE_4_5_HAIKU = "claude-4.5-haiku"

    # Claude 4 / 4.1
    CLAUDE_4_1_OPUS = "claude-4.1-opus"
    CLAUDE_4 = "claude-4"

    # Claude 3.7 (Deprecated but still active)
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet"

    # Claude 3.5 (Only Haiku remains active)
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku"


# Backward compatibility alias
ModelName = OpenAIModel


class ModelPricing(BaseModel):
    model_config = ConfigDict(frozen=True)
    input_1k: float
    output_1k: float


# Pricing per 1k tokens (Refined for late 2025)
PRICING: dict[str, ModelPricing] = {
    # OpenAI
    OpenAIModel.GPT_5_2_PRO.value: ModelPricing(input_1k=0.021, output_1k=0.168),
    OpenAIModel.GPT_5_2.value: ModelPricing(input_1k=0.00175, output_1k=0.014),
    OpenAIModel.GPT_5_2_MINI.value: ModelPricing(input_1k=0.00025, output_1k=0.002),
    OpenAIModel.GPT_5_2_NANO.value: ModelPricing(input_1k=0.00005, output_1k=0.0004),
    OpenAIModel.GPT_5_1.value: ModelPricing(input_1k=0.00125, output_1k=0.010),
    OpenAIModel.GPT_4_5.value: ModelPricing(input_1k=0.075, output_1k=0.150),
    OpenAIModel.O3_PRO.value: ModelPricing(input_1k=0.020, output_1k=0.080),
    OpenAIModel.O3.value: ModelPricing(input_1k=0.002, output_1k=0.008),
    OpenAIModel.O3_MINI.value: ModelPricing(input_1k=0.0011, output_1k=0.0044),
    OpenAIModel.O4_MINI.value: ModelPricing(input_1k=0.0011, output_1k=0.0044),
    OpenAIModel.O1_PRO.value: ModelPricing(input_1k=0.150, output_1k=0.600),
    OpenAIModel.O1.value: ModelPricing(input_1k=0.015, output_1k=0.060),
    OpenAIModel.O1_MINI.value: ModelPricing(input_1k=0.0011, output_1k=0.0044),
    OpenAIModel.GPT_4O.value: ModelPricing(input_1k=0.0025, output_1k=0.010),
    OpenAIModel.GPT_4O_MINI.value: ModelPricing(input_1k=0.00015, output_1k=0.0003),
    # Anthropic (Based on active status)
    AnthropicModel.CLAUDE_4_5_OPUS.value: ModelPricing(input_1k=0.005, output_1k=0.025),
    AnthropicModel.CLAUDE_4_5_SONNET.value: ModelPricing(input_1k=0.003, output_1k=0.015),
    AnthropicModel.CLAUDE_4_5_HAIKU.value: ModelPricing(input_1k=0.001, output_1k=0.005),
    AnthropicModel.CLAUDE_4_1_OPUS.value: ModelPricing(input_1k=0.015, output_1k=0.075),
    AnthropicModel.CLAUDE_4.value: ModelPricing(input_1k=0.003, output_1k=0.015),
    AnthropicModel.CLAUDE_3_7_SONNET.value: ModelPricing(input_1k=0.003, output_1k=0.015),
    AnthropicModel.CLAUDE_3_5_HAIKU.value: ModelPricing(input_1k=0.0008, output_1k=0.004),
}


def calculate_cost(model: str | OpenAIModel | AnthropicModel, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate the estimated cost for a given model and token count.
    Supports prefix matching to handle versioned strings.
    """
    pricing = None
    model_str = str(model)

    # 1. Try exact match
    pricing = PRICING.get(model_str)

    # 2. Try prefix match if exact match fails
    if not pricing:
        # Sort by length descending to match most specific prefix first
        sorted_keys = sorted(PRICING.keys(), key=len, reverse=True)
        for key in sorted_keys:
            if model_str.startswith(key):
                pricing = PRICING[key]
                break

    if not pricing:
        return 0.0

    cost = (input_tokens / 1000 * pricing.input_1k) + (output_tokens / 1000 * pricing.output_1k)
    return round(cost, 6)
