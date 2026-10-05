import os
import re

base_dir = r"C:\Users\gustavomunhoz-ieg\AndroidStudioProjects\Marvel\app\src\main"

replacements = {
    # fragment_home.xml
    r"Search database\.\.\.": "Pesquisar arquivo...",
    r"NO RECORDS MATCHING QUERY\.": "NENHUM OPERATIVO ENCONTRADO.",
    
    # fragment_draft.xml
    r"SQUAD ASSEMBLY PROTOCOL": "PROTOCOLO DE RECRUTAMENTO",
    r"Search operatives\.\.\.": "Buscar operativos...",
    r"OPERATIVES SELECTED:": "OPERATIVOS SELECIONADOS:",
    r"CONFIRM SQUAD": "CONFIRMAR ESQUADRÃO",
    
    # fragment_match.xml
    r"BIOMETRIC OPERATIVE MATCH": "ANÁLISE DE COMPATIBILIDADE",
    r"ENTER AGENT DESIGNATION:": "INSIRA SUA IDENTIFICAÇÃO:",
    r"E\.g\., Agent Coulson": "Ex: Agente Romanoff",
    r"INITIATE BIOMETRIC MATCH": "INICIAR RASTREAMENTO",
    r"SCANNING DATABASES\.\.\.": "BUSCANDO NO BANCO DE DADOS...",
    r"MATCH FOUND": "VÍNCULO ENCONTRADO",
    r"COMPATIBILITY: 99\.8%": "COMPATIBILIDADE: 99.8%",
    r"NEW SCAN": "NOVO RASTREAMENTO",
    
    # fragment_dossier.xml
    r">CODENAME<": ">CODINOME<",
    r">TRUE IDENTITY<": ">IDENTIDADE REAL<",
    r">ORIGIN<": ">ORIGEM<",
    r">GENDER<": ">GÊNERO<",
    r">BIOGRAPHY / HISTORY<": ">BIOGRAFIA / HISTÓRICO<",
    r">COMIC APPEARANCES<": ">APARIÇÕES EM QUADRINHOS<",
    
    # bottom_nav_menu.xml
    r'"BATTLE"': '"BATALHA"',
    r'"DRAFT"': '"ESQUADRÃO"',
    r'"HOME"': '"INÍCIO"',
    r'"MATCH"': '"SINTONIA"',
    r'"INTEL"': '"ARQUIVOS"',
    
    # DraftFragment.kt
    r"SQUAD SAVED:": "ESQUADRÃO SALVO:",
    
    # MatchFragment.kt
    r"PLEASE ENTER DESIGNATION": "POR FAVOR, INSIRA SUA IDENTIFICAÇÃO",
    
    # MatchViewModel.kt
    r"No match found in databases\.": "Nenhum vínculo encontrado no banco de dados.",
}

for root, _, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".xml") or file.endswith(".kt"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = content
            for old, new in replacements.items():
                new_content = re.sub(old, new, new_content)
                
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated: {file}")

print("Done translations.")
