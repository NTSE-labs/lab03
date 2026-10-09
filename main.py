"""Точка входа: запускает пункты 1--3 лабораторной работы."""

from pathlib import Path

from annotation import create_dataset_annotation
from class_named_copy import copy_dataset_with_class_names
from random_named_copy import copy_dataset_with_random_names


PROJECT_DIR: Path = Path(__file__).resolve().parent
SOURCE_DATASET_DIR: Path = PROJECT_DIR.parent / "lab01" / "dataset"
ANNOTATIONS_DIR: Path = PROJECT_DIR / "annotations"
OUTPUT_DIR: Path = PROJECT_DIR / "output"


def check_source_dataset(dataset_dir: Path) -> None:
    """Проверяет наличие исходного датасета."""
    if not dataset_dir.is_dir():
        raise FileNotFoundError(f"Исходный датасет не найден: {dataset_dir}")


def main() -> None:
    """Создаёт аннотацию и две преобразованные копии датасета."""
    check_source_dataset(SOURCE_DATASET_DIR)
    annotation_count = create_dataset_annotation(
        SOURCE_DATASET_DIR, PROJECT_DIR, ANNOTATIONS_DIR / "annotations.csv"
    )
    class_copy_count = copy_dataset_with_class_names(
        SOURCE_DATASET_DIR,
        OUTPUT_DIR / "class_named_dataset",
        PROJECT_DIR,
        ANNOTATIONS_DIR / "class_named_annotations.csv",
    )
    random_copy_count = copy_dataset_with_random_names(
        SOURCE_DATASET_DIR,
        OUTPUT_DIR / "random_dataset",
        PROJECT_DIR,
        ANNOTATIONS_DIR / "random_annotations.csv",
    )
    print(f"Создано строк аннотации: {annotation_count}")
    print(f"Скопировано файлов: {class_copy_count}")
    print(f"Скопировано файлов: {random_copy_count}")


if __name__ == "__main__":
    main()
