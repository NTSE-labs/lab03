"""Последовательное получение экземпляров заданного класса."""

from collections.abc import Iterator
from pathlib import Path
from dataset_common import find_image_files

PROJECT_DIR: Path = Path(__file__).resolve().parent
SOURCE_DATASET_DIR: Path = PROJECT_DIR.parent / "lab01" / "dataset"
_iterators: dict[tuple[Path, str], Iterator[Path]] = {}


def get_class_instance_paths(class_label: str, dataset_dir: Path) -> list[Path]:
    """Возвращает все изображения указанного класса."""
    class_dir = dataset_dir / class_label
    if not class_dir.is_dir():
        raise ValueError(f"Класс не найден: {class_label}")
    return find_image_files(class_dir)


def reset_instance_sequence(class_label: str | None = None, dataset_dir: Path | None = None) -> None:
    """Сбрасывает последовательность одного класса или все последовательности."""
    if class_label is None and dataset_dir is None:
        _iterators.clear()
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
