#!/usr/bin/env python3
import spacy
import sqlite3
import ast
import csv


def write_to_csv(fields, data, filename):
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    conn = sqlite3.connect('/home/leander/Desktop/automatic_KB_construction/recipes/old_recipes/recipes1.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Recipes;")
    rows = c.fetchall()
    nlp = spacy.load('en_core_web_trf')
    verbs = {}
    nouns = {}

    for recipe in rows:
        dictionary = ast.literal_eval(recipe[7])

        for key in dictionary:
            step = nlp(dictionary[key])
            sentences = list(step.sents)

            for sentence in sentences:
                for token in sentence:
                    word = token.lemma_.lower()

                    if token.pos_ == "VERB":
                        if word in verbs:
                            verbs[word] += 1
                        else:
                            verbs[word] = 1

                    elif token.pos_ == "NOUN":
                        if word in nouns:
                            nouns[word] += 1
                        else:
                            nouns[word] = 1

    sorted_verbs = dict(sorted(verbs.items(), key=lambda item: item[1], reverse=True))
    csv_verb = []
    for verb_k in sorted_verbs:
        csv_verb.append({'Verb': verb_k, 'Counter': sorted_verbs[verb_k]})

    sorted_nouns = dict(sorted(nouns.items(), key=lambda item: item[1], reverse=True))
    csv_noun = []
    for noun_k in sorted_nouns:
        csv_noun.append({'Noun': noun_k, 'Counter': sorted_nouns[noun_k]})

    write_to_csv(list(csv_verb[0].keys()), csv_verb, 'verbs_in_all_recipes.csv')
    write_to_csv(list(csv_noun[0].keys()), csv_noun, 'nouns_in_all_recipes.csv')



