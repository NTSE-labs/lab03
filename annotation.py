"""Создание CSV-аннотации исходного датасета."""

from pathlib import Path
from dataset_common import find_image_files, get_class_label, write_annotation

PROJECT_DIR: Path = Path(__file__).resolve().parent
SOURCE_DATASET_DIR: Path = PROJECT_DIR.parent / "lab01" / "dataset"
ANNOTATION_PATH: Path = PROJECT_DIR / "annotations" / "annotations.csv"


def create_dataset_annotation(dataset_dir: Path, project_dir: Path, annotation_path: Path) -> int:
    """Создаёт аннотацию изображений датасета и возвращает число строк."""
    return write_annotation(find_image_files(dataset_dir), project_dir, annotation_path, lambda image_path: get_class_label(image_path, dataset_dir))


def main() -> None:
    """Создаёт стандартную аннотацию исходного датасета."""
    count = create_dataset_annotation(SOURCE_DATASET_DIR, PROJECT_DIR, ANNOTATION_PATH)
    print(f"Создан {ANNOTATION_PATH}; записей: {count}")


if __name__ == "__main__":
    main()
