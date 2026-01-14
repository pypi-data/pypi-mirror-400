import torch
from typing import Any, Callable, Dict, List, Tuple

from segsoup.strategies.uniform import uniform_soup

def greedy_soup(
    state_dicts: List[Dict[str, Any]],
    evaluate_fn: Callable[[Dict[str, Any]], float],
    verbose: bool = False
) -> Tuple[Dict[str, torch.Tensor], float, List[int]]:
    """
    Constructs a greedy model soup from a list of checkpoints.

    The greedy strategy works as follows:
    1. Evaluate each checkpoint individually using `evaluate_fn`.
    2. Sort checkpoints by descending score.
    3. Start with the best individual checkpoint.
    4. Iteratively try adding remaining checkpoints (uniformly averaged);
       a checkpoint is kept only if it improves the evaluation score.

    This strategy requires instantiating and evaluating models via `evaluate_fn`,
    which must be user-defined.

    Args:
        state_dicts (List[Dict[str, Any]]):
            List of compatible model state_dicts.

        evaluate_fn (Callable[[Dict[str, Any]], float]):
            Function that evaluates a model checkpoint.
            It must accept a state_dict and return a scalar score
            (higher is better).

        verbose (bool = False):
            If True, prints detailed information about the greedy selection process.

    Returns:
        soup_state_dict (Dict[str, torch.Tensor]):
            The final greedy-averaged state_dict.

        best_score (float):
            Evaluation score of the final greedy soup.

        selected_indices (List[int]):
            Indices of the checkpoints selected during the greedy process.

    Raises:
        ValueError
            If `state_dicts` is empty or `evaluate_fn` is not provided.
    """


    if not state_dicts:
        raise ValueError("state_dicts must contain at least one element.")
    
    if evaluate_fn is None:
        raise ValueError("evaluate_fn is required for greedy strategy")

    scores = []
    for i, sd in enumerate(state_dicts):
        score = evaluate_fn(sd)
        scores.append(score)
        if verbose:
            print(f"Individual model {i} -> score {score: .4f}")

    order = sorted(range(len(state_dicts)), key=lambda i: scores[i], reverse=True)
    if verbose:
        print(f"Order by individual score: {order}")

    selected = [order[0]]
    current_soup = uniform_soup([state_dicts[selected[0]]])
    current_score = scores[selected[0]]

    if verbose:
        print(f"Starting with model {selected[0]} (score={current_score: .4f})")

    for idx in order[1:]:
        candidate_idxs = selected + [idx]
        candidate_sd = uniform_soup([state_dicts[i] for i in candidate_idxs])
        candidate_score = evaluate_fn(candidate_sd)
        if verbose:
            print(f"Trying to add {idx} -> candidate score {candidate_score}")
        if candidate_score > current_score:
            selected.append(idx)
            current_soup = candidate_sd
            current_score = candidate_score
            if verbose:
                print(f"Accepted {idx} -> new score {current_score: .4f}")
        else:
            if verbose:
                print(f"Rejected {idx} (no improvement)")

    return current_soup, current_score, selected