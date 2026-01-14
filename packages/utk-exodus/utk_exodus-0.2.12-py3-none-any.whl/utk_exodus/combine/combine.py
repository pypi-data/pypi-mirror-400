import csv


class ImportRefactor:
    """Remove old values from an import sheet."""

    def __init__(self, import_sheet, old_sheet):
        self.import_sheet = import_sheet
        self.old_sheet = old_sheet
        self.current_headers = self.__find_headers(import_sheet)
        self.old_headers = self.__find_headers(self.old_sheet)
        self.fields_to_nuke = list(set(self.old_headers) - set(self.current_headers))

    @staticmethod
    def __find_headers(sheet):
        with open(sheet, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            first = next(reader)
            return list(set(key for key in first.keys()))

    def create_csv_with_fields_to_nuke(self, sheet, new_sheet):
        data = []
        with open(sheet, "r", newline="") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                row.update((key, "") for key in self.fields_to_nuke)
                data.append(row)
        with open(new_sheet, "w", newline="") as outfile:
            fieldnames = reader.fieldnames + self.fields_to_nuke
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Read a csv and print the headers.")
    parser.add_argument(
        "-s", "--sheet", dest="sheet", help="Specify new csv.", required=True
    )
    parser.add_argument(
        "-o", "--old_sheet", dest="old_sheet", help="Specify old csv.", required=True
    )
    parser.add_argument(
        "-n", "--new_sheet", dest="new_sheet", help="Specify new csv.", required=True
    )
    args = parser.parse_args()
    ir = ImportRefactor(args.sheet, args.old_sheet)
    ir.create_csv_with_fields_to_nuke(args.sheet, args.new_sheet)
