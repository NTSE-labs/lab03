"""Копирование датасета с именами ``класс_номер.jpg``."""

import shutil
from pathlib import Path
from dataset_common import find_image_files, get_class_label, prepare_empty_directory, write_annotation

PROJECT_DIR: Path = Path(__file__).resolve().parent
SOURCE_DATASET_DIR: Path = PROJECT_DIR.parent / "lab01" / "dataset"
OUTPUT_DIR: Path = PROJECT_DIR / "output" / "class_named_dataset"
ANNOTATION_PATH: Path = PROJECT_DIR / "annotations" / "class_named_annotations.csv"


def get_class_named_path(
    source_path: Path,
    class_label: str,
    number: int,
    output_dir: Path,
) -> Path:
    """Строит путь назначения в формате ``класс_номер.расширение``."""
    return output_dir / f"{class_label}_{number}{source_path.suffix.lower()}"


def copy_dataset_with_class_names(source_dataset_dir: Path, output_dir: Path, project_dir: Path, annotation_path: Path) -> int:
    """Копирует датасет, добавляет класс в имена файлов и создаёт аннотацию."""
    prepare_empty_directory(output_dir)
    copied_paths: list[Path] = []
    labels: dict[Path, str] = {}
    class_numbers: dict[str, int] = {}
    for source_path in find_image_files(source_dataset_dir):
        class_label = get_class_label(source_path, source_dataset_dir)
        class_numbers[class_label] = class_numbers.get(class_label, 0) + 1
        target_path = get_class_named_path(
            source_path,
            class_label,
            class_numbers[class_label],
            output_dir,
        )
        shutil.copy2(source_path, target_path)
        copied_paths.append(target_path)
        labels[target_path] = class_label
    return write_annotation(copied_paths, project_dir, annotation_path, labels.__getitem__)


def main() -> None:
    """Создаёт стандартную копию датасета с именами, содержащими класс."""
    count = copy_dataset_with_class_names(SOURCE_DATASET_DIR, OUTPUT_DIR, PROJECT_DIR, ANNOTATION_PATH)
    print(f"Создан {OUTPUT_DIR}; скопировано файлов: {count}")


if __name__ == "__main__":
    main()
