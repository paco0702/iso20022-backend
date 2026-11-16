import re

def clean_up_xml_content(xml_content: str) -> str:
    return re.sub(r'>\s+<', '><', xml_content.strip().replace('\n', '').replace('\r', ''))