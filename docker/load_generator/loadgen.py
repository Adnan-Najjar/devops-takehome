#!/usr/bin/env python3

import os, time, random, threading, logging
import psycopg2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("loadgen")
user = os.environ["POSTGRES_USER"]
dbname = os.environ["POSTGRES_DB"]
password = os.environ["POSTGRES_PASSWORD"]

duration = int(os.getenv("DURATION", "120"))
concurrency = int(os.getenv("CONCURRENCY", "10"))

QUERIES = [
    "SELECT lt.name, COUNT(ls.set_num) FROM lego_themes lt JOIN lego_sets ls ON lt.id = ls.theme_id GROUP BY lt.name ORDER BY COUNT DESC LIMIT 10;",
    "SELECT * FROM lego_parts WHERE name ILIKE '%brick%' LIMIT 100;",
    "SELECT * FROM lego_inventory_parts ORDER BY random() LIMIT 50;",
    "SELECT * FROM lego_sets WHERE year BETWEEN 1990 AND 2010 AND num_parts > 200 ORDER BY num_parts DESC LIMIT 20;",
    "SELECT c.name, COUNT(ip.*) FROM lego_colors c JOIN lego_inventory_parts ip ON c.id = ip.color_id GROUP BY c.name ORDER BY COUNT DESC LIMIT 10;",
    "WITH RECURSIVE tree AS (SELECT id, name, parent_id FROM lego_themes WHERE parent_id IS NULL UNION ALL SELECT t.id, t.name, t.parent_id FROM lego_themes t JOIN tree ON t.parent_id = tree.id) SELECT * FROM tree LIMIT 50;",
    "SELECT p.name, pc.name AS category FROM lego_parts p JOIN lego_part_categories pc ON p.part_cat_id = pc.id WHERE pc.name LIKE '%Brick%' LIMIT 50;",
    "SELECT ls.name, ls.year, ls.num_parts FROM lego_sets ls WHERE ls.num_parts > (SELECT AVG(num_parts) FROM lego_sets) ORDER BY ls.num_parts DESC LIMIT 20;",
    "SELECT part_num, color_id, quantity, RANK() OVER (PARTITION BY inventory_id ORDER BY quantity DESC) FROM lego_inventory_parts LIMIT 200;",
    "SELECT t1.name AS theme, t2.name AS sub_theme FROM lego_themes t1 JOIN lego_themes t2 ON t1.id = t2.parent_id WHERE t1.name LIKE '%Technic%' LIMIT 20;",
    "INSERT INTO lego_colors (id, name, rgb, is_trans) VALUES (99999, 'test_color', '000000', 'f') ON CONFLICT DO NOTHING;",
    "DELETE FROM lego_colors WHERE id = 99999;",
    "UPDATE lego_sets SET num_parts = num_parts + 1 WHERE set_num = (SELECT set_num FROM lego_sets ORDER BY random() LIMIT 1);",
    "UPDATE lego_inventory_parts SET quantity = quantity + 1 WHERE inventory_id = (SELECT id FROM lego_inventories ORDER BY random() LIMIT 1) AND is_spare = false;",
    "UPDATE lego_sets SET num_parts = num_parts - 1 WHERE num_parts > 0 AND set_num = (SELECT set_num FROM lego_sets OFFSET floor(random() * (SELECT count(*) FROM lego_sets)) LIMIT 1);",
    "INSERT INTO lego_part_categories (id, name) VALUES (99999, 'test_category') ON CONFLICT DO NOTHING;",
]


def worker():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname=dbname, user=user, password=password, host="postgres"
    )
    cur = conn.cursor()
    deadline = time.time() + duration
    while time.time() < deadline:
        # Run a random query
        query = random.choice(QUERIES)
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            log.error("Query failed: %s", e)
            conn.rollback()

    # Close the cursor and connection
    cur.close()
    conn.close()


# Start threads for each query
log.info("Starting: %s workers, %ss", concurrency, duration)
threads = []
for i in range(concurrency):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

# Wait for all threads to finish
for t in threads:
    t.join()

log.info("Done")
