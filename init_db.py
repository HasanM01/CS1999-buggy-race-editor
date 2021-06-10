import sqlite3

DATABASE_FILE = "database.db"

# important:
#-------------------------------------------------------------
# This script initialises your SQLite database for you, just
# to get you started... there are better ways to express the
# data you're going to need... especially outside SQLite.
# For example... maybe flag_pattern should be an ENUM (which
# is available in most other SQL databases), or a foreign key
# to a pattern table?
#
# Also... the name of the database (here, in SQLite, it's a
# filename) appears in more than one place in the project.
# That doesn't feel right, does it?
#-------------------------------------------------------------

connection = sqlite3.connect(DATABASE_FILE)
print("- Opened database successfully in file \"{}\"".format(DATABASE_FILE))

# using Python's triple-quote for multi-line strings:

connection.execute("""
  DROP TABLE IF EXISTS buggies
""")

connection.execute("""
  CREATE TABLE IF NOT EXISTS buggies (
    id                    INTEGER PRIMARY KEY,
    qty_wheels            INTEGER DEFAULT 4,
    power_type            VARCHAR(20) DEFAULT 'petrol',
    power_units           INTEGER DEFAULT 1,
    aux_power_type        VARCHAR(20) DEFAULT 'none',
    aux_power_units       INTEGER DEFAULT 0,
    hamster_booster       INTEGER DEFAULT 0,
    flag_color            VARCHAR(20) DEFAULT 'white',
    flag_pattern          VARCHAR(20) DEFAULT 'plain',
    flag_color_secondary  VARCHAR(20) DEFAULT 'black',
    tyres                 VARCHAR(20) DEFAULT 'knobbly',
    qty_tyres             INTEGER DEFAULT 4,
    armour                VARCHAR(20) DEFAULT 'none',
    attack                VARCHAR(20) DEFAULT 'none',
    qty_attack            INTEGER DEFAULT 0,
    fireproof             VARCHAR(5) DEFAULT 'false',
    insulated             VARCHAR(5) DEFAULT 'false',
    antibiotic            VARCHAR(5) DEFAULT 'false',
    banging               VARCHAR(5) DEFAULT 'false',
    algo                  VARCHAR(20) DEFAULT 'steady',
    total_cost            NUMBER DEFAULT 0.0,
    user_id               INTEGER DEFAULT 1
  )
""")

connection.execute("""
  DROP TABLE IF EXISTS users
""")

connection.execute("""
  CREATE TABLE IF NOT EXISTS users (
  id                    INTEGER PRIMARY KEY,
  username              VARCHAR(20) NOT NULL
  )
""")

print("- Table \"buggies\" exists OK")

cursor = connection.cursor()

cursor.execute("SELECT * FROM buggies LIMIT 1")
rows = cursor.fetchall()
if len(rows) == 0:
  cursor.execute("INSERT INTO buggies (qty_wheels) VALUES (4)")
  connection.commit()
  print("- Added one 4-wheeled buggy")
else:
  print("- Found a buggy in the database, nice")

cursor.execute("INSERT INTO users (id, username) VALUES (1, 'hasan')")
connection.commit()

print("- OK, your database is ready")

connection.close()
