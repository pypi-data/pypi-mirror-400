import hashlib
from csv import DictWriter, DictReader
import os
import requests
from tqdm import tqdm


class HashSheet:
    def __init__(self, path, output):
        self.path = path
        self.output = output
        self.all_files = self.walk_sheets(path)

    @staticmethod
    def walk_sheets(path):
        """Walk through a directory and return a list of all files.

        Args:
            path (str): The path to the directory to walk through.

        Returns:
            list: A list of all files in the directory.

        Examples:
            >>> hs = HashSheet("tests/fixtures/bad_imports", "example.csv")
            >>> hs.walk_sheets("tests/fixtures/bad_imports")
            ['https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:248_MODS.xml', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:309_MODS.xml', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:118_OBJ.jp2', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:99_MODS.xml', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:374_MODS.xml', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:465_OBJ.jp2', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:356_MODS.xml', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:254_OBJ.jp2', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:451_OBJ.jp2', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:104_MODS.xml', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:419_MODS.xml', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:318_OBJ.jp2', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:463_MODS.xml', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:350_MODS.xml', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:108_OBJ.jp2', 'https://digital.lib.utk.edu/migration/mpaekefauver/mpaekefauver:420_MODS.xml']

        """
        all_files = []
        for path, directories, files in os.walk(path):
            for filename in files:
                with open(f"{path}/{filename}", "r") as f:
                    reader = DictReader(f)
                    for row in reader:
                        all_files.append(row["remote_files"])
        return all_files

    def checksum(self):
        """Calculate the sha1 checksum of all files listed in csvs in a directory.

        Returns:
            list: A list of dictionaries with the url and checksum of each file.

        Examples:
            No example to keep tests running quickly.

        """
        files_with_checksums = []
        for file in tqdm(self.all_files):
            hash = self.checksum_file(file)
            files_with_checksums.append(hash)
        return files_with_checksums

    @staticmethod
    def checksum_file(file):
        """Calculate the sha1 checksum of a file.

        Args:
            file (str): The path to the file to checksum.

        Returns:
            dict: A dictionary with the url and checksum of the file.

        Examples:
            >>> hs = HashSheet("tests/fixtures/bad_imports", "example.csv")
            >>> hs.checksum_file("https://raw.githubusercontent.com/utkdigitalinitiatives/utk-exodus/main/tests/fixtures/colloquy_202.xml")
            {'url': 'https://raw.githubusercontent.com/utkdigitalinitiatives/utk-exodus/main/tests/fixtures/colloquy_202.xml', 'checksum': '081a51fae0200f266d2933756d48441c4ea77b1e'}

        """
        response = requests.get(file, stream=True)
        response.raise_for_status()
        sha1 = hashlib.sha1()
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                sha1.update(chunk)
        return {"url": file, "checksum": sha1.hexdigest()}

    def write(self):
        with open(self.output, "w") as csvfile:
            writer = DictWriter(csvfile, fieldnames=["url", "checksum"])
            writer.writeheader()
            writer.writerows(self.checksum())
        return


if __name__ == "__main__":
    path = "tests/fixtures/bad_imports"
    output = "delete/sample_checksums.csv"
    checksum = HashSheet(path, output)
    checksum.write()
