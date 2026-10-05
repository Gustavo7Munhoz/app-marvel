import os

files_to_fix = [
    r"app\src\main\res\layout\fragment_draft.xml",
    r"app\src\main\res\layout\fragment_match.xml",
    r"app\src\main\res\layout\fragment_dossier.xml",
    r"app\src\main\res\menu\bottom_nav_menu.xml",
    r"app\src\main\java\com\example\marvel\ui\match\MatchFragment.kt",
    r"app\src\main\java\com\example\marvel\ui\draft\DraftFragment.kt",
    r"app\src\main\java\com\example\marvel\ui\match\MatchViewModel.kt"
]

base_dir = r"C:\Users\gustavomunhoz-ieg\AndroidStudioProjects\Marvel"

replacements = {
    "IDENTIFICAǟO": "IDENTIFICAÇÃO",
    "IDENTIFICAǟO": "IDENTIFICAÇÃO",
    "ESQUADRO": "ESQUADRÃO",
    "ESQUADRǟO": "ESQUADRÃO",
    "ESQUADRÃƒO": "ESQUADRÃO",
    "ANLISE": "ANÁLISE",
    "ANÁLISE": "ANÁLISE", 
    "VNCULO": "VÍNCULO",
    "IN?CIO": "INÍCIO",
    "INCIO": "INÍCIO",
    "GNERO": "GÊNERO",
    "HISTRICO": "HISTÓRICO",
    "APARIES": "APARIÇÕES",
    "APARIÇÕÕS": "APARIÇÕES",
}

for f in files_to_fix:
    path = os.path.join(base_dir, f)
    if not os.path.exists(path): continue
    
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
            
        # Also let's just do a clean english to portuguese replacement again on the raw content
        # in case it was missed, and write it properly.
        
        content = content.replace("IDENTIFICA??O", "IDENTIFICAÇÃO")
        content = content.replace("ESQUADR??O", "ESQUADRÃO")
        
        # Hardcode the known lines that got messed up:
        content = content.replace('android:title="ESQUADR??O"', 'android:title="ESQUADRÃO"')
        content = content.replace('android:title="ESQUADRǟO"', 'android:title="ESQUADRÃO"')
        content = content.replace('android:title="IN?CIO"', 'android:title="INÍCIO"')
        content = content.replace('android:title="IN?CIO"', 'android:title="INÍCIO"')
        content = content.replace('android:title="VNCULO"', 'android:title="VÍNCULO"')
        
        content = content.replace('POR FAVOR, INSIRA SUA IDENTIFICAǟO', 'POR FAVOR, INSIRA SUA IDENTIFICAÇÃO')
        content = content.replace('POR FAVOR, INSIRA SUA IDENTIFICA??O', 'POR FAVOR, INSIRA SUA IDENTIFICAÇÃO')
        
        content = content.replace('CONFIRMAR ESQUADRǟO', 'CONFIRMAR ESQUADRÃO')
        content = content.replace('ESQUADRǟO SALVO', 'ESQUADRÃO SALVO')
        
        content = content.replace('AN?LISE DE COMPATIBILIDADE', 'ANÁLISE DE COMPATIBILIDADE')
        
        content = content.replace('G?NERO', 'GÊNERO')
        content = content.replace('HIST?RICO', 'HISTÓRICO')
        content = content.replace('APARI??ES', 'APARIÇÕES')

        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
            
        print(f"Fixed {f}")
    except Exception as e:
        print(f"Error on {f}: {e}")
