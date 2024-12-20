# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import re
import sys
import os

class ConfigTranslator:
    def __init__(self):
        self.constants = {}

    def parse_xml(self, xml_input):
        try:
            return ET.fromstring(xml_input)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")

    def translate(self, xml_element, indent=0):
        if xml_element.tag == "config":
            return "\n".join(self.translate(child, indent) for child in xml_element)
        elif xml_element.tag == "list":
            return self.translate_list(xml_element, indent)
        elif xml_element.tag == "dict":
            return self.translate_dict(xml_element, indent)
        elif xml_element.tag == "constant":
            return self.translate_constant(xml_element, indent)
        elif xml_element.tag == "value":
            return xml_element.text.strip() if xml_element.text else ""
        elif xml_element.tag == "reference":
            return self.translate_reference(xml_element)
        elif xml_element.tag == "comment":
            return f"{' ' * indent}:: {xml_element.text.strip() if xml_element.text else ''}"
        else:
            raise ValueError(f"Unknown tag: {xml_element.tag}")

    def translate_list(self, xml_element, indent):
        values = []
        for child in xml_element:
            if child.tag == "comment":
                values.append(self.translate(child, indent + 4))
            else:
                values.append(self.translate(child, indent + 4))
        inner_content = "\n".join(values)
        return f"{'' * indent}(list\n{inner_content}\n{' ' * indent})"

    def translate_dict(self, xml_element, indent):
        entries = []
        for child in xml_element:
            if child.tag == "comment":
                entries.append(self.translate(child, indent + 4))
            elif child.tag == "entry":
                key = child.get("name")
                if not key:
                    raise ValueError("Missing 'name' attribute in <entry>")
                value = self.translate(child[0], indent + 4) if len(child) > 0 else ""
                entries.append(f"{' ' * (indent + 4)}{key} = {value};")
            else:
                raise ValueError(f"Invalid dictionary entry: {child.tag}")
        inner_content = "\n".join(entries)
        return f"{'' * indent}@{{\n{inner_content}\n{'' * indent}}}"

    def translate_constant(self, xml_element, indent):
        name = xml_element.get("name")
        if not name or not re.match(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
            raise ValueError(f"Invalid constant name: {name}")
        value = self.translate(xml_element[0], indent + 4) if len(xml_element) > 0 else ""
        self.constants[name] = value
        return f"{' ' * indent}{name} <- {value};"

    def translate_reference(self, xml_element):
        name = xml_element.get("name")
        if not name:
            raise ValueError("Missing 'name' attribute in <reference>")
        return f"${name}$"

    def resolve_constants(self, config_text):
        def replace_constant(match):
            name = match.group(1)
            if name not in self.constants:
                raise ValueError(f"Undefined constant: {name}")
            return self.constants[name]
        return re.sub(r"\$([a-zA-Z_][a-zA-Z0-9_]*)\$", replace_constant, config_text)

    def translate_and_resolve(self, xml_input):
        root = self.parse_xml(xml_input)
        translated = self.translate(root)
        return self.resolve_constants(translated)

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("Usage: python transformer.py <input_file.xml> [output_file.txt]")
            sys.exit(1)

        input_file = sys.argv[1]
        if not os.path.exists(input_file):
            print(f"Error: File '{input_file}' does not exist.")
            sys.exit(1)

        with open(input_file, 'r', encoding='utf-8') as file:
            xml_input = file.read()

        translator = ConfigTranslator()
        result = translator.translate_and_resolve(xml_input)

        output_file = "output.txt" if len(sys.argv) < 3 else sys.argv[2]
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(result)

        print(f"Translation complete. Output written to: {output_file}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)