from pathlib import Path
from . import _jonesum


def _load_vocabulary():
    package_dir = Path(__file__).parent
    vocabulary_file = package_dir / "vocabulary.txt"

    if not vocabulary_file.exists():
        vocabulary_file = package_dir / ".." / ".." / "src" / "vocabulary.txt"

    if not vocabulary_file.exists():
        raise FileNotFoundError(
            f"Could not find vocabulary.txt file. Looked in: {vocabulary_file}"
        )

    with open(vocabulary_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    return [line.strip() for line in lines if line.strip()]


class AlexJones:
    def __init__(self):
        vocabulary = _load_vocabulary()
        self._jonesum = _jonesum.Jonesum(vocabulary)

    def rant(self, sentence_count=None):
        if sentence_count is None:
            return self._jonesum.rant()
        return self._jonesum.rant(count=sentence_count)


Alex_Jones = AlexJones

__all__ = ["AlexJones", "Alex_Jones"]
