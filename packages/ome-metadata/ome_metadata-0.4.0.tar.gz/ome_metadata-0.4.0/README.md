# ome-metadata

Open Microscopy XML metadata (https://www.openmicroscopy.org/Schemas/) as a collection of Rust structs and enums, with translation to Python.

## Rust
``` 
use std::fs::read_to_string;
use ome_metadata::Ome;

let xml = read_to_string($file)?;
let ome: Ome = xml.parse()?;
let image = &ome.image.unwrap()[0];
println!("acquisition date: {:#?}", image.acquisition_date);
```

## Python
```
from ome_metadata import Ome

with open($file) as f:
    xml = f.read()
ome = Ome.from_xml(xml)
image = ome.image[0]
print(f"acquisition date: {image.acquisition_date}")
```