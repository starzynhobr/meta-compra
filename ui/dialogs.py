from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QMessageBox,
                             QCheckBox, QDoubleSpinBox, QComboBox, QSpinBox,
                             QTextEdit, QWidget, QScrollArea, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap


class AnimatedDialog(QDialog):
    """Dialog base com animação fade in"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Criar efeito de opacidade
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Animação fade in
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event):
        """Iniciar animação quando o dialog for mostrado"""
        super().showEvent(event)
        self.fade_animation.start()

class AddProductDialog(AnimatedDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Item")
        self.setModal(True)
        self.setFixedSize(450, 600)

        self.image_path = None
        self.setup_ui()

    def setup_ui(self):
        # Layout principal do dialog
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll Area para os campos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: #1a1a1a; border: none; }")

        # Widget container para os campos
        form_widget = QWidget()
        form_widget.setStyleSheet("QWidget { background-color: #1a1a1a; }")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        # Tipo (Meta ou Conta)
        form_layout.addWidget(QLabel("Tipo:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Meta de Compra", "Conta do Mês"])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form_layout.addWidget(self.type_combo)

        # Nome
        form_layout.addWidget(QLabel("Nome:"))
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(35)
        form_layout.addWidget(self.name_input)

        # Descrição (apenas para contas)
        self.desc_label = QLabel("Descrição:")
        form_layout.addWidget(self.desc_label)
        self.desc_input = QTextEdit()
        self.desc_input.setMinimumHeight(100)
        self.desc_input.setMaximumHeight(120)
        self.desc_input.setPlaceholderText("Descrição da conta (opcional)")
        form_layout.addWidget(self.desc_input)

        # Preço
        form_layout.addWidget(QLabel("Valor (R$):"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("R$ ")
        self.price_input.setMinimumHeight(35)
        form_layout.addWidget(self.price_input)

        # Campos específicos para contas
        self.installments_label = QLabel("Parcelas:")
        form_layout.addWidget(self.installments_label)

        self.installments_input = QSpinBox()
        self.installments_input.setMinimum(1)
        self.installments_input.setMaximum(99)
        self.installments_input.setValue(1)
        self.installments_input.setPrefix("x ")
        self.installments_input.setMinimumHeight(35)
        form_layout.addWidget(self.installments_input)

        self.day_label = QLabel("Dia do Pagamento:")
        form_layout.addWidget(self.day_label)

        self.day_input = QSpinBox()
        self.day_input.setMinimum(1)
        self.day_input.setMaximum(31)
        self.day_input.setValue(1)
        self.day_input.setMinimumHeight(35)
        form_layout.addWidget(self.day_input)

        # Link
        self.link_label = QLabel("Link:")
        form_layout.addWidget(self.link_label)
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("https://...")
        self.link_input.setMinimumHeight(35)
        form_layout.addWidget(self.link_input)

        # Imagem
        self.image_section_label = QLabel("Imagem (opcional):")
        form_layout.addWidget(self.image_section_label)

        image_layout = QHBoxLayout()
        self.image_label = QLabel("Nenhuma imagem")
        self.image_label.setFixedSize(120, 120)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px dashed #555; border-radius: 5px;")

        image_btn = QPushButton("Selecionar")
        image_btn.setMinimumHeight(35)
        image_btn.clicked.connect(self.select_image)

        image_layout.addWidget(self.image_label)
        image_layout.addWidget(image_btn, 1)
        form_layout.addLayout(image_layout)

        # Adicionar stretch no final
        form_layout.addStretch()

        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)

        # Botões fixos na parte inferior
        btn_container = QWidget()
        btn_container.setStyleSheet("background-color: #1a1a1a; padding: 10px;")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(20, 10, 20, 10)

        save_btn = QPushButton("Salvar")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.validate_and_accept)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        main_layout.addWidget(btn_container)

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


class EditProductDialog(AnimatedDialog):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Item")
        self.setModal(True)
        self.setFixedSize(450, 600)

        self.product = product
        self.image_path = None
        self.keep_current_image = True

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Layout principal do dialog
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll Area para os campos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: #1a1a1a; border: none; }")

        # Widget container para os campos
        form_widget = QWidget()
        form_widget.setStyleSheet("QWidget { background-color: #1a1a1a; }")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        # Tipo (Meta ou Conta)
        form_layout.addWidget(QLabel("Tipo:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Meta de Compra", "Conta do Mês"])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form_layout.addWidget(self.type_combo)

        # Nome
        form_layout.addWidget(QLabel("Nome:"))
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(35)
        form_layout.addWidget(self.name_input)

        # Descrição (apenas para contas)
        self.desc_label = QLabel("Descrição:")
        form_layout.addWidget(self.desc_label)
        self.desc_input = QTextEdit()
        self.desc_input.setMinimumHeight(100)
        self.desc_input.setMaximumHeight(120)
        self.desc_input.setPlaceholderText("Descrição da conta (opcional)")
        form_layout.addWidget(self.desc_input)

        # Preço
        form_layout.addWidget(QLabel("Valor (R$):"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("R$ ")
        self.price_input.setMinimumHeight(35)
        form_layout.addWidget(self.price_input)

        # Campos específicos para contas
        self.installments_label = QLabel("Parcelas:")
        form_layout.addWidget(self.installments_label)

        self.installments_input = QSpinBox()
        self.installments_input.setMinimum(1)
        self.installments_input.setMaximum(99)
        self.installments_input.setValue(1)
        self.installments_input.setPrefix("x ")
        self.installments_input.setMinimumHeight(35)
        form_layout.addWidget(self.installments_input)

        self.day_label = QLabel("Dia do Pagamento:")
        form_layout.addWidget(self.day_label)

        self.day_input = QSpinBox()
        self.day_input.setMinimum(1)
        self.day_input.setMaximum(31)
        self.day_input.setValue(1)
        self.day_input.setMinimumHeight(35)
        form_layout.addWidget(self.day_input)

        # Link
        self.link_label = QLabel("Link:")
        form_layout.addWidget(self.link_label)
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("https://...")
        self.link_input.setMinimumHeight(35)
        form_layout.addWidget(self.link_input)

        # Imagem
        self.image_section_label = QLabel("Imagem:")
        form_layout.addWidget(self.image_section_label)

        image_layout = QHBoxLayout()
        self.image_label = QLabel()
        self.image_label.setFixedSize(120, 120)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px dashed #555; border-radius: 5px;")

        image_btn = QPushButton("Alterar Imagem")
        image_btn.setMinimumHeight(35)
        image_btn.clicked.connect(self.select_image)

        image_layout.addWidget(self.image_label)
        image_layout.addWidget(image_btn, 1)
        form_layout.addLayout(image_layout)

        # Adicionar stretch no final
        form_layout.addStretch()

        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)

        # Botões fixos na parte inferior
        btn_container = QWidget()
        btn_container.setStyleSheet("background-color: #1a1a1a; padding: 10px;")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(20, 10, 20, 10)

        save_btn = QPushButton("Salvar")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.validate_and_accept)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        main_layout.addWidget(btn_container)

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

    
    def load_data(self):
        # Definir tipo
        item_type = self.product['type'] if 'type' in self.product.keys() else 'meta'
        self.type_combo.setCurrentIndex(1 if item_type == 'conta' else 0)

        self.name_input.setText(self.product['name'])
        self.price_input.setValue(self.product['price'])
        self.link_input.setText(self.product['link'] if 'link' in self.product.keys() and self.product['link'] else '')

        # Campos específicos de conta
        if item_type == 'conta':
            desc = self.product['description'] if 'description' in self.product.keys() and self.product['description'] else ''
            self.desc_input.setPlainText(desc)

            installments = self.product['installments'] if 'installments' in self.product.keys() and self.product['installments'] else 1
            self.installments_input.setValue(installments)

            day = self.product['installment_day'] if 'installment_day' in self.product.keys() and self.product['installment_day'] else 1
            self.day_input.setValue(day)

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


class EditSavedAmountDialog(AnimatedDialog):
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


class EditSalaryDialog(AnimatedDialog):
    def __init__(self, current_amount, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Salário")
        self.setModal(True)
        self.setFixedSize(300, 150)

        self.current_amount = current_amount
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Salário (R$):"))

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


class SettingsDialog(AnimatedDialog):
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
