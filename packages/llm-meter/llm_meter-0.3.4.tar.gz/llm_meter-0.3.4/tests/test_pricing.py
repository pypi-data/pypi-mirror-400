from llm_meter.providers.pricing import calculate_cost


def test_calculate_cost_exact_match():
    # gpt-4o (2025): 0.0025 input, 0.010 output
    cost = calculate_cost("gpt-4o", 1000, 1000)
    assert cost == 0.0025 + 0.010


def test_calculate_cost_prefix_match():
    # gpt-5.2-2025-12-25 should match gpt-5.2
    # gpt-5.2: 0.00175 input, 0.014 output
    cost = calculate_cost("gpt-5.2-2025-12-25", 1000, 1000)
    assert cost == 0.00175 + 0.014


def test_calculate_cost_unknown_model():
    cost = calculate_cost("non-existent-model", 1000, 1000)
    assert cost == 0.0


def test_calculate_cost_small_amounts():
    # gpt-4o-mini: 0.00015 input, 0.0003 output
    cost = calculate_cost("gpt-4o-mini", 100, 200)
    # (100/1000 * 0.00015) + (200/1000 * 0.0003)
    # 0.000015 + 0.00006 = 0.000075
    assert cost == 0.000075
