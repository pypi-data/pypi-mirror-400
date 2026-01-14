from typing import Any, Dict, List, Optional
import torch

def uniform_soup(state_dicts: List[Dict[str, Any]], weights: Optional[List[float]] = None) -> Dict[str, torch.Tensor]:
    """
    Computes a uniform (or weighted) average of model state_dicts.

    This function performs a parameter-wise weighted average of the given
    state_dicts. It assumes that all state_dicts share the same parameter keys
    and tensor shapes.

    Args:
        state_dicts (List[Dict[str, Any]]):
            List of compatible model state_dicts.

        weights (List[float], default=None):
            Averaging weights. If None, a uniform average is used.
            Must have the same length as `state_dicts` and sum to 1.0.

        Returns:
            soup_state_dict (Dict[str, torch.Tensor]):
                The averaged state_dict.

    Raises:
        ValueError
            If `state_dicts` is empty, weights are invalid, or their sum is not 1.0.

    Notes:
        - All values in the state_dicts must be `torch.Tensor`.
        - All state_dicts must be fully compatible.
        - Weights must sum exactly to 1.0.
    """

    if not state_dicts:
        raise ValueError("state_dicts must contain at least one element.")
    
    n = len(state_dicts)
    
    if weights is None:
        weights = [1.0 / n] * n
    
    if len(weights) != n:
        raise ValueError(f"Mismatch between models and weights: "
            f"received {len(state_dicts)} state_dicts but {len(weights)} weights.")

    s = sum(weights)
    if abs(s - 1.0) > 1e-6:
        raise ValueError(
            f"Invalid weights: values must sum to 1.0 (current sum: {sum(weights):.6f})."
        )

    sd = {k : state_dicts[0][k].clone() * weights[0] for k in state_dicts[0].keys()}
    for i in range(1, len(state_dicts)):
        for k in state_dicts[i].keys():
            sd[k] = sd[k] + state_dicts[i][k].clone() * weights[i]
    return sd
