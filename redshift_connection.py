import psycopg2
DB_NAME = ''
HOST = ''
POST = ''
USER = '' 
PASSWORD = ''
SCHEMA_NAME = 'public'

class ScrapyConnectToRedshift():
    def __init__(self, db_name=DB_NAME, schema_name=SCHEMA_NAME):
        # connection and session creation
        try:
            self.conn = psycopg2.connect(dbname=DB_NAME,
                                         host=HOST,
                                         port=POST,
                                         user=USER,
                                         password=PASSWORD)

            self.cursor = self.conn.cursor()
            self.schema_name = schema_name
        except Exception as err:
            self.schema_name = schema_name
            # raise Exception(str(err))

    def query(self, sql, need_commit=False):
        """
        Query Redshift, Please be noted, Redshift should only be accessible from celery for now, this function didn't
        filter input parameter, may have sql injection prob.
        :param sql: sql query
        :return: return as matrix tuple

        To use return, can write nested "for" loop, example:
        for row in instance.query:
            for elem in row:
                print elem
        """
        self.cursor.execute(sql)
        if need_commit:
            self.conn.commit()
        else:
            return self.cursor.fetchall()

    def bulk_insert(self, table_name, column_list, data_frame):
        try:
            sql = 'insert into "%s".%s (%s) values ' % (self.schema_name, table_name, ','.join(column_list))
            for data in data_frame:
                this_sql_line = '('
                for elem in column_list: # str(data[elem]) + ','
                    if isinstance(data[elem], str):
                        this_sql_line += "'%s'," % data[elem].replace("'", '')
                    else: # datetime 
                        this_sql_line += "'%s'," % data[elem]
                this_sql_line = this_sql_line[:-1] + '),'
                sql += this_sql_line
            sql = sql[:-1]
            print('------------------------- SQL -------------------------------')
            print(sql)
            # send_slack_notification(message=sql, channel=SLACK_CHANNEL_DEBUG)
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as err:
            print('-'*20 +'Opp! Some error has happend !!'+'-'*20)
            # send_slack_notification('[Redshift insert Error: %s], sql: %s' % (err, sql), channel=SLACK_CHANNEL_DEBUG)

    def __del__(self):
        self.cursor.close()
        self.conn.close()
