"""Последовательное получение экземпляров заданного класса."""

import csv
from collections.abc import Iterator
from pathlib import Path
from dataset_common import find_image_files

PROJECT_DIR: Path = Path(__file__).resolve().parent
SOURCE_DATASET_DIR: Path = PROJECT_DIR.parent / "lab01" / "dataset"
_iterators: dict[tuple[Path, str], Iterator[Path]] = {}
_annotation_iterators: dict[tuple[Path, str], Iterator[Path]] = {}


def get_class_instance_paths(class_label: str, dataset_dir: Path) -> list[Path]:
    """Возвращает все изображения указанного класса."""
    class_dir = dataset_dir / class_label
    if not class_dir.is_dir():
        raise ValueError(f"Класс не найден: {class_label}")
    return find_image_files(class_dir)


def get_annotated_instance_paths(
    class_label: str,
    annotation_path: Path,
) -> list[Path]:
    """Возвращает уникальные пути указанного класса из CSV-аннотации."""
    if not annotation_path.is_file():
        raise FileNotFoundError(f"Файл аннотации не найден: {annotation_path}")

    image_paths: list[Path] = []
    seen_paths: set[Path] = set()
    with annotation_path.open(encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            if row.get("class_label") != class_label:
                continue
            image_path = Path(row["absolute_path"])
            if image_path not in seen_paths:
                image_paths.append(image_path)
                seen_paths.add(image_path)
    return image_paths


def reset_instance_sequence(class_label: str | None = None, dataset_dir: Path | None = None) -> None:
    """Сбрасывает последовательность одного класса или все последовательности."""
    if class_label is None and dataset_dir is None:
        _iterators.clear()
        _annotation_iterators.clear()
        return
    if class_label is None or dataset_dir is None:
        raise ValueError("Для сброса одного класса укажите и class_label, и dataset_dir.")
    _iterators.pop((dataset_dir.resolve(), class_label), None)


def get_next_instance(class_label: str, dataset_dir: Path) -> Path | None:
    """Возвращает следующий неповторяющийся путь класса или ``None``."""
    key = (dataset_dir.resolve(), class_label)
    if key not in _iterators:
        _iterators[key] = iter(get_class_instance_paths(class_label, dataset_dir))
    return next(_iterators[key], None)


def get_next_annotated_instance(
    class_label: str,
    annotation_path: Path,
) -> Path | None:
    """Возвращает следующий путь класса из CSV-аннотации или ``None``."""
    key = (annotation_path.resolve(), class_label)
    if key not in _annotation_iterators:
        _annotation_iterators[key] = iter(
            get_annotated_instance_paths(class_label, annotation_path)
        )
    return next(_annotation_iterators[key], None)


def main() -> None:
    """Показывает последовательный обход первого найденного класса."""
    class_labels = sorted(path.name for path in SOURCE_DATASET_DIR.iterdir() if path.is_dir())
    if not class_labels:
        print("В датасете нет классов.")
        return
    class_label = class_labels[0]
    while (instance_path := get_next_instance(class_label, SOURCE_DATASET_DIR)) is not None:
        print(instance_path)


if __name__ == "__main__":
    main()
