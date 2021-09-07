import csv


def write_container_to_csv(data, filename):
    fields = ['Container', 'Concepts in Kitchenware', 'Top 3 concepts', 'Number of Unique Concepts',
              'Foods in Kitchenware', 'Top 3 Foods', 'Number of Unique Foods', 'Total Number of Food and Concepts',
              'Raw Data Collected']

    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def write_verbs_to_describe_to_csv(tool_or_food, data, filename):
    fields = [tool_or_food, 'Verbs', 'Top 3 Verbs', 'Antonyms', 'Antonyms of Top 3']
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def write_utensil_verb_to_csv(data, filename):
    fields = ['Utensil', 'Accuracy', 'Counter', 'CV Container Matches Txt Container', 'Overlaps', 'Verbs', 'Top 3 Verbs',
              'Antonyms', 'Top 3 Antonym']
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def write_utensil_foods_to_csv(data, filename):
    fields = ['Utensil', 'Accuracy', 'Counter', 'CV Container Matches Txt Container', 'Overlaps', 'Foods', 'Top 3 Foods',
              'ConceptFoods', 'Top 3 Concept Foods']
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


