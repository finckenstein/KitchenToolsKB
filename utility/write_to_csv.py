import csv


def write_container_to_csv(data, filename):
    fields = ['Container', 'Foods', 'Top 5 Foods', 'Number of Foods Contained',
              'ConceptFoods', 'Top 5 ConceptFoods', 'Number of ConceptFoods Contained']

    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def write_verbs_to_describe_to_csv(tool_or_food, data, filename):
    fields = [tool_or_food, 'Verbs', 'Top 5 Verbs', 'Antonyms', 'Top 5 Antonyms']
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def write_utensil_verb_to_csv(data, filename):
    fields = ['Utensil', 'Verbs', 'Top 5 most Valid Verbs', 'Top 5 most Reliable Verbs',
              'Antonyms', 'Antonyms of Top 5 most Valid Verbs', 'Antonyms of Top 5 most Reliable Verbs']
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def write_utensil_foods_to_csv(data, filename):
    fields = ['Utensil', 'Foods', 'Top 5 most Valid Foods', 'Top 5 most Reliable Foods',
              'ConceptFoods', 'Top 5 most Valid ConceptFoods', 'Top 5 most Reliable ConceptFoods']
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


