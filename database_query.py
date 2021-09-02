#!/usr/bin/env python3
import sqlite3
import utility.paths as pt


def sql_fetch_1to1_videos(url):
    recipe_conn = sqlite3.connect(pt.recipes_with_1to1_video)
    recipe_cursor = recipe_conn.cursor()
    if url == "all":
        recipe_cursor.execute("SELECT * FROM RecipesWith1To1Video;")
    else:
        recipe_cursor.execute("SELECT * FROM RecipesWith1To1Video WHERE URL = '" + url + "';")
    return recipe_cursor.fetchall()


def sql_fetch_recipe_db(url):
    recipe_connection = sqlite3.connect(pt.all_recipes)
    recipe_cursor = recipe_connection.cursor()
    if url == "all":
        recipe_cursor.execute("SELECT * FROM Recipes;")
    else:
        recipe_cursor.execute("SELECT * FROM Recipes WHERE URL = " + url + ";")
    return recipe_cursor.fetchall()


def sql_fetch_kitchenware_db():
    utils_connection = sqlite3.connect(pt.kitchenware)
    utils_cursor = utils_connection.cursor()
    utils_cursor.execute("SELECT * FROM Kitchenware;")
    return utils_cursor.fetchall()


class RecipeI:
    URL = 0
    TITLE = 1
    RATING = 2
    SERVING = 3
    TIME = 4
    CATEGORY = 5
    INGREDIENTS = 6
    PREPARATION = 7
    NUTRITION = 8


class RecipeWithVideoI:
    URL = 0
    TITLE = 1
    RATING = 2
    SERVING = 3
    TIME = 4
    CATEGORY = 5
    INGREDIENTS = 6
    PREPARATION = 7
    NUTRITION = 8
    VIDEO_ID = 9


class KitchenwareI:
    VERB = 0
    KITCHENWARE = 1
    DEFAULT = 2
