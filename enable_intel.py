import os

path = r"C:\Users\gustavomunhoz-ieg\AndroidStudioProjects\Marvel\app\src\main\res\menu\bottom_nav_menu.xml"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('android:enabled="false"', '')

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
