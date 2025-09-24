# Créer un venv : python3 -m venv .venv
# L’activer : source .venv/bin/activate
# Désactiver : deactivate
# Installer les dépendances : pip install -r requirements.txt
# Lancer l’application : python main.py

import flet as ft


def main(page: ft.Page):
    page.title = "Finance Project Mobile"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    txt_number1 = ft.TextField(label="Number 1", value="0")
    txt_number2 = ft.TextField(label="Number 2", value="0")
    txt_result = ft.TextField(label="Result", value="0")

    def btn_add_click(e):
        n1 = float(txt_number1.value)
        n2 = float(txt_number2.value)
        txt_result.value = str(n1 + n2)
        page.update()

    def btn_subtract_click(e):
        n1 = float(txt_number1.value)
        n2 = float(txt_number2.value)
        txt_result.value = str(n1 - n2)
        page.update()

    def btn_multiply_click(e):
        n1 = float(txt_number1.value)
        n2 = float(txt_number2.value)
        txt_result.value = str(n1 * n2)
        page.update()

    def btn_divide_click(e):
        n1 = float(txt_number1.value)
        n2 = float(txt_number2.value)
        if n2 != 0:
            txt_result.value = str(n1 / n2)
        else:
            txt_result.value = "Error: Division by zero"
        page.update()

    btn_add = ft.ElevatedButton(text="+", on_click=btn_add_click)
    btn_subtract = ft.ElevatedButton(text="-", on_click=btn_subtract_click)
    btn_multiply = ft.ElevatedButton(text="*", on_click=btn_multiply_click)
    btn_divide = ft.ElevatedButton(text="/", on_click=btn_divide_click)

    page.add(
        txt_number1,
        txt_number2,
        ft.Row([btn_add, btn_subtract, btn_multiply, btn_divide], alignment=ft.MainAxisAlignment.CENTER),
        txt_result,
    )
    page.update()
ft.app(target=main)

