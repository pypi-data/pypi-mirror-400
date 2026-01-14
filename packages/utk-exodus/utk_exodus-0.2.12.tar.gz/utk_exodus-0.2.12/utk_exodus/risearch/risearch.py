import requests
from urllib.parse import quote


class ResourceIndexSearch:
    def __init__(
        self,
        language="sparql",
        riformat="CSV",
        ri_endpoint="https://porter.lib.utk.edu/fedora/risearch",
    ):
        self.risearch_endpoint = ri_endpoint
        self.valid_languages = ("itql", "sparql")
        self.valid_formats = ("CSV", "Simple", "Sparql", "TSV", "JSON")
        self.language = self.validate_language(language)
        self.format = self.validate_format(riformat)
        self.base_url = (
            f"{self.risearch_endpoint}?type=tuples"
            f"&lang={self.language}&format={self.format}&limit=1000000"
        )

    def validate_language(self, language):
        if language in self.valid_languages:
            return language
        else:
            raise Exception(
                f"Supplied language is not valid: {language}. Must be one of {self.valid_languages}."
            )

    def validate_format(self, user_format):
        if user_format in self.valid_formats:
            return user_format
        else:
            raise Exception(
                f"Supplied format is not valid: {user_format}. Must be one of {self.valid_formats}."
            )

    @staticmethod
    def __clean_csv_results(split_results, uri_prefix):
        results = []
        for result in split_results:
            if result.startswith(uri_prefix):
                new_result = result.split(",")
                results.append(
                    (new_result[0].replace(uri_prefix, ""), int(new_result[1]))
                )
        return sorted(results, key=lambda x: x[1])

    def get_files(self, pid):
        if self.language != "sparql":
            raise Exception(
                f"You must use sparql as the language for this method.  You used {self.language}."
            )
        sparql_query = quote(
            f"SELECT $files FROM <#ri> WHERE {{ <info:fedora/{pid}> "
            f"<info:fedora/fedora-system:def/view#disseminates> $files . }}"
        )
        results = (
            requests.get(f"{self.base_url}&query={sparql_query}")
            .content.decode("utf-8")
            .split("\n")
        )
        return [
            result.split("/")[-1] for result in results if result.startswith("info")
        ]

    def __request_pids(self, request):
        results = (
            requests.get(f"{self.base_url}&query={request}")
            .content.decode("utf-8")
            .split("\n")
        )
        return [
            result.split("/")[-1] for result in results if result.startswith("info")
        ]

    def __request_json(self, request):
        return requests.get(f"{self.base_url}&query={request}").json()

    def get_images_no_parts(self, collection):
        """@Todo: Fix long queries."""
        members_of_collection_query = quote(
            f"SELECT ?pid FROM <#ri> WHERE "
            f"{{ ?pid <info:fedora/fedora-system:def/model#hasModel> <info:fedora/islandora:sp_large_image_cmodel> ; "
            f"<info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/{collection}> . }}"
        )
        members_of_collection_parts_query = quote(
            f"SELECT ?pid FROM <#ri> WHERE "
            f"{{ ?pid <info:fedora/fedora-system:def/model#hasModel> <info:fedora/islandora:sp_large_image_cmodel> ; "
            f"<info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/{collection}> ; "
            f"<info:fedora/fedora-system:def/relations-external#isConstituentOf> ?unknown. }}"
        )
        members_of_collection = self.__request_pids(members_of_collection_query)
        members_of_collection_parts = self.__request_pids(
            members_of_collection_parts_query
        )
        members_of_collection_no_parts = [
            pid
            for pid in members_of_collection
            if pid not in members_of_collection_parts
        ]
        return members_of_collection_no_parts

    def get_parent_collections(self, pid):
        query = quote(
            f"""SELECT ?parent FROM <#ri> WHERE {{<info:fedora/{pid}> <info:fedora/fedora-system:def/relations-external#isMemberOfCollection> ?parent .}}"""
        )
        collections = self.__request_pids(query)
        return collections

    def get_members_types_and_collections(self, pid):
        query = quote(
            f"""SELECT ?pid ?work_type ?collection FROM <#ri> WHERE {{?pid <info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/{pid}> ;<info:fedora/fedora-system:def/model#hasModel> ?work_type ;<info:fedora/fedora-system:def/relations-external#isMemberOfCollection> ?collection .}}"""
        )
        results = self.__request_json(query)
        return results

    def get_islandora_work_type(self, pid):
        query = quote(
            f"""SELECT ?work_type FROM <#ri> WHERE {{<info:fedora/{pid}> <info:fedora/fedora-system:def/model#hasModel> ?work_type .}}"""
        )
        results = requests.get(f"{self.base_url}&query={query}").content.decode("utf-8")
        return [
            result.strip()
            for result in results.split("\n")
            if "info:fedora/fedora-system:FedoraObject-3.0" not in result
        ][1]

    def count_books_and_pages_in_collection(self, collection):
        pages = []
        query = quote(
            f"""SELECT ?pid FROM <#ri> WHERE {{ ?pid <info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/{collection}>; <info:fedora/fedora-system:def/model#hasModel> <info:fedora/islandora:bookCModel> .}}"""
        )
        results = requests.get(f"{self.base_url}&query={query}").json()
        books = [result["pid"] for result in results["results"]]
        for book in books:
            query = quote(
                f"""SELECT ?page FROM <#ri> WHERE {{?page <http://islandora.ca/ontology/relsext#isPageOf> <{book}>.}}"""
            )
            page_results = requests.get(f"{self.base_url}&query={query}").json()
            for page in page_results["results"]:
                pages.append(page)
        return len(books), len(pages)

    def find_pages_in_book(self, book):
    #     query = quote(
    #         f"SELECT ?pid ?page WHERE {{ "
    #         f"?pid <info:fedora/fedora-system:def/model#hasModel> "
    #         f"<info:fedora/islandora:pageCModel> ;"
    #         f"<info:fedora/fedora-system:def/relations-external#isMemberOf> "
    #         f"<info:fedora/{book}> ; "
    #         f"<http://islandora.ca/ontology/relsext#isPageNumber> ?page . }}"
    #     )
        # page_results = requests.get(f"{self.base_url}&query={query}").content
        # TODO remove whichever of these is not being used
        # This was all added in an attempt to get the proper book titles from islandora
        # It worked but these were not the titles we were looking for so this isn't really doing much for us
        test_query = quote(
            f"SELECT ?pid ?page ?title WHERE {{ "
            f"?pid <info:fedora/fedora-system:def/model#hasModel> "
            f"<info:fedora/islandora:pageCModel> ;"
            f"<info:fedora/fedora-system:def/relations-external#isMemberOf> "
            f"<info:fedora/{book}> ; "
            f"<http://islandora.ca/ontology/relsext#isPageNumber> ?page ; "
            f"<http://purl.org/dc/elements/1.1/title> ?title . }}"
        )
        test_results = requests.get(f"{self.base_url}&query={test_query}").content
        # print(test_results)
        return self.clean_pages(test_results)

    def get_compound_object_parts(self, compound_object):
        query = quote(
            f"""PREFIX fedora: <info:fedora/fedora-system:def/relations-external#>
            PREFIX fedoraModel: <info:fedora/fedora-system:def/model#>
            PREFIX islandora: <http://islandora.ca/ontology/relsext#>
            SELECT ?pid ?sequence ?model WHERE {{ 
            ?pid fedora:isConstituentOf <info:fedora/{compound_object}>;
            fedoraModel:hasModel ?model;
            islandora:isSequenceNumberOf{compound_object.replace(':', '_')} ?sequence . 
            FILTER(REGEX(STR(?model), "islandora")) . }}
            """
        )
        results = requests.get(f"{self.base_url}&query={query}").content
        print(self.clean_compound_parts(results))
        return self.clean_compound_parts(results)

    @staticmethod
    def clean_pages(results):
        all_pages = []
        cleaned = results.decode("utf-8").split("\n")
        for item in cleaned:
            if item != '"pid","page","title"' and item != "":
                all_pages.append(
                    {"pid": item.split(",")[0], "page": item.split(",")[1], "title": item.split(",")[2]}
                )
        return all_pages

    @staticmethod
    def clean_compound_parts(results):
        all_parts = []
        cleaned = results.decode("utf-8").split("\n")
        for item in cleaned:
            if item != '"pid","sequence","model"' and item != "":
                all_parts.append(
                    {
                        "pid": item.split(",")[0],
                        "sequence": item.split(",")[1],
                        "model": item.split(",")[2],
                    }
                )
        return all_parts

    @staticmethod
    def __lookup_work_type(work_type):
        work_types = {
            "book": "info:fedora/islandora:bookCModel",
            "image": "info:fedora/islandora:sp_basic_image",
            "large_image": "info:fedora/islandora:sp_large_image_cmodel",
            "compound": "info:fedora/islandora:compoundCModel",
            "audio": "info:fedora/islandora:sp-audioCModel",
            "video": "info:fedora/islandora:sp_videoCModel",
            "pdf": "info:fedora/islandora:sp_pdf",
            "page": "info:fedora/islandora:pageCModel",
            "binary": "info:fedora/islandora:binaryObjectCModel",
            "oral_history": "info:fedora/islandora:oralhistoriesCModel",
        }
        return work_types.get(work_type, "unknown")

    def get_works_based_on_type_and_collection(self, work_type, collection):
        iri = self.__lookup_work_type(work_type).strip()
        query = quote(
            f"PREFIX rels-ext: <info:fedora/fedora-system:def/relations-external#>"
            f"PREFIX model: <info:fedora/fedora-system:def/model#>"
            f"SELECT ?pid WHERE {{ ?pid rels-ext:isMemberOfCollection <info:fedora/{collection}> ;"
            f"model:hasModel <{iri}> ."
            f"}}"
        )
        results = requests.get(f"{self.base_url}&query={query}").content.decode("utf-8")
        return [
            result
            for result in results.split("\n")
            if result != "" and result != '"pid"'
        ]

    def get_policies_for_pages_in_book(self, book):
        query = quote(
            f"PREFIX system: <info:fedora/fedora-system:def/view#>"
            f"PREFIX rels-ext: <info:fedora/fedora-system:def/relations-external#>"
            f"PREFIX model: <info:fedora/fedora-system:def/model#>"
            f"SELECT ?pid WHERE {{"
            f"?pid system:disseminates ?o ;"
            f"rels-ext:isMemberOf <{book}> ;"
            f"model:hasModel <info:fedora/islandora:pageCModel> ."
            f"FILTER(REGEX(STR(?o), 'POLICY')).}}"
        )
        results = requests.get(f"{self.base_url}&query={query}").content.decode("utf-8")
        return [
            result
            for result in results.split("\n")
            if result != "" and result != '"pid"'
        ]

    def get_policies_based_on_type_and_collection(self, work_type, collection):
        iri = self.__lookup_work_type(work_type).strip()
        query = quote(
            f"PREFIX system: <info:fedora/fedora-system:def/view#>"
            f"PREFIX rels-ext: <info:fedora/fedora-system:def/relations-external#>"
            f"PREFIX model: <info:fedora/fedora-system:def/model#>"
            f"SELECT ?pid WHERE {{"
            f"?pid system:disseminates ?o ;"
            f"rels-ext:isMemberOfCollection <info:fedora/{collection}> ;"
            f"model:hasModel <{iri}> ."
            f"FILTER(REGEX(STR(?o), 'POLICY')).}}"
        )
        results = requests.get(f"{self.base_url}&query={query}").content.decode("utf-8")
        if work_type != "book":
            return [
                result
                for result in results.split("\n")
                if result != "" and result != '"pid"'
            ]
        else:
            all_policies_from_book = []
            books = [
                result
                for result in results.split("\n")
                if result != "" and result != '"pid"'
            ]
            for book in books:
                all_policies_from_book.append(book)
                all_policies_from_book.extend(self.get_policies_for_pages_in_book(book))
            return all_policies_from_book

    def get_parent_book(self, pid):
        query = quote(
            f"SELECT ?book FROM <#ri> WHERE {{"
            f"<info:fedora/{pid}> <http://islandora.ca/ontology/relsext#isPageOf> ?book ."
            f"}}"
        )
        results = requests.get(f"{self.base_url}&query={query}").content.decode("utf-8")
        return results.split("\n")[1]

    def get_page_number(self, pid):
        query = quote(
            f"SELECT ?page FROM <#ri> WHERE {{"
            f"<info:fedora/{pid}> <http://islandora.ca/ontology/relsext#isPageNumber> ?page ."
            f"}}"
        )
        results = requests.get(f"{self.base_url}&query={query}").content.decode("utf-8")
        return results.split("\n")[1]

    def find_all_collections(self):
        ignore = (
            "info:fedora/islandora:root",
            "info:fedora/islandora:sp_large_image_collection",
            "info:fedora/islandora:sp_basic_image_collection",
            "info:fedora/islandora:manuscriptCollection",
            "info:fedora/islandora:compound_collection",
            "info:fedora/islandora:transformCollection",
            "info:fedora/islandora:bookCollection",
            "info:fedora/islandora:binary_object_collection",
            "info:fedora/islandora:audio_collection",
            "info:fedora/islandora:sp_pdf_collection",
            "info:fedora/islandora:video_collection",
            "info:fedora/digital:collections",
            "info:fedora/ir:citationCollection",
            "info:fedora/islandora:oralhistories_collection",
            "info:fedora/collections:test",
            "info:fedora/collections:rftatest",
        )
        query = quote(
            "SELECT ?collection WHERE { ?collection <info:fedora/fedora-system:def/model#hasModel> <info:fedora/islandora:collectionCModel> . }"
        )
        results = requests.get(f"{self.base_url}&query={query}").content.decode("utf-8")
        return [
            result.replace("info:fedora/", "")
            for result in results.split("\n")
            if result != "" and result not in ignore and result != '"collection"'
        ]

    def get_works_of_a_type_with_dsid(self, work_type, dsid):
        query = quote(
            f"""PREFIX system: <info:fedora/fedora-system:def/view#>
            SELECT ?pid WHERE {{
            ?pid <info:fedora/fedora-system:def/model#hasModel> <{self.__lookup_work_type(work_type)}> ;
            system:disseminates ?dsid .
            FILTER(REGEX(STR(?dsid), "{dsid}"))
            }}"""
        )
        results = requests.get(f"{self.base_url}&query={query}").content.decode("utf-8")
        return [
            result.replace("info:fedora/", "")
            for result in results.split("\n")
            if result != "" and result != '"pid"'
        ]

    def find_pids_and_pages_from_book_local_id(self, local_id):
        query = quote(
            f"""
            SELECT ?pid ?page WHERE {{
            ?pid <info:fedora/fedora-system:def/relations-external#isMemberOf> ?book ;
            <http://islandora.ca/ontology/relsext#isPageNumber> ?page .
            ?book <http://purl.org/dc/elements/1.1/identifier> ?id .
            FILTER(REGEX(?id, "{local_id}"))
            }}
            """
        )
        results = requests.get(f"{self.base_url}&query={query}").content.decode("utf-8")
        return [
            (result.replace("info:fedora/", "").split(",")[0], result.split(',')[1])
            for result in results.split("\n")
            if result != "" and result != '"pid","page"'
        ]


if __name__ == "__main__":
    risearch = ResourceIndexSearch()
    x = risearch.get_works_of_a_type_with_dsid("book", "MODS")
