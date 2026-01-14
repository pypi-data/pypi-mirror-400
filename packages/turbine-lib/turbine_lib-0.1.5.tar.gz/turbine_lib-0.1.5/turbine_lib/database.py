import sqlite3
import os

import yaml

from turbine_lib.binarydata import BinaryData
from turbine_lib.subfiledata import SubfileData


class Database:

    def __init__(self):
        self.db_ = None
        self.insert_request_ = None
        self.fetch_one_request_ = None
        self.get_rows_number_request_ = None
        
        self.create_table_command = """
            CREATE TABLE IF NOT EXISTS patch_data (
                fid INTEGER NOT NULL,
                binary_data BLOB,
                text_data TEXT,
                options TEXT NOT NULL
            );
        """
        
        self.insert_file_command = """
            INSERT INTO patch_data (fid,binary_data, text_data, options)
            VALUES (?,?, ?, ?);
        """
        
        self.fetch_one_command = "SELECT * FROM patch_data"
        self.clear_table_command = "DELETE FROM patch_data"
        self.get_rows_number_command = "SELECT Count(*) as count FROM patch_data"

    def close_database(self):
        if self.db_ is None:
            return True
            
        try:
            self.db_.commit()
            if self.insert_request_:
                self.insert_request_.close()
            if self.fetch_one_request_:
                self.fetch_one_request_.close()
            if self.get_rows_number_request_:
                self.get_rows_number_request_.close()
            self.db_.close()
            self.db_ = None
            return True
        except Exception as e:
            print(f"Database error when closing: {e}")
            return False

    def __del__(self):
        self.close_database()

    def init_database(self, filename):
        if not os.path.exists(os.path.dirname(filename) ):
            print(f"Cannot init database: file with name {filename} does not exist!")
            return False
            
        self.close_database()
        
        try:
            self.db_ = sqlite3.connect(filename)
            self.db_.execute("PRAGMA synchronous = OFF")
            self.db_.execute("PRAGMA count_changes = OFF")
            self.db_.execute("PRAGMA journal_mode = MEMORY")
            self.db_.execute("PRAGMA temp_store = MEMORY")
            self.db_.execute('PRAGMA encoding = "UTF-8"')
            
            self.db_.execute(self.create_table_command)
            self.db_.commit()
            
            return True
        except Exception as e:
            print(f"Error initializing database {filename}: {e}")
            if self.db_:
                self.db_.close()
            self.db_ = None
            return False

    def push_file(self, data):
        if self.db_ is None:
            print("Trying to push file to db, which hasn't been opened yet.")
            return False
            
        try:
            # options_str = str(data.options) if data.options else ""

            options_str = yaml.dump(data.options) if data.options else ""

            cursor = self.db_.cursor()
            cursor.execute(self.insert_file_command, 
                         (data.options["fid"],
                          bytes(data.binary_data),
                          data.text_data, 
                          options_str))
            self.db_.commit()
            return True
        except Exception as e:
            # 620872987
            print(f"SQLite3 error: {e}")
            return False

    def get_next_file(self):

        if self.db_ is None:
            print("Trying to get next file from db, which hasn't been opened yet.")
            return SubfileData()
            
        try:
            if self.fetch_one_request_ is None:
                self.fetch_one_request_ = self.db_.cursor()
                self.fetch_one_request_.execute(self.fetch_one_command)
                
            row = self.fetch_one_request_.fetchone()
            if row is None:
                return SubfileData()
                
            data = SubfileData()
            data.fid = row[0]
            data.binary_data = BinaryData(row[1])
            data.text_data = row[2] if row[2] else ""
            
            import yaml
            data.options = yaml.safe_load(row[3]) if row[3] else {}
            
            return data
        except Exception as e:
            print(f"SQLite3 fetch_one request error: {e}")
            return SubfileData()

    def count_rows(self):
        if self.db_ is None:
            print("Trying to execute sql query (Count rows) to db, which hasn't been opened yet.")
            return 0
            
        try:
            if self.get_rows_number_request_ is None:
                self.get_rows_number_request_ = self.db_.cursor()
                
            self.get_rows_number_request_.execute(self.get_rows_number_command)
            result = self.get_rows_number_request_.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error when counting rows: {e}")
            return 0