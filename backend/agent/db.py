import os
import mysql.connector 
import config

def get_db_connection():
    print("HOST:", os.getenv("MYSQL_HOST"))
    print("USER:", os.getenv("MYSQL_USER"))
    print("DB:", os.getenv("MYSQL_DB"))
    print("PASS:", os.getenv("MYSQL_PASSWORD"))
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )

def save_sentiment_results(data, time_range):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sentiment_results WHERE time_range = %s",(time_range,)
    )

    insert_sql = """
        insert into sentiment_results
        (time_range, sentiment, asset, reasoning)
        values (%s,%s,%s,%s)
    """
    rows = [] 
    for item in data: 
        rows.append((
            time_range,
            item["sentiment"],
            item["asset"],
            item.get("reasoning",""),

        ))

    if rows:
        cursor.executemany(insert_sql,rows)

    conn.commit()
    cursor.close()
    conn.close()    

