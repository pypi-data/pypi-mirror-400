import yaml
import os
import csv
from tqdm import tqdm
from .base import BaseProperty, StandardProperty, XMLtoDictProperty
from utk_exodus.risearch import ResourceIndexSearch


class TitleProperty(BaseProperty):
    """
    Used for Titles.

    Handles the mapping of different types of titles based on the provided XML data.

    - If just `titleInfo/title`, map to dcterms:title.
    - If just `titleInfo[@supplied="yes"]/title`, map to dcterms:title.
    - If `titleInfo[@supplied="yes"]/title` and `titleInfo/title`, map the former to dcterms:title, and the latter to
      dcterms:alternative.
    - If `titleInfo/partName`, concat to `titleInfo/title` in dcterms:title with a `,`.
    - If `titleInfo/partNumber`, concat to `titleInfo[@supplied="yes"]` in dcterms:alternative.
    - If `titleInfo/nonSort`, concat to `titleInfo/title` in dcterms:title.
    - If `titleInfo[@type="alternative"]`, map to dcterms:alternative.
    """

    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)
        self.various_titles = self.__extract_titles()

    def __extract_titles(self):
        titles_data = {
            "plain": self.__get_titles_from_xpath(
                'mods:titleInfo[not(@supplied)][not(@type="alternative")]/mods:title'
            ),
            "supplied": self.__get_titles_from_xpath(
                "mods:titleInfo[@supplied]/mods:title"
            ),
            "part_names": self.__get_titles_from_xpath("mods:titleInfo/mods:partName"),
            "part_numbers": self.__get_titles_from_xpath(
                "mods:titleInfo/mods:partNumber"
            ),
            "non_sorts": self.__get_titles_from_xpath("mods:titleInfo/mods:nonSort"),
            "alternatives": self.__get_titles_from_xpath(
                'mods:titleInfo[@type="alternative"]/mods:title'
            ),
        }
        return titles_data

    def __get_titles_from_xpath(self, xpath_expr):
        # Retrieve text content based on the given xpath expression.
        return [
            element.text
            for element in self.root.xpath(xpath_expr, namespaces=self.namespaces)
        ]

    def find(self):
        """
        Handles the mapping of different types of titles based on the provided XML data.

        Returns:
            dict: A dictionary containing the mapped titles.

        Example:
             >>> titles = TitleProperty("tests/fixtures/utsmc_17870.xml", {"mods": "http://www.loc.gov/mods/v3"})
             >>> titles.find()
             ... #doctest: +NORMALIZE_WHITESPACE
             {'title': ['Prussian heroes march'], 'alternative_title': ['Prussian heroes: Prussen helden march']}
        """
        titles = []
        alternatives = []
        titles_data = self.various_titles

        # Handle supplied and plain titles mapping to dcterms:title and dcterms:alternative.
        if titles_data["supplied"] and titles_data["plain"]:
            titles.extend(titles_data["supplied"])
            alternatives.extend(titles_data["plain"])
        else:
            titles.extend(titles_data["supplied"] + titles_data["plain"])

        # Handle alternative titles mapping to dcterms:alternative.
        alternatives.extend(titles_data["alternatives"])

        return {"title": titles, "alternative_title": alternatives}


class RoleAndNameProperty(XMLtoDictProperty):
    def __init__(self, file):
        super().__init__(file)
        self.all_names = self.__find_all_names()

    def __find_all_names(self):
        if "mods:name" in self.doc["mods:mods"]:
            all_names = self.doc["mods:mods"]["mods:name"]
            if isinstance(all_names, list):
                return all_names
            elif isinstance(all_names, dict):
                return [all_names]
            elif isinstance(all_names, str):
                return [all_names]
            else:
                return ["Problem"]
        else:
            return []

    def find(self):
        """
        Find all names and roles in the XML file.

        Returns:
            dict: A dictionary containing the roles and names.

        Examples:
            >>> roles_and_names = RoleAndNameProperty("tests/fixtures/harp_1.xml")
            >>> roles_and_names.find()
            {'utk_composer': ['Swan, W. H. (William H.)', 'Swan, Marcus Lafayette'], 'utk_compiler': ['Swan, W. H. (William H.)', 'Swan, Marcus Lafayette']}
        """
        roles_and_names = {}
        for name in self.all_names:
            local_roles = []
            try:
                local_roles.append(
                    f"utk_{name['mods:role']['mods:roleTerm']['#text'].lower().replace(' ', '_')}"
                )
            except KeyError:
                print(name)
            # TODO: A name can have multiple roles
            except TypeError:
                for role in name["mods:role"]:
                    local_roles.append(
                        f"utk_{role['mods:roleTerm']['#text'].lower().replace(' ', '_')}"
                    )
            # TODO: Rework this.  It's not pretty but it works.
            name_value = name["mods:namePart"]
            for role in local_roles:
                if isinstance(name_value, list):
                    for part in name_value:
                        if isinstance(part, dict) and part.get("mods:namePart"):
                            if role not in roles_and_names:
                                roles_and_names[role] = [part["mods:namePart"]]
                            else:
                                roles_and_names[role].append([part["mods:namePart"]])
                        if isinstance(part, str) and not part.startswith("http"):
                            if role not in roles_and_names:
                                roles_and_names[role] = [part]
                            else:
                                roles_and_names[role].append(part)
                elif role not in roles_and_names and not name_value.startswith("http"):
                    roles_and_names[role] = [name_value]
                elif not name_value.startswith("http"):
                    roles_and_names[role].append(name_value)
        return roles_and_names


class NameProperty(XMLtoDictProperty):
    """
    Used for names.
    """

    def __init__(self, file):
        super().__init__(file)
        self.all_names = self.__find_all_names()

    def __find_all_names(self):
        if "mods:name" in self.doc["mods:mods"]:
            all_names = self.doc["mods:mods"]["mods:name"]
            if isinstance(all_names, list):
                return all_names
            elif isinstance(all_names, dict):
                return [all_names]
            elif isinstance(all_names, str):
                return [all_names]
            else:
                return ["Problem"]
        else:
            return []

    def find(self):
        """
        Find all names in the XML file.

        Returns:
            dict: A dictionary containing the names.

        Examples:
            >>> names = NameProperty("tests/fixtures/harp_1.xml")
            >>> names.find()
            {'composer': ['http://id.loc.gov/authorities/names/no2002022963', 'http://id.loc.gov/authorities/names/n78013127'], 'compiler': ['http://id.loc.gov/authorities/names/no2002022963', 'http://id.loc.gov/authorities/names/n78013127']}
        """
        roles_and_names = {}
        for name in self.all_names:
            roles = []
            local_roles = []
            try:
                if isinstance(name["mods:role"], list):
                    for role in name["mods:role"]:
                        if isinstance(role["mods:roleTerm"], list):
                            for role_term in role["mods:roleTerm"]:
                                if isinstance(role_term, dict) and "#text" in role_term:
                                    roles.append(
                                        role_term["#text"].lower().replace(" ", "_")
                                    )
                                    local_roles.append(
                                        f"utk_{role_term['#text'].lower().replace(' ', '_')}"
                                    )
                                elif isinstance(role_term, str):
                                    roles.append(role_term.lower().replace(" ", "_"))
                                    local_roles.append(
                                        f"utk_{role_term.lower().replace(' ', '_')}"
                                    )
                        elif isinstance(role["mods:roleTerm"], dict):
                            if "#text" in role["mods:roleTerm"]:
                                roles.append(
                                    role["mods:roleTerm"]["#text"].lower().replace(" ", "_")
                                )
                                local_roles.append(
                                    f"utk_{role['mods:roleTerm']['#text'].lower().replace(' ', '_')}"
                                )
                        elif isinstance(role["mods:roleTerm"], str):
                            roles.append(
                                role["mods:roleTerm"].lower().replace(" ", "_")
                            )
                            local_roles.append(
                                f"utk_{role['mods:roleTerm'].lower().replace(' ', '_')}"
                            )
                else:
                    if isinstance(name["mods:role"]["mods:roleTerm"], list):
                        for role_term in name["mods:role"]["mods:roleTerm"]:
                            if isinstance(role_term, dict) and "#text" in role_term:
                                roles.append(
                                    role_term["#text"].lower().replace(" ", "_")
                                )
                                local_roles.append(
                                    f"utk_{role_term['#text'].lower().replace(' ', '_')}"
                                )
                            elif isinstance(role_term, str):
                                roles.append(role_term.lower().replace(" ", "_"))
                                local_roles.append(
                                    f"utk_{role_term.lower().replace(' ', '_')}"
                                )
                    elif isinstance(name["mods:role"]["mods:roleTerm"], dict):
                        roles.append(
                            name["mods:role"]["mods:roleTerm"]["#text"]
                            .lower()
                            .replace(" ", "_")
                        )
                        local_roles.append(
                            f"utk_{name['mods:role']['mods:roleTerm']['#text'].lower().replace(' ', '_')}"
                        )
                    elif isinstance(name["mods:role"]["mods:roleTerm"], str):
                        roles.append(
                            name["mods:role"]["mods:roleTerm"].lower().replace(" ", "_")
                        )
                        local_roles.append(
                            f"utk_{name['mods:role']['mods:roleTerm'].lower().replace(' ', '_')}"
                        )
            except KeyError:
                print(name)
            # TODO: Rework this.  It's not pretty but it works.
            name_value = name["mods:namePart"]
            if "@valueURI" in name:
                name_value = name["@valueURI"]
            for role in roles:
                if isinstance(name_value, list):
                    for part in name_value:
                        if isinstance(part, dict) and "@valueURI" in part:
                            if role not in roles_and_names:
                                roles_and_names[role] = [part["@valueURI"]]
                            else:
                                roles_and_names[role].append([part["@valueURI"]])
                elif role not in roles_and_names and name_value.startswith("http"):
                    roles_and_names[role] = [name_value]
                elif name_value.startswith("http"):
                    roles_and_names[role].append(name_value)
            for role in local_roles:
                if isinstance(name_value, list):
                    for part in name_value:
                        if isinstance(part, str) and not part.startswith("http"):
                            if role not in roles_and_names:
                                roles_and_names[role] = [part]
                            else:
                                roles_and_names[role].append(part)
                elif role not in roles_and_names and not name_value.startswith("http"):
                    roles_and_names[role] = [name_value]
                elif not name_value.startswith("http"):
                    roles_and_names[role].append(name_value)
        return roles_and_names


class GeoNamesProperty(BaseProperty):
    """
    Handles the mapping of different types of geonames based on the provided XML data.

    Args:
        path (str): The path to the XML file.
        namespaces (dict): A dictionary containing the namespaces used in the XML file.
    """

    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self, name):
        """
        Find all geonames in the XML file.

        Args:
            name (str): The name of the geoname.

        Returns:
            dict: A dictionary containing the geoname mappings.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> geonames = GeoNamesProperty("tests/fixtures/webster_1127.xml", NAMESPACES)
            >>> geonames.find("spatial")
            {'spatial': ['http://sws.geonames.org/4050810', 'http://sws.geonames.org/4609260', 'http://id.loc.gov/authorities/subjects/sh85057008']}
        """
        uris = [
            uri.replace("about.rdf", "")
            for uri in self.root.xpath(
                "mods:subject/mods:geographic/@valueURI", namespaces=self.namespaces
            )
        ]
        lc_uris = [
            uri
            for uri in self.root.xpath(
                "mods:subject[mods:geographic]/@valueURI", namespaces=self.namespaces
            )
        ]
        all_values = []
        for uri in lc_uris:
            all_values.append(uri)
        for uri in uris:
            all_values.append(uri)
        return {name: all_values}


class PhysicalLocationsProperties(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def __find_repositories(self):
        with_repository_designation = [
            thing.text
            for thing in self.root.xpath(
                'mods:location/mods:physicalLocation[@displayLabel="Repository"]',
                namespaces=self.namespaces,
            )
        ]
        others = [
            thing.text
            for thing in self.root.xpath(
                "mods:location/mods:physicalLocation[not(@displayLabel)]",
                namespaces=self.namespaces,
            )
        ]
        all_repositories = []
        for value in with_repository_designation:
            all_repositories.append(value)
        for value in others:
            if value is None or "University of Tennesse" in value:
                all_repositories.append(
                    "University of Tennessee, Knoxville. Special Collections"
                )
            else:
                all_repositories.append(value)
        return all_repositories

    def find(self):
        """
        Find all locations properties in the XML file.

        Returns:
            dict: A dictionary containing location properties.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> physical_location = PhysicalLocationsProperties("tests/fixtures/civilwar_1438.xml", NAMESPACES)
            >>> physical_location.find()
            {'repository': ['University of Tennessee, Knoxville. Special Collections'], 'archival_collection': ['O. P. Temple Papers,1862']}
        """
        return {
            "repository": self.__find_repositories(),
            "archival_collection": self.__find_archival_collections(),
        }

    def __find_archival_collections(self):
        all_archival_collections = []
        other_archival_collections = [
            collection.text
            for collection in self.root.xpath(
                'mods:location/mods:physicalLocation[@displayLabel="Collection"]',
                namespaces=self.namespaces,
            )
        ]
        primary_archival_collections = [
            collection
            for collection in self.root.xpath(
                'mods:relatedItem[@displayLabel="Collection"][mods:titleInfo]',
                namespaces=self.namespaces,
            )
        ]
        for collection in other_archival_collections:
            if collection not in all_archival_collections:
                all_archival_collections.append(collection)
        for collection in primary_archival_collections:
            identifier = ""
            title = ""
            output = ""
            for child in collection:
                if child.tag == "{http://www.loc.gov/mods/v3}identifier":
                    identifier = child.text
                elif child.tag == "{http://www.loc.gov/mods/v3}titleInfo":
                    for sub_child in child:
                        if sub_child.tag == "{http://www.loc.gov/mods/v3}title":
                            title = sub_child.text
            if title != "" and identifier != "":
                output = f"{title}, {identifier}"
            elif identifier != "":
                output = identifier
            elif title != "":
                output = title
            if output != "":
                all_archival_collections.append(output)
        return all_archival_collections


class DataProvider(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        """
        Find all data providers in the XML file.

        Returns:
            dict: A dictionary containing data provider information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> dataProvider = DataProvider("tests/fixtures/egypt_224.xml", NAMESPACES)
            >>> dataProvider.find()
            {'provider': ['University of Tennessee, Knoxville. Libraries'], 'intermediate_provider': ['Frank H. McClung Museum of Natural History and Culture']}
        """
        values = [
            value.text
            for value in self.root.xpath(
                "mods:recordInfo/mods:recordContentSource", namespaces=self.namespaces
            )
        ]
        return {
            "provider": ["University of Tennessee, Knoxville. Libraries"],
            "intermediate_provider": [
                value
                for value in values
                if value != "University of Tennessee, Knoxville. Libraries"
            ],
        }


class MachineDate(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        """
        Find all machine date information in the XML file.

        Returns:
            dict: A dictionary containing machine date information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> machineDate = MachineDate("tests/fixtures/volvoices_2993.xml", NAMESPACES)
            >>> machineDate.find()
            {'date_created_d': ['1948-01'], 'date_issued_d': ['1948'], 'date_other_d': []}
        """
        date_created = [
            value.text
            for value in self.root.xpath(
                'mods:originInfo/mods:dateCreated[@encoding="edtf"]',
                namespaces=self.namespaces,
            )
        ]
        date_issued = [
            value.text
            for value in self.root.xpath(
                'mods:originInfo/mods:dateIssued[@encoding="edtf"]',
                namespaces=self.namespaces,
            )
        ]
        date_other = [
            value.text
            for value in self.root.xpath(
                'mods:originInfo/mods:dateOther[@encoding="edtf"]',
                namespaces=self.namespaces,
            )
        ]
        return {
            "date_created_d": self.__sort_if_range(date_created),
            "date_issued_d": self.__sort_if_range(date_issued),
            "date_other_d": self.__sort_if_range(date_other),
        }

    @staticmethod
    def __sort_if_range(values):
        if len(values) == 2 and None not in values:
            values.sort()
            return [f"{values[0]}/{values[1]}"]
        elif len(values) == 2:
            for value in values:
                if value is not None:
                    return [value]
        else:
            return values


class SubjectProperty(BaseProperty):
    """Get subjects from the MODS XML file."""

    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find_topic(self):
        """Find all topics in the XML file.

        Returns:
            dict: A dictionary containing topics information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> subjects = SubjectProperty("tests/fixtures/knoxgardens_125.xml", NAMESPACES)
            >>> subjects.find_topic()
            {'subject': ['http://id.loc.gov/authorities/subjects/sh85101348', 'http://id.loc.gov/authorities/subjects/sh85053123', 'http://id.loc.gov/authorities/subjects/sh85103022', 'http://id.loc.gov/authorities/subjects/sh2008120720']}

        """
        xpaths = [
            "mods:subject[mods:topic]/@valueURI",
            "mods:subject/mods:topic/@valueURI",
            "mods:subject[mods:name/mods:namePart]/@valueURI",
            "mods:subject/mods:name/@valueURI",
            'mods:genre[@authority="aat"]/@valueURI',
            'mods:genre[@authority="lcmpt"]/@valueURI',
            'mods:genre[@authority="lcsh"]/@valueURI',
        ]

        # Execute each XPath query and collect results
        return_values = []
        for xpath in xpaths:
            uris = self.root.xpath(xpath, namespaces=self.namespaces)
            return_values.extend(uri.strip() for uri in uris)

        return {"subject": return_values}


class KeywordProperty(BaseProperty):
    """Get keywords from the MODS XML file."""

    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find_topic(self):
        """Find all topics in the XML file.

        Returns:
            dict: A dictionary containing topics information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> keywords = KeywordProperty("tests/fixtures/civilwar_1438.xml", NAMESPACES)
            >>> keywords.find_topic()
            {'keyword': ['Jurisdiction -- Tennessee, East -- History -- Civil War, 1861-1865', 'Actions and defenses -- Tennessee, East -- History -- Civil War, 1861-1865', 'Tennessee, East -- Politics and government -- 19th century', 'Wallace, Jesse G. -- Correspondence', 'Temple, Oliver Perry, 1820-1907 -- Correspondence']}

        """
        non_uris_topics = [
            value.text
            for value in self.root.xpath(
                "mods:subject[not(@valueURI)]/mods:topic[not(@valueURI)]",
                namespaces=self.namespaces,
            )
        ]
        non_uris_names = [
            value.text
            for value in self.root.xpath(
                "mods:subject[not(@valueURI)]/mods:name[not(@valueURI)]/mods:namePart[not(@valueURI)]",
                namespaces=self.namespaces,
            )
        ]
        all_initial_values = [non_uris_topics, non_uris_names]
        return_values = []
        for iterable in all_initial_values:
            for value in iterable:
                return_values.append(value)
        return {"keyword": return_values}


class TypesProperties(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        """
        Find all types properties information in the XML file.

        Returns:
            dict: A dictionary containing types properties information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> types = TypesProperties("tests/fixtures/utsmc_17870.xml", NAMESPACES)
            >>> types.find()
            {'form': ['http://vocab.getty.edu/aat/300026430'], 'resource_type': ['http://id.loc.gov/vocabulary/resourceTypes/not', 'http://id.loc.gov/vocabulary/resourceTypes/txt'], 'form_local': []}
        """
        return {
            "form": self.__find_edm_has_type(),
            "resource_type": self.__find_dcterms_type(),
            "form_local": self.__find_local_form(),
        }

    def __find_dcterms_type(self):
        genre_uris = {
            "cartographic": "http://id.loc.gov/vocabulary/resourceTypes/car",
            "image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "notated music": "http://id.loc.gov/vocabulary/resourceTypes/not",
            "still image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "text": "http://id.loc.gov/vocabulary/resourceTypes/txt",
        }
        type_of_resource_uris = {
            "text": "http://id.loc.gov/vocabulary/resourceTypes/txt",
            "cartographic": "http://id.loc.gov/vocabulary/resourceTypes/car",
            "notated music": "http://id.loc.gov/vocabulary/resourceTypes/not",
            "sound recording-nonmusical": "http://id.loc.gov/vocabulary/resourceTypes/aun",
            "sound recording": "http://id.loc.gov/vocabulary/resourceTypes/aud",
            "still image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "moving image": "http://id.loc.gov/vocabulary/resourceTypes/mov",
            "three dimensional object": "http://id.loc.gov/vocabulary/resourceTypes/art",
        }
        # TODO: Works but messy!
        genre_to_dcterms_match_1 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[not(@*)][string() = 'cartographic']",
                namespaces=self.namespaces,
            )
        ]
        genre_to_dcterms_match_2 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[not(@*)][string() = 'notated music']",
                namespaces=self.namespaces,
            )
        ]
        genre_to_dcterms_match_3 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'image']",
                namespaces=self.namespaces,
            )
        ]
        genre_to_dcterms_match_4 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'still image']",
                namespaces=self.namespaces,
            )
        ]
        genre_to_dcterms_match_5 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'text']",
                namespaces=self.namespaces,
            )
        ]
        genre_to_dcterms_matches = (
            genre_to_dcterms_match_1,
            genre_to_dcterms_match_2,
            genre_to_dcterms_match_3,
            genre_to_dcterms_match_4,
            genre_to_dcterms_match_5,
        )
        type_of_resource_to_dcterms_type = [
            value.text
            for value in self.root.xpath(
                "mods:typeOfResource[not(@collection)]", namespaces=self.namespaces
            )
        ]
        type_of_resource_collection = [
            value.text
            for value in self.root.xpath(
                "mods:typeOfResource[@collection]", namespaces=self.namespaces
            )
        ]
        all_dcterms_types = []
        for matches in genre_to_dcterms_matches:
            for match in matches:
                if match in genre_uris:
                    all_dcterms_types.append(genre_uris[match])
        for value in type_of_resource_to_dcterms_type:
            if value in type_of_resource_uris:
                all_dcterms_types.append(type_of_resource_uris[value])

        if len(type_of_resource_collection) > 0:
            all_dcterms_types.append("http://id.loc.gov/vocabulary/resourceTypes/col")
        return all_dcterms_types

    def __find_edm_has_type(self):
        lcgft_genres = [
            uri
            for uri in self.root.xpath(
                'mods:genre[@authority="lcgft"]/@valueURI', namespaces=self.namespaces
            )
        ]
        form_uris = [
            uri
            for uri in self.root.xpath(
                "mods:physicalDescription/mods:form/@valueURI",
                namespaces=self.namespaces,
            )
        ]
        all_matches = [lcgft_genres, form_uris]
        return_values = []
        for match in all_matches:
            for value in match:
                return_values.append(value)
        return return_values

    def __find_local_form(self):
        form_no_uri = [
            value.text
            for value in self.root.xpath(
                "mods:physicalDescription/mods:form[not(@valueURI)][not(@type='material')]",
                namespaces=self.namespaces,
            )
        ]
        genre_strings = [
            value.text
            for value in self.root.xpath(
                "mods:genre[not(@*) and not(text()='cartographic') and not(text()='notated music')]",
                namespaces=self.namespaces,
            )
        ]
        all_matches = [form_no_uri, genre_strings]
        return_values = []
        for match in all_matches:
            for value in match:
                return_values.append(value)
        return return_values


class LocalTypesProperties(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        """
        Find all local types properties information in the XML file.

        Returns:
            dict: A dictionary containing local types properties information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> local_types = LocalTypesProperties("tests/fixtures/egypt_224.xml", NAMESPACES)
            >>> local_types.find()
            {'resource_type_local': ['still image'], 'form_local': ['platinum prints']}
        """
        return {
            "resource_type_local": self.__find_dcterms_type(),
            "form_local": self.__find_local_form(),
        }

    def __find_dcterms_type(self):
        genre_uris = {
            "cartographic": "http://id.loc.gov/vocabulary/resourceTypes/car",
            "image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "notated music": "http://id.loc.gov/vocabulary/resourceTypes/not",
            "still image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "text": "http://id.loc.gov/vocabulary/resourceTypes/txt",
        }
        type_of_resource_uris = {
            "text": "http://id.loc.gov/vocabulary/resourceTypes/txt",
            "cartographic": "http://id.loc.gov/vocabulary/resourceTypes/car",
            "notated music": "http://id.loc.gov/vocabulary/resourceTypes/not",
            "sound recording-nonmusical": "http://id.loc.gov/vocabulary/resourceTypes/aun",
            "sound recording": "http://id.loc.gov/vocabulary/resourceTypes/aud",
            "still image": "http://id.loc.gov/vocabulary/resourceTypes/img",
            "moving image": "http://id.loc.gov/vocabulary/resourceTypes/mov",
            "three dimensional object": "http://id.loc.gov/vocabulary/resourceTypes/art",
        }
        # TODO: Works but messy!
        genre_to_dcterms_match_1 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[not(@*)][string() = 'cartographic']",
                namespaces=self.namespaces,
            )
        ]
        genre_to_dcterms_match_2 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[not(@*)][string() = 'notated music']",
                namespaces=self.namespaces,
            )
        ]
        genre_to_dcterms_match_3 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'image']",
                namespaces=self.namespaces,
            )
        ]
        genre_to_dcterms_match_4 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'still image']",
                namespaces=self.namespaces,
            )
        ]
        genre_to_dcterms_match_5 = [
            value.text
            for value in self.root.xpath(
                "mods:genre[@authority = 'dct'][string() = 'text']",
                namespaces=self.namespaces,
            )
        ]
        genre_to_dcterms_matches = (
            genre_to_dcterms_match_1,
            genre_to_dcterms_match_2,
            genre_to_dcterms_match_3,
            genre_to_dcterms_match_4,
            genre_to_dcterms_match_5,
        )
        type_of_resource_to_dcterms_type = [
            value.text
            for value in self.root.xpath(
                "mods:typeOfResource[not(@collection)]", namespaces=self.namespaces
            )
        ]
        type_of_resource_collection = [
            value.text
            for value in self.root.xpath(
                "mods:typeOfResource[@collection]", namespaces=self.namespaces
            )
        ]
        all_dcterms_types = []
        for matches in genre_to_dcterms_matches:
            for match in matches:
                if match in genre_uris:
                    all_dcterms_types.append(match)
        for value in type_of_resource_to_dcterms_type:
            if value in type_of_resource_uris:
                all_dcterms_types.append(value)

        if len(type_of_resource_collection) > 0:
            all_dcterms_types.append("http://id.loc.gov/vocabulary/resourceTypes/col")
        return all_dcterms_types

    def __find_local_form(self):
        form_no_uri = [
            value.text
            for value in self.root.xpath(
                "mods:physicalDescription/mods:form[not(@type='material')]",
                namespaces=self.namespaces,
            )
        ]
        genre_strings = [
            value.text
            for value in self.root.xpath(
                "mods:genre[not(text()='cartographic') and not(text()='notated music')]",
                namespaces=self.namespaces,
            )
        ]
        all_matches = [form_no_uri, genre_strings]
        return_values = []
        for match in all_matches:
            for value in match:
                return_values.append(value)
        return return_values


class PublisherProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        """
        Find all publisher property information in the XML file.

        Returns:
            dict: A dictionary containing publisher property information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> publisher = PublisherProperty("tests/fixtures/playbills:1052.xml", NAMESPACES)
            >>> publisher.find()
            {'publisher': []}
        """
        return {
            "publisher": [
                uri
                for uri in self.root.xpath(
                    "mods:originInfo/mods:publisher/@valueURI",
                    namespaces=self.namespaces,
                )
            ]
        }


class RightsOrLicenseProperties(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        """
        Find all rights or liscense property information in the XML file.

        Returns:
            dict: A dictionary containing rights or license property information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> rights = RightsOrLicenseProperties("tests/fixtures/heilman:1010.xml", NAMESPACES)
            >>> rights.find()
            {'license': ['http://creativecommons.org/licenses/by-nc-nd/3.0/'], 'rights_statement': ['http://rightsstatements.org/vocab/InC/1.0/']}
        """
        final = {}
        rights = [
            uri
            for uri in self.root.xpath(
                'mods:accessCondition[not(@type="restriction on access")]/@xlink:href',
                namespaces=self.namespaces,
            )
            if "rightsstatements.org" in uri
        ]
        licenses = [
            uri.replace("https://", "http://")
            for uri in self.root.xpath(
                'mods:accessCondition[not(@type="restriction on access")]/@xlink:href',
                namespaces=self.namespaces,
            )
            if "creativecommons.org" in uri
        ]
        # If Rights, set.
        if len(rights) > 0:
            final["rights_statement"] = rights
        # If Licenses, set.
        if len(licenses) > 0:
            final["license"] = licenses
        # If no rights and a license, set a rights.
        if len(rights) == 0 and len(licenses) > 0:
            if licenses[0] == "http://creativecommons.org/publicdomain/zero/1.0/":
                final["rights_statement"] = [
                    "http://rightsstatements.org/vocab/NKC/1.0/"
                ]
            else:
                final["rights_statement"] = [
                    "http://rightsstatements.org/vocab/InC/1.0/"
                ]
        # If no rights and no license, set a rights.
        elif len(rights) == 0 and len(licenses) == 0:
            final["rights_statement"] = [
                "http://rightsstatements.org/vocab/CNE/1.0/"
            ]
        return final


class PublicationPlaceProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self):
        """
        Find all publication place property information in the XML file.

        Returns:
            dict: A dictionary containing publication place property information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> publication_place = PublicationPlaceProperty("tests/fixtures/volvoices_2495.xml", NAMESPACES)
            >>> publication_place.find()
            {'publication_place': ['http://id.loc.gov/authorities/names/n82063401']}
        """
        return {
            "publication_place": [
                uri
                for uri in self.root.xpath(
                    "mods:originInfo/mods:place/mods:placeTerm/@valueURI",
                    namespaces=self.namespaces,
                )
            ]
        }


class LanguageURIProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find_term(self):
        """
        Find all language URI properties in the XML file.

        Returns:
            dict: A dictionary containing language URI property information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> language_uri = LanguageURIProperty("tests/fixtures/utsmc:725.xml", NAMESPACES)
            >>> language_uri.find_term()
            {'language': ['http://id.loc.gov/vocabulary/iso639-2/fre', 'http://id.loc.gov/vocabulary/iso639-2/ita']}
        """
        terms_and_uris = {
            "English": "http://id.loc.gov/vocabulary/iso639-2/eng",
            "French": "http://id.loc.gov/vocabulary/iso639-2/fre",
            "German": "http://id.loc.gov/vocabulary/iso639-2/ger",
            "Italian": "http://id.loc.gov/vocabulary/iso639-2/ita",
            "Latin": "http://id.loc.gov/vocabulary/iso639-2/lat",
            "No linguistic content": "http://id.loc.gov/vocabulary/iso639-2/zxx",
            "Russian": "http://id.loc.gov/vocabulary/iso639-2/rus",
            "Spanish": "http://id.loc.gov/vocabulary/iso639-2/spa",
            "Swedish": "http://id.loc.gov/vocabulary/iso639-2/swe",
            "en": "http://id.loc.gov/vocabulary/iso639-2/eng",
        }
        language_terms = [
            value.text
            for value in self.root.xpath(
                "mods:language/mods:languageTerm", namespaces=self.namespaces
            )
        ]
        lanuage_uris = []
        for language in language_terms:
            if language in terms_and_uris:
                lanuage_uris.append(terms_and_uris[language])
        return {"language": lanuage_uris}


class ExtentProperty(BaseProperty):
    """
    Class to Handle Extent Information.

    Args:
        path (str): The path to the file.
        namespaces (dict): Namespaces to be used in the XPath queries.
    """

    def __init__(self, path: str, namespaces: dict):
        super().__init__(path, namespaces)

    def find(self):
        """
        Finds and returns a dictionary containing the extent information of a record.

        Returns:
            dict: A dictionary containing the extent information.

        Examples:
            >>> NAMESPACES = {
            ... 'mods': 'http://www.loc.gov/mods/v3',
            ... 'xlink': 'http://www.w3.org/1999/xlink' }
            >>> extent_property = ExtentProperty("tests/fixtures/knoxgardens_125.xml", NAMESPACES)
            >>> extent_property.find()
            {'extent': ['3 1/4 x 5 inches']}

        """
        extents_without_units = [
            text.text
            for text in self.root.xpath(
                "mods:physicalDescription/mods:extent[not(@unit)]",
                namespaces=self.namespaces,
            )
        ]

        extents_with_units = [
            f"{node.text} {node.attrib['unit']}"
            for node in self.root.xpath(
                "mods:physicalDescription/mods:extent[@unit]",
                namespaces=self.namespaces,
            )
            if node.text is not None and "unit" in node.attrib
        ]

        # Combine extents with and without units into a single list
        final_extent = extents_with_units + extents_without_units

        return {"extent": final_extent}


class MetadataMapping:
    def __init__(self, path_to_mapping, file_path, membership_details=None):
        self.path = path_to_mapping
        self.membership_details = membership_details
        self.fieldnames = []
        self.all_files = self.__get_all_files(file_path)
        self.mapping_data = yaml.safe_load(open(path_to_mapping, "r"))["mapping"]
        self.namespaces = {
            "mods": "http://www.loc.gov/mods/v3",
            "xlink": "http://www.w3.org/1999/xlink",
        }
        self.output_data = self.__execute(self.namespaces)

    @staticmethod
    def __get_all_files(path):
        all_files = []
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                all_files.append(os.path.join(root, name))
        return all_files

    def __execute(self, namespaces):
        all_file_data = []
        all_pages = []
        for file in tqdm(self.all_files):
            # TODO: Ultimately, parents should be populated based on relationship.
            model = self.__dereference_islandora_type(file)
            output_data = {
                "source_identifier": file.split("/")[-1]
                .replace("_MODS.xml", "")
                .replace(".xml", ""),
                "model": model,
                "sequence": "",
                "remote_files": "",
                "parents": " | ".join(
                    ResourceIndexSearch().get_parent_collections(
                        file.split("/")[-1].replace("_MODS.xml", "").replace(".xml", "")
                    ),
                ),
                "has_work_type": self.__get_utk_ontology_value(model),
                "primary_identifier": file.split("/")[-1]
                .replace("_MODS.xml", "")
                .replace(".xml", ""),
            }
            self.__dereference_islandora_type(file)
            for rdf_property in self.mapping_data:
                if "special" not in rdf_property:
                    final_values = ""
                    values = StandardProperty(file, namespaces).find(
                        rdf_property["xpaths"]
                    )
                    if len(values) > 0:
                        # TODO: Make delimeter configurable
                        final_values = " | ".join(values)
                    output_data[rdf_property["name"]] = final_values
                else:
                    special = self.__lookup_special_property(
                        rdf_property["special"], file, namespaces, rdf_property["name"]
                    )
                    for k, v in special.items():
                        # TODO: Make delimeter configurable
                        if v != [[]]:
                            try:
                                output_data[k] = " | ".join(v)
                            except TypeError:
                                print(f"{TypeError}: {file}")
            self.__find_unique_fieldnames(output_data)
            all_file_data.append(output_data)
        for item in all_file_data:
            pages = self.look_for_pages(item)
            parts = self.look_for_compound_parts(item)
            for page in pages:
                new_page = item.copy()
                new_page["source_identifier"] = page["pid"].replace("info:fedora/", "")
                new_page["parents"] = item["source_identifier"]
                new_page["model"] = "Page"
                new_page["sequence"] = page["page"]
                all_pages.append(new_page)
            for part in parts:
                new_part = item.copy()
                new_part["source_identifier"] = part["pid"].replace("info:fedora/", "")
                new_part["parents"] = item["source_identifier"]
                new_part["model"] = "Page"
                new_part["sequence"] = part["sequence"]
                all_pages.append(new_part)
        for page in all_pages:
            all_file_data.append(page)
        return all_file_data

    def look_for_pages(self, data):
        if data["model"] == "Book":
            return ResourceIndexSearch().find_pages_in_book(data["source_identifier"])
        return []

    def look_for_compound_parts(self, data):
        if data["model"] == "CompoundObject":
            return ResourceIndexSearch().get_compound_object_parts(data["source_identifier"])
        return []

    def __find_unique_fieldnames(self, data):
        for k, v in data.items():
            if k not in self.fieldnames:
                self.fieldnames.append(k)
        return

    def __dereference_islandora_type(self, file):
        islandora_types = {
            "info:fedora/islandora:sp-audioCModel": "Audio",
            "info:fedora/islandora:bookCModel": "Book",
            "info:fedora/islandora:compoundCModel": "CompoundObject",
            "info:fedora/islandora:binaryObjectCModel": "Generic",
            "info:fedora/islandora:sp_large_image_cmodel": "Image",
            "info:fedora/islandora:sp_basic_image": "Image",
            "info:fedora/islandora:sp_pdf": "Pdf",
            "info:fedora/islandora:sp_videoCModel": "Video",
        }
        x = ResourceIndexSearch().get_islandora_work_type(
            file.split("/")[-1]
            .replace("_MODS.xml", "")
            .replace(".xml", "")
            .replace("_", ":")
        )
        return islandora_types[x]

    @staticmethod
    def __get_utk_ontology_value(model):
        ontology_values = {
            "Audio": "https://ontology.lib.utk.edu/works#AudioWork",
            "Book": "https://ontology.lib.utk.edu/works#BookWork",
            "CompoundObject": "https://ontology.lib.utk.edu/works#CompoundObjectWork",
            "Generic": "https://ontology.lib.utk.edu/works#GenericWork",
            "Image": "https://ontology.lib.utk.edu/works#ImageWork",
            "Pdf": "https://ontology.lib.utk.edu/works#PDFWork",
            "Video": "https://ontology.lib.utk.edu/works#VideoWork",
        }
        return ontology_values[model]

    @staticmethod
    def __lookup_special_property(special_property, file, namespaces, name):
        if special_property == "TitleProperty":
            return TitleProperty(file, namespaces).find()
        elif special_property == "NameProperty":
            return NameProperty(file).find()
        elif special_property == "RoleAndNameProperty":
            return RoleAndNameProperty(file).find()
        elif special_property == "GeoNamesProperty":
            return GeoNamesProperty(file, namespaces).find(name)
        elif special_property == "DataProvider":
            return DataProvider(file, namespaces).find()
        elif special_property == "PhysicalLocationsProperties":
            return PhysicalLocationsProperties(file, namespaces).find()
        elif special_property == "SubjectProperty":
            return SubjectProperty(file, namespaces).find_topic()
        elif special_property == "KeywordProperty":
            return KeywordProperty(file, namespaces).find_topic()
        elif special_property == "TypesProperties":
            return TypesProperties(file, namespaces).find()
        elif special_property == "LocalTypesProperties":
            return LocalTypesProperties(file, namespaces).find()
        elif special_property == "LanguageURIProperty":
            return LanguageURIProperty(file, namespaces).find_term()
        elif special_property == "PublisherProperty":
            return PublisherProperty(file, namespaces).find()
        elif special_property == "PublicationPlaceProperty":
            return PublicationPlaceProperty(file, namespaces).find()
        elif special_property == "RightsOrLicenseProperties":
            return RightsOrLicenseProperties(file, namespaces).find()
        elif special_property == "ExtentProperty":
            return ExtentProperty(file, namespaces).find()
        elif special_property == "MachineDate":
            return MachineDate(file, namespaces).find()
        else:
            # Handle unknown special property
            raise ValueError(f"Unknown special property: {special_property}")

    def write_csv(self, filename):
        with open(filename, "w", newline="") as bulkrax_sheet:
            writer = csv.DictWriter(
                bulkrax_sheet, fieldnames=self.fieldnames, quoting=csv.QUOTE_MINIMAL
            )
            writer.writeheader()
            for data in self.output_data:
                writer.writerow(data)
        return
