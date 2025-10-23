from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QScrollArea, QMessageBox, QFrame, QTabWidget,
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QUrl, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt6.QtGui import QDesktopServices
from ui.card_widget import ProductCard, format_brl
from ui.dialogs import AddProductDialog, EditProductDialog, EditSavedAmountDialog, EditSalaryDialog, SettingsDialog
from database import Database


class FlowLayout(QHBoxLayout):
    """Layout que organiza widgets em flow horizontal com wrap"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(20)
        self.setContentsMargins(20, 20, 20, 20)
        self._items = []
    
    def addWidget(self, widget):
        self._items.append(widget)
        super().addWidget(widget)
    
    def clear_layout(self):
        while self.count():
            item = self.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._items.clear()


class MainWindow(QMainWindow):
    def __init__(self, db, config):
        super().__init__()
        self.db = db
        self.config = config
        self.selected_items = {}  # Dicionário para rastrear itens selecionados {id: price}

        self.setWindowTitle("Meta de Compra")
        self.setMinimumSize(1000, 550)
        self.resize(1400, 750)

        self.setup_ui()
        self.load_products()
    
    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(70)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Valor guardado e salário (esquerda)
        values_layout = QHBoxLayout()

        self.saved_label = QLabel("Valor Guardado: R$ 0,00")
        self.saved_label.setObjectName("savedAmount")

        edit_saved_btn = QPushButton("Editar")
        edit_saved_btn.setObjectName("editSavedBtn")
        edit_saved_btn.clicked.connect(self.edit_saved_amount)

        self.salary_label = QLabel("Salário: R$ 0,00")
        self.salary_label.setObjectName("salaryAmount")

        edit_salary_btn = QPushButton("Editar")
        edit_salary_btn.setObjectName("editSavedBtn")
        edit_salary_btn.clicked.connect(self.edit_salary)

        values_layout.addWidget(self.saved_label)
        values_layout.addWidget(edit_saved_btn)
        values_layout.addSpacing(30)
        values_layout.addWidget(self.salary_label)
        values_layout.addWidget(edit_salary_btn)

        header_layout.addLayout(values_layout)
        header_layout.addStretch()
        
        # Botões direita
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        add_btn = QPushButton("Adicionar")
        add_btn.setObjectName("addButton")
        add_btn.clicked.connect(self.add_product)

        forecast_btn = QPushButton("📊")
        forecast_btn.setObjectName("settingsButton")
        forecast_btn.setFixedSize(40, 40)
        forecast_btn.setToolTip("Previsão de Parcelas")
        forecast_btn.clicked.connect(self.toggle_sidebar)

        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("settingsButton")
        settings_btn.setFixedSize(40, 40)
        settings_btn.clicked.connect(self.open_settings)

        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(forecast_btn)
        buttons_layout.addWidget(settings_btn)
        
        header_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(header)

        # Container principal com sidebar e conteúdo
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Tabs para separar Metas e Contas
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")

        # Tab de Metas
        metas_tab = QWidget()
        metas_layout = QVBoxLayout(metas_tab)
        metas_layout.setContentsMargins(0, 0, 0, 0)

        metas_scroll = QScrollArea()
        metas_scroll.setWidgetResizable(True)
        metas_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.metas_container = QWidget()
        self.metas_container.setObjectName("cardsContainer")
        metas_container_layout = QVBoxLayout(self.metas_container)
        metas_container_layout.setContentsMargins(0, 0, 0, 0)
        metas_container_layout.setSpacing(0)

        self.metas_flow_container = QWidget()
        self.metas_flow_container.setObjectName("flowContainer")
        self.metas_flow_layout = FlowLayout(self.metas_flow_container)

        metas_container_layout.addWidget(self.metas_flow_container)
        metas_container_layout.addStretch()

        metas_scroll.setWidget(self.metas_container)
        metas_layout.addWidget(metas_scroll)

        # Tab de Contas
        contas_tab = QWidget()
        contas_layout = QVBoxLayout(contas_tab)
        contas_layout.setContentsMargins(0, 0, 0, 0)

        contas_scroll = QScrollArea()
        contas_scroll.setWidgetResizable(True)
        contas_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.contas_container = QWidget()
        self.contas_container.setObjectName("cardsContainer")
        contas_container_layout = QVBoxLayout(self.contas_container)
        contas_container_layout.setContentsMargins(0, 0, 0, 0)
        contas_container_layout.setSpacing(0)

        self.contas_flow_container = QWidget()
        self.contas_flow_container.setObjectName("flowContainer")
        self.contas_flow_layout = FlowLayout(self.contas_flow_container)

        contas_container_layout.addWidget(self.contas_flow_container)
        contas_container_layout.addStretch()

        contas_scroll.setWidget(self.contas_container)
        contas_layout.addWidget(contas_scroll)

        # Adicionar tabs
        self.tabs.addTab(metas_tab, "Metas de Compra")
        self.tabs.addTab(contas_tab, "Contas do Mês")

        # Adicionar tabs ao container
        content_layout.addWidget(self.tabs, 3)

        # Sidebar com previsão de parcelas
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        self.sidebar.setVisible(False)  # Inicialmente oculta

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 15, 15, 15)
        sidebar_layout.setSpacing(10)

        sidebar_title = QLabel("Previsão de Parcelas")
        sidebar_title.setObjectName("sidebarTitle")
        sidebar_layout.addWidget(sidebar_title)

        # Scroll area para os meses
        forecast_scroll = QScrollArea()
        forecast_scroll.setWidgetResizable(True)
        forecast_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        forecast_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        forecast_scroll.setStyleSheet("QScrollArea { background-color: #1f1f1f; border: none; }")

        self.forecast_container = QWidget()
        self.forecast_container.setStyleSheet("QWidget { background-color: #1f1f1f; }")
        self.forecast_layout = QVBoxLayout(self.forecast_container)
        self.forecast_layout.setSpacing(8)
        self.forecast_layout.setContentsMargins(0, 0, 0, 0)

        forecast_scroll.setWidget(self.forecast_container)
        sidebar_layout.addWidget(forecast_scroll)

        content_layout.addWidget(self.sidebar, 1)

        main_layout.addWidget(content_container)

        # Footer com total de contas, saldo e somatório de selecionados
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFixedHeight(50)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(30, 0, 30, 0)

        self.bills_label = QLabel("Contas do Mês: R$ 0,00")
        self.bills_label.setObjectName("billsTotal")

        footer_layout.addWidget(self.bills_label)
        footer_layout.addStretch()

        # Painel de somatório de itens selecionados
        self.selected_panel = QFrame()
        self.selected_panel.setObjectName("selectedPanel")
        self.selected_panel.setVisible(False)  # Oculto por padrão

        selected_layout = QHBoxLayout(self.selected_panel)
        selected_layout.setContentsMargins(15, 5, 15, 5)
        selected_layout.setSpacing(10)

        selected_icon = QLabel("☑")
        selected_icon.setObjectName("selectedIcon")

        self.selected_label = QLabel("Itens selecionados: 0")
        self.selected_label.setObjectName("selectedCount")

        self.selected_total_label = QLabel("Total: R$ 0,00")
        self.selected_total_label.setObjectName("selectedTotal")

        selected_layout.addWidget(selected_icon)
        selected_layout.addWidget(self.selected_label)
        selected_layout.addWidget(self.selected_total_label)

        footer_layout.addWidget(self.selected_panel)
        footer_layout.addStretch()

        self.balance_label = QLabel("Saldo: R$ 0,00")
        self.balance_label.setObjectName("balanceAmount")

        footer_layout.addWidget(self.balance_label)

        main_layout.addWidget(footer)

        # Atualizar valor guardado
        self.update_saved_label()
        self.update_salary_label()
        self.update_bills_and_balance()
        self.update_forecast()

    def update_saved_label(self):
        amount = self.db.get_saved_amount()
        self.saved_label.setText(f"Valor Guardado: {format_brl(amount)}")
        return amount

    def update_salary_label(self):
        salary = self.db.get_salary()
        self.salary_label.setText(f"Salário: {format_brl(salary)}")
        return salary

    def update_bills_and_balance(self):
        bills_total = self.db.get_monthly_bills_total()
        salary = self.db.get_salary()
        balance = salary - bills_total

        self.bills_label.setText(f"Contas do Mês: {format_brl(bills_total)}")

        # Definir cor do saldo baseado em positivo/negativo
        if balance >= 0:
            self.balance_label.setProperty("positive", "true")
        else:
            self.balance_label.setProperty("positive", "false")

        self.balance_label.setText(f"Saldo: {format_brl(balance)}")
        self.balance_label.style().unpolish(self.balance_label)
        self.balance_label.style().polish(self.balance_label)

        return bills_total, balance

    def update_forecast(self):
        """Atualiza a sidebar com previsão de parcelas"""
        # Limpar forecast anterior
        while self.forecast_layout.count():
            item = self.forecast_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Obter previsão
        forecast = self.db.get_monthly_forecast()

        if not forecast:
            no_forecast = QLabel("Nenhuma conta parcelada")
            no_forecast.setObjectName("noForecast")
            no_forecast.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.forecast_layout.addWidget(no_forecast)
            return

        # Criar item para cada mês
        for month_data in forecast:
            month_item = QFrame()
            month_item.setObjectName("forecastItem")

            item_layout = QHBoxLayout(month_item)
            item_layout.setContentsMargins(10, 8, 10, 8)
            item_layout.setSpacing(10)

            month_label = QLabel(month_data['month'])
            month_label.setObjectName("forecastMonth")

            value_label = QLabel(format_brl(month_data['total']))
            value_label.setObjectName("forecastValue")

            # Se for zero, marcar diferente
            if month_data['total'] == 0:
                value_label.setProperty("zero", "true")
                value_label.style().unpolish(value_label)
                value_label.style().polish(value_label)

            item_layout.addWidget(month_label)
            item_layout.addStretch()
            item_layout.addWidget(value_label)

            self.forecast_layout.addWidget(month_item)

        self.forecast_layout.addStretch()

    def load_products(self):
        # Limpar cards existentes
        self.metas_flow_layout.clear_layout()
        self.contas_flow_layout.clear_layout()

        # Limpar seleção anterior
        self.selected_items.clear()
        self.update_selected_panel()

        # Carregar produtos
        show_purchased = self.config.get_show_purchased()
        products = self.db.get_all_products(show_purchased)
        saved_amount = self.update_saved_label()
        self.update_bills_and_balance()
        self.update_forecast()

        # Separar metas e contas
        metas = []
        contas = []
        for p in products:
            if 'type' in p.keys() and p['type'] == 'conta':
                contas.append(p)
            else:
                metas.append(p)

        # Verificar se há produtos
        if not products:
            no_products = QLabel("Nenhum item adicionado ainda.\nClique em 'Adicionar' para começar!")
            no_products.setObjectName("noProducts")
            no_products.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.metas_container.layout().insertWidget(0, no_products)
            return

        # Criar cards de metas
        if not metas:
            no_metas = QLabel("Nenhuma meta cadastrada")
            no_metas.setObjectName("noProducts")
            no_metas.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.metas_container.layout().insertWidget(0, no_metas)
        else:
            for product in metas:
                card = ProductCard(product, saved_amount)
                card.edit_clicked.connect(self.edit_product)
                card.remove_clicked.connect(self.remove_product)
                card.purchase_clicked.connect(self.toggle_purchase)
                card.link_clicked.connect(self.open_link)
                card.selection_changed.connect(self.on_selection_changed)
                self.metas_flow_layout.addWidget(card)

        # Criar cards de contas
        if not contas:
            no_contas = QLabel("Nenhuma conta cadastrada")
            no_contas.setObjectName("noProducts")
            no_contas.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.contas_container.layout().insertWidget(0, no_contas)
        else:
            for product in contas:
                card = ProductCard(product, saved_amount)
                card.edit_clicked.connect(self.edit_product)
                card.remove_clicked.connect(self.remove_product)
                card.purchase_clicked.connect(self.toggle_purchase)
                card.link_clicked.connect(self.open_link)
                card.selection_changed.connect(self.on_selection_changed)
                self.contas_flow_layout.addWidget(card)
    
    def add_product(self):
        dialog = AddProductDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.db.add_product(
                name=data['name'],
                price=data['price'],
                link=data['link'],
                image_path=data['image_path'],
                item_type=data['type'],
                description=data.get('description'),
                installments=data.get('installments'),
                installment_day=data.get('installment_day')
            )
            self.load_products()
    
    def edit_product(self, product_id):
        # Buscar produto
        products = self.db.get_all_products(True)
        product = next((p for p in products if p['id'] == product_id), None)

        if product:
            dialog = EditProductDialog(product, self)
            if dialog.exec():
                data = dialog.get_data()

                if data['keep_current_image']:
                    self.db.update_product(
                        product_id=product_id,
                        name=data['name'],
                        price=data['price'],
                        link=data['link'],
                        item_type=data['type'],
                        description=data.get('description'),
                        installments=data.get('installments'),
                        installment_day=data.get('installment_day')
                    )
                else:
                    self.db.update_product(
                        product_id=product_id,
                        name=data['name'],
                        price=data['price'],
                        link=data['link'],
                        image_path=data['image_path'],
                        item_type=data['type'],
                        description=data.get('description'),
                        installments=data.get('installments'),
                        installment_day=data.get('installment_day')
                    )

                self.load_products()
    
    def remove_product(self, product_id):
        reply = QMessageBox.question(
            self, "Confirmar Remoção",
            "Tem certeza que deseja remover este produto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_product(product_id)
            self.load_products()
    
    def toggle_purchase(self, product_id):
        self.db.toggle_purchased(product_id)
        self.load_products()
    
    def open_link(self, link):
        if link:
            QDesktopServices.openUrl(QUrl(link))
    
    def edit_saved_amount(self):
        current = self.db.get_saved_amount()
        dialog = EditSavedAmountDialog(current, self)

        if dialog.exec():
            new_amount = dialog.get_amount()
            self.db.update_saved_amount(new_amount)
            self.load_products()

    def edit_salary(self):
        current = self.db.get_salary()
        dialog = EditSalaryDialog(current, self)

        if dialog.exec():
            new_salary = dialog.get_amount()
            self.db.update_salary(new_salary)
            self.update_salary_label()
            self.update_bills_and_balance()

    def toggle_sidebar(self):
        """Mostra/oculta a sidebar de previsão com animação"""
        is_visible = self.sidebar.isVisible()

        if not is_visible:
            # Mostrar sidebar
            self.sidebar.setVisible(True)

            # Animação de fade in
            self.sidebar_opacity = QGraphicsOpacityEffect(self.sidebar)
            self.sidebar.setGraphicsEffect(self.sidebar_opacity)

            self.sidebar_fade = QPropertyAnimation(self.sidebar_opacity, b"opacity")
            self.sidebar_fade.setDuration(300)
            self.sidebar_fade.setStartValue(0.0)
            self.sidebar_fade.setEndValue(1.0)
            self.sidebar_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.sidebar_fade.start()
        else:
            # Ocultar sidebar
            self.sidebar_opacity = QGraphicsOpacityEffect(self.sidebar)
            self.sidebar.setGraphicsEffect(self.sidebar_opacity)

            self.sidebar_fade = QPropertyAnimation(self.sidebar_opacity, b"opacity")
            self.sidebar_fade.setDuration(200)
            self.sidebar_fade.setStartValue(1.0)
            self.sidebar_fade.setEndValue(0.0)
            self.sidebar_fade.setEasingCurve(QEasingCurve.Type.InCubic)
            self.sidebar_fade.finished.connect(lambda: self.sidebar.setVisible(False))
            self.sidebar_fade.start()

    def open_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            self.load_products()

    def on_selection_changed(self, product_id, is_selected, price):
        """Atualiza o painel de somatório quando um card é selecionado/deselecionado"""
        if is_selected:
            self.selected_items[product_id] = price
        else:
            self.selected_items.pop(product_id, None)

        self.update_selected_panel()

    def update_selected_panel(self):
        """Atualiza o painel de somatório com os itens selecionados"""
        count = len(self.selected_items)
        total = sum(self.selected_items.values())

        if count > 0:
            self.selected_panel.setVisible(True)
            self.selected_label.setText(f"Itens selecionados: {count}")
            self.selected_total_label.setText(f"Total: {format_brl(total)}")
        else:
            self.selected_panel.setVisible(False)
