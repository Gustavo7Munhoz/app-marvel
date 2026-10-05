import os
import re

path = r"C:\Users\gustavomunhoz-ieg\AndroidStudioProjects\Marvel\app\src\main\res\layout\fragment_battle.xml"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace header
content = content.replace("COMBAT SIMULATION", "SIMULAÇÃO DE COMBATE")
content = content.replace("MARVEL BATTLE", "SIMULADOR DE BATALHA")

# Remove search inputs block entirely and replace with a simple button
# We look for <!-- SEARCH INPUTS --> down to the end of the LinearLayout that holds it and the button
pattern = r"<!-- SEARCH INPUTS -->.*?INITIATE SIMULATION.*?</com\.google\.android\.material\.button\.MaterialButton>"
replacement = """<!-- CONFRONTO -->
        <com.google.android.material.button.MaterialButton
            android:id="@+id/btnCompare"
            android:layout_width="match_parent"
            android:layout_height="64dp"
            android:layout_margin="16dp"
            android:text="INTERCEPTAR VILÃO (SQUAD ALEATÓRIO)"
            android:textColor="@color/shield_black"
            android:textSize="14sp"
            android:textStyle="bold"
            app:backgroundTint="@color/shield_cyan_glow"
            app:cornerRadius="4dp" />
"""
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Translate stats
content = content.replace("INTELLIGENCE", "INTELIGÊNCIA")
content = content.replace("STRENGTH", "FORÇA")
content = content.replace("SPEED", "VELOCIDADE")
content = content.replace("DURABILITY", "DURABILIDADE")
content = content.replace("POWER", "PODER")
content = content.replace("COMBAT", "COMBATE")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated fragment_battle.xml")
