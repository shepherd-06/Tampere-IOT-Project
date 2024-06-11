import re


def parse_attributes(attributes):
    pattern = re.compile(
        r"Kaleva sports park ➞ (Entire area|Whole area) ➞ (.*?) ➞")
    parsed_output = []
    for attribute in attributes:
        match = pattern.search(attribute['name'])
        if match:
            area = match.group(2)
            parsed_output.append(f"Kaleva sports park ({area})")
    return parsed_output
