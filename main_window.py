"""Графический интерфейс Flet для операций с изображениями датасета."""

from pathlib import Path

import flet as ft

from annotation import create_dataset_annotation
from class_named_copy import copy_dataset_with_class_names
from dataset_common import find_image_files, get_class_label
from next_instance import get_next_instance, reset_instance_sequence
from random_named_copy import copy_dataset_with_random_names


def main(page: ft.Page) -> None:
    """Создаёт и запускает элементы главного окна приложения."""
    source_dataset: Path | None = None
    pending_action: str | None = None

    page.title = "Работа с датасетом"
    page.window.width = 900
    page.window.height = 720
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO

    source_path_text = ft.Text("Исходный датасет не выбран.")
    status_text = ft.Text()
    image_path_text = ft.Text(selectable=True)
    image_preview = ft.Image(
        src="",
        visible=False,
        width=560,
        height=400,
        fit=ft.BoxFit.CONTAIN,
    )
    class_buttons = ft.Row(wrap=True, spacing=10)

    # FilePicker используется из обработчиков кнопок напрямую через await.
    source_picker = ft.FilePicker()
    destination_picker = ft.FilePicker()
    annotation_picker = ft.FilePicker()

    # Для текущего десктопного приложения добавляем сервисы на страницу.
    page.services.extend(
        [source_picker, destination_picker, annotation_picker]
    )

    def show_status(message: str, is_error: bool = False) -> None:
        """Показывает результат операции или сообщение об ошибке."""
        status_text.value = message
        status_text.color = ft.Colors.RED if is_error else ft.Colors.GREEN
        page.update()

    def refresh_class_buttons() -> None:
        """Создаёт кнопки просмотра следующего изображения по классам."""
        class_buttons.controls.clear()

        if source_dataset is None:
            page.update()
            return

        try:
            class_labels = sorted(
                {
                    get_class_label(image_path, source_dataset)
                    for image_path in find_image_files(source_dataset)
                }
            )
        except (FileNotFoundError, ValueError) as error:
            show_status(str(error), is_error=True)
            return

        for class_label in class_labels:
            class_buttons.controls.append(
                ft.Button(
                    content=f"Следующий: {class_label}",
                    on_click=lambda event, label=class_label: (
                        show_next_instance(label)
                    ),
                )
            )

        page.update()

    def show_next_instance(class_label: str) -> None:
        """Показывает следующее изображение выбранного класса."""
        if source_dataset is None:
            show_status("Сначала выберите исходный датасет.", is_error=True)
            return

        try:
            image_path = get_next_instance(class_label, source_dataset)
        except (FileNotFoundError, ValueError) as error:
            show_status(str(error), is_error=True)
            return

        if image_path is None:
            show_status(f"Экземпляры класса «{class_label}» закончились.")
            return

        try:
            image_preview.src = image_path.read_bytes()
        except OSError as error:
            show_status(f"Не удалось открыть изображение: {error}", is_error=True)
            return
        image_preview.visible = True
        image_path_text.value = str(image_path)
        show_status(f"Показано изображение класса «{class_label}».")

    def set_source_dataset(path: str | None) -> None:
        """Устанавливает выбранную папку исходного датасета."""
        nonlocal source_dataset

        if path is None:
            return

        selected_path = Path(path)

        if not selected_path.is_dir():
            show_status("Выбранный путь не является папкой.", is_error=True)
            return

        source_dataset = selected_path
        reset_instance_sequence()

        source_path_text.value = f"Исходный датасет: {source_dataset}"
        image_preview.visible = False
        image_path_text.value = ""

        refresh_class_buttons()
        show_status("Исходный датасет выбран.")

    async def choose_source(event: ft.ControlEvent) -> None:
        """Открывает диалог выбора папки исходного датасета."""
        try:
            path = await source_picker.get_directory_path(
                dialog_title="Выберите исходный датасет"
            )
            set_source_dataset(path)
        except Exception as error:
            show_status(f"Не удалось выбрать папку: {error}", is_error=True)

    async def save_annotation(event: ft.ControlEvent) -> None:
        """Создаёт CSV-аннотацию в выбранном месте."""
        if source_dataset is None:
            show_status("Сначала выберите исходный датасет.", is_error=True)
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

            annotation_path = Path(path)
            count = create_dataset_annotation(
                source_dataset,
                annotation_path.parent,
                annotation_path,
            )
            show_status(f"Аннотация создана: {count} строк.")
        except (FileNotFoundError, OSError, ValueError) as error:
            show_status(
                f"Не удалось создать аннотацию: {error}",
                is_error=True,
            )
        except Exception as error:
            show_status(
                f"Не удалось открыть диалог сохранения: {error}",
                is_error=True,
            )

    async def create_copy(action: str) -> None:
        """Выбирает папку назначения и создаёт копию датасета."""
        nonlocal pending_action

        if source_dataset is None:
            show_status("Сначала выберите исходный датасет.", is_error=True)
            return

        pending_action = action

        try:
            destination_path = await destination_picker.get_directory_path(
                dialog_title="Выберите папку назначения"
            )

            if destination_path is None:
                return

            destination = Path(destination_path)

            if pending_action == "class_copy":
                count = copy_dataset_with_class_names(
                    source_dataset,
                    destination / "class_named_dataset",
                    destination,
                    destination / "class_named_annotations.csv",
                )
                show_status(f"Создано файлов: {count}.")

            elif pending_action == "dataset_copy":
                count = copy_dataset_with_random_names(
                    source_dataset,
                    destination / "numbered_dataset",
                    destination,
                    destination / "numbered_annotations.csv",
                )
                show_status(f"Создано файлов: {count}.")

        except (FileNotFoundError, OSError, ValueError) as error:
            show_status(f"Не удалось создать датасет: {error}", is_error=True)
        except Exception as error:
            show_status(
                f"Не удалось выбрать папку назначения: {error}",
                is_error=True,
            )
        finally:
            pending_action = None

    async def create_class_copy(event: ft.ControlEvent) -> None:
        """Создаёт копию с именами «класс_номер»."""
        await create_copy("class_copy")

    async def create_numbered_copy(event: ft.ControlEvent) -> None:
        """Создаёт копию с нумерованными именами."""
        await create_copy("dataset_copy")

    page.add(
        ft.Text(
            "Обработка датасета",
            size=28,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Row(
            [
                ft.Button(
                    content="Выбрать датасет",
                    on_click=choose_source,
                ),
                source_path_text,
            ]
        ),
        ft.Divider(),
        ft.Row(
            [
                ft.Button(
                    content="Создать аннотацию CSV",
                    on_click=save_annotation,
                ),
                ft.Button(
                    content="Копия: класс_номер",
                    on_click=create_class_copy,
                ),
                ft.Button(
                    content="Копия: датасет_номер",
                    on_click=create_numbered_copy,
                ),
            ],
            wrap=True,
        ),
        status_text,
        ft.Divider(),
        ft.Text("Просмотр следующего экземпляра класса", size=20),
        class_buttons,
        image_preview,
        image_path_text,
    )


if __name__ == "__main__":
    ft.run(main)
