from libifcb import ROIReader
import json

sample1 = ROIReader("testdata/D20140117T003426_IFCB014.hdr", "testdata/D20140117T003426_IFCB014.adc", "testdata/D20140117T003426_IFCB014.roi")


print(str(len(sample1.rois)) + " ROIs in sample")

print("Bin header:")
print(json.dumps(sample1.header, indent=4))

image_by_roi_index = sample1.rois[1899].image
image_by_roi_index.save("testout/D20140117T003426_IFCB014_02177.png") # This list only contains valid ROIs - indexes will not match with other software!
image_by_adc_index = sample1.rows[2176].image
image_by_adc_index.save("testout/D20140117T003426_IFCB014_02177.tiff") # ADC row indexes start from one, but we start from zero to be pythonic
image_by_trigger_index = sample1.triggers[2102].rois[0].image
image_by_trigger_index.save("testout/D20140117T003426_IFCB014_02177.jpeg") # As do trigger indexes, this is trigger #2104

print("Trigger number for ROI #2177: " + str(sample1.rows[2176].trigger.index))
print("ROI number for trigger #2103: " + str(sample1.triggers[2102].rois[0].index))
print("Raw trigger data for ROI #2177: ")
trigger_data = sample1.rows[2176].trigger.raw
print(json.dumps(trigger_data, indent=4))

# All should match https://ifcb-data.whoi.edu/image?image=02177&bin=D20140117T003426_IFCB014

tests = {}

tests["1.a"] = (image_by_roi_index.width == 520)
tests["1.b"] = (image_by_roi_index.height == 628)
tests["1.c"] = (image_by_adc_index.width == 520)
tests["1.d"] = (image_by_adc_index.height == 628)
tests["1.e"] = (image_by_trigger_index.width == 520)
tests["1.f"] = (image_by_trigger_index.height == 628)

tests["2.a"] = (trigger_data["trigger_number"] == "2103")
tests["2.b"] = (trigger_data["roi_width"] == "520")
tests["2.c"] = (trigger_data["roi_height"] == "628")


passes = 0
total = len(tests.keys())
for key in tests.keys():
    if tests[key]:
        print("[PASS] Test " + key)
        passes += 1
    else:
        print("[FAIL] Test " + key)

print(str(passes) + "/" + str(total) + " tests passed")
