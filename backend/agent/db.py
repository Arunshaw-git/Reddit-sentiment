import os
import mysql.connector 
import config

def get_db_connection():
    is_prod = os.getenv("NODE_ENV") == "production"

    print("HOST:", os.getenv("MYSQL_HOST"))
    print("PORT:", os.getenv("MYSQL_PORT"))
    print("USER:", os.getenv("MYSQL_USER"))
    print("DB:", os.getenv("MYSQL_DATABASE"))
    print("PROD:", is_prod)
    
    config = {
        "host": os.getenv("MYSQL_HOST"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
    }

    if is_prod:
        config.update({
            "ssl_disabled": False,
            "ssl_verify_cert": False,
        })

    return mysql.connector.connect(**config)

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

