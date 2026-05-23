import flet as ft
def main(page: ft.Page):
    print([x for x in dir(page) if 'storage' in x.lower()])
    page.window_destroy()
ft.app(target=main)
