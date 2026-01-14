import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

from .util import (
    get_root_of_xml, amount_of_elements, create_qgis_palette_tree, export_qml)

__all__ = [
    "qml2df"
]

def qml2df(fname: str) -> pd.DataFrame:
    root = get_root_of_xml(fname)
    assert amount_of_elements(root, 'colorPalette') == 1, \
        'only single palletes are currently implemented'

    # go through the QGIS style file
    for att in root.iter('colorPalette'):
        pallette = []
        for entry in att: pallette.append(entry.attrib)
        df = pd.DataFrame(pallette)
        if 'value' in df.columns: df = df.set_index('value')
    return df

def df2qml(df: pd.DataFrame,
           fname: str) -> None:

    tree = create_qgis_palette_tree(df)
    export_qml(tree, fname)
    return