import sqlite3


class Database:
    """数据库操作类（支持多用户）"""

    def __init__(self, table_name):
        self.conn = sqlite3.connect('user_info.db')
        self.table_name = table_name
        self.create_table()

    def create_table(self):
        """创建用户专属表"""
        cursor = self.conn.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                         (name TEXT, gender TEXT, nation TEXT, 
                          birth TEXT, address TEXT, id TEXT PRIMARY KEY, 
                          photo_path TEXT)''')
        self.conn.commit()

    def insert_user(self, user_data):
        """插入用户数据"""
        cursor = self.conn.cursor()
        cursor.execute(f'INSERT INTO {self.table_name} VALUES (?,?,?,?,?,?,?)', user_data)
        self.conn.commit()

    def get_all_users(self):
        """获取当前用户的所有数据"""
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT name, gender, nation, id FROM {self.table_name}')
        return cursor.fetchall()

    def search_user(self, id_number):
        """查询用户信息"""
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {self.table_name} WHERE id=?', (id_number,))
        return cursor.fetchone()

    def delete_user(self, id_number):
        """删除用户信息"""
        cursor = self.conn.cursor()
        cursor.execute(f'DELETE FROM {self.table_name} WHERE id=?', (id_number,))
        self.conn.commit()

