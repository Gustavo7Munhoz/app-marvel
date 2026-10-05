import bpy
import bmesh
import math
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RES_DRAWABLE = os.path.join(MAIN_DIR, "res", "drawable-nodpi")
os.makedirs(RES_DRAWABLE, exist_ok=True)

# 1. Reset e Setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
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

col = bpy.data.collections.new("MCU_Gauntlet_Authentic")
scene.collection.children.link(col)
root = bpy.data.objects.new("Gauntlet_Root", None)
col.objects.link(root)

# 2. Materiais PBR
def create_uru_gold():
    mat = bpy.data.materials.new("Mat_Uru_Gold")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (0.86, 0.60, 0.14, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.18
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.90
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.90
    return mat

def create_dark_iron():
    mat = bpy.data.materials.new("Mat_Dark_Iron")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.90
    bsdf.inputs['Roughness'].default_value = 0.35
    return mat

def create_gem_mat(color, name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    out = nodes['Material Output']
    bsdf = nodes['Principled BSDF']
    emit = nodes.new('ShaderNodeEmission')
    mix = nodes.new('ShaderNodeMixShader')

    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['IOR'].default_value = 1.77
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.95
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.95

    emit.inputs['Color'].default_value = color
    emit.inputs['Strength'].default_value = 7.0
    mix.inputs['Fac'].default_value = 0.35

    mat.node_tree.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    mat.node_tree.links.new(emit.outputs['Emission'], mix.inputs[2])
    mat.node_tree.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return mat

mat_gold = create_uru_gold()
mat_dark = create_dark_iron()

mat_mind    = create_gem_mat((1.0, 0.85, 0.0, 1.0), "MatMind")
mat_power   = create_gem_mat((0.70, 0.05, 1.0, 1.0), "MatPower")
mat_space   = create_gem_mat((0.05, 0.55, 1.0, 1.0), "MatSpace")
mat_reality = create_gem_mat((1.0, 0.03, 0.05, 1.0), "MatReality")
mat_time    = create_gem_mat((0.05, 1.0, 0.25, 1.0), "MatTime")
mat_soul    = create_gem_mat((1.0, 0.45, 0.02, 1.0), "MatSoul")

def make_mesh_obj(name, bm, mat, subsurf=True, parent=root):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    for p in mesh.polygons:
        p.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    col.objects.link(obj)
    if parent:
        obj.parent = parent
    if subsurf:
        sub = obj.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = 1
        sub.render_levels = 1
    return obj

# 3. ANTEBRAÇO TÁTICO DE NIDAVELLIR (Forearm Vambrace)
bm_forearm = bmesh.new()
segs = 20
forearm_levels = [
    # (Z, rx, ry, off_y)
    (-1.50, 0.48, 0.38, 0.0),
    (-1.20, 0.54, 0.42, 0.01), # crista de curvatura
    (-0.90, 0.50, 0.39, 0.01),
    (-0.65, 0.45, 0.35, 0.0),
    (-0.48, 0.43, 0.33, 0.0),  # junção com o pulso
]
f_rings = []
for z, rx, ry, off_y in forearm_levels:
    ring = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        x = rx * math.cos(ang)
        y = ry * math.sin(ang) + off_y
        ring.append(bm_forearm.verts.new((x, y, z)))
    f_rings.append(ring)

for r in range(len(forearm_levels) - 1):
    for i in range(segs):
        ni = (i + 1) % segs
        bm_forearm.faces.new([f_rings[r][i], f_rings[r][ni], f_rings[r+1][ni], f_rings[r+1][i]])
bm_forearm.faces.new(f_rings[0])
make_mesh_obj("Vambrace_Body", bm_forearm, mat_gold)

# Cristas laterais de armadura no antebraço
for side in [-1, 1]:
    bm_ridge = bmesh.new()
    bmesh.ops.create_cube(bm_ridge, size=1.0)
    for v in bm_ridge.verts:
        v.co.x = side * (0.50 + v.co.x * 0.06)
        v.co.y *= 0.22
        v.co.z = -1.05 + v.co.z * 0.40
    make_mesh_obj(f"Forearm_Fin_{side}", bm_ridge, mat_gold)

# 4. BRACELETE DE PULSO ARTICULADO (Articulated Wrist Cuff)
for idx, (cz, scale) in enumerate([(-0.48, 1.02), (-0.36, 1.05), (-0.24, 1.02)]):
    bm_cuff = bmesh.new()
    bmesh.ops.create_cone(bm_cuff, cap_ends=True, cap_tris=False, segments=segs,
                          radius1=0.45 * scale, radius2=0.43 * scale, depth=0.10)
    for v in bm_cuff.verts:
        v.co.z += cz
        v.co.y *= 0.78
    make_mesh_obj(f"Wrist_Ring_{idx}", bm_cuff, mat_gold if idx != 1 else mat_dark)

# 5. CORPO DA MÃO (Hand Metacarpal Carapace)
# Do pulso (-0.24) até os nós dos dedos (+0.40)
bm_hand = bmesh.new()
hand_levels = [
    # (Z, rx, ry, off_y)
    (-0.24, 0.44, 0.33, 0.0),
    (-0.08, 0.50, 0.36, 0.01),
    ( 0.12, 0.56, 0.38, 0.02), # nível da joia da mente
    ( 0.28, 0.60, 0.36, 0.03),
    ( 0.42, 0.62, 0.32, 0.03), # crista dos nós
]
h_rings = []
for z, rx, ry, off_y in hand_levels:
    ring = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        x = rx * math.cos(ang)
        y = ry * math.sin(ang) + off_y
        ring.append(bm_hand.verts.new((x, y, z)))
    h_rings.append(ring)

for r in range(len(hand_levels) - 1):
    for i in range(segs):
        ni = (i + 1) % segs
        bm_hand.faces.new([h_rings[r][i], h_rings[r][ni], h_rings[r+1][ni], h_rings[r+1][i]])
bm_hand.faces.new(h_rings[-1])
make_mesh_obj("Hand_Carapace", bm_hand, mat_gold)

# 6. ENGASTES E AS 6 JOIAS DO INFINITO
def add_gem_socket(name, loc, rx, ry, rz, gem_mat, rot=(0,0,0)):
    # 1. Bezel dourado reforçado
    bm_b = bmesh.new()
    bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=16,
                          radius1=rx * 1.35, radius2=rx * 1.15, depth=rz * 0.9)
    for v in bm_b.verts:
        v.co.y *= (ry / rx)
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
    make_mesh_obj(name + "_Bezel", bm_b, mat_gold)

    # 2. Gema cabochão facetada
    bm_g = bmesh.new()
    bmesh.ops.create_icosphere(bm_g, subdivisions=3, radius=1.0)
    for v in bm_g.verts:
        v.co.x *= rx
        v.co.y *= ry
        v.co.z *= rz
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
    make_mesh_obj(name + "_Gem", bm_g, gem_mat, subsurf=False)

    # 3. Luz interna da gema
    l = bpy.data.lights.new(name + "_Light", 'POINT')
    l.color = gem_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3]
    l.energy = 45.0
    l.shadow_soft_size = 0.04
    lo = bpy.data.objects.new(name + "_LightObj", l)
    lo.location = loc
    lo.parent = root
    col.objects.link(lo)

# 6.1 Joia da Mente (Grande cabochão dourado central no dorso)
add_gem_socket("Mind", (0.0, -0.36, 0.16), 0.18, 0.13, 0.09, mat_mind, rot=(math.radians(90), 0, 0))

# 6.2 4 Joias dos Nós dos Dedos
add_gem_socket("Power",   ( 0.36, -0.27, 0.43), 0.09, 0.07, 0.06, mat_power,   rot=(math.radians(82), math.radians( 16), 0))
add_gem_socket("Reality", ( 0.12, -0.32, 0.45), 0.09, 0.07, 0.06, mat_reality, rot=(math.radians(86), math.radians(  5), 0))
add_gem_socket("Space",   (-0.12, -0.32, 0.45), 0.10, 0.08, 0.06, mat_space,   rot=(math.radians(86), math.radians( -5), 0))
add_gem_socket("Time",    (-0.36, -0.27, 0.43), 0.09, 0.07, 0.06, mat_time,    rot=(math.radians(82), math.radians(-16), 0))

# 6.3 Joia da Alma (Polegar)
add_gem_socket("Soul",    (-0.52, -0.12, 0.08), 0.09, 0.07, 0.06, mat_soul,    rot=(math.radians(65), math.radians(-42), 0))

# 7. DEDOS ARTICULADOS ROBUSTOS (Thick Interlocking Armor Plates)
# Cada dedo é construído com 3 placas anatômicas largas e chanfradas
def build_armored_finger(name, knuckle_pos, yaw_deg, lengths, widths):
    bm_f = bmesh.new()
    cur_p = list(knuckle_pos)
    
    # 3 falanges: ligeira curvatura anatômica para a frente (fist-ready pose)
    pitch_angles = [14.0, 20.0, 26.0]
    
    for seg_i, (length, (wx, wy)) in enumerate(zip(lengths, widths)):
        rad_yaw = math.radians(yaw_deg)
        rad_pitch = math.radians(pitch_angles[seg_i])
        
        # Junta escura entre falanges
        bmesh.ops.create_icosphere(bm_f, subdivisions=2, radius=wx * 0.46)
        for v in bm_f.verts[-42:]:
            v.co.x += cur_p[0]
            v.co.y += cur_p[1]
            v.co.z += cur_p[2]
            
        # Vetor avanço
        dz = length * math.cos(rad_pitch)
        dy = -length * math.sin(rad_pitch)
        dx = length * math.sin(rad_yaw)
        
        next_p = [cur_p[0] + dx, cur_p[1] + dy, cur_p[2] + dz]
        mid_p = [(cur_p[0] + next_p[0])/2.0, (cur_p[1] + next_p[1])/2.0, (cur_p[2] + next_p[2])/2.0]
        
        # Placa de armadura com crista superior chanfrada
        r_bottom = wx * 0.52
        r_top = wx * 0.45 if seg_i < 2 else wx * 0.22 # ponta de garra na última falange
        bmesh.ops.create_cone(bm_f, cap_ends=True, cap_tris=False, segments=12,
                              radius1=r_bottom, radius2=r_top, depth=length * 1.05)
        for v in bm_f.verts[-26:]:
            v.co.y *= (wy / wx)
            v.co.x += mid_p[0]
            v.co.y += mid_p[1]
            v.co.z += mid_p[2]
            
        cur_p = next_p

    make_mesh_obj(name, bm_f, mat_gold, subsurf=True)

# 4 Dedos largos da armadura:
# Mínimo (Pinky)
build_armored_finger("Finger_Pinky", (0.36, -0.24, 0.43), yaw_deg=7,
                     lengths=[0.24, 0.20, 0.17], widths=[(0.23, 0.19), (0.20, 0.17), (0.17, 0.14)])

# Anelar (Ring)
build_armored_finger("Finger_Ring", (0.12, -0.28, 0.45), yaw_deg=2,
                     lengths=[0.29, 0.24, 0.19], widths=[(0.24, 0.20), (0.21, 0.17), (0.18, 0.14)])

# Médio (Middle) - Mais longo
build_armored_finger("Finger_Middle", (-0.12, -0.28, 0.45), yaw_deg=-2,
                     lengths=[0.33, 0.27, 0.21], widths=[(0.25, 0.21), (0.22, 0.18), (0.18, 0.14)])

# Indicador (Index)
build_armored_finger("Finger_Index", (-0.36, -0.24, 0.43), yaw_deg=-7,
                     lengths=[0.28, 0.23, 0.18], widths=[(0.24, 0.20), (0.21, 0.17), (0.17, 0.14)])

# Polegar de Titã (Curvado na lateral)
bm_thumb = bmesh.new()
t_nodes = [
    [-0.52, -0.06, 0.06],
    [-0.56, -0.16, 0.18],
    [-0.50, -0.26, 0.28],
    [-0.40, -0.32, 0.35]
]
for i in range(len(t_nodes)-1):
    p1 = t_nodes[i]
    p2 = t_nodes[i+1]
    bmesh.ops.create_cone(bm_thumb, cap_ends=True, cap_tris=False, segments=12,
                          radius1=0.15 - i*0.025, radius2=0.12 - i*0.025, depth=0.20)
    mx = (p1[0]+p2[0])/2.0
    my = (p1[1]+p2[1])/2.0
    mz = (p1[2]+p2[2])/2.0
    for v in bm_thumb.verts[-26:]:
        v.co.x += mx
        v.co.y += my
        v.co.z += mz
make_mesh_obj("Finger_Thumb", bm_thumb, mat_gold, subsurf=True)

# 8. CANAIS DE ENERGIA DE NIDAVELLIR (Engraved Energy Conduits)
# Linhas douradas em relevo conectando o pulso a cada gema
for target_x, target_z in [(0.0, 0.16), (0.36, 0.43), (0.12, 0.45), (-0.12, 0.45), (-0.36, 0.43)]:
    bm_line = bmesh.new()
    bmesh.ops.create_cube(bm_line, size=1.0)
    # Linha fina conectando de z=-0.24 até a gema
    mid_z = (-0.24 + target_z) / 2.0
    len_z = target_z - (-0.24)
    for v in bm_line.verts:
        v.co.x = (target_x * 0.5) + v.co.x * 0.02
        v.co.y = -0.38 + v.co.y * 0.015
        v.co.z = mid_z + v.co.z * (len_z * 0.5)
    make_mesh_obj(f"Energy_Line_{target_x}", bm_line, mat_gold, subsurf=False)

# 9. ILUMINAÇÃO DE ESTÚDIO CINEMATOGRÁFICO MCU
def add_light(name, ltype, loc, color, energy):
    ld = bpy.data.lights.new(name, ltype)
    ld.color = color
    ld.energy = energy
    if ltype in ('POINT', 'SPOT'):
        ld.shadow_soft_size = 0.12
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    col.objects.link(lo)

add_light("KeyGold", 'AREA', (1.8, -3.2, 1.2), (1.0, 0.90, 0.72), 380)
add_light("FillCyan", 'AREA', (-2.2, -2.4, 0.3), (0.15, 0.85, 1.0), 180)
add_light("RimTop", 'SPOT', (0.0, 2.5, 2.8), (1.0, 0.96, 0.88), 500)
add_light("RimBottom", 'POINT', (0.4, 2.0, -1.5), (0.8, 0.3, 1.0), 200)

# Câmera perfeitamente enquadrada no conjunto (do topo dos dedos à base do antebraço)
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 62
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = (0.0, -3.8, 0.05)
cam.rotation_euler = (math.radians(88), 0, 0)
col.objects.link(cam)
scene.camera = cam

# Test Render
test_path = os.path.join(RES_DRAWABLE, "test_authentic.png")
scene.render.filepath = test_path
bpy.ops.render.render(write_still=True)
print(f"Render concluído: {test_path}")
