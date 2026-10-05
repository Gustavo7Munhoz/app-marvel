import os
import re

base = r"C:\Users\gustavomunhoz-ieg\AndroidStudioProjects\Marvel\app\src\main\res\layout"

# Files to update - replace 'android:background="@color/shield_black"' in their headers with the rounded drawable
files = [
    "fragment_battle.xml",
    "fragment_draft.xml",
    "fragment_match.xml",
    "fragment_dossier.xml",
]

for fname in files:
    path = os.path.join(base, fname)
    if not os.path.exists(path):
        print(f"Not found: {fname}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace first occurrence of black header background with rounded one
    # The header LinearLayouts use android:background="@color/shield_black"
    new_content = content.replace(
        'android:background="@color/shield_black"',
        'android:background="@drawable/bg_header_rounded"',
        1  # Only replace the first occurrence (the header)
    )
    
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated: {fname}")
    else:
        print(f"No change (check manually): {fname}")
