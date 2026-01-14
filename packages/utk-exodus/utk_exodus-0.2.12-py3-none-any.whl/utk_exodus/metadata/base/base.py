from lxml import etree
import xmltodict


class BaseProperty:
    def __init__(self, path, namespaces):
        self.path = path
        self.namespaces = namespaces
        self.root = etree.parse(path)
        self.root_as_str = etree.tostring(self.root)


class StandardProperty(BaseProperty):
    def __init__(self, path, namespaces):
        super().__init__(path, namespaces)

    def find(self, xpaths):
        all_values = []
        for xpath in xpaths:
            matches = self.root.xpath(xpath, namespaces=self.namespaces)
            for match in matches:
                if not xpath.endswith("@xlink:href") and match.text is not None:
                    all_values.append(match.text)
                elif xpath.endswith("@xlink:href"):
                    all_values.append(match)
        return all_values


class XMLtoDictProperty:
    def __init__(self, file):
        self.path = file
        self.namespaces = {
            "http://www.loc.gov/mods/v3": "mods",
            "http://www.w3.org/1999/xlink": "xlink",
        }
        self.doc = self.__get_doc(file)

    def __get_doc(self, path):
        with open(path) as fd:
            return xmltodict.parse(
                fd.read(), process_namespaces=True, namespaces=self.namespaces
            )
