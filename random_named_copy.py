"""Копирование датасета со случайными уникальными номерами файлов."""

import random
import shutil
from pathlib import Path
from dataset_common import find_image_files, get_class_label, prepare_empty_directory, write_annotation

RANDOM_NUMBER_MIN: int = 0
RANDOM_NUMBER_MAX: int = 10_000
PROJECT_DIR: Path = Path(__file__).resolve().parent
SOURCE_DATASET_DIR: Path = PROJECT_DIR.parent / "lab01" / "dataset"
OUTPUT_DIR: Path = PROJECT_DIR / "output" / "random_dataset"
ANNOTATION_PATH: Path = PROJECT_DIR / "annotations" / "random_annotations.csv"


def get_dataset_named_path(
    source_path: Path,
    dataset_name: str,
    number: int,
    output_dir: Path,
) -> Path:
    """Строит путь назначения в формате ``датасет_номер.расширение``."""
    return output_dir / f"{dataset_name}_{number}{source_path.suffix.lower()}"


def create_unique_random_numbers(count: int) -> list[int]:
    """Возвращает ``count`` неповторяющихся чисел из диапазона 0…10000."""
    population_size = RANDOM_NUMBER_MAX - RANDOM_NUMBER_MIN + 1
    if count > population_size:
        raise ValueError(
            "Число файлов превышает количество доступных уникальных номеров "
            f"({population_size})."
        )
    return random.sample(
        range(RANDOM_NUMBER_MIN, RANDOM_NUMBER_MAX + 1),
        count,
    )


def copy_dataset_with_random_names(
    source_dataset_dir: Path,
    output_dir: Path,
    project_dir: Path,
    annotation_path: Path,
) -> int:
    """Копирует датасет с уникальными случайными номерами от 0 до 10000."""
    source_paths = find_image_files(source_dataset_dir)
    numbers = create_unique_random_numbers(len(source_paths))
    prepare_empty_directory(output_dir)
    copied_paths: list[Path] = []
    labels: dict[Path, str] = {}
    for source_path, number in zip(source_paths, numbers, strict=True):
        target_path = get_dataset_named_path(
            source_path,
            source_dataset_dir.name,
            number,
            output_dir,
        )
        shutil.copy2(source_path, target_path)
        copied_paths.append(target_path)
        labels[target_path] = get_class_label(source_path, source_dataset_dir)

    copied_paths.sort(
        key=lambda path: int(path.stem.rsplit("_", maxsplit=1)[-1])
    )
    return write_annotation(copied_paths, project_dir, annotation_path, labels.__getitem__)


def main() -> None:
    """Создаёт стандартную копию датасета со случайными именами."""
    count = copy_dataset_with_random_names(SOURCE_DATASET_DIR, OUTPUT_DIR, PROJECT_DIR, ANNOTATION_PATH)
    print(f"Создан {OUTPUT_DIR}; скопировано файлов: {count}")


if __name__ == "__main__":
    main()
