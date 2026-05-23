import flet as ft
def main(page: ft.Page):
    with open("flet_dir.txt", "w") as f:
        f.write("PAGE DIR:\n")
        for x in dir(page):
            f.write(x + "\n")
        f.write("\nSESSION DIR:\n")
        for x in dir(page.session):
            f.write(x + "\n")
    page.window.destroy() if hasattr(page, 'window') else None
    
ft.app(target=main)
