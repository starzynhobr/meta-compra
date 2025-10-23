from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QIcon
import io


def format_brl(value):
    """Formata valor para padrão brasileiro R$ x.xxx,xx"""
    return f"R$ {value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


class ProductCard(QFrame):
    edit_clicked = pyqtSignal(int)
    remove_clicked = pyqtSignal(int)
    purchase_clicked = pyqtSignal(int)
    link_clicked = pyqtSignal(str)
    selection_changed = pyqtSignal(int, bool, float)  # id, is_selected, price

    def __init__(self, product, saved_amount, parent=None):
        super().__init__(parent)
        self.product = product
        self.saved_amount = saved_amount
        self.is_purchased = bool(product['purchased'])
        self.is_conta = product['type'] == 'conta' if 'type' in product.keys() else False
        self.is_selected = False

        self.setObjectName("productCard")
        # Cards de conta precisam ser um pouco mais altos por causa do badge e info de vencimento
        # Aumentado para acomodar botões em duas linhas e melhor espaçamento
        height = 325 if self.is_conta else 305
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
        layout.setContentsMargins(12, 12, 12, 10)
        layout.setSpacing(0)

        # Container para imagem com check sobreposto
        image_container = QFrame()
        image_container.setFixedSize(170, 140)

        # Imagem
        self.image_label = QLabel(image_container)
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

        # Check icon sobreposto (só visível se comprado)
        self.check_label = QLabel("✓", image_container)
        self.check_label.setObjectName("checkIcon")
        self.check_label.setFixedSize(28, 28)
        self.check_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.check_label.move(137, 5)  # Posiciona no canto superior direito
        self.check_label.setVisible(self.is_purchased)

        layout.addWidget(image_container)
        layout.addSpacing(12)  # Espaço entre imagem e badge/nome (aumentado)

        # Badge de tipo (para contas)
        if self.is_conta:
            type_badge = QLabel("CONTA")
            type_badge.setObjectName("typeBadge")
            type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            type_badge.setFixedHeight(20)
            layout.addWidget(type_badge)
            layout.addSpacing(6)

        # Nome
        name_label = QLabel(self.product['name'])
        name_label.setObjectName("productName")
        name_label.setWordWrap(True)
        name_label.setFixedHeight(36)  # Altura fixa para não invadir outros elementos
        name_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(name_label)
        layout.addSpacing(2)

        # Valor
        installments = self.product['installments'] if 'installments' in self.product.keys() else None
        if self.is_conta and installments and installments > 1:
            value_text = f"{format_brl(self.product['price'])} ({installments}x)"
        else:
            value_text = format_brl(self.product['price'])

        value_label = QLabel(value_text)
        value_label.setObjectName("productPrice")
        layout.addWidget(value_label)

        # Informação adicional para contas
        if self.is_conta:
            day = self.product['installment_day'] if 'installment_day' in self.product.keys() and self.product['installment_day'] else 1
            info_label = QLabel(f"Vencimento: dia {day}")
            info_label.setObjectName("billInfo")
            layout.addWidget(info_label)

        layout.addSpacing(4)  # Espaço antes da barra de progresso

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

        layout.addSpacing(6)  # Espaço antes dos botões
        
        # Botões organizados em duas linhas
        buttons_container = QVBoxLayout()
        buttons_container.setSpacing(5)

        # Linha 1: Botão de compra/link (somente se houver link)
        has_link = 'link' in self.product.keys() and self.product['link']

        if has_link:
            btn_link_layout = QHBoxLayout()
            btn_link_layout.setSpacing(5)

            if self.is_conta:
                # Para contas, mostrar botão de link
                self.buy_btn = QPushButton("Link")
                self.buy_btn.setObjectName("buyButton")
                self.buy_btn.setProperty("enabled", "true")
                self.buy_btn.clicked.connect(lambda: self.link_clicked.emit(self.product['link']))
            else:
                # Para metas, mostrar se pode comprar
                can_buy = self.saved_amount >= self.product['price']
                self.buy_btn = QPushButton("Comprar")
                self.buy_btn.setObjectName("buyButton")
                self.buy_btn.setProperty("enabled", "true" if can_buy else "false")
                self.buy_btn.clicked.connect(lambda: self.link_clicked.emit(self.product['link']))

            btn_link_layout.addWidget(self.buy_btn)
            buttons_container.addLayout(btn_link_layout)

        # Linha 2: Botões de ação
        action_layout = QHBoxLayout()
        action_layout.setSpacing(4)

        # Botão de seleção para somatório
        self.select_btn = QPushButton("☐")  # Checkbox vazio
        self.select_btn.setObjectName("selectButton")
        self.select_btn.setFixedSize(30, 30)
        self.select_btn.setCheckable(True)
        self.select_btn.clicked.connect(self.toggle_selection)

        # Botão de marcar como pago/comprado
        if self.is_conta:
            toggle_btn = QPushButton("✓")  # Check para contas
        else:
            toggle_btn = QPushButton("🛒")  # Carrinho para metas

        toggle_btn.setObjectName("iconButton")
        toggle_btn.setFixedSize(30, 30)
        toggle_btn.clicked.connect(lambda: self.purchase_clicked.emit(self.product['id']))

        edit_btn = QPushButton("✏")
        edit_btn.setObjectName("iconButton")
        edit_btn.setFixedSize(30, 30)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.product['id']))

        remove_btn = QPushButton("🗑")
        remove_btn.setObjectName("iconButton")
        remove_btn.setFixedSize(30, 30)
        remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.product['id']))

        action_layout.addWidget(self.select_btn)
        action_layout.addWidget(toggle_btn)
        action_layout.addWidget(edit_btn)
        action_layout.addWidget(remove_btn)
        action_layout.addStretch()

        buttons_container.addLayout(action_layout)
        layout.addLayout(buttons_container)
    
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

        # Atualizar botão de compra se ele existir
        has_link = 'link' in self.product.keys() and self.product['link']
        if has_link and hasattr(self, 'buy_btn'):
            can_buy = self.saved_amount >= self.product['price']
            self.buy_btn.setProperty("enabled", "true" if can_buy else "false")
            self.style().unpolish(self.buy_btn)
            self.style().polish(self.buy_btn)

    def toggle_selection(self):
        """Alterna o estado de seleção do card"""
        self.is_selected = not self.is_selected

        # Atualizar aparência do botão
        if self.is_selected:
            self.select_btn.setText("☑")  # Checkbox marcado
            self.select_btn.setProperty("selected", "true")
            self.setProperty("selected", "true")
        else:
            self.select_btn.setText("☐")  # Checkbox vazio
            self.select_btn.setProperty("selected", "false")
            self.setProperty("selected", "false")

        # Forçar atualização do estilo
        self.select_btn.style().unpolish(self.select_btn)
        self.select_btn.style().polish(self.select_btn)
        self.style().unpolish(self)
        self.style().polish(self)

        # Emitir sinal de mudança de seleção
        self.selection_changed.emit(self.product['id'], self.is_selected, self.product['price'])
