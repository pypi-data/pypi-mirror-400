import os
from collections.abc import Sequence

from datasets import load_dataset

from .utils import DATA_DIR, string_length_mb


def download_hf_dataset(
    dataset_params: Sequence[str], *, split: str, path: str, max_mb: float = 100, column: str = "text"
) -> None:
    """
    Download a dataset from Hugging Face and save it into a single text file.

    Args:
        dataset_params: Parameters for the dataset to download.
        split: The split of the dataset to download, e.g. "train", "test", "validation".
        path: The path to save the dataset to.
        max_mb: The maximum size of the dataset to download in MB. Defaults to 100 MB.
        column: The column of the dataset to save. Defaults to "text".
    """

    os.makedirs(os.path.dirname(path), exist_ok=True)
    dataset = load_dataset(*dataset_params, split=split, streaming=True)

    written = 0
    with open(path, "w", encoding="utf-8") as f:
        for row in dataset:
            text = row.get(column, "").strip()  # type: ignore
            if not text:
                continue

            text += "\n"
            mb = string_length_mb(text)
            if written + mb > max_mb:
                print(f"Reached target bytes ({max_mb:.1f} MB). To download more data adjust `max_mb` parameter.")
                break

            f.write(text)
            written += mb

    print(f"Wrote {written:.1f} MB to {path}")


if __name__ == "__main__":
    download_hf_dataset(
        ["Salesforce/wikitext", "wikitext-103-raw-v1"],
        split="test",
        path=os.path.join(DATA_DIR, "wikitext-test.txt"),
        max_mb=100,
        column="text",
    )
