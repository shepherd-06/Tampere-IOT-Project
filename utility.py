def process_attribute_name(attr_name):
    parts_to_remove = [
        "Päätaso",
        "Tampere (tilannekuva)",
        "Keskusta",
        "➞",
        "Koko alue",
        "use_seconds",
        "user_count",
        "visit_count"
    ]
    for part in parts_to_remove:
        attr_name = attr_name.replace(part, "")
    
    return "||".join([part.strip() for part in attr_name.split("➞") if part.strip()])
