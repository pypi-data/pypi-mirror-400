import csv
# personal note, this is still being used right? I still need to exodus fix_stuff for these last few collections that need to be uploaded

class FixMetadata:
    def __init__(self, titles, remove_columns=False):
        self.titles = titles
        self.remove_columns = remove_columns

    def update_metadata(self, csv_filename):
        keywords = self.titles
        remove_columns = self.remove_columns
        keywords_list = [keyword.lower() for keyword in keywords.split(',')]
        with open(csv_filename, mode='r', newline='') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)

        attachment_rows = [row for row in rows if row['model'].lower() == 'attachment']
        fileset_rows = [row for row in rows if row['model'].lower() == 'fileset']

        if len(attachment_rows) + len(fileset_rows) != len(rows):
            print("works found in sheet, will not be written to outfile")
            # sys.exit(1)

        attachment_rows.sort(key=lambda row: ('obj' in row['title'].lower() or 'preserve' in row['title'].lower(), row['title'].lower()))
        fileset_rows.sort(key=lambda row: ('obj' in row['title'].lower() or 'preserve' in row['title'].lower(), row['title'].lower()))
        rows = attachment_rows + fileset_rows

        for row in rows:
            if row['title'].lower() == 'ocr':
                row['rdf_type'] = 'http://pcdm.org/use#ExtractedText'
            elif row['title'].lower() == 'hocr':
                row['rdf_type'] = 'http://pcdm.org/file-format-types#HTML'
            elif row['title'].lower() == 'preserve':
                row['rdf_type'] = 'http://pcdm.org/use#PreservationFile'

        with open(csv_filename.split(".csv")[0] + "_fixed.csv", mode='w', newline='') as outfile:
            fieldnames = reader.fieldnames
            required_fieldnames = ['source_identifier', 'title', 'model', 'visibility', 'rdf_type']
            for field in required_fieldnames:
                if field not in fieldnames:
                    fieldnames.append(field)
            if remove_columns:
                # Here are the columns that will not get removed when using the remove columns option
                fieldnames = ['source_identifier', 'title', 'model', 'visibility']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                if any(keyword in row['title'].lower() for keyword in keywords_list):
                    row['visibility'] = 'restricted'
                elif 'visibility' in row and row['visibility'] == "":
                    row['visibility'] = "open" # set default to open if not there
                elif 'visibility' not in row:
                    row['visibility'] = "open" # set default to open if not there
                if remove_columns:
                    row = {key: row[key] for key in fieldnames}
                writer.writerow(row)

if __name__ == "__main__":
    print("use this space to test metadata fixes if needed")