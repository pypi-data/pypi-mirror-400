#!/usr/bin/env python3
"""Quick test to verify Similarity eval type support."""
from typing import get_type_hints, get_args
import inspect
from arato_client.resources.evals import EvalsResource, AsyncEvalsResource


def test_similarity_eval_sync():
    """Test that sync create method accepts Similarity eval type."""
    # Get the type hints for the create method
    hints = get_type_hints(EvalsResource.create)
    eval_type_hint = hints.get('eval_type')

    # Get the literal values
    if hasattr(eval_type_hint, '__args__'):
        eval_types = get_args(eval_type_hint)
        print(f"✓ Sync create method eval_type options: {eval_types}")
        assert "Similarity" in eval_types, "Similarity should be in eval_type options"

    # Check that the method signature includes the new parameters
    sig = inspect.signature(EvalsResource.create)
    params = sig.parameters

    assert "validator_type" in params, "validator_type parameter should exist"
    assert "threshold" in params, "threshold parameter should exist"
    assert "compare_to_field" in params, "compare_to_field parameter should exist"

    print("✓ Sync create method has validator_type, threshold, and compare_to_field parameters")

    # Check update method
    update_sig = inspect.signature(EvalsResource.update)
    update_params = update_sig.parameters

    assert "validator_type" in update_params, "validator_type parameter should exist in update"
    assert "threshold" in update_params, "threshold parameter should exist in update"
    assert "compare_to_field" in update_params, "compare_to_field parameter should exist in update"

    print("✓ Sync update method has validator_type, threshold, and compare_to_field parameters")


def test_similarity_eval_async():
    """Test that async create method accepts Similarity eval type."""
    # Get the type hints for the create method
    hints = get_type_hints(AsyncEvalsResource.create)
    eval_type_hint = hints.get('eval_type')

    # Get the literal values
    if hasattr(eval_type_hint, '__args__'):
        eval_types = get_args(eval_type_hint)
        print(f"✓ Async create method eval_type options: {eval_types}")
        assert "Similarity" in eval_types, "Similarity should be in eval_type options"

    # Check that the method signature includes the new parameters
    sig = inspect.signature(AsyncEvalsResource.create)
    params = sig.parameters

    assert "validator_type" in params, "validator_type parameter should exist"
    assert "threshold" in params, "threshold parameter should exist"
    assert "compare_to_field" in params, "compare_to_field parameter should exist"

    print("✓ Async create method has validator_type, threshold, and compare_to_field parameters")

    # Check update method
    update_sig = inspect.signature(AsyncEvalsResource.update)
    update_params = update_sig.parameters

    assert "validator_type" in update_params, "validator_type parameter should exist in update"
    assert "threshold" in update_params, "threshold parameter should exist in update"
    assert "compare_to_field" in update_params, "compare_to_field parameter should exist in update"

    print("✓ Async update method has validator_type, threshold, and compare_to_field parameters")


if __name__ == "__main__":
    print("Testing Similarity eval type support...\n")

    test_similarity_eval_sync()
    print()
    test_similarity_eval_async()

    print("\n✅ All tests passed! Similarity eval type is properly supported.")
