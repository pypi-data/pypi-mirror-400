import requests
import xmltodict
from urllib.parse import quote


class FedoraObject:
    def __init__(self, auth, fedora_uri, pid):
        self.auth = auth
        self.fedora_uri = fedora_uri
        self.pid = f"{pid.replace('info:fedora/','').strip()}"

    @staticmethod
    def __guess_extension(content_type):
        mimetypes = {
            "image/tiff": "tif",
            "image/jp2": "jp2",
            "application/xml": "xml",
            "application/pdf": "pdf",
            "audio/vnd.wave": "wav",
            "image/jpeg": "jpg",
            "text/plain": "txt",
            "text/x-asm": "vtt",
            "text/x-c++": "vtt",
            "text/x-c": "vtt",
            "video/dv": "dv",
        }
        return mimetypes.get(content_type, "bin")

    def getDatastream(self, dsid, output, as_of_date=None):
        if as_of_date:
            r = requests.get(
                f"{self.fedora_uri}/objects/{self.pid}/datastreams/{dsid}/content?asOfDateTime={as_of_date}",
                auth=self.auth,
                allow_redirects=True,
            )
        else:
            r = requests.get(
                f"{self.fedora_uri}/objects/{self.pid}/datastreams/{dsid}/content",
                auth=self.auth,
                allow_redirects=True,
            )
        if r.status_code == 200 and as_of_date:
            open(
                f'{output}/{self.pid}_{dsid}_{as_of_date}.{self.__guess_extension(r.headers.get("Content-Type", "application/binary"))}',
                "wb",
            ).write(r.content)
        elif r.status_code == 200:
            open(
                f'{output}/{self.pid}_{dsid}.{self.__guess_extension(r.headers.get("Content-Type", "application/binary"))}',
                "wb",
            ).write(r.content)
        else:
            print(f"{r.status_code} on {self.pid}.")
        return

    def streamDatastream(self, dsid):
        r = requests.get(
            f"{self.fedora_uri}/objects/{self.pid}/datastreams/{dsid}/content",
            auth=self.auth,
            allow_redirects=True,
            stream=True,
        )
        return r

    def getDatastreamHistory(self, dsid):
        r = requests.get(
            f"{self.fedora_uri}/objects/{self.pid}/datastreams/{dsid}/history?format=xml",
            auth=self.auth,
            allow_redirects=True,
        )
        return xmltodict.parse(r.content.decode("utf-8"))

    def write_all_versions(self, dsid, output):
        history = self.getDatastreamHistory(dsid)
        if isinstance(history["datastreamHistory"]["datastreamProfile"], dict):
            self.getDatastream(
                dsid, output, history["datastreamHistory"]["datastreamProfile"]["dsCreateDate"]
            )
        else:
            for version in history["datastreamHistory"]["datastreamProfile"]:
                self.getDatastream(dsid, output, version["dsCreateDate"])
        return

    def add_datastream(self, dsid, file, mimetype="text/plain"):
        r = requests.post(
            f"{self.fedora_uri}/objects/{self.pid}/datastreams/{dsid}?controlGroup=M&dsLabel={dsid}&versionable=true"
            f"&dsState=A&logMessage=Added+{dsid}+datastream+to+{self.pid}.",
            auth=self.auth,
            headers={"Content-Type": mimetype},
            data=open(file, "rb"),
        )
        return r

    def purge_relationship(self, predicate, object, is_literal=True):
        body = f"/objects/{self.pid}/relationships?subject=info%3afedora/{self.pid}&predicate={quote(predicate)}&object={quote(object)}&isLiteral={is_literal}"
        r = requests.delete(
            f"{self.fedora_uri}{body}",
            auth=self.auth,
        )
        return r

    def add_relationship(self, predicate, object, is_literal=True):
        r = requests.post(
            f"{self.fedora_uri}/objects/{self.pid}/relationships/new?subject=info%3afedora/{self.pid}&predicate={quote(predicate)}&object={quote(object)}&isLiteral={is_literal}",
            auth=self.auth,
        )
        return r

    def remove_membership_of_page(self, book_pid):
        # Remove the isPageOf relationship
        self.purge_relationship(
            "http://islandora.ca/ontology/relsext#isPageOf", f"info:fedora/{book_pid}", False
        )
        # Remove isMemberOf relationship
        self.purge_relationship(
            "info:fedora/fedora-system:def/relations-external#isMemberOf",
            f"info:fedora/{book_pid}",
            False
        )
        return

    def add_membership_of_page(self, book_pid):
        self.add_relationship(
            "http://islandora.ca/ontology/relsext#isPageOf", f"info:fedora/{book_pid}", False
        )
        self.add_relationship(
            "info:fedora/fedora-system:def/relations-external#isMemberOf", f"info:fedora/{book_pid}", False
        )
        return

    def remove_sequencing(self, sequence_number):
        self.purge_relationship(
            "http://islandora.ca/ontology/relsext#isSequenceNumber", sequence_number, True
        )
        self.purge_relationship(
            "http://islandora.ca/ontology/relsext#isPageNumber", sequence_number, True
        )
        self.purge_relationship(
            "http://islandora.ca/ontology/relsext#isSection", sequence_number, True
        )
        return

    def add_sequencing(self, sequence_number):
        self.add_relationship(
            "http://islandora.ca/ontology/relsext#isSequenceNumber", sequence_number, True
        )
        self.add_relationship(
            "http://islandora.ca/ontology/relsext#isPageNumber", sequence_number, True
        )
        self.add_relationship(
            "http://islandora.ca/ontology/relsext#isSection", sequence_number, True
        )
        return


if __name__ == "__main__":
    import os
    x = FedoraObject(
        auth=(os.getenv("FEDORA_USERNAME"), os.getenv("FEDORA_PASSWORD")),
        fedora_uri=os.getenv("FEDORA_URI"),
        pid="beacon:35815"
    )
    x.remove_membership_of_page("beacon:35814")
    x.remove_sequencing("10")
    x.add_sequencing("12")
    x.add_membership_of_page("beacon:35825")
