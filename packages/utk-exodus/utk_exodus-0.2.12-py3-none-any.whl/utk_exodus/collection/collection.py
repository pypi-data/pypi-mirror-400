from lxml import etree
from lxml.etree import XMLSyntaxError
from io import BytesIO
import csv
from utk_exodus.fedora import FedoraObject
from utk_exodus.restrict import Restrictions
import os
from tqdm import tqdm


class CollectionMetadata:
    """Grabs All Metadata for a Collection Object in Fedora."""

    def __init__(self, pid):
        self.pid = pid
        self.namespaces = {
            "mods": "http://www.loc.gov/mods/v3",
            "xlink": "http://www.w3.org/1999/xlink",
        }
        self.mods = self.get_metadata(pid)

    def simplify_xpath(self, xpath):
        try:
            return " | ".join(
                [value.text for value in self.mods.xpath(xpath, namespaces=self.namespaces)]
            )
        except TypeError:
            return ""

    def get_text_from_multiple_xpaths(self, xpaths):
        all_matches = []
        for xpath in xpaths:
            all_matches.extend(
                [
                    value.text
                    for value in self.mods.xpath(xpath, namespaces=self.namespaces)
                ]
            )
        return " | ".join(all_matches)

    def grab_all_metadata(self):
        return {
            "source_identifier": self.pid,
            "model": "Collection",
            "parents": "",
            "title": self.simplify_xpath("mods:titleInfo/mods:title"),
            "abstract": self.simplify_xpath("mods:abstract"),
            "contributor": "",
            "utk_contributor": self.get_text_from_multiple_xpaths(
                [
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Contributor")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Addressee")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Arranger")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Associated Name")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Autographer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Censor")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Choreographer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Client")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Contractor")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Copyright Holder")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Dedicatee")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Depicted")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Distributor")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Donor")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Editor")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Editor of Compilation")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Former Owner")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Honoree")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Host Institution")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Instrumentalist")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Interviewer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Issuing Body")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Music Copyist")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Musical Director")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Organizer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Originator")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Owner")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Performer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Printer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Printer of Plates")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Producer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Production Company")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Publisher")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Restorationist")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Set Designer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Signer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Speaker")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Stage Director")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Stage Manager")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Standards Body")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Surveyor")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Translator")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Videographer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Witness")]]/mods:namePart',
                ]
            ),
            "creator": "",
            "utk_creator": self.get_text_from_multiple_xpaths(
                [
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Creator")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Architect")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Artist")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Attributed Name")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Author")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Binding Designer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Cartographer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Compiler")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Composer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Correspondent")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Costume Designer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Designer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Engraver")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Illustrator")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Interviewee")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Lithographer")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Lyricist")]]/mods:namePart',
                    'mods:name[mods:role/mods:roleTerm[contains(.,"Photographer")]]/mods:namePart',
                ]
            ),
            "date_created": self.simplify_xpath(
                "mods:originInfo/mods:dateCreated[not(@encoding)]"
            ),
            "date_issued": self.simplify_xpath(
                "mods:originInfo/mods:dateIssued[not(@encoding)]"
            ),
            "date_created_d": self.simplify_xpath(
                "mods:originInfo/mods:dateCreated[@encoding]"
            ),
            "date_issued_d": self.simplify_xpath(
                "mods:originInfo/mods:dateIssued[@encoding]"
            ),
            "utk_publisher": self.simplify_xpath("mods:originInfo/mods:publisher"),
            "publisher": "",
            "publication_place": "",
            "extent": self.simplify_xpath("mods:physicalDescription/mods:extent"),
            "form": self.simplify_xpath("mods:physicalDescription/mods:form"),
            "subject":  self.get_text_from_multiple_xpaths(
                [
                    'mods:subject/mods:topic/@valueURI',
                    'mods:subject[mods:topic]/@valueURI'
                ]
            ),
            "keyword": self.simplify_xpath("mods:subject/mods:topic"),
            "spatial": "",
            "resource_type": "",
            "note": self.simplify_xpath("mods:note"),
            "repository": "",
            "visibility": self.get_policy(self.pid),
        }

    @staticmethod
    def get_metadata(pid):
        fedora = FedoraObject(
            auth=(
                os.environ.get("FEDORA_USERNAME"),
                os.environ.get("FEDORA_PASSWORD"),
            ),
            fedora_uri=os.environ.get("FEDORA_URI"),
            pid=f"{pid.replace('info:fedora/', '').strip()}",
        )
        r = fedora.streamDatastream("MODS")
        try:
            return etree.parse(BytesIO(r.content))
        except XMLSyntaxError:
            return etree.fromstring(
                """
                <mods xmlns="http://www.loc.gov/mods/v3" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-5.xsd">
                  <titleInfo>
                    <title></title>
                  </titleInfo>
                </mods>
                """
            )

    @staticmethod
    def get_policy(pid):
        fedora = FedoraObject(
            auth=(
                os.environ.get("FEDORA_USERNAME"),
                os.environ.get("FEDORA_PASSWORD"),
            ),
            fedora_uri=os.environ.get("FEDORA_URI"),
            pid=f"{pid.replace('info:fedora/', '').strip()}",
        )
        r = fedora.streamDatastream("POLICY")
        if r.status_code == 200:
            with open("tmp/POLICY.xml", "wb") as f:
                f.write(r.content)
            restrictions = Restrictions("tmp/POLICY.xml").get()
            if restrictions.get("work_restricted", "open"):
                return "restricted"
        else:
            return "open"


class CollectionImporter:
    def __init__(self, collections):
        self.collections = collections
        self.collection_metadata = self.__build_collections()
        self.headers = [k for k, v in self.collection_metadata[0].items()]

    def __build_collections(self):
        return [
            CollectionMetadata(collection).grab_all_metadata()
            for collection in tqdm(self.collections)
        ]

    def write_csv(self, filename):
        with open(filename, "w", newline="") as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in self.collection_metadata:
                writer.writerow(data)
        return
