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
    fields = [tool_or_food, 'Verbs', 'Top 3 Verbs', 'Antonyms']
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

