from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QMessageBox,
                             QCheckBox, QDoubleSpinBox, QComboBox, QSpinBox,
                             QTextEdit, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Item")
        self.setModal(True)
        self.setMinimumSize(400, 500)

        self.image_path = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Tipo (Meta ou Conta)
        layout.addWidget(QLabel("Tipo:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Meta de Compra", "Conta do Mês"])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)

        # Nome
        layout.addWidget(QLabel("Nome:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Descrição (apenas para contas)
        self.desc_label = QLabel("Descrição:")
        layout.addWidget(self.desc_label)
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setPlaceholderText("Descrição da conta (opcional)")
        layout.addWidget(self.desc_input)

        # Preço
        layout.addWidget(QLabel("Valor (R$):"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("R$ ")
        layout.addWidget(self.price_input)

        # Campos específicos para contas
        self.installments_label = QLabel("Parcelas:")
        layout.addWidget(self.installments_label)

        installments_layout = QHBoxLayout()
        self.installments_input = QSpinBox()
        self.installments_input.setMinimum(1)
        self.installments_input.setMaximum(99)
        self.installments_input.setValue(1)
        self.installments_input.setPrefix("x ")
        installments_layout.addWidget(self.installments_input)
        installments_layout.addStretch()
        layout.addLayout(installments_layout)

        self.day_label = QLabel("Dia do Pagamento:")
        layout.addWidget(self.day_label)

        day_layout = QHBoxLayout()
        self.day_input = QSpinBox()
        self.day_input.setMinimum(1)
        self.day_input.setMaximum(31)
        self.day_input.setValue(1)
        day_layout.addWidget(self.day_input)
        day_layout.addStretch()
        layout.addLayout(day_layout)

        # Link
        self.link_label = QLabel("Link:")
        layout.addWidget(self.link_label)
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("https://...")
        layout.addWidget(self.link_input)

        # Imagem
        self.image_section_label = QLabel("Imagem (opcional):")
        layout.addWidget(self.image_section_label)

        image_layout = QHBoxLayout()
        self.image_label = QLabel("Nenhuma imagem")
        self.image_label.setFixedSize(100, 100)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px dashed #555; border-radius: 5px;")

        image_btn = QPushButton("Selecionar")
        image_btn.clicked.connect(self.select_image)

        image_layout.addWidget(self.image_label)
        image_layout.addWidget(image_btn)
        layout.addLayout(image_layout)

        # Botões
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self.validate_and_accept)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # Inicializar estado
        self.on_type_changed(0)

    def on_type_changed(self, index):
        """Mostra/esconde campos baseado no tipo selecionado"""
        is_conta = index == 1

        # Campos específicos de conta
        self.desc_label.setVisible(is_conta)
        self.desc_input.setVisible(is_conta)
        self.installments_label.setVisible(is_conta)
        self.installments_input.setVisible(is_conta)
        self.day_label.setVisible(is_conta)
        self.day_input.setVisible(is_conta)

        # Ajustar labels
        if is_conta:
            self.link_label.setText("Link (opcional):")
            self.image_section_label.setText("Imagem (opcional):")
        else:
            self.link_label.setText("Link de Compra:")
            self.image_section_label.setText("Imagem:")

        self.adjustSize()
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Imagem", "",
            "Imagens (*.png *.jpg *.jpeg *.gif *.webp)"
        )
        
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled)
    
    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Atenção", "Por favor, insira o nome.")
            return

        if self.price_input.value() <= 0:
            QMessageBox.warning(self, "Atenção", "Por favor, insira um valor válido.")
            return

        self.accept()

    def get_data(self):
        is_conta = self.type_combo.currentIndex() == 1

        return {
            'type': 'conta' if is_conta else 'meta',
            'name': self.name_input.text().strip(),
            'price': self.price_input.value(),
            'link': self.link_input.text().strip(),
            'image_path': self.image_path,
            'description': self.desc_input.toPlainText().strip() if is_conta else None,
            'installments': self.installments_input.value() if is_conta else None,
            'installment_day': self.day_input.value() if is_conta else None
        }


class EditProductDialog(QDialog):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Item")
        self.setModal(True)
        self.setMinimumSize(400, 500)

        self.product = product
        self.image_path = None
        self.keep_current_image = True

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Tipo (Meta ou Conta)
        layout.addWidget(QLabel("Tipo:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Meta de Compra", "Conta do Mês"])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)

        # Nome
        layout.addWidget(QLabel("Nome:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Descrição (apenas para contas)
        self.desc_label = QLabel("Descrição:")
        layout.addWidget(self.desc_label)
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setPlaceholderText("Descrição da conta (opcional)")
        layout.addWidget(self.desc_input)

        # Preço
        layout.addWidget(QLabel("Valor (R$):"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("R$ ")
        layout.addWidget(self.price_input)

        # Campos específicos para contas
        self.installments_label = QLabel("Parcelas:")
        layout.addWidget(self.installments_label)

        installments_layout = QHBoxLayout()
        self.installments_input = QSpinBox()
        self.installments_input.setMinimum(1)
        self.installments_input.setMaximum(99)
        self.installments_input.setValue(1)
        self.installments_input.setPrefix("x ")
        installments_layout.addWidget(self.installments_input)
        installments_layout.addStretch()
        layout.addLayout(installments_layout)

        self.day_label = QLabel("Dia do Pagamento:")
        layout.addWidget(self.day_label)

        day_layout = QHBoxLayout()
        self.day_input = QSpinBox()
        self.day_input.setMinimum(1)
        self.day_input.setMaximum(31)
        self.day_input.setValue(1)
        day_layout.addWidget(self.day_input)
        day_layout.addStretch()
        layout.addLayout(day_layout)

        # Link
        self.link_label = QLabel("Link:")
        layout.addWidget(self.link_label)
        self.link_input = QLineEdit()
        layout.addWidget(self.link_input)

        # Imagem
        self.image_section_label = QLabel("Imagem:")
        layout.addWidget(self.image_section_label)

        image_layout = QHBoxLayout()
        self.image_label = QLabel()
        self.image_label.setFixedSize(100, 100)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px dashed #555; border-radius: 5px;")

        image_btn = QPushButton("Alterar Imagem")
        image_btn.clicked.connect(self.select_image)

        image_layout.addWidget(self.image_label)
        image_layout.addWidget(image_btn)
        layout.addLayout(image_layout)

        # Botões
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self.validate_and_accept)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def on_type_changed(self, index):
        """Mostra/esconde campos baseado no tipo selecionado"""
        is_conta = index == 1

        # Campos específicos de conta
        self.desc_label.setVisible(is_conta)
        self.desc_input.setVisible(is_conta)
        self.installments_label.setVisible(is_conta)
        self.installments_input.setVisible(is_conta)
        self.day_label.setVisible(is_conta)
        self.day_input.setVisible(is_conta)

        # Ajustar labels
        if is_conta:
            self.link_label.setText("Link (opcional):")
            self.image_section_label.setText("Imagem (opcional):")
        else:
            self.link_label.setText("Link de Compra:")
            self.image_section_label.setText("Imagem:")

        self.adjustSize()
    
    def load_data(self):
        # Definir tipo
        item_type = self.product.get('type', 'meta')
        self.type_combo.setCurrentIndex(1 if item_type == 'conta' else 0)

        self.name_input.setText(self.product['name'])
        self.price_input.setValue(self.product['price'])
        self.link_input.setText(self.product.get('link') or '')

        # Campos específicos de conta
        if item_type == 'conta':
            self.desc_input.setPlainText(self.product.get('description') or '')
            self.installments_input.setValue(self.product.get('installments') or 1)
            self.day_input.setValue(self.product.get('installment_day') or 1)

        if self.product['image']:
            pixmap = QPixmap()
            pixmap.loadFromData(self.product['image'])
            scaled = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("Sem imagem")
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Imagem", "",
            "Imagens (*.png *.jpg *.jpeg *.gif *.webp)"
        )
        
        if file_path:
            self.image_path = file_path
            self.keep_current_image = False
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled)
    
    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Atenção", "Por favor, insira o nome.")
            return

        if self.price_input.value() <= 0:
            QMessageBox.warning(self, "Atenção", "Por favor, insira um valor válido.")
            return

        self.accept()

    def get_data(self):
        is_conta = self.type_combo.currentIndex() == 1

        return {
            'type': 'conta' if is_conta else 'meta',
            'name': self.name_input.text().strip(),
            'price': self.price_input.value(),
            'link': self.link_input.text().strip(),
            'image_path': self.image_path,
            'keep_current_image': self.keep_current_image,
            'description': self.desc_input.toPlainText().strip() if is_conta else None,
            'installments': self.installments_input.value() if is_conta else None,
            'installment_day': self.day_input.value() if is_conta else None
        }


class EditSavedAmountDialog(QDialog):
    def __init__(self, current_amount, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Valor Guardado")
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        self.current_amount = current_amount
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("Valor Guardado (R$):"))
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(9999999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("R$ ")
        self.amount_input.setValue(self.current_amount)
        layout.addWidget(self.amount_input)
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def get_amount(self):
        return self.amount_input.value()


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setModal(True)
        self.setFixedSize(450, 230)
        
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Mostrar itens comprados
        self.show_purchased_check = QCheckBox("Mostrar itens comprados")
        self.show_purchased_check.setChecked(self.config.get_show_purchased())
        layout.addWidget(self.show_purchased_check)
        
        # Caminho do banco de dados
        layout.addWidget(QLabel("Local do Banco de Dados:"))
        
        db_layout = QHBoxLayout()
        self.db_path_label = QLabel(self.config.get_db_path() or "Não configurado")
        self.db_path_label.setWordWrap(True)
        self.db_path_label.setStyleSheet("padding: 5px; background: #2a2a2a; border-radius: 3px;")
        
        change_db_btn = QPushButton("Alterar Local")
        change_db_btn.clicked.connect(self.change_db_location)

        import_db_btn = QPushButton("Importar Banco Existente")
        import_db_btn.clicked.connect(self.import_db)

        db_layout.addWidget(self.db_path_label, 3)

        # Layout para os dois botões
        db_buttons_layout = QVBoxLayout()
        db_buttons_layout.setSpacing(5)
        db_buttons_layout.addWidget(change_db_btn)
        db_buttons_layout.addWidget(import_db_btn)

        db_layout.addLayout(db_buttons_layout, 1)
        
        layout.addLayout(db_layout)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addStretch()
        layout.addLayout(btn_layout)
    
    def change_db_location(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Selecionar Local do Banco de Dados", 
            "", "Banco de Dados (*.db)"
        )
        
        if file_path:
            if not file_path.endswith('.db'):
                file_path += '.db'
            self.db_path_label.setText(file_path)

    def import_db(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Banco de Dados Existente",
            "", "Banco de Dados (*.db)"
        )
        
        if file_path:
            self.db_path_label.setText(file_path)

    def save_settings(self):
        self.config.set_show_purchased(self.show_purchased_check.isChecked())
        
        new_path = self.db_path_label.text()
        if new_path != "Não configurado" and new_path != self.config.get_db_path():
            reply = QMessageBox.question(
                self, "Alterar Local do Banco",
                "Deseja realmente alterar o local do banco de dados?\n"
                "O programa será reiniciado.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.config.set_db_path(new_path)
                QMessageBox.information(self, "Atenção", 
                                       "Por favor, reinicie o programa para aplicar as alterações.")
        
        self.accept()
