import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtGui import QDesktopServices, QIcon
from PyQt6.QtCore import Qt
from config import Config
from database import Database
from ui.main_window import MainWindow


def select_db_location():
    """Permite usuário selecionar onde salvar o banco de dados"""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Primeiro Acesso")
    msg.setText("Bem-vindo ao Meta de Compra!\n\n"
                "Selecione onde deseja salvar seus dados.")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()
    
    file_path, _ = QFileDialog.getSaveFileName(
        None, "Selecionar Local do Banco de Dados",
        str(Path.home() / "meta_compra.db"),
        "Banco de Dados (*.db)"
    )
    
    if file_path:
        if not file_path.endswith('.db'):
            file_path += '.db'
        return file_path
    
    return None


def main():
    app = QApplication(sys.argv)
    
    # Configurar aparência
    app.setStyle('Fusion')
    
    # Carregar configurações
    config = Config()
    
    # Verificar se é a primeira vez
    db_path = config.get_db_path()
    
    if not db_path:
        # Criar automaticamente em LocalAppData
        if sys.platform == 'win32':
            app_data = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
        else:
            app_data = Path.home() / '.local' / 'share'
        
        meta_folder = app_data / 'MetaDeCompra'
        meta_folder.mkdir(parents=True, exist_ok=True)
        db_path = str(meta_folder / 'meta_compra.db')
        
        config.set_db_path(db_path)
    
    # Verificar se o arquivo existe, criar se necessário
    db_file = Path(db_path)
    if not db_file.parent.exists():
        db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Inicializar banco de dados
    try:
        db = Database(db_path)
    except Exception as e:
        QMessageBox.critical(None, "Erro", 
                           f"Erro ao abrir banco de dados:\n{str(e)}")
        sys.exit(1)
    
    # Carregar estilos
    if getattr(sys, 'frozen', False):
        # Rodando como .exe
        base_path = Path(sys._MEIPASS)
    else:
        # Rodando como script
        base_path = Path(__file__).parent
    
    style_file = base_path / "styles.qss"
    if style_file.exists():
        with open(style_file, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())

    # ADICIONAR ESTAS LINHAS
    icon_file = base_path / "icon.ico"
    if icon_file.exists():
        app.setWindowIcon(QIcon(str(icon_file)))
    
    # Criar e exibir janela principal
    window = MainWindow(db, config)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
