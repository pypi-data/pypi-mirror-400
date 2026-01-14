import os
from typing import Any, Dict
import torch

MODEL_EXTENSIONS = ['.pt', '.pth', '.bin', '.ckpt']

def load_weights(path: str, verbose: bool=False) -> Dict[str, Any]:
    """
    Loads PyTorch model weight files from a directory.

    This function scans the specified directory and loads each file using
    `torch.load`. The loaded objects are assumed to be PyTorch state_dicts
    or checkpoints and are mapped to the appropriate device (GPU if available,
    otherwise CPU).

    Args:
        path (str):
            Path to the directory containing the model weight files.

        verbose (bool):
            If True, prints the path of each loaded file. Defaults to False.

    Returns:
        list:
            A list of loaded PyTorch objects (typically state_dicts or checkpoints),
            ordered alphabetically by filename.

    Notes:
        - Invalid or corrupted files will raise an exception during loading.
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    state_dicts = []
    
    files = sorted(
        f for f in os.listdir(path)
        if f.lower().endswith(tuple(ext.lower() for ext in MODEL_EXTENSIONS))
    )

    for f in files:
        model_path = os.path.join(path, f)
        state_dicts.append(torch.load(model_path, map_location=device))
        if verbose:
            print(f'Loaded {model_path}')

    return state_dicts