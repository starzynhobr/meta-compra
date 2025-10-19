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
        
        # Tabela de produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                link TEXT,
                image BLOB,
                purchased INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de configurações (valor guardado)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                saved_amount REAL DEFAULT 0
            )
        ''')
        
        # Inserir valor inicial se não existir
        cursor.execute('SELECT COUNT(*) FROM settings')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO settings (id, saved_amount) VALUES (1, 0)')
        
        conn.commit()
        conn.close()
    
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
    
    def add_product(self, name, price, link, image_path):
        conn = self.connect()
        cursor = conn.cursor()
        
        image_blob = self.process_image(image_path) if image_path else None
        
        cursor.execute('''
            INSERT INTO products (name, price, link, image)
            VALUES (?, ?, ?, ?)
        ''', (name, price, link, image_blob))
        
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    def update_product(self, product_id, name, price, link, image_path=None):
        conn = self.connect()
        cursor = conn.cursor()
        
        if image_path:
            image_blob = self.process_image(image_path)
            cursor.execute('''
                UPDATE products 
                SET name=?, price=?, link=?, image=?
                WHERE id=?
            ''', (name, price, link, image_blob, product_id))
        else:
            cursor.execute('''
                UPDATE products 
                SET name=?, price=?, link=?
                WHERE id=?
            ''', (name, price, link, product_id))
        
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
