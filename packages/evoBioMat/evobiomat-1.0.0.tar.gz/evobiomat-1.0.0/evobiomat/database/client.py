import pymysql
import threading
from queue import Queue, Empty
from ..errors.exceptions import DatabaseError, ConfigurationError

class SimpleConnectionPool:
    """
    A thread-safe, simple connection pool for PyMySQL.
    """
    def __init__(self, db_config: dict, pool_size: int = 5):
        self.db_config = db_config
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self.local = threading.local()
        
        # Validate config
        required_keys = ['host', 'user', 'password', 'database']
        if not all(k in db_config for k in required_keys):
            raise ConfigurationError(f"Missing database config keys. Required: {required_keys}")
            
        # Initialize pool
        try:
            for _ in range(pool_size):
                conn = self._create_connection()
                self.pool.put(conn)
        except Exception as e:
            raise DatabaseError(f"Failed to initialize connection pool: {e}")

    def _create_connection(self):
        return pymysql.connect(
            host=self.db_config['host'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],
            port=self.db_config.get('port', 3306),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False  # We manage transactions manually
        )

    def get_connection(self):
        try:
            return self.pool.get(timeout=2)
        except Empty:
            # If empty, create a temporary one or block? 
            # For this simple implementation, we'll try to create one if pool is empty/exhausted
            # but ideally we block. Let's strict block or fail.
            raise DatabaseError("Connection pool exhausted.")

    def return_connection(self, conn):
        try:
            # Ping to check if alive, if not reconnect
            conn.ping(reconnect=True)
            self.pool.put(conn)
        except Exception:
            # If broken, create new
            try:
                new_conn = self._create_connection()
                self.pool.put(new_conn)
            except Exception:
                pass # Should log this

    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()

class DatabaseClient:
    def __init__(self, db_config: dict):
        self.pool = SimpleConnectionPool(db_config)
        self.init_schema()

    def init_schema(self):
        conn = self.pool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                CREATE TABLE IF NOT EXISTS face_biometrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(255) UNIQUE NOT NULL,
                    face_encoding LONGBLOB NOT NULL,
                    encoding_version VARCHAR(32) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );
                """
                cursor.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Schema initialization failed: {e}")
        finally:
            self.pool.return_connection(conn)

    def store_biometric(self, user_id: str, encrypted_encoding: bytes, version: str) -> bool:
        conn = self.pool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO face_biometrics (user_id, face_encoding, encoding_version)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    face_encoding = VALUES(face_encoding),
                    encoding_version = VALUES(encoding_version)
                """
                cursor.execute(sql, (user_id, encrypted_encoding, version))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Failed to store biometric for {user_id}: {e}")
        finally:
            self.pool.return_connection(conn)

    def fetch_all_encodings(self):
        """
        Returns a list of dicts: [{'user_id': str, 'face_encoding': bytes, 'encoding_version': str}]
        """
        conn = self.pool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT user_id, face_encoding, encoding_version FROM face_biometrics"
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            raise DatabaseError(f"Failed to fetch encodings: {e}")
        finally:
            self.pool.return_connection(conn)
            
    def get_encoding_by_user_id(self, user_id: str):
        conn = self.pool.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT user_id, face_encoding, encoding_version FROM face_biometrics WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                return cursor.fetchone()
        except Exception as e:
            raise DatabaseError(f"Failed to fetch user {user_id}: {e}")
        finally:
            self.pool.return_connection(conn)
