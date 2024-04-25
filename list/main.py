import flet as ft
import mysql.connector
import sys
from mysql.connector import errorcode

args = sys.argv

if len(args) > 1:
    username_index = args.index("--username")
    if username_index != -1 and username_index + 1 < len(args):
        current_username = args[username_index + 1]
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="task"
    )
    cursor = conn.cursor()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Неверные учетные данные для доступа к базе данных")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("База данных не существует")
    else:
        print(err)

try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed TINYINT DEFAULT 0
    )
    ''')
except mysql.connector.Error as err:
    print(f"Ошибка создания таблицы: {err}")

class Database:
    @staticmethod
    def add_task(name):
        try:
            cursor.execute('INSERT INTO tasks (name) VALUES (%s)', (name,))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Ошибка добавления задачи: {err}")

    @staticmethod
    def get_tasks():
        try:
            cursor.execute('SELECT * FROM tasks')
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Ошибка получения задач: {err}")

    @staticmethod
    def delete_task(task_id):
        try:
            cursor.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Ошибка удаления задачи: {err}")

class Task(ft.UserControl):
    def __init__(self, task_id, task_name, task_status_change, task_delete):
        super().__init__()
        self.task_id = task_id
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete

    def build(self):
        self.display_task = ft.Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Редактировать задачу",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Удалить задачу",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Обновить задачу",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return ft.Column(controls=[self.display_view, self.edit_view])

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()


    def save_clicked(self, e):
        new_name = self.edit_name.value
        self.display_task.label = new_name
        try:
            cursor.execute('UPDATE tasks SET name = %s WHERE id = %s', (new_name, self.task_id))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Ошибка обновления задачи: {err}")
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        try:
            cursor.execute('UPDATE tasks SET completed = %s WHERE id = %s', (int(self.completed), self.task_id))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Ошибка обновления статуса задачи: {err}")
        self.task_status_change(self)

    def delete_clicked(self, e):
        try:
            cursor.execute('DELETE FROM tasks WHERE id = %s', (self.task_id,))
            conn.commit()
            self.task_delete(self)
        except mysql.connector.Error as err:
            print(f"Ошибка удаления задачи: {err}")

class TodoApp(ft.UserControl):
    def build(self):
        self.new_task = ft.TextField(
            hint_text="Что нужно сделать?",
            on_submit=self.add_clicked,
            expand=True,
            max_length=255
        )
        self.tasks = ft.Column()

        self.filter = ft.Tabs(
            scrollable=False,
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="все"), ft.Tab(text="активные"), ft.Tab(text="завершенные")],
        )

        self.items_left = ft.Text("0 активных элементов")

        existing_tasks = Database.get_tasks()
        for task_data in existing_tasks:
            task_id, task_name, created_at, completed = task_data
            task = Task(task_id, task_name, self.task_status_change, self.task_delete)
            task.completed = bool(completed)
            self.tasks.controls.append(task)

        return ft.Column(
            width=600,
            controls=[
                ft.Row(
                    [ft.Text(value="Список задач", style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.FloatingActionButton(
                            icon=ft.icons.ADD, on_click=self.add_clicked
                        ),
                    ],
                ),
                ft.Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.items_left,
                                ft.OutlinedButton(
                                    text="Очистить завершенные", on_click=self.clear_clicked
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    def add_clicked(self, e):
        if self.new_task.value:
            try:
                cursor.execute('INSERT INTO tasks (name) VALUES (%s)', (self.new_task.value,))
                conn.commit()
                task_id = cursor.lastrowid
                task = Task(task_id, self.new_task.value, self.task_status_change, self.task_delete)
                self.tasks.controls.append(task)
                self.new_task.value = ""
                self.new_task.focus()
                self.update()
            except mysql.connector.Error as err:
                print(f"Ошибка добавления задачи: {err}")

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()


    def tabs_changed(self, e):
        self.update()

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                task.delete_clicked(None)


    def update(self):
        try:
            status = self.filter.tabs[self.filter.selected_index].text
            cursor.execute('SELECT COUNT(*) FROM tasks WHERE completed = 0')
            count = cursor.fetchone()[0]
            for task in self.tasks.controls:
                task.visible = (
                    status == "все"
                    or (status == "активные" and not task.completed)
                    or (status == "завершенные" and task.completed)
                )
            self.items_left.value = f"{count} активных элементов осталось"
        except mysql.connector.Error as err:
            print(f"Ошибка обновления интерфейса: {err}")
        super().update()

async def main(page: ft.Page):
    page.title = "Список задач"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    page.add(TodoApp())

ft.app(main)
