import flet as ft
from importlib import reload
import config
from utils import get_configured_logger
from typing import Optional, List

log = get_configured_logger()


def reload_tags_dict():
    reload(config)
    log.info("Reloaded tags_dict")
    return config.tags_dict


class tags_selector(ft.Column):
    def __init__(
            self,
            tags_dict: dict = config.tags_dict,
            on_change=None
    ):
        super().__init__()
        self.is_isolated = True
        self.on_change = on_change
        self.tags_dict = tags_dict
        self.edit_bool = True

    def build(self):
        self.tags_textfield = ft.TextField(
            label="tags",
            value="",
            expand=True,
            read_only=not self.edit_bool,
        )

        self.tags_save_button = ft.IconButton(
            icon=ft.icons.SAVE,
            tooltip="SAVE",
            visible=self.edit_bool,
            on_click=self.save_tags,
        )
        self.tags_edit_button = ft.IconButton(
            icon=ft.icons.EDIT,
            tooltip="EDIT",
            visible=not self.edit_bool,
            on_click=self.edit_tags,
        )
        self.tags_clear_button = ft.IconButton(
            icon=ft.icons.CLEAR,
            tooltip="CLEAR",
            on_click=self.clear,
        )

        self.tags_edit_view = ft.Row(
            controls=[
                self.tags_textfield,
                self.tags_save_button,
                self.tags_edit_button,
                self.tags_clear_button,
            ],
        )

        self.init_tags_add_view()

        self.controls = [
            self.tags_edit_view,
            self.tags_add_view,
        ]

    def _refresh(self):
        """同步 edit_bool 的更新"""
        self.tags_textfield.read_only = not self.edit_bool
        self.tags_save_button.visible = self.edit_bool
        self.tags_edit_button.visible = not self.edit_bool
        self.tags_add_view.visible = self.edit_bool

    def init_tags_add_view(self):
        """生成 tags_add_view"""
        self.tags_add_view = ft.Column(
            controls=[
                ft.Row(wrap=True),  # self.tags_add_view.controls[0]: root tags view
                ft.Row(wrap=True),  # self.tags_add_view.controls[1]: child tags view
            ],
            visible=self.edit_bool,
        )
        for key, value in self.tags_dict.items():
            tag_button = ft.FilledButton(text=key, on_click=self.click_root_tag)
            tag_button.tooltip = value if type(value) == str else "Expand/"
            self.tags_add_view.controls[0].controls.append(tag_button)

        tags_reload_button = ft.IconButton(
            icon=ft.icons.REFRESH,
            tooltip="Reload tags",
            on_click=self.reload_tags,
        )
        self.tags_add_view.controls[0].controls.append(tags_reload_button)

    # Event Handlers
    def click_root_tag(self, e):
        if type(self.tags_dict[e.control.text]) == str:
            self.tags_textfield.value += e.control.tooltip
        elif type(self.tags_dict[e.control.text]) == dict:
            self.tags_add_view.controls[1].controls = []
            for key, value in self.tags_dict[e.control.text].items():
                tag_button = ft.FilledTonalButton(text=key, on_click=self.click_child_tag)
                tag_button.tooltip = value if type(value) == str else "暂不支持三级标签"
                self.tags_add_view.controls[1].controls.append(tag_button)
        self.update()

    def click_child_tag(self, e):
        if e.control.tooltip == "暂不支持三级标签":
            log.error("暂不支持三级标签")
            raise ValueError("暂不支持三级标签")
        self.tags_textfield.value += e.control.tooltip
        self.tags_add_view.controls[1].controls = []
        self.update()

    def save_tags(self, e):
        self.edit_bool = False
        self._refresh()
        self.update()
        if self.on_change:
            self.on_change(self.tags_textfield.value)

    def edit_tags(self, e):
        self.edit_bool = True
        self._refresh()
        self.update()

    def reload_tags(self, e):
        """重新加载 tags_dict"""
        reloaded_tags_dict = reload_tags_dict()
        self.tags_dict = reloaded_tags_dict
        self.init_tags_add_view()
        self.controls[1] = self.tags_add_view
        self.update()

    def clear(self, e):
        self.tags_textfield.value = ""
        self.update()


class content_editor(ft.TextField):
    def __init__(
        self,
        on_change=None,
    ):
        super().__init__()
        self.on_change = on_change
        self.edit_bool = True
        self.is_isolated = True

    def build(self):
        self.label = "edit"
        self.value = ""
        self.multiline = True
        self.read_only = not self.edit_bool
        self.disabled = False

    def editing(self):
        self.edit_bool = True
        self.read_only = not self.edit_bool
        self.update()

    def saved(self):
        self.edit_bool = False
        self.read_only = not self.edit_bool
        self.update()

    def to_submit(self, tags_text: str):
        if self.edit_bool:
            log.error("Cannot submit when in edit mode.")
            raise ValueError("Cannot submit when in edit mode.")
        if tags_text:
            content_with_tags = tags_text + "\n" + self.value
        else:
            content_with_tags = self.value
        self.value = content_with_tags
        self.disabled = True
        self.update()
        if self.on_change:
            self.on_change(self.value)


class images_display(ft.Row):
    def __init__(
        self,
    ):
        super().__init__()
        self.is_isolated = True

    def build(self):
        self.scroll = "always"
        self.height = 200
        self.wrap = False
        self.controls = []
        self.visible = False

    def load(
            self,
            image_list: list = [],
    ):
        if image_list:
            self.controls = []
            for image in image_list:
                self.controls.append(ft.Image(src=image))
            self.visible = True
        self.update()


class interact_buttons(ft.Row):
    def __init__(
        self,
        on_change=None,
        on_prev=None,
    ):
        super().__init__()
        self.is_isolated = True
        self.saved_bool = False
        self.on_change = on_change
        self.on_prev = on_prev

    def build(self):
        self.prev_button = ft.IconButton(
            icon=ft.icons.NAVIGATE_BEFORE,
            tooltip="Previous memo",
            expand=True,
            on_click=self.on_prev_click,
        )
        self.next_button = ft.IconButton(
            icon=ft.icons.NAVIGATE_NEXT,
            tooltip="Next memo",
            expand=True,
            on_click=self.on_next_click,
            visible=not self.saved_bool,
        )
        self.submit_button = ft.IconButton(
            icon=ft.icons.SAVE_AS,
            tooltip="Submit",
            expand=True,
            on_click=self.on_submit_click,
            visible=self.saved_bool,
            disabled=not self.saved_bool,
        )

        self.controls = [
            self.prev_button,
            self.next_button,
            self.submit_button,
        ]

    def on_next_click(self, e=None):
        self.saved_bool = True
        self.next_button.visible = not self.saved_bool
        self.submit_button.visible = self.saved_bool
        self.submit_button.disabled = not self.saved_bool
        self.update()

    def on_submit_click(self, e=None):
        if self.on_change:
            self.on_change()
        self._clear()

    def on_prev_click(self, e=None):
        if self.saved_bool:
            self._clear()
        else:
            self.on_prev()

    def _clear(self):
        self.saved_bool = False
        self.next_button.visible = not self.saved_bool
        self.submit_button.visible = self.saved_bool
        self.submit_button.disabled = not self.saved_bool
        self.update()


if __name__ == "__main__":
    def on_tags_change(value):
        print(f"Tags changed to: {value}")
        pass

    def on_content_change(value):
        print(f"Content changed to: {value}")
        pass

    def on_buttons_change():
        print("Submit clicked.")
        pass

    def on_prev_click():
        print("Previous clicked.")
        pass

    def main(page: ft.Page):
        tags_selector_view = tags_selector(
            on_change=on_tags_change,
        )
        content_editor_view = content_editor(
            on_change=on_content_change,
        )
        images_display_view = images_display()
        interact_view = interact_buttons(
            on_change=on_buttons_change,
            on_prev=on_prev_click,
        )
        page.add(
            tags_selector_view,
            content_editor_view,
            images_display_view,
            interact_view,
        )
        images_display_view.load(
            image_list=[
                "/assets/icon.png",
                "/resource/2020/08/step_1626517240759_1620_1080.png"
            ]
        )

    ft.app(
        target=main,
        assets_dir="/Users/krdw/Desktop/code-to-learn/python/learn_flet/memos_rollback"
    )
