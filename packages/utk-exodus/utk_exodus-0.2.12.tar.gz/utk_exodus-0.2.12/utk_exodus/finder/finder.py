import csv
from tqdm import tqdm
from utk_exodus.risearch import ResourceIndexSearch


class FileOrganizer:
    def __init__(
            self,
            csv,
            what_to_add=['filesets', 'attachments'],
            remote='https://digital.lib.utk.edu/collections/islandora/object/'
    ):
        self.original_csv = csv
        self.remote = remote
        self.original_as_dict = self.__read()
        self.headers = self.__get_headers()
        self.new_csv_with_files = self.__add_files(what_to_add)

    def __read(self):
        csv_content = []
        with open(self.original_csv, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_content.append(row)
        return csv_content

    def __get_headers(self):
        original_headers = [k for k, v in self.original_as_dict[0].items()]
        original_headers.append('rdf_type')
        original_headers.append('file_language')
        return original_headers

    def __add_a_file(self, filename, row, preserve_and_obj=False, parent=""):
        default_headings = ('source_identifier', 'sequence', 'model', 'remote_files', 'title', 'abstract', 'parents', 'rdf_type')
        initial_data = {
            'source_identifier': f"{row['source_identifier'].replace('.xml', '')}_{filename}_fileset",
            'model': "FileSet",
            'sequence': row['sequence'],
            'remote_files': f"{self.remote}{row['source_identifier'].replace('_MODS.xml', '').replace('_', ':').replace('.xml', '')}/datastream/{filename}",
            'title': self.__get_filename_title(filename, preserve_and_obj, row),
            'abstract': f"{filename} for {row['source_identifier']}",
            'parents': f"{row['source_identifier'].replace('.xml', '')}_{filename}",
            'rdf_type': RDFTypeGenerator(row['model']).find_file_types(filename, preserve_and_obj),
            'file_language': ''
        }
        if parent != "":
            initial_data['parents'] = parent
        if preserve_and_obj is True and filename == "OBJ" and row['model'] == "Pdf":
            initial_data['parents'] = f"{row['source_identifier'].replace('.xml', '')}"
        if row['model'] == "Pdf" and filename in ("OBJ", "PDFA"):
            initial_data['remote_files'] = f"https://digital.lib.utk.edu/collections/islandora/object/{row['source_identifier'].replace('_MODS.xml', '').replace('_', ':').replace('.xml', '')}/datastream/{filename}/view.pdf"
        for k, v in row.items():
            if k not in default_headings:
                initial_data[k] = ''
        if row['model'] == "Audio" or row['model'] == "Video":
            if filename == "TRANSCRIPT":
                initial_data['file_language'] = 'en'
                initial_data['title'] = 'Captions in English'
            elif filename == "TRANSCRIPT-ES":
                initial_data['file_language'] = 'es'
                initial_data['title'] = 'Subtítulos en español'
        return initial_data

    def __add_an_attachment(self, filename, row, preserve_and_obj=False, parent=""):
        default_headings = ('source_identifier', 'sequence', 'model', 'remote_files', 'title', 'abstract', 'parents', 'rdf_type')
        initial_data = {
            'source_identifier': f"{row['source_identifier'].replace('.xml', '')}_{filename}",
            'model': "Attachment",
            'sequence': row['sequence'],
            'remote_files': "",
            'title': self.__get_filename_title(filename, preserve_and_obj, row),
            'abstract': f"{filename} for {row['source_identifier']}",
            'parents': row['source_identifier'].replace('.xml', ''),
            'rdf_type': RDFTypeGenerator(row['model']).find_file_types(filename, preserve_and_obj),
            'file_language': ''
        }
        if parent != "":
            initial_data['parents'] = parent
        for k, v in row.items():
            if k not in default_headings:
                initial_data[k] = ''
        if row['model'] == "Audio" or row['model'] == "Video":
            if filename == "TRANSCRIPT":
                initial_data['file_language'] = 'en'
                initial_data['title'] = 'Captions in English'
            elif filename == "TRANSCRIPT-ES":
                initial_data['file_language'] = 'es'
                initial_data['title'] = 'Subtítulos en español'
        return initial_data

    @staticmethod
    def __get_filename_title(dsid, preserve_and_obj, row):
        if preserve_and_obj and row['model'] == "Image":
            identifier = row['local_identifier'].split(' | ')[0]
            if dsid == "OBJ":
                return f"{identifier}_i"
            elif dsid == "PRESERVE":
                return f"{identifier}_p"
            else:
                return dsid
        elif preserve_and_obj and row['model'] == "Audio":
            identifier = row['local_identifier'].split(' | ')[0]
            if dsid == "OBJ":
                return f"{identifier}_p"
            elif dsid == "PROXY_MP3":
                return f"{identifier}_i"
            else:
                return dsid
        else:
            return dsid

    @staticmethod
    def __get_rdf_types_for_file(dsid, preserve_and_obj):
        if dsid == "OBJ" and preserve_and_obj is False:
            return "http://pcdm.org/use#PreservationFile | http://pcdm.org/use#IntermediateFile"
        elif dsid == "OBJ":
            return "http://pcdm.org/use#IntermediateFile"
        elif dsid == "PRESERVE":
            return "http://pcdm.org/use#PreservationFile"
        elif dsid == "MODS":
            return "http://pcdm.org/file-format-types#Markup"
        elif dsid == "POLICY":
            return "http://pcdm.org/file-format-types#StructuredText"
        elif dsid == "OCR":
            return "http://pcdm.org/use#ExtractedText"
        elif dsid == "HOCR":
            return "http://pcdm.org/file-format-types#HTML"
        else:
            return "http://pcdm.org/use#OriginalFile"

    def __add_files(self, what_to_add=['filesets', 'attachments']):
        new_csv_content = []
        for row in tqdm(self.original_as_dict):
            if row['model'] != "Page":
                new_csv_content.append(row)
            pid = row['source_identifier'].replace('_MODS.xml', '').replace('_', ":")
            all_files = FileSetFinder(pid).files
            if row['model'] == "Image":
                for dsid in all_files:
                    if 'PRESERVE' in all_files and 'OBJ' in all_files:
                        if 'attachments' in what_to_add:
                            new_csv_content.append(self.__add_an_attachment(dsid, row, True))
                        if 'filesets' in what_to_add:
                            new_csv_content.append(self.__add_a_file(dsid, row, True))
                    else:
                        if 'attachments' in what_to_add:
                            new_csv_content.append(self.__add_an_attachment(dsid, row))
                        if 'filesets' in what_to_add:
                            new_csv_content.append(self.__add_a_file(dsid, row))
            elif row['model'] == "Audio":
                for dsid in all_files:
                    if 'OBJ' in all_files and 'PROXY_MP3' in all_files:
                        new_csv_content.append(self.__add_an_attachment(dsid, row, True))
                        new_csv_content.append(self.__add_a_file(dsid, row, True))
                    else:
                        new_csv_content.append(self.__add_an_attachment(dsid, row))
                        new_csv_content.append(self.__add_a_file(dsid, row))
            elif row['model'] == "Video":
                for dsid in all_files:
                    if 'OBJ' in all_files and 'MP4' in all_files:
                        new_csv_content.append(self.__add_an_attachment(dsid, row, True))
                        new_csv_content.append(self.__add_a_file(dsid, row, True))
                    else:
                        new_csv_content.append(self.__add_an_attachment(dsid, row))
                        new_csv_content.append(self.__add_a_file(dsid, row))
            elif row['model'] == "Pdf":
                for dsid in all_files:
                    if 'OBJ' in all_files and 'PDFA' in all_files:
                        if dsid == "OBJ":
                            new_csv_content.append(self.__add_a_file(dsid, row, True))
                        else:
                            new_csv_content.append(self.__add_an_attachment(dsid, row, True))
                            new_csv_content.append(self.__add_a_file(dsid, row, True))
                    else:
                        new_csv_content.append(self.__add_an_attachment(dsid, row))
                        new_csv_content.append(self.__add_a_file(dsid, row))
            elif row['model'] == "Collection":
                pass
            elif row['model'] == "Book":
                for dsid in all_files:
                    if 'PRESERVE' in all_files and 'OBJ' in all_files:
                        if 'attachments' in what_to_add:
                            new_csv_content.append(self.__add_an_attachment(dsid, row, True))
                        if 'filesets' in what_to_add:
                            new_csv_content.append(self.__add_a_file(dsid, row, True))
                    else:
                        if 'attachments' in what_to_add:
                            new_csv_content.append(self.__add_an_attachment(dsid, row))
                        if 'filesets' in what_to_add:
                            new_csv_content.append(self.__add_a_file(dsid, row))
            elif row['model'] == "CompoundObject":
                for dsid in all_files:
                    if 'PRESERVE' in all_files and 'OBJ' in all_files:
                        if 'attachments' in what_to_add:
                            new_csv_content.append(self.__add_an_attachment(dsid, row, True))
                        if 'filesets' in what_to_add:
                            new_csv_content.append(self.__add_a_file(dsid, row, True))
                    else:
                        if 'attachments' in what_to_add:
                            new_csv_content.append(self.__add_an_attachment(dsid, row))
                        if 'filesets' in what_to_add:
                            new_csv_content.append(self.__add_a_file(dsid, row))
            elif row['model'] == "Page":
                dsids_to_remove = ('MODS', 'RELS-INT', 'PDF')
                for dsid in dsids_to_remove:
                    if dsid in all_files:
                        all_files.remove(dsid)
                for dsid in all_files:
                    if 'PRESERVE' in all_files and 'OBJ' in all_files:
                        if 'attachments' in what_to_add:
                            new_csv_content.append(self.__add_an_attachment(dsid, row, True, parent=row['parents']))
                        if 'filesets' in what_to_add:
                            new_csv_content.append(self.__add_a_file(dsid, row, True))
                    else:
                        if 'attachments' in what_to_add:
                            new_csv_content.append(self.__add_an_attachment(dsid, row, parent=row['parents']))
                        if 'filesets' in what_to_add:
                            new_csv_content.append(self.__add_a_file(dsid, row))
            else:
                raise Exception(f"Unknown work type on {row['source_identifier']}: {row['model']}")
        return new_csv_content

    def write_csv(self, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in self.new_csv_with_files:
                writer.writerow(data)
        return


class FileSetFinder:
    def __init__(self, pid):
        self.universal_ignores = (
            'DC', 'RELS-EXT', 'TECHMD', 'PREVIEW', 'JPG', 'JP2', 'MEDIUM_SIZE', 'POLICY', 'TN', 'MODS', 'POLICY'
        )
        self.pid = pid.replace('.xml', '')
        self.files = self.__get_all_files()

    def __get_all_files(self):
        results = ResourceIndexSearch().get_files(self.pid)
        return [result for result in results if result not in self.universal_ignores]


class RDFTypeGenerator:
    def __init__(self, parent_type):
        self.parent_type = parent_type

    def find_file_types(self, dsid, preserve_and_obj):
        if self.parent_type == "Image":
            return self.__get_rdf_types_for_file_on_an_image(dsid, preserve_and_obj)
        elif self.parent_type == "Audio":
            return self.__get_rdf_types_for_file_on_an_audio_work(dsid, preserve_and_obj)
        elif self.parent_type == "Video":
            return self.__get_rdf_types_for_file_on_a_video_work(dsid, preserve_and_obj)
        elif self.parent_type == "Book":
            return self.__get_rdf_types_for_file_on_a_book(dsid, preserve_and_obj)
        elif self.parent_type == "Pdf":
            return self.__get_rdf_types_for_file_on_a_pdf_work(dsid, preserve_and_obj)
        elif self.parent_type == "Page":
            return self.__get_rdf_types_for_file_on_a_pdf_work(dsid, preserve_and_obj)
        elif self.parent_type == "CompoundObject":
            return self.__get_rdf_types_for_file_on_a_compound_object(dsid)
        else:
            raise Exception(f"Parent type unknown: {self.parent_type}")

    @staticmethod
    def __get_rdf_types_for_file_on_an_image(dsid, preserve_and_obj):
        if dsid == "OBJ" and preserve_and_obj is False:
            return "http://pcdm.org/use#PreservationFile | http://pcdm.org/use#IntermediateFile"
        elif dsid == "OBJ":
            return "http://pcdm.org/use#IntermediateFile"
        elif dsid == "PRESERVE":
            return "http://pcdm.org/use#PreservationFile"
        elif dsid == "MODS":
            return "http://pcdm.org/file-format-types#Markup"
        elif dsid == "POLICY":
            return "http://pcdm.org/file-format-types#StructuredText"
        elif dsid == "OCR":
            return "http://pcdm.org/use#ExtractedText"
        elif dsid == "HOCR":
            return "http://pcdm.org/file-format-types#HTML"
        else:
            return "http://pcdm.org/use#OriginalFile"

    @staticmethod
    def __get_rdf_types_for_file_on_an_audio_work(dsid, preserve_and_obj):
        if dsid == "OBJ" and preserve_and_obj is False:
            return "http://pcdm.org/use#PreservationFile | http://pcdm.org/use#IntermediateFile"
        elif dsid == "OBJ":
            return "http://pcdm.org/use#PreservationFile"
        elif dsid == "PROXY_MP3":
            return "http://pcdm.org/use#IntermediateFile"
        elif dsid == "POLICY":
            return "http://pcdm.org/file-format-types#StructuredText"
        elif dsid == "MODS":
            return "http://pcdm.org/file-format-types#Markup"
        elif dsid == "TRANSCRIPT":
            return "http://pcdm.org/use#Transcript"
        elif dsid == "TRANSCRIPT-ES":
            return "http://pcdm.org/use#Transcript"
        elif dsid == "TN":
            return "http://pcdm.org/use#ThumbnailImage"
        else:
            return "http://pcdm.org/use#OriginalFile"

    @staticmethod
    def __get_rdf_types_for_file_on_a_video_work(dsid, preserve_and_obj):
        if dsid == "OBJ" and preserve_and_obj is False:
            return "http://pcdm.org/use#PreservationFile | http://pcdm.org/use#IntermediateFile"
        elif dsid == "OBJ":
            return "http://pcdm.org/use#PreservationFile"
        elif dsid == "MP4":
            return "http://pcdm.org/use#IntermediateFile"
        elif dsid == "POLICY":
            return "http://pcdm.org/file-format-types#StructuredText"
        elif dsid == "MODS":
            return "http://pcdm.org/file-format-types#Markup"
        elif dsid == "TRANSCRIPT":
            return "http://pcdm.org/use#Transcript"
        elif dsid == "TRANSCRIPT-ES":
            return "http://pcdm.org/use#Transcript"
        elif dsid == "TN":
            return "http://pcdm.org/use#ThumbnailImage"
        else:
            return "http://pcdm.org/use#OriginalFile"

    @staticmethod
    def __get_rdf_types_for_file_on_a_pdf_work(dsid, preserve_and_obj):
        if dsid == "OBJ" and preserve_and_obj is False:
            return "http://pcdm.org/use#PreservationFile | http://pcdm.org/use#IntermediateFile"
        elif dsid == "PDFA":
            return "http://pcdm.org/use#PreservationFile"
        elif dsid == "OBJ":
            return "http://pcdm.org/use#IntermediateFile | http://pcdm.org/use#OriginalFile"
        elif dsid == "POLICY":
            return "http://pcdm.org/file-format-types#StructuredText"
        elif dsid == "MODS":
            return "http://pcdm.org/file-format-types#Markup"
        elif dsid == "OCR":
            return "http://pcdm.org/use#ExtractedText"
        elif dsid == "HOCR":
            return "http://pcdm.org/file-format-types#HTML"
        else:
            return "http://pcdm.org/use#OriginalFile"

    @staticmethod
    def __get_rdf_types_for_file_on_a_book(dsid, preserve_and_obj):
        if dsid == "OBJ" and preserve_and_obj is False:
            return "http://pcdm.org/use#PreservationFile | http://pcdm.org/use#IntermediateFile"
        elif dsid == "OBJ":
            return "http://pcdm.org/use#PreservationFile"
        elif dsid == "MODS":
            return "http://pcdm.org/file-format-types#Markup"
        elif dsid == "TRANSCRIPT":
            return "http://pcdm.org/use#Transcript"
        elif dsid == "OCR":
            return "http://pcdm.org/use#ExtractedText"
        elif dsid == "PDF":
            return "http://pcdm.org/file-format-types#Document | http://pcdm.org/use#ServiceFile"
        elif dsid == "ORIGINAL":
            return "http://pcdm.org/file-format-types#Document | http://pcdm.org/use#ServiceFile | http://pcdm.org/use#OriginalFile"
        elif dsid == "ORIGINAL_EDITED":
            return "http://pcdm.org/file-format-types#Document | http://pcdm.org/use#ServiceFile"
        elif dsid == "TEI":
            return "http://pcdm.org/file-format-types#Markup"
        else:
            return "http://pcdm.org/use#OriginalFile"

    @staticmethod
    def __get_rdf_types_for_file_on_a_compound_object(dsid):
        if dsid == "MODS":
            return "http://pcdm.org/file-format-types#Markup"
        elif dsid == "AIP":
            return "http://pcdm.org/use#PreservationFile"
        elif dsid == "DIP":
            return "http://pcdm.org/use#IntermediateFile"
        else:
            return "http://pcdm.org/use#OriginalFile"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Add files to a CSV.')
    parser.add_argument("-s", "--sheet", dest="sheet", help="Specify original csv.", required=True)
    parser.add_argument(
        "-f", "--files_sheet", dest="files_sheet", help="Optional: specify files sheet."
    )
    parser.add_argument(
        '-w', "--what_to_add", dest="what_to_add", help="What To Add to Sheet", default="everything"
    )
    parser.add_argument(
        '-r', "--remote", dest="remote", help="Remote File Server", default='https://digital.lib.utk.edu/collections/islandora/object/'
    )
    args = parser.parse_args()
    files_sheet = f"{args.sheet.replace('.csv', '')}_with_filesets_and_attachments.csv"
    what_to_add = ['filesets', 'attachments']
    if args.files_sheet:
        files_sheet = args.files_sheet
    if args.what_to_add != 'everything':
        what_to_add = [args.what_to_add]
    """Take a CSV and Add files to it"""
    x = FileOrganizer(
        args.sheet,
        what_to_add,
        args.remote
    )
    x.write_csv(files_sheet)
    """Below: Get datastreams of a PID without the ones to ignore"""
    # x = FileSetFinder('heilman:150')
    # print(x.files)
    """Below: Get Large Images from a Collection with on constituent parts of a compound object"""
    # x = ResourceIndexSearch().get_images_no_parts('collections:boydcs')
    # with open('temp/things_to_download.txt', 'w') as things_to_download:
    #     for pid in x:
    #         things_to_download.write(f"{pid}\n")
