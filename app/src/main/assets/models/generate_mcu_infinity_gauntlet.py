import bpy
import bmesh
import math
import os
import sys

print("=========================================================")
print("MODELAGEM DA AUTÊNTICA MANOPLA DO THANOS (MCU INFINITY WAR)")
print(f"Versão do Blender: {bpy.app.version_string}")
print("=========================================================")

# Diretórios
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RES_DRAWABLE = os.path.join(MAIN_DIR, "res", "drawable-nodpi")
USER_DOCS_BLENDER = os.path.expanduser(r"~\Documents\Blender")
PROJECT_ROOT = os.path.abspath(os.path.join(MAIN_DIR, "..", ".."))

os.makedirs(RES_DRAWABLE, exist_ok=True)
os.makedirs(USER_DOCS_BLENDER, exist_ok=True)

# Reset da cena
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Configuração de Render (Cycles com Denoising para vidro e ouro fotorrealistas)
scene.render.engine = 'CYCLES'
try:
    scene.cycles.device = 'GPU'
except:
    scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.resolution_x = 420
scene.render.resolution_y = 420

# Coleção
col = bpy.data.collections.new("MCU_Infinity_Gauntlet")
scene.collection.children.link(col)

# -------------------------------------------------------------------------
# 1. MATERIAIS PBR DE NÍVEL CINEMATOGRÁFICO
# -------------------------------------------------------------------------
def create_gold_uru_material():
    mat = bpy.data.materials.new("Mat_Uru_Gold_Cinematic")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Ouro quente envelhecido de Nidavellir
    bsdf.inputs['Base Color'].default_value = (0.88, 0.63, 0.16, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.96
    bsdf.inputs['Roughness'].default_value = 0.22
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.8
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.8

    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_dark_metal_material():
    mat = bpy.data.materials.new("Mat_Dark_Armor_Joints")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.12, 0.11, 0.10, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.40

    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_gem_material(name, gem_color, emission_strength=5.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    emit = nodes.new('ShaderNodeEmission')
    mix = nodes.new('ShaderNodeMixShader')

    # Cristal com alta refração e transmissão (estilo joia facetada lapidada)
    bsdf.inputs['Base Color'].default_value = gem_color
    bsdf.inputs['Roughness'].default_value = 0.03
    bsdf.inputs['IOR'].default_value = 1.77
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.94
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.94

    emit.inputs['Color'].default_value = gem_color
    emit.inputs['Strength'].default_value = emission_strength

    mix.inputs['Fac'].default_value = 0.35
    mat.node_tree.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    mat.node_tree.links.new(emit.outputs['Emission'], mix.inputs[2])
    mat.node_tree.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return mat

mat_gold = create_gold_uru_material()
mat_dark = create_dark_metal_material()

# 6 Joias
mat_gem_mind = create_gem_material("Mat_Mind", (1.0, 0.82, 0.0, 1.0), 6.0)     # Amarelo Mente
mat_gem_power = create_gem_material("Mat_Power", (0.65, 0.05, 0.98, 1.0), 5.5)  # Roxo Poder
mat_gem_space = create_gem_material("Mat_Space", (0.05, 0.55, 1.0, 1.0), 5.5)   # Azul Espaço
mat_gem_reality = create_gem_material("Mat_Reality", (1.0, 0.03, 0.05, 1.0), 5.5) # Vermelho Realidade
mat_gem_time = create_gem_material("Mat_Time", (0.05, 1.0, 0.30, 1.0), 5.5)    # Verde Tempo
mat_gem_soul = create_gem_material("Mat_Soul", (1.0, 0.45, 0.02, 1.0), 5.5)    # Laranja Alma

# -------------------------------------------------------------------------
# 2. HIERARQUIA E CONSTRUÇÃO DA GEOMETRIA
# -------------------------------------------------------------------------
root = bpy.data.objects.new("Infinity_Gauntlet_MCU", None)
col.objects.link(root)

def finish_mesh_object(name, bm, material, parent=root, smooth=True, subsurf=False):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
            
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(material)
    col.objects.link(obj)
    if parent:
        obj.parent = parent
        
    if subsurf:
        sub = obj.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = 1
        sub.render_levels = 1

    return obj

# 2.1 ANTEBRAÇO ROBUSTO ESCULPIDO (Forearm Armor)
# Perfil chanfrado com placas sobrepostas
bm_arm = bmesh.new()
layers = [
    # (Z, Raio X, Raio Y, Offset Y)
    (-2.4, 0.70, 0.54, 0.05),
    (-2.1, 0.75, 0.58, 0.04),
    (-1.6, 0.72, 0.56, 0.02),
    (-1.2, 0.68, 0.54, 0.00),
    (-0.8, 0.64, 0.50, -0.02),
    (-0.55, 0.60, 0.47, -0.03)
]
segs = 20
ring_verts = []
for z, rx, ry, off_y in layers:
    ring = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        # Contorno anatômico com crista superior e base mais plana
        x = rx * math.cos(ang)
        y = ry * math.sin(ang) + off_y
        if y < 0: # lado da palma
            y *= 0.90
        ring.append(bm_arm.verts.new((x, y, z)))
    ring_verts.append(ring)

for r in range(len(layers) - 1):
    r1 = ring_verts[r]
    r2 = ring_verts[r + 1]
    for i in range(segs):
        ni = (i + 1) % segs
        bm_arm.faces.new([r1[i], r1[ni], r2[ni], r2[i]])
bm_arm.faces.new(ring_verts[0]) # tampa inferior
obj_arm = finish_mesh_object("Gauntlet_Forearm", bm_arm, mat_gold, subsurf=True)

# 2.2 BRACELETE DE PULSO ARTICULADO (Wrist Cuffs)
bm_wrist = bmesh.new()
w_layers = [
    (-0.55, 0.63, 0.49),
    (-0.42, 0.66, 0.52),
    (-0.30, 0.62, 0.48)
]
w_rings = []
for z, rx, ry in w_layers:
    ring = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        ring.append(bm_wrist.verts.new((rx * math.cos(ang), ry * math.sin(ang), z)))
    w_rings.append(ring)

for r in range(len(w_layers) - 1):
    for i in range(segs):
        ni = (i + 1) % segs
        bm_wrist.faces.new([w_rings[r][i], w_rings[r][ni], w_rings[r+1][ni], w_rings[r+1][i]])
finish_mesh_object("Gauntlet_Wrist_Cuff", bm_wrist, mat_gold, subsurf=True)

# Frisos pretos/bronze entre as juntas do pulso
bm_w_trim = bmesh.new()
bmesh.ops.create_cone(bm_w_trim, cap_ends=True, cap_tris=False, segments=20,
                      radius1=0.64, radius2=0.64, depth=0.08)
for v in bm_w_trim.verts:
    v.co.z -= 0.42
    v.co.y *= 0.85
finish_mesh_object("Gauntlet_Wrist_JointTrim", bm_w_trim, mat_dark)

# 2.3 DORSO DA MÃO (Hand Dorsal Plate & Palm)
# Placa central larga, esculpida, com curvatura para as 4 juntas
bm_hand = bmesh.new()
h_layers = [
    # (Z, Raio X, Raio Y, Offset Y)
    (-0.30, 0.62, 0.47, 0.0),
    (-0.10, 0.68, 0.46, 0.02),  # nível do polegar
    ( 0.15, 0.72, 0.44, 0.03),  # centro do dorso (onde fica a joia da mente)
    ( 0.45, 0.70, 0.40, 0.04),  # base dos engastes dos nós dos dedos
]
h_rings = []
for z, rx, ry, off_y in h_layers:
    ring = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        x = rx * math.cos(ang)
        y = ry * math.sin(ang) + off_y
        ring.append(bm_hand.verts.new((x, y, z)))
    h_rings.append(ring)

for r in range(len(h_layers) - 1):
    for i in range(segs):
        ni = (i + 1) % segs
        bm_hand.faces.new([h_rings[r][i], h_rings[r][ni], h_rings[r+1][ni], h_rings[r+1][i]])
bm_hand.faces.new(h_rings[-1]) # fecha topo
finish_mesh_object("Gauntlet_Hand_Body", bm_hand, mat_gold, subsurf=True)

# 2.4 PLACA DE ENGRENAGEM E ENERGIA DO DORSO (Ornate Mind Bezel Housing)
# Base ornamentada esculpida na armadura para a Joia da Mente
bm_housing = bmesh.new()
bmesh.ops.create_cone(bm_housing, cap_ends=True, cap_tris=False, segments=16,
                      radius1=0.26, radius2=0.21, depth=0.10)
for v in bm_housing.verts:
    # Achata em Y e inclina para acompanhar a curvatura do dorso
    v.co.x *= 1.25
    v.co.y = -0.45 + v.co.z * 0.25
    v.co.z = 0.15 + v.co.y * 0.1
finish_mesh_object("Housing_MindStone", bm_housing, mat_dark, subsurf=True)

# 2.5 FUNÇÃO PARA CRIAR GEMA CABOCHÃO OVAL LAPIDADA (Faceted Cabochon Gem)
def create_cabochon_gem(name, loc, size_x, size_y, size_z, material, rot=(0,0,0)):
    bm_g = bmesh.new()
    # Malha de cabochão abobadado lapidado
    segs = 16
    # Anel base
    base_v = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        base_v.append(bm_g.verts.new((size_x * 0.85 * math.cos(ang), size_y * 0.85 * math.sin(ang), 0.0)))
    
    # Anel intermediário (cintura)
    mid_v = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        mid_v.append(bm_g.verts.new((size_x * math.cos(ang), size_y * math.sin(ang), size_z * 0.35)))
        
    # Anel superior (mesa arredondada)
    top_v = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        top_v.append(bm_g.verts.new((size_x * 0.60 * math.cos(ang), size_y * 0.60 * math.sin(ang), size_z * 0.75)))
        
    # Ápice abobadado
    apex = bm_g.verts.new((0, 0, size_z))
    bottom = bm_g.verts.new((0, 0, -size_z * 0.25))

    for i in range(segs):
        ni = (i + 1) % segs
        bm_g.faces.new([bottom, base_v[ni], base_v[i]])
        bm_g.faces.new([base_v[i], base_v[ni], mid_v[ni], mid_v[i]])
        bm_g.faces.new([mid_v[i], mid_v[ni], top_v[ni], top_v[i]])
        bm_g.faces.new([top_v[i], top_v[ni], apex])

    # Rotacionar e posicionar
    for v in bm_g.verts:
        if rot[0] != 0:
            rad = rot[0]
            y = v.co.y * math.cos(rad) - v.co.z * math.sin(rad)
            z = v.co.y * math.sin(rad) + v.co.z * math.cos(rad)
            v.co.y, v.co.z = y, z
        if rot[1] != 0:
            rad = rot[1]
            x = v.co.x * math.cos(rad) + v.co.z * math.sin(rad)
            z = -v.co.x * math.sin(rad) + v.co.z * math.cos(rad)
            v.co.x, v.co.z = x, z
        if rot[2] != 0:
            rad = rot[2]
            x = v.co.x * math.cos(rad) - v.co.y * math.sin(rad)
            y = v.co.x * math.sin(rad) + v.co.y * math.cos(rad)
            v.co.x, v.co.y = x, y
        v.co.x += loc[0]
        v.co.y += loc[1]
        v.co.z += loc[2]

    gem_obj = finish_mesh_object(name, bm_g, material, subsurf=True)
    
    # Adiciona pequena luz de ponto dentro da gema para brilho translúcido estonteante
    light_data = bpy.data.lights.new(name + "_InternalLight", 'POINT')
    light_data.color = material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3]
    light_data.energy = 45.0
    light_data.shadow_soft_size = 0.05
    light_obj = bpy.data.objects.new(name + "_Light", light_data)
    light_obj.location = loc
    light_obj.parent = root
    col.objects.link(light_obj)

    return gem_obj

# Moldura dourada com garras (Prongs) para engaste
def create_bezel(name, loc, size_x, size_y, depth, rot=(0,0,0)):
    bm_b = bmesh.new()
    bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=16,
                          radius1=size_x * 1.35, radius2=size_x * 1.15, depth=depth)
    for v in bm_b.verts:
        v.co.y *= (size_y / size_x)
        if rot[0] != 0:
            rad = rot[0]
            y = v.co.y * math.cos(rad) - v.co.z * math.sin(rad)
            z = v.co.y * math.sin(rad) + v.co.z * math.cos(rad)
            v.co.y, v.co.z = y, z
        if rot[1] != 0:
            rad = rot[1]
            x = v.co.x * math.cos(rad) + v.co.z * math.sin(rad)
            z = -v.co.x * math.sin(rad) + v.co.z * math.cos(rad)
            v.co.x, v.co.z = x, z
        v.co.x += loc[0]
        v.co.y += loc[1]
        v.co.z += loc[2]
    return finish_mesh_object(name, bm_b, mat_gold, subsurf=True)

# 1. JOIA DA MENTE (Mind Stone) - Grande cabochão central dourado/amarelo
create_bezel("Bezel_Mind", (0.0, -0.47, 0.15), size_x=0.22, size_y=0.17, depth=0.06, rot=(math.radians(90), 0, 0))
create_cabochon_gem("Gem_Mind", (0.0, -0.48, 0.15), size_x=0.20, size_y=0.15, size_z=0.16, material=mat_gem_mind, rot=(math.radians(90), 0, 0))

# 4 NÓS DOS DEDOS (Knuckle Armor Band)
# Barra reforçada das juntas onde as 4 joias se assentam
bm_knuckles = bmesh.new()
bmesh.ops.create_cube(bm_knuckles, size=1.0)
for v in bm_knuckles.verts:
    v.co.x *= 1.10
    v.co.y = -0.40 + v.co.y * 0.22
    v.co.z = 0.48 + v.co.z * 0.16
    # Arqueamento natural da mão fechada
    v.co.y -= 0.10 * (v.co.x ** 2)
finish_mesh_object("Gauntlet_Knuckle_Bar", bm_knuckles, mat_gold, subsurf=True)

# 2. JOIA DO PODER (Roxo) - Dedo Mínimo
create_bezel("Bezel_Power", (0.42, -0.38, 0.52), size_x=0.11, size_y=0.09, depth=0.04, rot=(math.radians(78), math.radians(18), 0))
create_cabochon_gem("Gem_Power", (0.42, -0.39, 0.52), size_x=0.10, size_y=0.08, size_z=0.11, material=mat_gem_power, rot=(math.radians(78), math.radians(18), 0))

# 3. JOIA DA REALIDADE (Vermelho) - Dedo Anelar
create_bezel("Bezel_Reality", (0.16, -0.44, 0.58), size_x=0.11, size_y=0.09, depth=0.04, rot=(math.radians(82), math.radians(8), 0))
create_cabochon_gem("Gem_Reality", (0.16, -0.45, 0.58), size_x=0.10, size_y=0.08, size_z=0.11, material=mat_gem_reality, rot=(math.radians(82), math.radians(8), 0))

# 4. JOIA DO ESPAÇO (Azul) - Dedo Médio
create_bezel("Bezel_Space", (-0.12, -0.46, 0.60), size_x=0.12, size_y=0.10, depth=0.04, rot=(math.radians(86), 0, 0))
create_cabochon_gem("Gem_Space", (-0.12, -0.47, 0.60), size_x=0.11, size_y=0.09, size_z=0.12, material=mat_gem_space, rot=(math.radians(86), 0, 0))

# 5. JOIA DO TEMPO (Verde) - Dedo Indicador
create_bezel("Bezel_Time", (-0.38, -0.42, 0.55), size_x=0.11, size_y=0.09, depth=0.04, rot=(math.radians(80), math.radians(-14), 0))
create_cabochon_gem("Gem_Time", (-0.38, -0.43, 0.55), size_x=0.10, size_y=0.08, size_z=0.11, material=mat_gem_time, rot=(math.radians(80), math.radians(-14), 0))

# 6. JOIA DA ALMA (Laranja) - Lateral do Polegar
create_bezel("Bezel_Soul", (-0.66, -0.16, 0.10), size_x=0.11, size_y=0.09, depth=0.04, rot=(math.radians(55), math.radians(-48), 0))
create_cabochon_gem("Gem_Soul", (-0.67, -0.18, 0.10), size_x=0.10, size_y=0.09, size_z=0.11, material=mat_gem_soul, rot=(math.radians(55), math.radians(-48), 0))

# -------------------------------------------------------------------------
# 2.6 DEDOS ARTICULADOS MCU: POSE PODEROSA DE COMBATE (Curved Titan Grasp)
# -------------------------------------------------------------------------
# Cada dedo é composto de 3 placas sobrepostas com dobras anatômicas
def build_mcu_finger(name, knuckle_pos, base_yaw, lengths, thicknesses, flex_angles):
    bm_f = bmesh.new()
    cur_p = list(knuckle_pos)
    cur_pitch = flex_angles[0]
    cur_yaw = base_yaw

    for seg_i, (length, thick) in enumerate(zip(lengths, thicknesses)):
        # Junta mecânica escura
        j_radius = thick * 0.96
        bmesh.ops.create_icosphere(bm_f, subdivisions=2, radius=j_radius)
        for v in bm_f.verts[-42:]:
            v.co.x += cur_p[0]
            v.co.y += cur_p[1]
            v.co.z += cur_p[2]

        # Segmento da placa de ouro com chanfro e crista dorsal
        rad_pitch = math.radians(cur_pitch)
        rad_yaw = math.radians(cur_yaw)
        
        # Vetor direção do osso da falange
        # Curvatura pronunciada para frente (fechando a mão como na manopla do MCU)
        dx = length * math.sin(rad_yaw) * math.cos(rad_pitch)
        dy = -length * math.cos(rad_yaw) * math.cos(rad_pitch)
        dz = length * math.sin(rad_pitch)

        next_p = [cur_p[0] + dx, cur_p[1] + dy, cur_p[2] + dz]
        mid_p = [(cur_p[0] + next_p[0]) / 2.0, (cur_p[1] + next_p[1]) / 2.0, (cur_p[2] + next_p[2]) / 2.0]

        # Cilindro de armadura chanfrada
        r1 = thick
        r2 = thick * 0.85 if seg_i < 2 else thick * 0.40 # ponta afiada na garra final
        bmesh.ops.create_cone(bm_f, cap_ends=True, cap_tris=False, segments=12,
                              radius1=r1, radius2=r2, depth=length)
        
        # Rotaciona o cilindro para alinhar com o vetor (dx, dy, dz)
        for v in bm_f.verts[-26:]:
            # Escala ligeiramente para criar crista anatômica
            v.co.x *= 1.15
            # Translação
            v.co.x += mid_p[0]
            v.co.y += mid_p[1]
            v.co.z += mid_p[2]

        cur_p = next_p
        # Dobra cada falange progressivamente para frente (curva de garra de titã)
        if seg_i + 1 < len(flex_angles):
            cur_pitch += flex_angles[seg_i + 1]

    return finish_mesh_object(name, bm_f, mat_gold, subsurf=True)

# Dedos com curvatura orgânica e imponente (Garras de titã articuladas)
# Mínimo (Pinky)
build_mcu_finger("Finger_Pinky", (0.42, -0.32, 0.54), base_yaw=10, 
                 lengths=[0.24, 0.20, 0.18], thicknesses=[0.11, 0.09, 0.07],
                 flex_angles=[45, 30, 25])

# Anelar (Ring)
build_mcu_finger("Finger_Ring", (0.16, -0.38, 0.60), base_yaw=4, 
                 lengths=[0.30, 0.24, 0.20], thicknesses=[0.12, 0.10, 0.08],
                 flex_angles=[48, 32, 28])

# Médio (Middle) - O maior e mais imponente
build_mcu_finger("Finger_Middle", (-0.12, -0.40, 0.63), base_yaw=0, 
                 lengths=[0.34, 0.28, 0.22], thicknesses=[0.13, 0.11, 0.085],
                 flex_angles=[50, 35, 30])

# Indicador (Index)
build_mcu_finger("Finger_Index", (-0.38, -0.36, 0.58), base_yaw=-6, 
                 lengths=[0.31, 0.25, 0.20], thicknesses=[0.12, 0.10, 0.08],
                 flex_angles=[48, 32, 28])

# Polegar Poderoso (Thumb) - Curvado lateralmente em oposição aos dedos
bm_thumb = bmesh.new()
# Base do polegar
t_base = [-0.64, -0.12, 0.10]
t_mid1 = [-0.68, -0.28, 0.24]
t_mid2 = [-0.62, -0.40, 0.36]
t_tip  = [-0.50, -0.46, 0.44]

for p1, p2, r_start, r_end in [(t_base, t_mid1, 0.15, 0.13), (t_mid1, t_mid2, 0.13, 0.11), (t_mid2, t_tip, 0.11, 0.06)]:
    bmesh.ops.create_cone(bm_thumb, cap_ends=True, cap_tris=False, segments=12,
                          radius1=r_start, radius2=r_end, depth=0.22)
    mx = (p1[0] + p2[0]) / 2.0
    my = (p1[1] + p2[1]) / 2.0
    mz = (p1[2] + p2[2]) / 2.0
    for v in bm_thumb.verts[-26:]:
        v.co.x += mx
        v.co.y += my
        v.co.z += mz
finish_mesh_object("Finger_Thumb_MCU", bm_thumb, mat_gold, subsurf=True)

# -------------------------------------------------------------------------
# 3. ILUMINAÇÃO DE ESTÚDIO CINEMATOGRÁFICO MCU
# -------------------------------------------------------------------------
def create_light(name, ltype, loc, color, energy, radius=0.2):
    ldata = bpy.data.lights.new(name, ltype)
    ldata.color = color
    ldata.energy = energy
    if ltype in ('POINT', 'SPOT'):
        ldata.shadow_soft_size = radius
    lobj = bpy.data.objects.new(name, ldata)
    lobj.location = loc
    col.objects.link(lobj)
    return lobj

# Luz Principal Quente Frontal (Dourada)
create_light("Light_Key_Gold", 'AREA', (1.8, -3.2, 1.4), (1.0, 0.90, 0.70), 380)
# Luz de Preenchimento Ciano S.H.I.E.L.D. (contraste cromático clássico Marvel)
create_light("Light_Fill_Cyan", 'AREA', (-2.4, -2.6, 0.2), (0.1, 0.85, 1.0), 180)
# Luz de Contorno Superior (Rim Light)
create_light("Light_Rim_Top", 'SPOT', (0.0, 2.8, 3.0), (1.0, 0.95, 0.85), 550)
# Luz de Contorno Inferior
create_light("Light_Rim_Bottom", 'POINT', (0.6, 2.0, -1.8), (0.7, 0.2, 1.0), 220)

# Câmera Frontal Levemente Angulada para Capturar o Poder e os Reflexos das Joias
cam_data = bpy.data.cameras.new("MCU_Gauntlet_Camera")
cam_data.lens = 72 # Teleobjetiva média clássica de cinema
cam_obj = bpy.data.objects.new("MCU_Gauntlet_Camera", cam_data)
cam_obj.location = (0.0, -4.5, 0.05)
cam_obj.rotation_euler = (math.radians(91.5), 0, 0)
col.objects.link(cam_obj)
scene.camera = cam_obj

# -------------------------------------------------------------------------
# 4. SALVAMENTO DO PROJETO .BLEND E EXPORTAÇÃO GLB
# -------------------------------------------------------------------------
blend_user_docs = os.path.join(USER_DOCS_BLENDER, "Manopla_Thanos.blend")
blend_project_path = os.path.join(SCRIPT_DIR, "manopla_thanos.blend")
glb_export_path = os.path.join(SCRIPT_DIR, "manopla_thanos.glb")
glb_root_path = os.path.join(PROJECT_ROOT, "manopla_thanos.glb")

bpy.ops.wm.save_as_mainfile(filepath=blend_project_path)
bpy.ops.wm.save_as_mainfile(filepath=blend_user_docs)
print(f"Salvo arquivo .blend em: {blend_user_docs}")

try:
    bpy.ops.export_scene.gltf(
        filepath=glb_export_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_yup=True
    )
    import shutil
    shutil.copy2(glb_export_path, glb_root_path)
    print(f"Exportado GLB com sucesso em: {glb_export_path}")
except Exception as e:
    print(f"Erro ao exportar GLB: {e}")

# -------------------------------------------------------------------------
# 5. RENDERIZAÇÃO DOS 24 FRAMES 360° E HERO BANNER
# -------------------------------------------------------------------------
NUM_FRAMES = 24
print(f"Renderizando {NUM_FRAMES} frames da autêntica Manopla do Thanos...")

for f in range(NUM_FRAMES):
    angle_deg = f * (360.0 / NUM_FRAMES)
    root.rotation_euler = (0, 0, math.radians(angle_deg))
    frame_name = f"manopla_3d_{f:02d}.png"
    frame_path = os.path.join(RES_DRAWABLE, frame_name)
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    print(f"Frame {f+1:02d}/{NUM_FRAMES} ({angle_deg:.0f}°) concluído.")

# Hero Render com pose dramática de filme
scene.render.resolution_x = 720
scene.render.resolution_y = 720
root.rotation_euler = (math.radians(-6), math.radians(10), math.radians(22))
hero_path = os.path.join(RES_DRAWABLE, "manopla_hero_3d.png")
scene.render.filepath = hero_path
bpy.ops.render.render(write_still=True)
print(f"Hero render concluído em: {hero_path}")

print("\n=======================================================")
print("MANOPLA MCU RECONSTRUÍDA COM SUCESSO TOTAL!")
print("=======================================================")
