import csv


class WriteToCSV:
    def __init__(self, fields):
        self.field_to_write = fields

    def write_to_csv(self, data, filename):
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.field_to_write)
            writer.writeheader()
            writer.writerows(data)

    def write_csv_header(self, filename):
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.field_to_write)
            writer.writeheader()

    def append_to_csv(self, data, filename):
        with open(filename, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.field_to_write)
            writer.writerows(data)


