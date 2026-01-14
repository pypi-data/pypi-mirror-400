import click
import os
import requests
import shutil
from utk_exodus.finder import FileOrganizer
from utk_exodus.fedora import FedoraObject
from utk_exodus.curate import FileCurator
from utk_exodus.metadata import MetadataMapping
from utk_exodus.risearch import ResourceIndexSearch
from utk_exodus.restrict import RestrictionsSheet
from utk_exodus.validate import ValidateMigration
from pathlib import Path
from tqdm import tqdm


class InterfaceController:
    def __init__(self, config, output, remote, total_size):
        self.config = self.__load_config(config)
        self.output = output
        self.remote = remote
        self.total_size = total_size

    @staticmethod
    def __load_config(config):
        configs = {
            "utk_dc": "utk_dc.yml",
            "samvera": "samvera_default.yml",
            "utk_dc_no_uris": "utk_dc_no_uris.yml",
            "utk_dc_no_uris_or_names": "utk_no_uris_no_names.yml",
        }
        config_path = Path(__file__).parent / "../config"
        return config_path / configs.get(config)

    def __curate_filesets_and_attachments(self, csv_file):
        click.echo(
            click.style(
                "Curating filesets and attachments ...", fg="magenta", bold=True
            )
        )
        curator = FileCurator(f"{csv_file}")
        curator.write_files_and_attachments_only(
            f"{self.output}/{self.output.split('/')[-1]}.csv_filesheets_and_attachments_only.csv",
            attachments_per_sheet=int(self.total_size),
            multi_sheets="multi",
        )
        curator.write_works_and_collections_only(
            f"{self.output}/{self.output.split('/')[-1]}_works_and_collections_only.csv"
        )
        return

    def __generate_metadata_sheet(self, path):
        click.echo(click.style("Generating metadata sheet ...", fg="green", bold=True))
        os.makedirs(self.output, exist_ok=True)
        metadata = MetadataMapping(self.config, path)
        os.makedirs("tmp", exist_ok=True)
        metadata.write_csv("tmp/works.csv")
        return

    @staticmethod
    def __get_mods(collection, work_type):
        click.echo(click.style("Finding MODS files ...", fg="red", bold=True))
        risearch = ResourceIndexSearch().get_works_based_on_type_and_collection(
            work_type, collection
        )
        return risearch

    @staticmethod
    def __get_m3():
        r = requests.get(
            "https://raw.githubusercontent.com/utkdigitalinitiatives/m3_profiles/main/maps/utk.yml"
        )
        with open("tmp/m3.yml", "wb") as f:
            f.write(r.content)
        return

    def __grab_file_info(self):
        click.echo(click.style("Grabbing file info ...", fg="yellow", bold=True))
        x = FileOrganizer("tmp/works.csv", ["filesets", "attachments"], self.remote)
        x.write_csv(f"{self.output}/{self.output.split('/')[-1]}.csv")
        self.__get_m3()
        return

    def __validate_import(self):
        click.echo(click.style("Validating import ...", fg="blue", bold=True))
        validator = ValidateMigration(
            profile="tmp/m3.yml",
            migration_sheet=f"{self.output}/{self.output.split('/')[-1]}.csv",
        )
        validator.iterate()
        return

    def build_import_from_directory(self, path):
        self.__generate_metadata_sheet(path)
        self.__grab_file_info()
        self.__validate_import()
        self.__curate_filesets_and_attachments(
            f"{self.output}/{self.output.split('/')[-1]}.csv"
        )
        click.echo(click.style("Done ...", fg="cyan", bold=True))
        return

    @staticmethod
    def __get_policies(collection, work_type):
        click.echo(click.style("Finding Policy files ...", fg="red", bold=True))
        risearch = ResourceIndexSearch().get_policies_based_on_type_and_collection(
            work_type, collection
        )
        return risearch

    @staticmethod
    def __download(files, path, dsid):
        for record in tqdm(files):
            fedora = FedoraObject(
                auth=(
                    os.environ.get("FEDORA_USERNAME"),
                    os.environ.get("FEDORA_PASSWORD"),
                ),
                fedora_uri=os.environ.get("FEDORA_URI"),
                pid=f"{record.replace('info:fedora/', '').strip()}",
            )
            fedora.getDatastream(dsid=dsid, output=path)
        return

    def __download_policies(self, collection, work_type):
        policies = self.__get_policies(collection, work_type)
        os.makedirs("tmp/policy_downloads", exist_ok=True)
        os.makedirs("tmp/policy_downloads/current_collection", exist_ok=True)
        self.__download(policies, "tmp/policy_downloads/current_collection", "POLICY")
        return

    def __download_mods(self, collection, work_type):
        mods = self.__get_mods(collection, work_type)
        os.makedirs("tmp", exist_ok=True)
        os.makedirs("tmp/mods_downloads", exist_ok=True)
        os.makedirs("tmp/mods_downloads/current_collection", exist_ok=True)
        self.__download(mods, "tmp/mods_downloads/current_collection", "MODS")
        return

    def restrict_files_and_works(self, original_sheet, policies_location):
        click.echo(click.style("Restricting files and works ...", fg="red", bold=True))
        x = RestrictionsSheet(original_sheet, policies_location)
        x.write_csv(f"{self.output}/{self.output.split('/')[-1]}_visibility.csv")
        return

    def download_mods(self, collection, work_type):
        # @TODO: Rename this
        # @TODO: Make sure this works elsewhere
        self.__download_mods(collection, work_type)
        self.__generate_metadata_sheet("tmp/mods_downloads/current_collection")
        shutil.rmtree("tmp/mods_downloads/current_collection")
        self.__download_policies(collection, work_type)
        self.__grab_file_info()
        self.restrict_files_and_works(
            f"{self.output}/{self.output.split('/')[-1]}.csv",
            "tmp/policy_downloads/current_collection",
        )
        shutil.rmtree("tmp/policy_downloads/current_collection")
        self.__validate_import()
        self.__curate_filesets_and_attachments(
            f"{self.output}/{self.output.split('/')[-1]}_visibility.csv"
        )
        click.echo(click.style("Done ...", fg="cyan", bold=True))
        return
