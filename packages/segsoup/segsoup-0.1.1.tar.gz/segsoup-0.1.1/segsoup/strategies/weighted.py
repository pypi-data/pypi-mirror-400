from typing import Any, Dict, List
import torch

from segsoup.strategies.uniform import uniform_soup

def weighted_soup(state_dicts: List[Dict[str, Any]], weights: List[float]) -> Dict[str, torch.Tensor]:
    """
    Compute a weighted model soup from a list of checkpoints.

    This is a thin wrapper around `uniform_soup` that requires explicit weights.
    It exists mainly for semantic clarity and API completeness.

    Args:
        state_dicts (List[Dict[str, Any]]):
            List of compatible model state_dicts.

        weights (List[float]):
            Averaging weights. Must have the same length as `state_dicts`
            and sum to 1.0.

    Returns:
        soup_state_dict (Dict[str, torch.Tensor]):
            The weighted-averaged state_dict.

    Raises:
        ValueError
            If weights are invalid or incompatible with `state_dicts`.
    """
    return uniform_soup(state_dicts, weights)