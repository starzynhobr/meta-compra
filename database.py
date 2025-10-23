import sqlite3
from datetime import datetime
from PIL import Image
import io

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.create_tables()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        # Tabela de produtos (metas e contas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT DEFAULT 'meta',
                name TEXT NOT NULL,
                price REAL NOT NULL,
                link TEXT,
                image BLOB,
                description TEXT,
                installments INTEGER,
                installment_day INTEGER,
                purchased INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de configurações (valor guardado e salário)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                saved_amount REAL DEFAULT 0,
                salary REAL DEFAULT 0
            )
        ''')
        
        # Inserir valor inicial se não existir
        cursor.execute('SELECT COUNT(*) FROM settings')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO settings (id, saved_amount) VALUES (1, 0)')

        # Migração: adicionar novas colunas se não existirem
        self.migrate_database(cursor)

        conn.commit()
        conn.close()

    def migrate_database(self, cursor):
        """Adiciona novas colunas ao banco de dados existente"""
        # Verificar quais colunas existem em products
        cursor.execute('PRAGMA table_info(products)')
        columns = [column[1] for column in cursor.fetchall()]

        # Adicionar colunas se não existirem
        if 'type' not in columns:
            cursor.execute('ALTER TABLE products ADD COLUMN type TEXT DEFAULT "meta"')

        if 'description' not in columns:
            cursor.execute('ALTER TABLE products ADD COLUMN description TEXT')

        if 'installments' not in columns:
            cursor.execute('ALTER TABLE products ADD COLUMN installments INTEGER')

        if 'installment_day' not in columns:
            cursor.execute('ALTER TABLE products ADD COLUMN installment_day INTEGER')

        # Verificar colunas em settings
        cursor.execute('PRAGMA table_info(settings)')
        settings_columns = [column[1] for column in cursor.fetchall()]

        if 'salary' not in settings_columns:
            cursor.execute('ALTER TABLE settings ADD COLUMN salary REAL DEFAULT 0')
    
    def process_image(self, image_path):
        """Redimensiona e converte imagem para BLOB"""
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            
            # Redimensionar mantendo aspecto
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Converter para bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            return img_bytes.getvalue()
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")
            return None
    
    def add_product(self, name, price, link, image_path, item_type='meta',
                    description=None, installments=None, installment_day=None):
        conn = self.connect()
        cursor = conn.cursor()

        image_blob = self.process_image(image_path) if image_path else None

        cursor.execute('''
            INSERT INTO products (type, name, price, link, image, description,
                                installments, installment_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item_type, name, price, link, image_blob, description,
              installments, installment_day))

        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    def update_product(self, product_id, name, price, link, image_path=None,
                      item_type='meta', description=None, installments=None,
                      installment_day=None):
        conn = self.connect()
        cursor = conn.cursor()

        if image_path:
            image_blob = self.process_image(image_path)
            cursor.execute('''
                UPDATE products
                SET type=?, name=?, price=?, link=?, image=?, description=?,
                    installments=?, installment_day=?
                WHERE id=?
            ''', (item_type, name, price, link, image_blob, description,
                  installments, installment_day, product_id))
        else:
            cursor.execute('''
                UPDATE products
                SET type=?, name=?, price=?, link=?, description=?,
                    installments=?, installment_day=?
                WHERE id=?
            ''', (item_type, name, price, link, description,
                  installments, installment_day, product_id))

        conn.commit()
        conn.close()
    
    def delete_product(self, product_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
        conn.commit()
        conn.close()
    
    def toggle_purchased(self, product_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT purchased FROM products WHERE id=?', (product_id,))
        current = cursor.fetchone()[0]
        new_value = 0 if current == 1 else 1
        cursor.execute('UPDATE products SET purchased=? WHERE id=?', (new_value, product_id))
        conn.commit()
        conn.close()
        return new_value
    
    def get_all_products(self, show_purchased=True):
        conn = self.connect()
        cursor = conn.cursor()
        
        if show_purchased:
            cursor.execute('SELECT * FROM products ORDER BY purchased ASC, created_at DESC')
        else:
            cursor.execute('SELECT * FROM products WHERE purchased=0 ORDER BY created_at DESC')
        
        products = cursor.fetchall()
        conn.close()
        return products
    
    def get_saved_amount(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT saved_amount FROM settings WHERE id=1')
        amount = cursor.fetchone()[0]
        conn.close()
        return amount
    
    def update_saved_amount(self, amount):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('UPDATE settings SET saved_amount=? WHERE id=1', (amount,))
        conn.commit()
        conn.close()

    def get_salary(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT salary FROM settings WHERE id=1')
        result = cursor.fetchone()
        salary = result[0] if result and result[0] else 0
        conn.close()
        return salary

    def update_salary(self, salary):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('UPDATE settings SET salary=? WHERE id=1', (salary,))
        conn.commit()
        conn.close()

    def get_monthly_bills_total(self):
        """Retorna o total de contas do mês (soma das parcelas mensais)"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price FROM products
            WHERE type='conta' AND purchased=0
        ''')
        bills = cursor.fetchall()
        conn.close()

        # O price já é o valor da parcela mensal
        # Se tiver 36x de R$ 631, o price é R$ 631 (valor mensal)
        total = sum(bill[0] for bill in bills)

        return total

    def get_products_by_type(self, item_type, show_purchased=True):
        """Retorna produtos filtrados por tipo"""
        conn = self.connect()
        cursor = conn.cursor()

        if show_purchased:
            cursor.execute('''
                SELECT * FROM products
                WHERE type=?
                ORDER BY purchased ASC, created_at DESC
            ''', (item_type,))
        else:
            cursor.execute('''
                SELECT * FROM products
                WHERE type=? AND purchased=0
                ORDER BY created_at DESC
            ''', (item_type,))

        products = cursor.fetchall()
        conn.close()
        return products

    def get_monthly_forecast(self):
        """Retorna previsão de parcelas para os próximos meses"""
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, installments, installment_day FROM products
            WHERE type='conta' AND purchased=0
        ''')
        bills = cursor.fetchall()
        conn.close()

        if not bills:
            return []

        # Calcular parcelas por mês
        current_date = datetime.now()
        monthly_totals = {}

        for bill in bills:
            price = bill[0]  # price já é o valor da parcela mensal
            installments = bill[1] if bill[1] else 1

            # Adicionar parcela para cada mês
            for i in range(installments):
                month_date = current_date + relativedelta(months=i)
                month_key = month_date.strftime("%Y-%m")
                month_name = month_date.strftime("%b/%Y")

                if month_key not in monthly_totals:
                    monthly_totals[month_key] = {'name': month_name, 'total': 0}

                monthly_totals[month_key]['total'] += price

        # Ordenar por data e converter para lista
        sorted_months = sorted(monthly_totals.items())
        forecast = [{'month': v['name'], 'total': v['total']} for k, v in sorted_months]

        # Adicionar um mês a mais com R$ 0,00
        if forecast:
            last_month_date = current_date + relativedelta(months=len(sorted_months))
            forecast.append({
                'month': last_month_date.strftime("%b/%Y"),
                'total': 0
            })

        return forecast
