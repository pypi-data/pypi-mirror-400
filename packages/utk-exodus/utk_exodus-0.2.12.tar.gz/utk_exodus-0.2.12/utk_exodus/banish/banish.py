from csv import DictReader, DictWriter

class BanishFiles:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.csv_contents = self.__read_csv()

    def __read_csv(self):
        with open(self.csv_file, "r") as file:
            reader = DictReader(file)
            return [
                row for row in reader if "MODS" not in row.get("source_identifier") and "POLICY" not in row.get("source_identifier")
            ]

    def write(self, output_file):
        with open(output_file, "w") as file:
            writer = DictWriter(file, fieldnames=self.csv_contents[0].keys())
            writer.writeheader()
            writer.writerows(self.csv_contents)

