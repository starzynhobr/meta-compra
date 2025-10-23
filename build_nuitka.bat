@echo off
echo ========================================
echo  Compilando Meta de Compra com Nuitka
echo ========================================
echo.

REM Limpar builds anteriores
if exist "main.dist" rmdir /s /q "main.dist"
if exist "main.build" rmdir /s /q "main.build"

echo Iniciando compilacao (isso pode levar varios minutos)...
echo.

python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyqt6 ^
    --windows-icon-from-ico=icon.ico ^
    --windows-console-mode=disable ^
    --company-name="Meta de Compra" ^
    --product-name="Meta de Compra" ^
    --file-version=1.0.0.0 ^
    --product-version=1.0.0.0 ^
    --file-description="Aplicativo de Gerenciamento de Metas e Contas" ^
    --include-data-file=styles.qss=styles.qss ^
    --include-data-file=icon.ico=icon.ico ^
    --include-package=ui ^
    --include-module=database ^
    --include-module=config ^
    --assume-yes-for-downloads ^
    --output-filename=MetaDeCompra.exe ^
    --lto=yes ^
    --jobs=4 ^
    main.py

echo.
echo ========================================
echo  Compilacao concluida!
echo  Executavel: main.dist\MetaDeCompra.exe
echo ========================================
pause
