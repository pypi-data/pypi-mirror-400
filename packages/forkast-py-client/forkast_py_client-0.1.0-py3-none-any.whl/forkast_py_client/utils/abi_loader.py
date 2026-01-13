import json
from importlib import resources

_ABI_CACHE: dict[str, dict] = {}


def load_abi(filename: str):
    """
    Load a contract ABI JSON file.

    :param filename: ABI JSON filename
    :return: Parsed ABI content
    """
    if not filename.endswith(".json"):
        raise ValueError(f"Invalid ABI filename: {filename}")

    if filename in _ABI_CACHE:
        return _ABI_CACHE[filename]

    try:
        abi_path = resources.files("forkast_py_client.abi").joinpath(filename)
        with abi_path.open("r", encoding="utf-8") as f:
            abi = json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"ABI file '{filename}' not found in forkast_py_client/abi")

    _ABI_CACHE[filename] = abi
    return abi
