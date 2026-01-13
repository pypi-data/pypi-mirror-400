from pathlib import Path


def get_include() -> str:
    """Get the path to the simde-py include directory.

    Returns:
        str: The path to the include directory.
    """
    return str(Path(__file__).parent / "simde")
