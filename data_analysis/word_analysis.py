#!/usr/bin/env python3
import sqlite3

if __name__ == "__main__":
    conn = sqlite3.connect('/home/leander/Desktop/automatic_KB_construction/recipes/old_recipes/recipes1.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Recipes;")
    rows = c.fetchall()
    i = 0
    for row in rows:
        if "bring to a boil" in row[7]:
            print(row[7])
            i += 1
    print(i)
