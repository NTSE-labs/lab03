"""Общие операции с файлами датасета и CSV-аннотациями."""

import csv
import os
import shutil
from collections.abc import Callable, Iterable
from pathlib import Path

IMAGE_EXTENSIONS: frozenset[str] = frozenset({".jpg", ".jpeg"})
ANNOTATION_COLUMNS: tuple[str, str, str] = ("absolute_path", "relative_path", "class_label")


def find_image_files(dataset_dir: Path) -> list[Path]:
    """Возвращает отсортированные изображения из датасета."""
    if not dataset_dir.is_dir():
        raise FileNotFoundError(f"Каталог датасета не найден: {dataset_dir}")
    return sorted(path for path in dataset_dir.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)


def get_class_label(image_path: Path, dataset_dir: Path) -> str:
    """Определяет метку класса по первой папке внутри датасета."""
    relative_path = image_path.relative_to(dataset_dir)
    if len(relative_path.parts) < 2:
        raise ValueError(f"Файл должен находиться в папке класса: {image_path}")
    return relative_path.parts[0]


def get_project_relative_path(file_path: Path, project_dir: Path) -> str:
    """Возвращает путь к файлу относительно каталога проекта."""
    return Path(os.path.relpath(file_path.resolve(), project_dir.resolve())).as_posix()


def prepare_empty_directory(directory: Path) -> None:
    """Создаёт пустой каталог назначения."""
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)


def write_annotation(image_paths: Iterable[Path], project_dir: Path, annotation_path: Path, class_getter: Callable[[Path], str]) -> int:
    """Записывает CSV с абсолютным путём, относительным путём и меткой класса."""
    annotation_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with annotation_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=ANNOTATION_COLUMNS)
        writer.writeheader()
        for image_path in image_paths:
            writer.writerow({"absolute_path": str(image_path.resolve()), "relative_path": get_project_relative_path(image_path, project_dir), "class_label": class_getter(image_path)})
            count += 1
    return count


def main() -> None:
    """Сообщает назначение общего модуля при самостоятельном запуске."""
    print("dataset_common.py содержит общие функции для скриптов задания.")


if __name__ == "__main__":
    main()
