import re
from pathlib import Path
import keyword

# Old fbs generator
class FBSGenerator:
    def __init__(self, dump_cs_filepath: Path, fbs_filepath: Path) -> None:
        self.dump_cs_filepath = dump_cs_filepath
        self.fbs_filepath = fbs_filepath

        self.python_keywords = set(keyword.kwlist)
        self.types = {'bool', 'byte', 'ubyte', 'int', 'uint', 'long', 'ulong', 'float', 'double', 'string'}

        # Regex to extract enum definitions from the C# dump.
        self.reEnum = re.compile(
            r"""// Namespace: FlatData
public enum (.{1,128}?) // TypeDefIndex: \d+?
{
	// Fields
	public (.+?) value__; // 0x0
(.+?)
}""",
            re.M | re.S,
        )
        self.reEnumField = re.compile(r'public const (.+?) (.+?) = (-?\d+?);')

        # Regex to extract struct definitions from the C# dump.
        self.reStruct = re.compile(
            r"""struct (.{0,128}?) :.{0,128}?IFlatbufferObject.{0,128}?
\{
(.+?)
\}
""",
            re.M | re.S,
        )
        self.reStructProperty = re.compile(r"""public (.+) (.+?) { get; }""")

    def _sanitize_enum_key(self, key: str) -> str:
        if key in self.python_keywords or key == 'None':
            #return f'{key}_'
            return f'{key}'
        return key

    def _write_enums_to_fbs(self, enums: dict, f) -> None:
        for name, enum in enums.items():
            # Create the comma-separated list of enum fields.
            enum_fields = ',\n    '.join(
                f'{self._sanitize_enum_key(key)} = {value}'
                for value, key in enum['fields'].items()
            )
            f.write(f'enum {name}: {enum["format"]}{{\n')
            f.write(f'    {enum_fields}\n')
            f.write('}\n\n')

    @staticmethod
    def _is_list_property(name: str) -> bool:
        return len(name) > 6 and name.endswith('Length')

    @staticmethod
    def _process_list_property(name: str, intern: str) -> tuple:
        list_name = name[:-6]
        pattern = f'public (.+?) {re.escape(list_name)}' + r'\(int j\) { }'
        if (match := re.search(pattern, intern)):
            return list_name, match[1], True
        return name, '', False

    @staticmethod
    def _remove_nullable(typ: str) -> str:
        return typ[9:-1] if typ.startswith('Nullable<') else typ

    def _process_property(self, name: str, typ: str, intern: str) -> tuple | None:
        if name == 'ByteBuffer':
            return None

        is_list = False
        if self._is_list_property(name):
            name, new_type, is_list = self._process_list_property(name, intern)
            typ = new_type or typ

        typ = self._remove_nullable(typ)
        if is_list:
            typ = f'[{typ}]'
        return name, typ

    def _extract_enums(self, data: str) -> dict:
        enums = {}
        for name, fmt, field_text in self.reEnum.findall(data):
            # Skip enums with a dot in the name (if any)
            if '.' in name:
                continue

            fields = {}
            for type_str, key, num in self.reEnumField.findall(field_text):
                # Use the numeric value as key and the field name as value.
                fields[int(num)] = key
            enums[name] = {'format': fmt, 'fields': fields}
        return enums

    def _extract_structs(self, data: str) -> dict:
        structs = {}
        for key, intern in self.reStruct.findall(data):
            properties = {}
            for prop in self.reStructProperty.finditer(intern):
                result = self._process_property(prop.group(2), prop.group(1), intern)
                if result is not None:
                    name, typ = result
                    properties[name] = typ
            if properties:
                structs[key] = properties
        return structs

    def _write_structs_to_fbs(self, structs: dict, enums: dict, f) -> None:
        for key, struct in structs.items():
            f.write(f'table {key}{{\n')
            for pname, ptype in struct.items():
                # If the property is a list type, adjust its type name.
                if ptype.startswith('['):
                    typ = ptype[1:-1]
                    if typ.endswith('Length'):
                        typ = typ[:-6]
                    '''
                    if pname in [typ, 'None'] or pname in self.python_keywords:
                        pname += '_'
                    '''
                    if typ not in structs and typ not in enums and typ not in self.types:
                        continue

                '''
                if pname in [ptype, 'None'] or pname in self.python_keywords:
                    pname += '_'
                '''
                ptype = ptype.replace('sbyte', 'ubyte')
                f.write(f'    {pname}: {ptype};\n')
            f.write('}\n\n')

    def generate_fbs(self) -> None:
        with open(self.dump_cs_filepath, 'rt', encoding='utf-8') as f:
            data = f.read()

        enums = self._extract_enums(data)
        structs = self._extract_structs(data)

        with open(self.fbs_filepath, 'wt', encoding='utf-8') as f:
            f.write('namespace FlatData;\n\n')
            self._write_enums_to_fbs(enums, f)
            self._write_structs_to_fbs(structs, enums, f)

        print(f"FBS file generated at: {self.fbs_filepath}")