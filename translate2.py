import os
import re

base_dir = r"C:\Users\gustavomunhoz-ieg\AndroidStudioProjects\Marvel\app\src\main\res\layout\fragment_dossier.xml"

replacements = {
    r'"CODENAME"': '"CODINOME"',
    r'"TRUE IDENTITY"': '"IDENTIDADE REAL"',
    r'"ORIGIN"': '"ORIGEM"',
    r'"GENDER"': '"GÊNERO"',
    r'"BIOGRAPHY / HISTORY"': '"BIOGRAFIA / HISTÓRICO"',
    r'"COMIC APPEARANCES"': '"APARIÇÕES EM QUADRINHOS"',
}

with open(base_dir, "r", encoding="utf-8") as f:
    content = f.read()

new_content = content
for old, new in replacements.items():
    new_content = re.sub(old, new, new_content)

with open(base_dir, "w", encoding="utf-8") as f:
    f.write(new_content)
    
print("Fixed dossier translations.")
