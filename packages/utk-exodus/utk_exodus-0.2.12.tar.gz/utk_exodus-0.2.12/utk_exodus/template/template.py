import yaml
from csv import DictWriter


class ImportTemplate:
    def __init__(self, profile, model):
        self.profile = profile
        self.model = model
        self.loaded_m3 = yaml.safe_load(open(profile))
        self.headers = self.__get_all_properties()

    def __get_base_properties(self):
        return [
            "source_identifier",
            "model",
            "sequence",
            "remote_files",
            "parents",
            "visibility",
        ]

    def __get_all_properties(self):
        properties = self.__get_base_properties()
        for k, v in self.loaded_m3["properties"].items():
            if self.model in v["available_on"]["class"]:
                properties.append(k)
        return properties

    def add_cardinality(self):
        row = {}
        for k, v in self.loaded_m3["properties"].items():
            if self.model in v["available_on"]["class"]:
                row[k] = (
                    f"Minimum: {v['cardinality'].get('minimum', 0)} / Maximum: {v['cardinality'].get('maximum', 'n')}"
                )
                row[k] = (
                    f"{v['cardinality'].get('minimum', 0)}, {v['cardinality'].get('maximum', 'n')}"
                )
        return row

    def add_range(self):
        row = {}
        for k, v in self.loaded_m3["properties"].items():
            if self.model in v["available_on"]["class"]:
                row[k] = v.get("range").split("#")[-1]
        return row

    def add_guidelines(self):
        row = {}
        for k, v in self.loaded_m3["properties"].items():
            if self.model in v["available_on"]["class"]:
                if "usage_guidelines" in v:
                    row[k] = v.get("usage_guidelines").get("default", "")
                elif "definition" in v:
                    row[k] = v.get("definition").get("default", "")
                else:
                    row[k] = ""
        return row

    def write(self, filename):
        with open(filename, "w") as f:
            writer = DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
            writer.writerow(self.add_cardinality())
            writer.writerow(self.add_range())
            writer.writerow(self.add_guidelines())


if __name__ == "__main__":
    it = ImportTemplate("tmp/m3.yml", "Image")
    it.write("full_template.csv")
