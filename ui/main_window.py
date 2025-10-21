from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QScrollArea, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from ui.card_widget import ProductCard
from ui.dialogs import AddProductDialog, EditProductDialog, EditSavedAmountDialog, SettingsDialog
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
        
        self.setWindowTitle("Meta de Compra")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)
        
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
        header.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Valor guardado (esquerda)
        saved_layout = QHBoxLayout()
        self.saved_label = QLabel("Valor Guardado: R$ 0,00")
        self.saved_label.setObjectName("savedAmount")
        
        edit_saved_btn = QPushButton("Editar")
        edit_saved_btn.setObjectName("editSavedBtn")
        edit_saved_btn.clicked.connect(self.edit_saved_amount)
        
        saved_layout.addWidget(self.saved_label)
        saved_layout.addWidget(edit_saved_btn)
        
        header_layout.addLayout(saved_layout)
        header_layout.addStretch()
        
        # Botões direita
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        add_btn = QPushButton("Adicionar")
        add_btn.setObjectName("addButton")
        add_btn.clicked.connect(self.add_product)
        
        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("settingsButton")
        settings_btn.setFixedSize(40, 40)
        settings_btn.clicked.connect(self.open_settings)
        
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(settings_btn)
        
        header_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(header)
        
        # Área de scroll para os cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container dos cards
        self.cards_container = QWidget()
        self.cards_container.setObjectName("cardsContainer")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(0)
        
        # Flow container
        self.flow_container = QWidget()
        self.flow_container.setObjectName("flowContainer")
        self.flow_layout = FlowLayout(self.flow_container)
        
        self.cards_layout.addWidget(self.flow_container)
        self.cards_layout.addStretch()
        
        scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(scroll_area)

        # Footer com total de contas
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFixedHeight(60)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(30, 0, 30, 0)

        footer_layout.addStretch()

        self.bills_label = QLabel("Contas do Mês: R$ 0,00")
        self.bills_label.setObjectName("billsTotal")

        footer_layout.addWidget(self.bills_label)

        main_layout.addWidget(footer)

        # Atualizar valor guardado
        self.update_saved_label()
        self.update_bills_label()
    
    def update_saved_label(self):
        amount = self.db.get_saved_amount()
        self.saved_label.setText(f"Valor Guardado: R$ {amount:,.2f}")
        return amount

    def update_bills_label(self):
        total = self.db.get_monthly_bills_total()
        self.bills_label.setText(f"Contas do Mês: R$ {total:,.2f}")
        return total
    
    def load_products(self):
        # Limpar cards existentes
        self.flow_layout.clear_layout()

        # Carregar produtos
        show_purchased = self.config.get_show_purchased()
        products = self.db.get_all_products(show_purchased)
        saved_amount = self.update_saved_label()
        self.update_bills_label()

        if not products:
            no_products = QLabel("Nenhum produto adicionado ainda.\nClique em 'Adicionar' para começar!")
            no_products.setObjectName("noProducts")
            no_products.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_layout.insertWidget(0, no_products)
            return

        # Criar cards
        for product in products:
            card = ProductCard(product, saved_amount)
            card.edit_clicked.connect(self.edit_product)
            card.remove_clicked.connect(self.remove_product)
            card.purchase_clicked.connect(self.toggle_purchase)
            card.link_clicked.connect(self.open_link)

            self.flow_layout.addWidget(card)
    
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
    
    def open_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            self.load_products()
