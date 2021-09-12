#!/usr/bin/env python3
import spacy
from nltk.corpus import wordnet
nlp = spacy.load("en_core_web_trf")


def get_top_5(sorted_v):
    assert sorted_v == dict(sorted(sorted_v.items(), key=lambda item: item[1], reverse=True))
    maxi = max(sorted_v.values())
    counter = 0
    print(maxi)

    top_5_dict = {}
    for elem in sorted_v:
        print(counter)
        if maxi != sorted_v[elem]:
            counter += 1
            maxi = sorted_v[elem]
        if counter == 5:
            break
        else:
            top_5_dict[elem] = sorted_v[elem]
    return top_5_dict


def get_antonyms_from_dic(verbs_dic, has_counter):
    antonyms_of_tool = {}
    for verb_key in verbs_dic:
        if has_counter:
            counter = verbs_dic[verb_key]['Counter']
        else:
            counter = verbs_dic[verb_key]
        # print(verb_key, verbs_dic[verb_key])
        if verb_key is not None:
            for syn in wordnet.synsets(verb_key):
                for l in syn.lemmas():
                    if l.antonyms():
                        antonym = l.antonyms()[0].name()
                        if antonym in antonyms_of_tool:
                            antonyms_of_tool[antonym]['Original Verb'].append(verb_key)
                            antonyms_of_tool[antonym]['Verb Counter'] += counter
                        else:
                            antonyms_of_tool[antonym] = {'Original Verb': [verb_key],
                                                         'Verb Counter': counter}
    return antonyms_of_tool


if __name__ == "__main__":
    # string = "Where is it I need to be? Note: Use ½ cup (65) for scooping the batter to yield 4 thicker pancakes; Use ⅓ cup (40 g) to yield 6 smaller pancakes. Add the onions and saute onions until translucent."
    # step = nlp(string)
    # sentences = list(step.sents)
    #
    # for sentence in sentences:
    #     for token in sentence:
    #         print(token.text, token.pos_, token.dep_)
    dic = {'flip': 10, 'add': 20, 'turn': 15, 'cook': 12, 'simmer': 19, 'bake': 1, 'toast': 11, 'help': 1, 'firm': 1, 'collapse': 100}
    sorted_dict = dict(sorted(dic.items(), key=lambda item: item[1], reverse=True))
    print("\n\n", sorted_dict, "\n\n")

    top_5 = get_top_5(sorted_dict)
    print(top_5)

    print("\n\n", get_antonyms_from_dic(dic, False))
    print("\n\n", get_antonyms_from_dic(top_5, False))





