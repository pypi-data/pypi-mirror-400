import xml.etree.ElementTree as ET
import csv
from tqdm import tqdm
import os


class Restrictions:
    def __init__(self, policy):
        self.policy = policy
        self.ns = {"xacml": "urn:oasis:names:tc:xacml:1.0:policy"}
        self.root = self.__parse(policy)

    @staticmethod
    def __parse(policy):
        tree = ET.parse(policy)
        return tree.getroot()

    def find_rules(self):
        rules = []
        for rule in self.root.findall(".//xacml:Rule", self.ns):
            rule_id = rule.get("RuleId")
            effect = rule.get("Effect")
            rules.append((rule_id, effect))
        return rules

    def find_restricted_datastreams(self):
        restricted_datastreams = []
        for rule in self.root.findall(
            './/xacml:Rule[@RuleId="deny-dsid-mime"]', self.ns
        ):
            for resource in rule.findall(".//xacml:Resource", self.ns):
                dsid = resource.find(".//xacml:AttributeValue", self.ns).text
                restricted_datastreams.append(dsid)
        return restricted_datastreams

    def find_objects_only_accessible_by_certain_users(self):
        users_with_access = []
        for rule in self.root.findall(
            './/xacml:Rule[@RuleId="deny-access-functions"]', self.ns
        ):
            for condition in rule.findall(
                './/xacml:Condition[@FunctionId="urn:oasis:names:tc:xacml:1.0:function:not"]',
                self.ns,
            ):
                for apply in condition.findall(
                    './/xacml:Apply[@FunctionId="urn:oasis:names:tc:xacml:1.0:function:string-at-least-one-member-of"]',
                    self.ns,
                ):
                    users_with_access.append(
                        apply.find(".//xacml:AttributeValue", self.ns).text
                    )
        return users_with_access

    def determine_if_work_restricted(self):
        if len(self.find_objects_only_accessible_by_certain_users()) > 0:
            return True
        return False

    def get(self):
        return {
            "work_restricted": self.determine_if_work_restricted(),
            "restricted_datastreams": self.find_restricted_datastreams(),
        }


class RestrictionsSheet:
    def __init__(self, original_sheet, policies_location):
        self.original_sheet = original_sheet
        self.policies_location = policies_location
        self.original_as_dict = self.__read(original_sheet)
        self.headers = self.__get_headers()
        self.rows_with_visibility = self.add_visibility()

    @staticmethod
    def __read(csv_file):
        csv_content = []
        with open(csv_file, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_content.append(row)
        return csv_content

    def __get_headers(self):
        original_headers = [k for k, v in self.original_as_dict[0].items()]
        original_headers.append("visibility")
        return original_headers

    def add_visibility(self):
        new_csv_content = []
        for row in tqdm(self.original_as_dict):
            pid = row["source_identifier"].split("_")[0]
            datastream = None
            visibility = "open"
            if len(row["source_identifier"].split("_")) > 1:
                datastream = row["source_identifier"].split("_")[1]
            if os.path.exists(f"{self.policies_location}/{pid}_POLICY.xml"):
                restrictions = Restrictions(
                    f"{self.policies_location}/{pid}_POLICY.xml"
                ).get()
                if restrictions["work_restricted"]:
                    visibility = "restricted"
                elif datastream in restrictions["restricted_datastreams"]:
                    visibility = "restricted"
            current_data = {}
            for k, v in row.items():
                current_data[k] = v
            current_data["visibility"] = visibility
            new_csv_content.append(current_data)
        return new_csv_content

    def write_csv(self, filename):
        with open(filename, "w", newline="") as bulkrax_sheet:
            writer = csv.DictWriter(bulkrax_sheet, fieldnames=self.headers)
            writer.writeheader()
            for data in self.rows_with_visibility:
                writer.writerow(data)
        return


