import psycopg2
import logging
logger = logging.getLogger()

INSERT_NEW_USER = """
                    INSERT INTO user_info(user_id, user_name, balance, referral_number)
                    VALUES(%s, %s, %s, %s)
                  """

UPDATE_BALANCE = """UPDATE user_info
                SET balance = balance + 10, referral_number = referral_number + 1
                WHERE user_name = %s"""

class DataSource:
    def __init__(self, database_url):
        self.database_url = database_url

    def get_connection(self):
        return psycopg2.connect(self.database_url, sslmode='allow')

    @staticmethod
    def close_connection(conn):
        if conn is not None:
            conn.close()

    def create_tables(self):
        commands = (
            """
                CREATE TABLE IF NOT EXISTS user_info (
                    user_id BIGINT PRIMARY KEY,
                    user_name VARCHAR(32) NOT NULL,
                    balance SMALLINT,
                    referral_number SMALLINT
                )
            """,)
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            for command in commands:
                cur.execute(command)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)

    def check_valid_param(self, user_name, param):
        conn = None
        try:
            if user_name == param:
                return False
            else:
                conn = self.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT user_name FROM user_info WHERE user_name = %s", [param])
                doc = cur.fetchone()
                cur.close()
                conn.commit()
                return bool(doc)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)

    def add_new_user(self, user_id, user_name, balance, referral_number):
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_name FROM user_info WHERE user_name = %s", [user_name])
            doc = cur.fetchone()
            if doc == None:
                cur.execute(INSERT_NEW_USER, [user_id, user_name, balance, referral_number])
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)

    def update_balance(self, user_name):
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(UPDATE_BALANCE, (user_name,))
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)
    
    def get_balance(self, user_name):
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT balance, referral_number FROM user_info WHERE user_name = %s", [user_name])
            result = cur.fetchone()
            cur.close()
            conn.commit()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)

    def get_ranking(self):
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_name, balance FROM user_info ORDER BY balance DESC LIMIT 10")
            result = cur.fetchall()
            cur.close()
            conn.commit()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)
