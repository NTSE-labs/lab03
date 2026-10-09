"""Классы-итераторы для экземпляров класса и всего датасета."""

from collections.abc import Iterator
from pathlib import Path
from dataset_common import find_image_files, get_class_label
from next_instance import get_class_instance_paths

PROJECT_DIR: Path = Path(__file__).resolve().parent
SOURCE_DATASET_DIR: Path = PROJECT_DIR.parent / "lab01" / "dataset"


class ClassIterator:
    """Итерирует неповторяющиеся изображения одного класса."""

    def __init__(self, class_label: str, dataset_dir: Path) -> None:
        self._paths: Iterator[Path] = iter(get_class_instance_paths(class_label, dataset_dir))

    def __iter__(self) -> "ClassIterator":
        """Возвращает себя как объект-итератор."""
        return self

    def __next__(self) -> Path:
        """Возвращает следующий путь изображения или возбуждает StopIteration."""
        return next(self._paths)


class DatasetIterator:
    """Итерирует все изображения датасета парами (метка класса, путь)."""

    def __init__(self, dataset_dir: Path) -> None:
        self._dataset_dir: Path = dataset_dir
        self._paths: Iterator[Path] = iter(find_image_files(dataset_dir))

    def __iter__(self) -> "DatasetIterator":
        """Возвращает себя как объект-итератор."""
        return self

    def __next__(self) -> tuple[str, Path]:
        """Возвращает метку и путь следующего изображения."""
        path = next(self._paths)
        return get_class_label(path, self._dataset_dir), path


def main() -> None:
    """Показывает первые пять элементов итератора всего датасета."""
    for index, (class_label, image_path) in enumerate(DatasetIterator(SOURCE_DATASET_DIR), start=1):
        print(f"{class_label}: {image_path}")
        if index == 5:
            break


if __name__ == "__main__":
    main()
