import os

fragments = [
    r"app\src\main\java\com\example\marvel\HomeFragment.kt",
    r"app\src\main\java\com\example\marvel\ui\draft\DraftFragment.kt",
    r"app\src\main\java\com\example\marvel\ui\battle\BattleFragment.kt",
    r"app\src\main\java\com\example\marvel\ui\match\MatchFragment.kt",
    r"app\src\main\java\com\example\marvel\ui\intel\IntelFragment.kt"
]

base_dir = r"C:\Users\gustavomunhoz-ieg\AndroidStudioProjects\Marvel"

on_create_code = """
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enterTransition = com.google.android.material.transition.MaterialFadeThrough()
        exitTransition = com.google.android.material.transition.MaterialFadeThrough()
    }
"""

for frag in fragments:
    path = os.path.join(base_dir, frag)
    if not os.path.exists(path):
        print(f"Not found: {path}")
        continue
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "MaterialFadeThrough" in content:
        print(f"Already injected in {frag}")
        continue
        
    # Inject onCreate after `class X : Fragment() {`
    # Note: we need to find the exact class definition
    class_def_idx = content.find("class ")
    if class_def_idx == -1:
        continue
        
    bracket_idx = content.find("{", class_def_idx)
    if bracket_idx != -1:
        new_content = content[:bracket_idx+1] + on_create_code + content[bracket_idx+1:]
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Injected in {frag}")

print("Done adding transitions.")
