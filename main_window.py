"""Графический интерфейс Flet для аннотации и просмотра датасета."""
import base64
from pathlib import Path
from typing import Any

import flet as ft

from annotation import create_dataset_annotation
from class_named_copy import copy_dataset_with_class_names
from next_instance import get_next_annotated_instance, reset_instance_sequence
from random_named_copy import copy_dataset_with_random_names


CLASS_LABELS = ("cat", "dog")


def get_result_count(result: Any) -> int:
    """Возвращает число файлов из результата копирования разных форматов."""
    if isinstance(result, int):
        return result
    try:
        return len(result)
    except TypeError:
        return 0


def resolve_image_path(value: str | Path, annotation_path: Path) -> Path:
    """Разрешает абсолютный или относительный путь из CSV-аннотации."""
    image_path = Path(value).expanduser()

    if image_path.is_absolute():
        candidates = [image_path]
    else:
        candidates = [
            Path.cwd() / image_path,
            annotation_path.parent / image_path,
            annotation_path.parent.parent / image_path,
        ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    checked_paths = "\n".join(str(path.resolve()) for path in candidates)
    raise FileNotFoundError(
        f"Изображение не найдено: {image_path}\nПроверены пути:\n{checked_paths}"
    )


def main(page: ft.Page) -> None:
    """Создаёт интерфейс для генерации аннотаций, копирования и просмотра."""
    source_dataset: Path | None = None
    selected_dataset: str | None = None
    annotations_by_dataset: dict[str, Path] = {}

    page.title = "Работа с датасетом"
    page.window.width = 1000
    page.window.height = 800
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO

    source_path_text = ft.Text("Исходный датасет не выбран.", selectable=True)
    status_text = ft.Text()
    image_path_text = ft.Text("Изображение ещё не выбрано.", selectable=True)
    image_preview = ft.Image(
        src="",
        visible=False,
        width=600,
        height=430,
        fit=ft.BoxFit.CONTAIN,
        gapless_playback=True,
        error_content=ft.Text("Не удалось отобразить изображение."),
    )

    class_named_checkbox = ft.Checkbox(
        label="Копия с именами класс_номер",
        disabled=True,
        value=False,
    )
    random_checkbox = ft.Checkbox(
        label="Копия со случайными номерами",
        disabled=True,
        value=False,
    )

    source_picker = ft.FilePicker()
    destination_picker = ft.FilePicker()
    annotation_picker = ft.FilePicker()
    page.services.extend([source_picker, destination_picker, annotation_picker])

    def show_status(message: str, is_error: bool = False) -> None:
        """Показывает результат операции или сообщение об ошибке."""
        status_text.value = message
        status_text.color = ft.Colors.RED if is_error else ft.Colors.GREEN
        page.update()

    def clear_preview(message: str = "Изображение ещё не выбрано.") -> None:
        """Очищает предпросмотр и подпись к изображению."""
        image_preview.src = ""
        image_preview.visible = False
        image_path_text.value = message

    def get_selected_annotation_path() -> Path | None:
        """Возвращает CSV-аннотацию выбранной копии датасета."""
        if selected_dataset is None:
            return None
        return annotations_by_dataset.get(selected_dataset)

    def set_selected_dataset(dataset_key: str | None) -> None:
        """Устанавливает единственный выбранный датасет и сбрасывает просмотр."""
        nonlocal selected_dataset
        selected_dataset = dataset_key
        class_named_checkbox.value = dataset_key == "class_named"
        random_checkbox.value = dataset_key == "random"
        reset_instance_sequence()
        clear_preview("Выберите следующий экземпляр кнопкой выше.")
        page.update()

    def select_dataset(event: ft.ControlEvent) -> None:
        """Обрабатывает переключение флажков выбора копии датасета."""
        if event.control is class_named_checkbox:
            new_selection = "class_named" if class_named_checkbox.value else None
        else:
            new_selection = "random" if random_checkbox.value else None

        set_selected_dataset(new_selection)

    class_named_checkbox.on_change = select_dataset
    random_checkbox.on_change = select_dataset

    def show_next_instance(class_label: str) -> None:
        """Получает следующий путь через итератор и отображает изображение."""
        annotation_path = get_selected_annotation_path()
        if annotation_path is None:
            show_status("Сначала создайте копию и выберите её флажком.", True)
            return

        if not annotation_path.is_file():
            show_status(
                f"CSV-аннотация не найдена: {annotation_path}. "
                "Создайте копию датасета заново.",
                True,
            )
            return

        try:
            returned_path = get_next_annotated_instance(
                class_label,
                annotation_path,
            )
        except (FileNotFoundError, OSError, ValueError, KeyError) as error:
            show_status(f"Не удалось получить следующий экземпляр: {error}", True)
            return

        if returned_path is None:
            clear_preview(
                f"Экземпляры класса «{class_label}» закончились."
            )
            show_status(f"Экземпляры класса «{class_label}» закончились.")
            return

        try:
            image_path = resolve_image_path(returned_path, annotation_path)
            image_bytes = image_path.read_bytes()
            if not image_bytes:
                raise ValueError(f"Файл изображения пуст: {image_path}")
        except (OSError, ValueError, TypeError) as error:
            clear_preview()
            show_status(f"Не удалось открыть изображение: {error}", True)
            return

        # Base64-строка передаётся в Image, чтобы не зависеть от локального пути
        # на стороне визуального компонента Flet.
        image_preview.src = base64.b64encode(image_bytes).decode("ascii")
        image_preview.visible = True
        image_path_text.value = str(image_path)
        image_preview.update()
        show_status(f"Показано изображение класса «{class_label}».")

    def set_source_dataset(path: str | None) -> None:
        """Проверяет и устанавливает выбранную папку исходного датасета."""
        nonlocal source_dataset
        if path is None:
            return

        selected_path = Path(path).expanduser().resolve()
        if not selected_path.is_dir():
            show_status("Выбранный путь не является папкой.", True)
            return

        class_dirs = [
            item for item in selected_path.iterdir() if item.is_dir()
        ]
        if not class_dirs:
            show_status(
                "В выбранной папке нет подпапок классов. "
                "Выберите корень dataset, содержащий cat и dog.",
                True,
            )
            return

        source_dataset = selected_path
        source_path_text.value = f"Исходный датасет: {source_dataset}"
        set_selected_dataset(None)
        show_status("Исходный датасет выбран.")

    async def choose_source(event: ft.ControlEvent) -> None:
        """Открывает диалог выбора исходного датасета."""
        try:
            path = await source_picker.get_directory_path(
                dialog_title="Выберите корневую папку dataset"
            )
            set_source_dataset(path)
        except Exception as error:
            show_status(f"Не удалось выбрать папку: {error}", True)

    async def save_annotation(event: ft.ControlEvent) -> None:
        """Создаёт CSV-аннотацию исходного датасета в выбранном месте."""
        if source_dataset is None:
            show_status("Сначала выберите исходный датасет.", True)
            return

        try:
            path = await annotation_picker.save_file(
                dialog_title="Сохранить аннотацию",
                file_name="annotations.csv",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["csv"],
            )
            if path is None:
                return

            annotation_path = Path(path).expanduser().resolve()
            count = create_dataset_annotation(
                source_dataset,
                annotation_path.parent,
                annotation_path,
            )
            show_status(f"Аннотация создана. Количество строк: {count}.")
        except (FileNotFoundError, OSError, ValueError) as error:
            show_status(f"Не удалось создать аннотацию: {error}", True)
        except Exception as error:
            show_status(f"Ошибка при сохранении аннотации: {error}", True)

    def validate_destination(destination: Path) -> None:
        """Запрещает размещать производные копии внутри исходного датасета."""
        if source_dataset is None:
            raise ValueError("Сначала выберите исходный датасет.")

        resolved_destination = destination.resolve()
        resolved_source = source_dataset.resolve()
        if (
            resolved_destination == resolved_source
            or resolved_source in resolved_destination.parents
        ):
            raise ValueError(
                "Папка назначения не должна находиться внутри исходного "
                "dataset: иначе новые копии попадут в исходный набор "
                "при следующем копировании. Выберите родительскую папку "
                "например NTSE, либо отдельную папку для результатов."
            )

    async def create_copy(action: str) -> None:
        """Создаёт выбранную копию и подключает её CSV для просмотра."""
        if source_dataset is None:
            show_status("Сначала выберите исходный датасет.", True)
            return

        try:
            destination_text = await destination_picker.get_directory_path(
                dialog_title="Выберите папку, в которой создать результаты"
            )
            if destination_text is None:
                return

            destination = Path(destination_text).expanduser().resolve()
            validate_destination(destination)

            if action == "class_copy":
                annotation_path = destination / "class_named_annotations.csv"
                result = copy_dataset_with_class_names(
                    source_dataset,
                    destination / "class_named_dataset",
                    destination,
                    annotation_path,
                )
                dataset_key = "class_named"
                class_named_checkbox.disabled = False
                annotations_by_dataset[dataset_key] = annotation_path.resolve()

            elif action == "random_copy":
                annotation_path = destination / "numbered_annotations.csv"
                result = copy_dataset_with_random_names(
                    source_dataset,
                    destination / "numbered_dataset",
                    destination,
                    annotation_path,
                )
                dataset_key = "random"
                random_checkbox.disabled = False
                annotations_by_dataset[dataset_key] = annotation_path.resolve()

            else:
                raise ValueError(f"Неизвестная операция копирования: {action}")

            set_selected_dataset(dataset_key)
            count = get_result_count(result)
            show_status(
                f"Копирование завершено: {count} изображений. "
                f"Аннотация: {annotation_path.resolve()}"
            )

        except (FileNotFoundError, OSError, ValueError) as error:
            show_status(f"Не удалось создать копию датасета: {error}", True)
        except Exception as error:
            show_status(f"Ошибка при копировании датасета: {error}", True)

    async def create_class_copy(event: ft.ControlEvent) -> None:
        """Создаёт копию, в которой имя каждого файла содержит класс."""
        await create_copy("class_copy")

    async def create_numbered_copy(event: ft.ControlEvent) -> None:
        """Создаёт копию с числовыми именами файлов."""
        await create_copy("random_copy")

    page.add(
        ft.Text(
            "Обработка датасета",
            size=28,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Row(
            controls=[
                ft.Button(content="Выбрать датасет", on_click=choose_source),
                source_path_text,
            ],
            wrap=True,
        ),
        ft.Divider(),
        ft.Row(
            controls=[
                ft.Button(
                    content="Создать аннотацию CSV",
                    on_click=save_annotation,
                ),
                ft.Button(
                    content="Копия: класс_номер",
                    on_click=create_class_copy,
                ),
                ft.Button(
                    content="Копия: случайный номер",
                    on_click=create_numbered_copy,
                ),
            ],
            wrap=True,
        ),
        status_text,
        ft.Divider(),
        ft.Text("Выберите созданную копию для просмотра", size=20),
        ft.Row(controls=[class_named_checkbox, random_checkbox], wrap=True),
        ft.Text("Получение следующего экземпляра", size=20),
        ft.Row(
            controls=[
                ft.Button(
                    content="Следующая кошка",
                    on_click=lambda event: show_next_instance("cat"),
                ),
                ft.Button(
                    content="Следующая собака",
                    on_click=lambda event: show_next_instance("dog"),
                ),
            ],
            wrap=True,
        ),
        image_preview,
        image_path_text,
    )


if __name__ == "__main__":
    ft.run(main)
