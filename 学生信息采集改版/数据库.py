import sqlite3

class Database:
    """数据库操作类，用于管理用户信息"""

    def __init__(self):
        # 连接SQLite数据库
        self.conn = sqlite3.connect('user_info.db')
        self.create_table()
    
    def create_table(self):
        """创建用户信息表"""
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                         (name TEXT, gender TEXT, nation TEXT, 
                          birth TEXT, address TEXT, id TEXT PRIMARY KEY, 
                          photo_path TEXT)''')
        self.conn.commit()

    def insert_user(self, user_data):
        """插入用户数据"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?)', user_data)
        self.conn.commit()

    def get_all_users(self):
        """获取所有用户简略信息"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT name, gender, id FROM users')
        return cursor.fetchall()

    def search_user(self, id_number):
        """根据身份证号查询用户信息"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id=?', (id_number,))
        return cursor.fetchone()

    def delete_user(self, id_number):
        """删除指定身份证号的用户信息"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM users WHERE id=?', (id_number,))
        self.conn.commit()