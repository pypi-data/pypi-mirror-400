"""Eval resource classes for API clients."""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from ..models import ClassificationClass, NumericRange
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import AratoClient, AsyncAratoClient # noqa: F401


class EvalsResource(BaseResource):
    """Handles operations related to experiment evaluations (evals)."""

    def list(self, *, notebook_id: str, experiment_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """List all evals for a specific experiment."""
        return self._get(f"/notebooks/{notebook_id}/experiments/{experiment_id}/evals")

    def create(
        self,
        *,
        notebook_id: str,
        experiment_id: str,
        name: str,
        eval_type: Literal["Numeric", "Binary", "Classification", "Similarity"],
        context: str = "prompt_and_response",
        prompt: Optional[str] = None,
        ranges: Optional[List[NumericRange]] = None,
        fail_on_positive: Optional[bool] = None,
        classes: Optional[List[ClassificationClass]] = None,
        validator_type: Optional[Literal["cosine", "jaccard"]] = None,
        threshold: Optional[float] = None,
        compare_to_field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new evaluation configuration for an experiment.

        Args:
            notebook_id: ID of the notebook.
            experiment_id: ID of the experiment.
            name: Name of the eval.
            eval_type: Type of the eval ("Numeric", "Binary", "Classification", or "Similarity").
            context: The data the eval receives (e.g., "response").
            prompt: The prompt used for model-based evals (not used for Similarity).
            ranges: Score ranges for "Numeric" evals.
            fail_on_positive: For "Binary" evals, if true, "yes" indicates failure.
            classes: Categories for "Classification" evals.
            validator_type: Similarity algorithm for "Similarity" evals ("cosine" or "jaccard").
            threshold: Similarity threshold percentage (0-100) for "Similarity" evals.
            compare_to_field: Field name to compare against for "Similarity" evals.

        Returns:
            The created eval object.
        """
        payload: Dict[str, Any] = {"name": name, "eval_type": eval_type, "context": context}
        if prompt:
            payload["prompt"] = prompt
        if ranges:
            payload["ranges"] = ranges
        if fail_on_positive is not None:
            payload["fail_on_positive"] = fail_on_positive
        if classes:
            payload["classes"] = classes
        if validator_type:
            payload["validator_type"] = validator_type
        if threshold is not None:
            payload["threshold"] = threshold
        if compare_to_field:
            payload["compare_to_field"] = compare_to_field
        return self._post(
            f"/notebooks/{notebook_id}/experiments/{experiment_id}/evals",
            json=payload
        )

    def retrieve(
        self, *, notebook_id: str, experiment_id: str, eval_id: str
    ) -> Dict[str, Any]:
        """Retrieve a specific eval by ID."""
        return self._get(f"/notebooks/{notebook_id}/experiments/{experiment_id}/evals/{eval_id}")

    def update(
        self,
        *,
        notebook_id: str,
        experiment_id: str,
        eval_id: str,
        name: Optional[str] = None,
        context: Optional[str] = None,
        ranges: Optional[List[NumericRange]] = None,
        fail_on_positive: Optional[bool] = None,
        validator_type: Optional[Literal["cosine", "jaccard"]] = None,
        threshold: Optional[float] = None,
        compare_to_field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing evaluation configuration."""
        payload = {}
        if name:
            payload["name"] = name
        if context:
            payload["context"] = context
        if ranges:
            payload["ranges"] = ranges
        if fail_on_positive is not None:
            payload["fail_on_positive"] = fail_on_positive
        if validator_type:
            payload["validator_type"] = validator_type
        if threshold is not None:
            payload["threshold"] = threshold
        if compare_to_field:
            payload["compare_to_field"] = compare_to_field
        return self._put(
            f"/notebooks/{notebook_id}/experiments/{experiment_id}/evals/{eval_id}",
            json=payload
        )


class AsyncEvalsResource(AsyncBaseResource):
    """Handles async operations related to experiment evals."""

    async def list(
        self, *, notebook_id: str, experiment_id: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """List all evals for a specific experiment."""
        return await self._get(
            f"/notebooks/{notebook_id}/experiments/{experiment_id}/evals"
        )

    async def create(
        self,
        *,
        notebook_id: str,
        experiment_id: str,
        name: str,
        eval_type: Literal["Numeric", "Binary", "Classification", "Similarity"],
        context: str = "prompt_and_response",
        prompt: Optional[str] = None,
        ranges: Optional[List[NumericRange]] = None,
        fail_on_positive: Optional[bool] = None,
        classes: Optional[List[ClassificationClass]] = None,
        validator_type: Optional[Literal["cosine", "jaccard"]] = None,
        threshold: Optional[float] = None,
        compare_to_field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new evaluation configuration for an experiment."""
        payload: Dict[str, Any] = {"name": name, "eval_type": eval_type, "context": context}
        if prompt:
            payload["prompt"] = prompt
        if ranges:
            payload["ranges"] = ranges
        if fail_on_positive is not None:
            payload["fail_on_positive"] = fail_on_positive
        if classes:
            payload["classes"] = classes
        if validator_type:
            payload["validator_type"] = validator_type
        if threshold is not None:
            payload["threshold"] = threshold
        if compare_to_field:
            payload["compare_to_field"] = compare_to_field
        return await self._post(
            f"/notebooks/{notebook_id}/experiments/{experiment_id}/evals",
            json=payload
        )

    async def retrieve(
        self, *, notebook_id: str, experiment_id: str, eval_id: str
    ) -> Dict[str, Any]:
        """Retrieve a specific eval by ID."""
        return await self._get(
            f"/notebooks/{notebook_id}/experiments/{experiment_id}/evals/{eval_id}"
        )

    async def update(
        self,
        *,
        notebook_id: str,
        experiment_id: str,
        eval_id: str,
        name: Optional[str] = None,
        context: Optional[str] = None,
        ranges: Optional[List[NumericRange]] = None,
        fail_on_positive: Optional[bool] = None,
        validator_type: Optional[Literal["cosine", "jaccard"]] = None,
        threshold: Optional[float] = None,
        compare_to_field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing evaluation configuration."""
        payload = {}
        if name:
            payload["name"] = name
        if context:
            payload["context"] = context
        if ranges:
            payload["ranges"] = ranges
        if fail_on_positive is not None:
            payload["fail_on_positive"] = fail_on_positive
        if validator_type:
            payload["validator_type"] = validator_type
        if threshold is not None:
            payload["threshold"] = threshold
        if compare_to_field:
            payload["compare_to_field"] = compare_to_field
        return await self._put(
            f"/notebooks/{notebook_id}/experiments/{experiment_id}/evals/{eval_id}",
            json=payload
        )
