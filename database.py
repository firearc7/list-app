import sqlite3
import os

DATABASE_DIR = os.path.join(os.path.dirname(__file__), 'data')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'list_app.db')

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create lists table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create list_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS list_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        list_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        address TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (list_id) REFERENCES lists (id) ON DELETE CASCADE
    )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

# --- Lists CRUD ---
def create_list(title, note):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lists (title, note) VALUES (?, ?)", (title, note))
    list_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return list_id

def get_all_lists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, note FROM lists ORDER BY created_at DESC")
    lists = cursor.fetchall()
    conn.close()
    return lists

def search_lists(query):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, note FROM lists WHERE title LIKE ? OR note LIKE ? ORDER BY created_at DESC", 
                   ('%' + query + '%', '%' + query + '%'))
    lists = cursor.fetchall()
    conn.close()
    return lists

def get_list_by_id(list_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, note FROM lists WHERE id = ?", (list_id,))
    list_data = cursor.fetchone()
    conn.close()
    return list_data

def update_list_details(list_id, title, note):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE lists SET title = ?, note = ? WHERE id = ?", (title, note, list_id))
    conn.commit()
    conn.close()

def delete_list(list_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lists WHERE id = ?", (list_id,))
    conn.commit() # Cascade delete should handle list_items
    conn.close()

# --- List Items CRUD ---
def add_item_to_list(list_id, name, address, notes):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO list_items (list_id, name, address, notes) VALUES (?, ?, ?, ?)",
                   (list_id, name, address, notes))
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id

def get_items_for_list(list_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address, notes FROM list_items WHERE list_id = ? ORDER BY created_at ASC", (list_id,))
    items = cursor.fetchall()
    conn.close()
    return items

def get_list_item_by_id(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, list_id, name, address, notes FROM list_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return item

def update_list_item(item_id, name, address, notes):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE list_items SET name = ?, address = ?, notes = ? WHERE id = ?",
                   (name, address, notes, item_id))
    conn.commit()
    conn.close()

def delete_list_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM list_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

# Initialize the database and tables when this module is imported
init_db()
