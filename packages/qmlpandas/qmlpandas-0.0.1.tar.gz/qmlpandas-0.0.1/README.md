# qmlpandas

Simple parser to convert Q-GIS style file to a Pandas DataFrame, and vice-versa.

## Status 
Current styles implemented: 
* Color Palette

## Installation
The library can be installed via `pip`:
```bash 
pip install git+https://codeberg.org/baltena/qmlpandas
```

## Examples 

A simple qml-file for a color pallet looks like the following:

```xml 
<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="1">
<rasterrenderer opacity="1" alphaBand="0" band="1" type="paletted">
  <rasterTransparency/>
  <colorPalette>
	<paletteEntry color="#73df1f" label="name" alpha="255" value="1"/>
	<paletteEntry ... />
  </colorPalette>
</rasterrenderer>
</qgis>
```

In order to convert this to a pandas DataFrame one con do the following:

```python
from qmlpandas.parsing import qml2df

file_location = 'XYZ.qml'
df = qml2df(file_location)
```

Similarly a pandas DataFrame can be converted to a QGIS style file, as follows:

```python
import pandas as pd
from qmlpandas.parsing import df2qml

file_out = 'XYZ.qml'

df = pd.DataFrame([{"value": 1, "color":"#73df1f", "label": "A", "alpha": 255},
                   {"value": 2, "color":"#e89919", "label": "B", "alpha": 255}
                   ])
df = df.set_index('value')
df2qml(df, file_out)
```

For a color palette, the DataFrame should have the following structure:

```python
>>> df 
         color label  alpha
value                      
1      #73df1f     A    255
2      #e89919     B    255
```