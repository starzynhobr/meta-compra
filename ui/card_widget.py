from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QIcon
import io

class ProductCard(QFrame):
    edit_clicked = pyqtSignal(int)
    remove_clicked = pyqtSignal(int)
    purchase_clicked = pyqtSignal(int)
    link_clicked = pyqtSignal(str)
    
    def __init__(self, product, saved_amount, parent=None):
        super().__init__(parent)
        self.product = product
        self.saved_amount = saved_amount
        self.is_purchased = bool(product['purchased'])
        self.is_conta = product['type'] == 'conta' if 'type' in product.keys() else False

        self.setObjectName("productCard")
        # Cards de conta precisam ser um pouco mais altos por causa do badge e info de vencimento
        height = 310 if self.is_conta else 290
        self.setFixedSize(200, height)

        self.setup_ui()
        self.setup_animations()

        if self.is_purchased:
            self.setProperty("purchased", "true")
            self.style().unpolish(self)
            self.style().polish(self)

        if self.is_conta:
            self.setProperty("cardType", "conta")
            self.style().unpolish(self)
            self.style().polish(self)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Container para imagem com check
        image_container = QFrame()
        image_container.setFixedSize(170, 140)
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)

        # Imagem
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(170, 140)
        self.image_label.setScaledContents(False)

        if self.product['image']:
            pixmap = QPixmap()
            pixmap.loadFromData(self.product['image'])
            scaled_pixmap = pixmap.scaled(170, 140, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Sem Imagem")
            self.image_label.setObjectName("noImage")
        
        image_layout.addWidget(self.image_label)
        
        # Check icon (só visível se comprado)
        self.check_label = QLabel("✓")
        self.check_label.setObjectName("checkIcon")
        self.check_label.setFixedSize(30, 30)
        self.check_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.check_label.setVisible(self.is_purchased)
        image_layout.addWidget(self.check_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(image_container)
        
        # Badge de tipo (para contas)
        if self.is_conta:
            type_badge = QLabel("CONTA")
            type_badge.setObjectName("typeBadge")
            type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            type_badge.setFixedHeight(20)
            layout.addWidget(type_badge)

        # Nome
        name_label = QLabel(self.product['name'])
        name_label.setObjectName("productName")
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(40)
        layout.addWidget(name_label)

        # Valor
        installments = self.product['installments'] if 'installments' in self.product.keys() else None
        if self.is_conta and installments and installments > 1:
            value_text = f"R$ {self.product['price']:,.2f} ({installments}x)"
        else:
            value_text = f"R$ {self.product['price']:,.2f}"

        value_label = QLabel(value_text)
        value_label.setObjectName("productPrice")
        layout.addWidget(value_label)

        # Informação adicional para contas
        if self.is_conta:
            day = self.product['installment_day'] if 'installment_day' in self.product.keys() and self.product['installment_day'] else 1
            info_label = QLabel(f"Vencimento: dia {day}")
            info_label.setObjectName("billInfo")
            layout.addWidget(info_label)

        # Barra de progresso (apenas para metas)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)

        if not self.is_conta:
            percentage = min(100, int((self.saved_amount / self.product['price']) * 100)) if self.product['price'] > 0 else 0
            self.progress.setValue(percentage)

            if self.is_purchased:
                self.progress.setVisible(False)

            layout.addWidget(self.progress)
        else:
            self.progress.setVisible(False)
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        
        # Botão de compra/link
        if self.is_conta:
            # Para contas, apenas abrir link se houver
            has_link = 'link' in self.product.keys() and self.product['link']
            self.buy_btn = QPushButton("Link")
            self.buy_btn.setObjectName("buyButton")
            self.buy_btn.setProperty("enabled", "true" if has_link else "false")
            self.buy_btn.clicked.connect(lambda: self.link_clicked.emit(self.product['link']))
        else:
            # Para metas, mostrar se pode comprar
            can_buy = self.saved_amount >= self.product['price']
            self.buy_btn = QPushButton("Comprar")
            self.buy_btn.setObjectName("buyButton")
            self.buy_btn.setProperty("enabled", "true" if can_buy else "false")
            self.buy_btn.clicked.connect(lambda: self.link_clicked.emit(self.product['link']))

        btn_layout.addWidget(self.buy_btn)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        action_layout.setSpacing(5)

        # Botão de marcar como pago/comprado
        if self.is_conta:
            toggle_btn = QPushButton("✓")  # Check para contas
        else:
            toggle_btn = QPushButton("🛒")  # Carrinho para metas

        toggle_btn.setObjectName("iconButton")
        toggle_btn.setFixedSize(35, 35)
        toggle_btn.clicked.connect(lambda: self.purchase_clicked.emit(self.product['id']))

        edit_btn = QPushButton("✏")
        edit_btn.setObjectName("iconButton")
        edit_btn.setFixedSize(35, 35)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.product['id']))

        remove_btn = QPushButton("🗑")
        remove_btn.setObjectName("iconButton")
        remove_btn.setFixedSize(35, 35)
        remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.product['id']))

        action_layout.addWidget(toggle_btn)
        action_layout.addWidget(edit_btn)
        action_layout.addWidget(remove_btn)
        
        btn_layout.addLayout(action_layout)
        layout.addLayout(btn_layout)
    
    def setup_animations(self):
        # Criar efeito de opacidade
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Animação fade in
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Iniciar animação
        self.fade_in.start()
        
    def update_saved_amount(self, new_amount):
        self.saved_amount = new_amount
        percentage = min(100, int((self.saved_amount / self.product['price']) * 100)) if self.product['price'] > 0 else 0
        self.progress.setValue(percentage)
        
        can_buy = self.saved_amount >= self.product['price']
        self.buy_btn.setProperty("enabled", "true" if can_buy else "false")
        self.style().unpolish(self.buy_btn)
        self.style().polish(self.buy_btn)
