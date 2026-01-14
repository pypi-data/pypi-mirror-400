#!/usr/bin/env python3

from utk_exodus.finder import FileOrganizer
from utk_exodus.metadata import MetadataMapping
from utk_exodus.validate import ValidateMigration
from utk_exodus.controller import InterfaceController
from utk_exodus.template import ImportTemplate
from utk_exodus.combine import ImportRefactor
from utk_exodus.checksum import HashSheet
from utk_exodus.collection import CollectionImporter
from utk_exodus.risearch import ResourceIndexSearch
from utk_exodus.banish import BanishFiles
from utk_exodus.fedora import FedoraObject
from utk_exodus.review import ExistingImport
from utk_exodus.fixes import FixMetadata
import click
import requests
import os
from tqdm import tqdm
from csv import DictReader


@click.group()
def cli() -> None:
    pass


@cli.command("works", help="Create import sheet for works with metadata.")
@click.option(
    "--config",
    "-c",
    default="config/utk_dc.yml",
    help="Path to the configuration file for metadata mapping.",
)
@click.option(
    "--path",
    "-p",
    required=True,
    help="Path to the directory containing the metadata files.",
)
@click.option(
    "--output",
    "-o",
    default="delete/works.csv",
    help="Path to the output file you want to write to.",
)
def works(config: str, path: str, output: str) -> None:
    metadata = MetadataMapping(config, path)
    metadata.write_csv(output)
    r = requests.get(
        "https://raw.githubusercontent.com/utkdigitalinitiatives/m3_profiles/main/maps/utk.yml"
    )
    with open("delete/m3.yml", "wb") as f:
        f.write(r.content)
    print("Validating import ...")
    validator = ValidateMigration(profile="delete/m3.yml", migration_sheet=output)
    validator.iterate()


@cli.command(
    "add_files", help="Add filesets and attachments to and existing import sheet."
)
@click.option(
    "--sheet", "-s", help="Specify the original metadata works csv.", required=True
)
@click.option("--files_sheet", "-f", help="Optional: specify new sheet to write to.")
@click.option(
    "--what_to_add",
    "-w",
    help="Specify adding attachments, filesheets, or everything",
    default="everything",
)
@click.option(
    "--remote",
    "-r",
    help="Specify remote address of files",
    default="https://digital.lib.utk.edu/collections/islandora/object/",
)
def add_files(sheet: str, files_sheet: str, what_to_add: str, remote: str) -> None:
    if not files_sheet:
        files_sheet = f"{sheet.replace('.csv', '')}_with_filesets_and_attachments.csv"
    if what_to_add == "everything":
        what_to_add = ["filesets", "attachments"]
    """Take a CSV and Add files to it"""
    x = FileOrganizer(sheet, what_to_add, remote)
    x.write_csv(files_sheet)


@cli.command("works_and_files", help="Create import sheet with works and files.")
@click.option(
    "--config",
    "-c",
    default="utk_dc",
    type=click.Choice(
        ["utk_dc", "samvera", "utk_dc_no_uris", "utk_dc_no_uris_or_names"],
        case_sensitive=False,
    ),
    help="The configuration you want to use. By default, utk_dc.",
)
@click.option(
    "--collection",
    "-l",
    help="Specify the collection you want to download metadata for.",
)
@click.option(
    "--model",
    "-m",
    type=click.Choice(
        ["book", "image", "large_image", "pdf", "audio", "video", "compound"], case_sensitive=False
    ),
    help="The model you want to download metadata for.",
)
@click.option(
    "--path",
    "-p",
    help="Path to the directory containing the metadata files.",
)
@click.option(
    "--output",
    "-o",
    default="new_set",
    help="Path to the output directory you want to create.",
)
@click.option(
    "--remote",
    "-r",
    help="Specify remote address of files",
    default="https://digital.lib.utk.edu/collections/islandora/object/",
)
@click.option(
    "--total_size",
    "-t",
    help="Specify maximum number of attachments and filesets per sheet.",
    default=800,
)
def works_and_files(
    collection: str,
    config: str,
    model: str,
    path: str,
    output: str,
    remote: str,
    total_size: int,
) -> None:
    if model and collection:
        interface = InterfaceController(config, output, remote, total_size)
        interface.download_mods(collection, model)
    elif path:
        interface = InterfaceController(config, output, remote, total_size)
        interface.build_import_from_directory(path)
    else:
        print(
            "You must specify either a path to a directory or both a collection and model."
        )


@cli.command(
    "generate_sheet", help="Create full sample for content model from m3 profile."
)
@click.option(
    "--model",
    "-m",
    type=click.Choice(
        [
            "Attachment",
            "Audio",
            "Book",
            "CompoundObject",
            "GenericWork",
            "Image",
            "Newspaper",
            "PDF",
            "Video",
        ],
        case_sensitive=True,
    ),
    help="The content models to find rules about.",
)
@click.option(
    "--output",
    "-o",
    help="Specify where to write your output file.",
)
def generate_sheet(
    model: str,
    output: str,
) -> None:
    r = requests.get(
        "https://raw.githubusercontent.com/utkdigitalinitiatives/m3_profiles/main/maps/utk.yml"
    )
    with open("tmp/m3.yml", "wb") as f:
        f.write(r.content)
    it = ImportTemplate("tmp/m3.yml", model)
    it.write(output)


@cli.command(
    "remove_old_values", help="Remove old values from a previous import sheet."
)
@click.option(
    "--sheet",
    "-s",
    required=True,
    help="Specify the current sheet.",
)
@click.option(
    "--old_sheet",
    "-o",
    required=True,
    help="Specify the old sheet with unused values you want to remove.",
)
@click.option(
    "--new_sheet",
    "-n",
    required=True,
    help="Specify where you want to write the new sheet.",
)
def remove_old_values(
    sheet: str,
    old_sheet: str,
    new_sheet: str,
) -> None:
    ir = ImportRefactor(sheet, old_sheet)
    ir.create_csv_with_fields_to_nuke(sheet, new_sheet)
    print(f"Refactored sheet written to {new_sheet}.")


@cli.command(
    "hash_errors",
    help="Create sheet from a directory of errored import sheets.",
)
@click.option(
    "--path",
    "-p",
    required=True,
    help="Specify the path to the directory of sheets.",
)
@click.option(
    "--output",
    "-o",
    required=True,
    help="Specify where you want to write your sheets.",
)
def hash_errors(
    path: str,
    output: str,
) -> None:
    print(f"Generating checksums for bad files in csvs in {path}.")
    hs = HashSheet(path, output)
    hs.write()
    print(f"Hash sheet written to {output}.")


@cli.command(
    "generate_collection_metadata",
    help="Generate metadata for a collection.",
)
@click.option(
    "--collection",
    "-l",
    required=False,
    help="Specify the collection you want to download metadata for.",
)
@click.option(
    "--output",
    "-o",
    required=False,
    default="tmp/collections.csv",
    help="Specify where to write output.",
)
def generate_collection_metadata(
    collection: str,
    output: str,
) -> None:
    if collection:
        print(f"Generating metadata for {collection}.")
        x = CollectionImporter([collection])
    else:
        print("Generating metadata for all collections.")
        collections = ResourceIndexSearch().find_all_collections()
        x = CollectionImporter(collections)
    x.write_csv(output)
    print("Done. Metadata written to tmp/all_collections.csv.")

@cli.command(
    "banish",
    help="Remove Polices and MODS from import sheets",
)
@click.option(
    "--directory",
    "-d",
    required=True,
    help="The directory of CSVs you want to remove POLICY and MODS from",
)
def banish(
    directory: str,
) -> None:
    print(f"MODS and POLICIES From {directory}.")
    for path, directories, files in os.walk(directory):
        for file in tqdm(files):
            if file.endswith(".csv"):
                bf = BanishFiles(os.path.join(path, file))
                bf.write(os.path.join(path, file))

@cli.command(
    "get_all_versions",
    help="Download all versions of a datastream.",
)
@click.option(
    "--directory",
    "-d",
    required=True,
    help="The directory to write the versions to.",
)
@click.option(
    "--type",
    "-t",
    required=True,
    type=click.Choice(
        [
            "book", "image", "large_image", "pdf", "audio", "video", "compound", "page", "binary", "oral_history"
        ],
        case_sensitive=False
    ),
    help="The content model you want",
)
@click.option(
    "--dsid",
    "-ds",
    required=True,
    help="The datastream you want to download versions of.",
)
def get_all_versions(
    directory: str,
    type: str,
    dsid: str,
) -> None:
    print(f"Downloading all versions of {dsid} to {directory}.")
    for pid in tqdm(ResourceIndexSearch().get_works_of_a_type_with_dsid(type, dsid)):
        fedora = FedoraObject(
            auth=(os.getenv("FEDORA_USERNAME"), os.getenv("FEDORA_PASSWORD")),
            fedora_uri=os.getenv("FEDORA_URI"),
            pid=pid,
        )
        fedora.write_all_versions(dsid, directory)
    print("Done.")

@cli.command(
    "export_errors",
    help="Using a CSV, export all the errors from failed imports",
)
@click.option(
    "--csv",
    "-c",
    required=True,
    help="The CSV you want to read in",
)
@click.option(
    "--directory",
    "-d",
    required=True,
    help="Where to export the errors to",
)
def export_errors(
    csv: str,
    directory: str,
) -> None:
    print(f"Exporting errors from {csv} to {directory}.")
    with open(csv, "r") as file:
        reader = DictReader(file)
        import_ids = [row["Link to Errors"].split('/')[-2] for row in reader if row["Ongoing Issues"] == "Y"]
    ei = ExistingImport(import_ids, directory, initial_auth=(os.getenv('HYKU_BASIC_AUTH_USER'), os.getenv('HYKU_BASIC_AUTH_PASS')))
    ei.sign_in_to_hyku(os.getenv('HYKU_USER'), os.getenv('HYKU_PASS'))
    ei.export_errors()

@cli.command(
    "add_datastreams",
    help="Add datastreams to existing PIDS",
)
@click.option(
    "--path",
    "-p",
    required=True,
    help="Path to the Original Files",
)
def add_datastreams(
    path: str,
) -> None:
    print(f"Adding datastreams {path}.")
    for path, directories, files in os.walk(path):
        for file in tqdm(files):
            pid = file.split('_')[0]
            dsid = file.split('_')[1].split('.')[0]
            fedora = FedoraObject(
                auth=(os.getenv("FEDORA_USERNAME"), os.getenv("FEDORA_PASSWORD")),
                fedora_uri=os.getenv("FEDORA_URI"),
                pid=pid,
            )
            fedora.add_datastream(dsid, os.path.join(path, file))

@cli.command(
    "fix_metadata_sheet",
    help="Sorts and makes metadata fixes to filesets and attachments CSVs",
)
@click.option(
    "--csv",
    "-c",
    required=True,
    help="The CSV you want to read in or dir with only filesets and attachments CSVs",
)
@click.option(
    "--titles",
    "-t",
    required=False,
    default="MODS,Preserve,Release,Bioform,RELS-INT,HOCR,METS,ALTO",
    help="Optionally specify which titles to restrict visibility for, default is MODS,Preserve,Release,Bioform,RELS-INT,HOCR,METS,ALTO",
)
@click.option(
    "--remove_columns",
    "-r",
    required=False,
    default="N",
    help="Optionally specify if unnecessary columns should be removed (Y/N). Will remove everything except source_identifier', 'title', 'model', and 'visibility' columns",
)
def fix_metadata(
    csv: str,
    titles: str,
    remove_columns: str
) -> None:
    rc = (remove_columns.lower() == "y" or remove_columns.lower() == "yes")
    print(f"Running metadata fixes on {csv} and restricting {titles} " + ("and removing all columns except 'source_identifier', 'title', 'model', 'visibility'" if rc else "and keeping all columns"))
    path = csv
    updater = FixMetadata(titles, rc)
    if os.path.isdir(path):
        for filename in tqdm(os.listdir(path)):
            if filename.endswith('.csv'):
                csv_filename = os.path.join(path, filename)
                updater.update_metadata(csv_filename)
    else:
        updater.update_metadata(path)