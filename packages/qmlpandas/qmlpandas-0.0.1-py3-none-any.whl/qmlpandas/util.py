import os
import pandas as pd

from io import StringIO
from xml.etree import ElementTree

__all__ = [
    "get_root_of_xml",
    "amount_of_elements",
    "import_table_string",
]

HEADER_LINE = '<!DOCTYPE qgis PUBLIC ''http://mrcc.com/qgis.dtd'' ''SYSTEM''>'

# xml functions
def get_root_of_xml(fname: str) -> ElementTree:
    assert os.path.isfile(fname), \
        ('please provide correct path and file name')
    dom = ElementTree.parse(fname)
    root = dom.getroot()
    return root

def amount_of_elements(tree: ElementTree,
                       name: str) -> int:
    return [elem.tag for elem in tree.iter()].count(name)

def create_qgis_palette_tree(df: pd.DataFrame) -> ElementTree:
    # Create the file structure.
    qstyle = ElementTree.Element('qgis')
    qstyle.set('version', '1')

    rrender = ElementTree.SubElement(qstyle, 'rasterrenderer',
                                     opacity="1",
                                     alphaBand="0",
                                     band="1",
                                     type="paletted")

    palette = ElementTree.SubElement(rrender, 'colorPalette')
    # specify the palette
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        row_dict.update({'value': str(idx)})
        row_dict = {key: str(val) for key, val in row_dict.items()}
        entry = ElementTree.SubElement(palette, 'paletteEntry',
                                       **row_dict)
    return qstyle

def export_qml(qstyle: ElementTree,
               fout: str) -> None:
    # Write XML file.
    ElementTree.indent(qstyle)
    xml_str = ElementTree.tostring(qstyle, encoding='utf-8').decode('utf-8')
    with open(fout, 'w', encoding='utf-8') as f:
        f.write(f"{HEADER_LINE}\n")
        f.write(xml_str)
    return

# pandas functions
def import_table_string(table: str,
                        **kwargs)-> pd.DataFrame:
    column_index = kwargs.get('column_index', -1)
    delim = kwargs.get('delimiter', r",\s*")
    tbl = pd.read_csv(StringIO(table),
                      index_col=column_index,
                      sep=delim,
                      quotechar='"',
                      skipinitialspace=True,
                      engine='python')
    return tbl