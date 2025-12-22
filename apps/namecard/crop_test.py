import os
from apps.namecard.service import NameCardProcessor
job_dir = r"E:\testdata\namecard_local_test_001"
image_path = r'E:\testdata\Receipt_2025-07-22_075811.jpg'

p = NameCardProcessor(job_dir, debug=True)
cards = p.segment_and_save(image_path)

print(f"Found {len(cards)} cards")
for c in cards:
    print(c)