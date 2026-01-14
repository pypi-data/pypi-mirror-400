from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from segsoup.strategies.greedy import greedy_soup
from segsoup.strategies.uniform import uniform_soup
from segsoup.strategies.weighted import weighted_soup

class Strategy(Enum):
    UNIFORM = "uniform"
    WEIGHTED = "weighted"
    GREEDY = "greedy"

def get_segmentation_soup(state_dicts: List[Dict[str, Any]], strategy: str, weights: Optional[List[float]] = None, 
                          evaluate_fn: Optional[Callable[[Dict[str, Any]], float]] = None, verbose: bool= False):
    """
    Builds a model soup from a list of segmentation model checkpoints.

    Depending on the selected strategy, it combines multiple model `state_dict`s 
    into a single averaged checkpoint ("model soup").

    Supported strategies:
    - "uniform": uniform average of all checkpoints.
    - "weighted": weighted average of all checkpoints using user-provided weights.
    - "greedy": greedy model soup that iteratively adds checkpoints if they improve
      a user-defined evaluation metric.

    Args:
        state_dicts (List[Dict[str, Any]]):
            List of model state_dicts. All state_dicts are assumed to be compatible
            (same architecture, same parameter keys and shapes).

        strategy (str or Strategy):
            Soup strategy to apply. One of {"uniform", "weighted", "greedy"}.

        weights (List[float] = None):
            Weights used for the "weighted" strategy. Must have the same length as
            `state_dicts` and sum to 1.0. Ignored for other strategies.

        evaluate_fn ([Callable[[Dict[str, Any]], float]] = None):
            Evaluation function required for the "greedy" strategy.
            It must take a state_dict as input and return a scalar score
            (higher is better). Ignored for other strategies.

        verbose (bool = False):
            If True, prints progress information during greedy soup construction.

    Returns:
        soup_state_dict (Dict[str, torch.Tensor]):
            The resulting averaged state_dict.

        score (float):
            Final evaluation score of the greedy soup. None for uniform and weighted strategies.

        selected_indices (List[int]):
            Indices of the checkpoints selected by the greedy strategy.
            None for uniform and weighted strategies.

    Raises:
        ValueError
            If inputs are invalid, required arguments are missing, or the strategy is unknown.
    """
    if not state_dicts:
        raise ValueError("state_dicts must contain at least one element.")
    
    if isinstance(strategy, str):
        strat = Strategy(strategy.lower())
    elif isinstance(strategy, Strategy):
        strat = strategy
    else:
        raise ValueError("strategy must be a Strategy or str")
    
    if strat is Strategy.UNIFORM:
        soup = uniform_soup(state_dicts)
        return soup, None, None
    
    if strat is Strategy.WEIGHTED:

        if weights is None or len(weights) == 0:
            raise ValueError("The 'weighted' strategy requires a non-empty list of weights.")
        
        if len(weights) != len(state_dicts):
            raise ValueError(f"Mismatch between models and weights: "
            f"received {len(state_dicts)} state_dicts but {len(weights)} weights.")

        soup = weighted_soup(state_dicts, weights)
        return soup, None, None

    if strat is Strategy.GREEDY:
        soup, score, selected = greedy_soup(state_dicts, evaluate_fn=evaluate_fn, verbose=verbose)
        return soup, score, selected

    raise ValueError(f"Unknown strategy: {strat}")
