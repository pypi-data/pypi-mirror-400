# libifcb
An optimised, native Python library for working with IFCB data. Implements lazy-loading wherever possible and maintains open file pointers for speedy access. Returns standard Pillow image objects for further processing.

## Example
```python
from libifcb import ROIReader
import json

sample = ROIReader("testdata/D20140117T003426_IFCB014.hdr", "testdata/D20140117T003426_IFCB014.adc", "testdata/D20140117T003426_IFCB014.roi")

print(json.dumps(sample.header, indent=4)) # We can read the header, with cleaned variable names, as a dictionary

for trigger in sample.triggers:
    print(json.dumps(trigger.raw, indent=4)) # We can also dump raw trigger data as dictionaries
print(str(len(sample1.rois)) + " ROIs") # How many actual ROIs did we get?

sample.rois[1899].image.save("testout/D20140117T003426_IFCB014_02177.png") # This list only contains valid ROIs - indexes will not match with other software!
sample.rows[2176].image.save("testout/D20140117T003426_IFCB014_02177.tiff") # ADC row indexes start from one, but we start from zero to be pythonic - This will return None types for 0-ROI triggers!
sample.triggers[2102].rois[0].image.save("testout/D20140117T003426_IFCB014_02177.jpeg") # As do trigger indexes, this is trigger #2103
```
