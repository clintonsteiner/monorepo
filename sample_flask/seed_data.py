import os, time, numpy as np, polars as pl, psycopg
from datetime import datetime, timedelta

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/newsdb")

def seed():
    while True:
        try:
            with psycopg.connect(DB_URL, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute("CREATE TABLE IF NOT EXISTS raw_mentions (timestamp TIMESTAMP, network TEXT, topic TEXT)")
                    # SPEED BOOST: Indexing the timestamp and topic
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON raw_mentions (timestamp)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_topic_net ON raw_mentions (topic, network)")
                print("Database and Indexes ready.")
            break
        except:
            print("Waiting for Postgres...")
            time.sleep(2)

    # (Same data generation logic as before...)
    start = datetime(2022, 1, 1)
    networks, topics = ['CNN', 'FOXNEWS', 'MSNBC'], ['Ukraine', 'Russia']
    records = []
    for topic in topics:
        for net in networks:
            x = np.linspace(0, 100, 2160)
            spike = 20 * np.exp(-0.5 * ((x - 60) / 5)**2) + np.random.normal(2, 0.5, 2160)
            for i, count in enumerate(spike):
                if count <= 0: continue
                base_time = start + timedelta(hours=i)
                for _ in range(int(count)):
                    records.append((base_time + timedelta(seconds=np.random.randint(0, 3600)), net, topic))

    df = pl.DataFrame(records, schema=["timestamp", "network", "topic"])
    df.write_database("raw_mentions", DB_URL, if_table_exists="append", engine="adbc")
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
