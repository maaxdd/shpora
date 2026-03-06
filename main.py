import sys
import pymysql
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QDialog, QFrame
)
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt

# Настройки подключения к БД (измените под себя)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'lopushok_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


class LoginWindow(QDialog):
    """Окно авторизации"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лопушок - Авторизация")
        self.setFixedSize(300, 250)
        # Цвета по брендбуку
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel { font-family: 'Gabriola'; font-size: 24px; color: #001c3d; }
            QLineEdit { border: 1px solid #00CC76; padding: 5px; border-radius: 3px; font-family: 'Gabriola'; font-size: 18px; }
            QPushButton { background-color: #00CC76; color: white; padding: 8px; border-radius: 3px; font-family: 'Gabriola'; font-size: 18px; }
            QPushButton:hover { background-color: #00A85F; }
            QPushButton#guestBtn { background-color: #CEFFE6; color: #001c3d; border: 1px solid #00CC76; }
            QPushButton#guestBtn:hover { background-color: #00CC76; color: white; }
        """)

        layout = QVBoxLayout()

        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.authenticate)

        self.guest_btn = QPushButton("Войти как гость")
        self.guest_btn.setObjectName("guestBtn")
        self.guest_btn.clicked.connect(self.guest_login)

        layout.addWidget(title)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(10)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.guest_btn)

        self.setLayout(layout)
        self.user_role = None

    def authenticate(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Внимание", "Заполните все поля!")
            return

        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT r.Title as role 
                    FROM User u 
                    JOIN Role r ON u.RoleID = r.ID 
                    WHERE u.Login = %s AND u.Password = %s
                ''', (login, password))
                user = cur.fetchone()

            conn.close()

            if user:
                self.user_role = user['role']
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось подключиться к БД:\n{e}")

    def guest_login(self):
        self.user_role = "Гость"
        self.accept()


class ProductItemWidget(QFrame):
    """Кастомный виджет для отображения одного товара в списке"""

    def __init__(self, product):
        super().__init__()
        # Применение стиля обрамления для каждого элемента списка (согласно ТЗ)
        self.setStyleSheet("""
            QFrame { border: 1px solid #00CC76; border-radius: 5px; background-color: #CEFFE6; margin: 2px; }
            QLabel { border: none; background-color: transparent; color: #001c3d; }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # 1. Изображение
        self.image_label = QLabel()
        image_path = product['image'] if product['image'] else 'picture.png'
        pixmap = QPixmap(image_path)

        # Если по пути из БД нет файла, ставим заглушку
        if pixmap.isNull():
            pixmap = QPixmap('picture.png')

        self.image_label.setPixmap(
            pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.image_label.setFixedSize(100, 100)
        layout.addWidget(self.image_label)

        # 2. Инфо о товаре
        info_layout = QVBoxLayout()

        title_text = f"{product['product_type']} | {product['title']}"
        self.title_label = QLabel(title_text)
        self.title_label.setFont(QFont("Gabriola", 18, QFont.Weight.Bold))

        self.article_label = QLabel(f"Артикул: {product['article']}")
        self.article_label.setFont(QFont("Gabriola", 14))

        materials = product['materials'] if product['materials'] else "Нет материалов"
        self.materials_label = QLabel(f"Материалы: {materials}")
        self.materials_label.setFont(QFont("Gabriola", 14))
        self.materials_label.setWordWrap(True)

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.article_label)
        info_layout.addWidget(self.materials_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        # 3. Стоимость
        self.price_label = QLabel(f"{product['min_cost']} ₽")
        self.price_label.setFont(QFont("Gabriola", 18, QFont.Weight.Bold))
        layout.addWidget(self.price_label, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self, role):
        super().__init__()
        self.user_role = role
        self.setWindowTitle(f"Лопушок - Каталог (Вы вошли как: {self.user_role})")
        self.resize(950, 600)

        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QLabel { font-family: 'Gabriola'; color: #001c3d; }
            QListWidget { background-color: #FFFFFF; border: none; outline: none; }
            QListWidget::item:selected { background-color: transparent; }
            QPushButton { background-color: #CEFFE6; border: 1px solid #00CC76; border-radius: 5px; padding: 5px 15px; font-family: 'Gabriola'; font-size: 16px; }
            QPushButton:hover { background-color: #00CC76; color: white; }
            QLineEdit, QComboBox { border: 1px solid #00CC76; padding: 5px; border-radius: 3px; font-family: 'Gabriola'; font-size: 15px; background-color: #FFFFFF; }
        """)

        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.all_products = []

        self.init_ui()
        self.load_product_types()
        self.load_data()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Верхняя панель ---
        top_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите наименование для поиска...")
        self.search_input.textChanged.connect(self.on_filter_change)

        self.sort_cb = QComboBox()
        self.sort_cb.addItems(["Без сортировки", "Мин. стоимость (возр.)", "Мин. стоимость (убыв.)"])
        self.sort_cb.currentIndexChanged.connect(self.on_filter_change)

        self.filter_cb = QComboBox()
        self.filter_cb.addItem("Все типы")
        self.filter_cb.currentIndexChanged.connect(self.on_filter_change)

        top_layout.addWidget(self.search_input, stretch=2)
        top_layout.addWidget(self.sort_cb, stretch=1)
        top_layout.addWidget(self.filter_cb, stretch=1)
        main_layout.addLayout(top_layout)

        # --- Список ---
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        # --- Панель администратора ---
        # Выводится ТОЛЬКО если у пользователя есть права
        if self.user_role in ['Администратор', 'Менеджер']:
            admin_layout = QHBoxLayout()
            self.add_btn = QPushButton("Добавить продукт")
            self.edit_btn = QPushButton("Редактировать")
            self.delete_btn = QPushButton("Удалить")

            admin_layout.addWidget(self.add_btn)
            admin_layout.addWidget(self.edit_btn)
            admin_layout.addWidget(self.delete_btn)
            admin_layout.addStretch()

            main_layout.addLayout(admin_layout)

        # --- Панель пагинации ---
        bottom_layout = QHBoxLayout()
        self.prev_btn = QPushButton("<")
        self.prev_btn.clicked.connect(self.prev_page)
        self.page_label = QLabel("Страница 1 из 1")
        self.page_label.setFont(QFont("Gabriola", 16))
        self.next_btn = QPushButton(">")
        self.next_btn.clicked.connect(self.next_page)

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.prev_btn)
        bottom_layout.addWidget(self.page_label)
        bottom_layout.addWidget(self.next_btn)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

    def get_db_connection(self):
        try:
            return pymysql.connect(**DB_CONFIG)
        except Exception:
            return None

    def load_product_types(self):
        conn = self.get_db_connection()
        if not conn: return
        with conn.cursor() as cur:
            cur.execute("SELECT Title FROM ProductType")
            for row in cur.fetchall():
                self.filter_cb.addItem(row['Title'])
        conn.close()

    def on_filter_change(self):
        self.current_page = 1
        self.load_data()

    def load_data(self):
        conn = self.get_db_connection()
        if not conn: return

        search_text = self.search_input.text()
        sort_index = self.sort_cb.currentIndex()
        filter_text = self.filter_cb.currentText()

        query = '''
            SELECT p.ID as id, p.Title as title, pt.Title as product_type, 
                   p.ArticleNumber as article, p.MinCostForAgent as min_cost, p.Image as image,
                   GROUP_CONCAT(m.Title SEPARATOR ', ') as materials
            FROM Product p
            JOIN ProductType pt ON p.ProductTypeID = pt.ID
            LEFT JOIN ProductMaterial pm ON p.ID = pm.ProductID
            LEFT JOIN Material m ON pm.MaterialID = m.ID
            WHERE p.Title LIKE %s
        '''
        params = [f"%{search_text}%"]

        if filter_text != "Все типы":
            query += " AND pt.Title = %s"
            params.append(filter_text)

        query += " GROUP BY p.ID"

        if sort_index == 1:
            query += " ORDER BY p.MinCostForAgent ASC"
        elif sort_index == 2:
            query += " ORDER BY p.MinCostForAgent DESC"

        with conn.cursor() as cur:
            cur.execute(query, params)
            self.all_products = cur.fetchall()

        conn.close()

        self.total_pages = max(1, (len(self.all_products) + self.items_per_page - 1) // self.items_per_page)
        self.display_page()

    def display_page(self):
        self.list_widget.clear()
        self.page_label.setText(f"Страница {self.current_page} из {self.total_pages}")

        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_items = self.all_products[start:end]

        for product in page_items:
            item = QListWidgetItem(self.list_widget)
            widget = ProductItemWidget(product)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.setItemWidget(item, widget)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_page()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 1. Запуск окна авторизации
    login_dialog = LoginWindow()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # 2. Если авторизация успешна - запускаем основное окно и передаем роль
        window = MainWindow(login_dialog.user_role)
        window.show()
        sys.exit(app.exec())