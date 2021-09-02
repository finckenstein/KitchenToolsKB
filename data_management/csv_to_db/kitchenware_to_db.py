#!/usr/bin/env python3
import sqlite3
import pandas as pd


class KitchenwareToDB:
    def __init__(self):
        conn = sqlite3.connect('/home/leander/Desktop/automatic_KB_construction/contains_edge/kitchenware.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS Kitchenware ("
                  "Verb text Unique Primary Key, "
                  "Kitchenware text, "
                  "Default_Kitchenware text);")
        conn.commit()

        r_recipes = pd.read_csv('/home/leander/Desktop/automatic_KB_construction/contains_edge/kitchenware.csv')
        r_recipes.to_sql('Kitchenware', conn, if_exists='replace', index=False)
