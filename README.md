# Meta de Compra

Programa minimalista para gerenciar metas de compra de produtos.

## Funcionalidades

- Adicionar produtos com nome, valor, link e imagem
- Acompanhar progresso de economia comparado ao valor dos produtos
- Marcar produtos como comprados
- Editar e remover produtos
- Salvar dados em banco SQLite
- Imagens armazenadas diretamente no banco (BLOB)
- Interface dark theme minimalista
- Responsivo e redimensionável

## Instalação

1. Instalar dependências:
```bash
pip install -r requirements.txt
```

2. Executar o programa:
```bash
python main.py
```

## Primeira Execução

Na primeira vez, o programa pedirá para você escolher onde salvar o banco de dados.
Você pode escolher uma pasta sincronizada com OneDrive/Google Drive.

## Estrutura

```
meta_compra/
├── main.py              # Ponto de entrada
├── config.py            # Gerenciamento de configurações
├── database.py          # Gerenciamento SQLite
├── styles.qss           # Estilos dark theme
├── ui/
│   ├── __init__.py
│   ├── main_window.py   # Janela principal
│   ├── card_widget.py   # Widget do card de produto
│   └── dialogs.py       # Diálogos (adicionar/editar/config)
└── requirements.txt
```

## Configurações

Clique no ícone de engrenagem (⚙) no canto superior direito para:
- Mostrar/ocultar itens comprados
- Alterar local do banco de dados

## Gerar Executável

Para gerar um executável standalone:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "MetaDeCompra" main.py
```

O executável será criado na pasta `dist/`.
