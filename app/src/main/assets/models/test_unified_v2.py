import bpy
import bmesh
import math
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RES_DRAWABLE = os.path.join(MAIN_DIR, "res", "drawable-nodpi")
os.makedirs(RES_DRAWABLE, exist_ok=True)

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
scene.render.resolution_x = 450
scene.render.resolution_y = 450

col = bpy.data.collections.new("MCU_Infinity_Gauntlet_V2")
scene.collection.children.link(col)
root = bpy.data.objects.new("Gauntlet_Root", None)
col.objects.link(root)

# 1. MATERIAIS CINEMATOGRÁFICOS MCU
def make_uru_gold():
    mat = bpy.data.materials.new("Mat_Uru_Gold")
    mat.use_nodes = True
    b = mat.node_tree.nodes['Principled BSDF']
    # Tom quente, rico e majestoso de ouro antigo de Nidavellir
    b.inputs['Base Color'].default_value = (0.86, 0.62, 0.16, 1.0)
    b.inputs['Metallic'].default_value = 0.98
    b.inputs['Roughness'].default_value = 0.20
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.90
    return mat

def make_dark_iron():
    mat = bpy.data.materials.new("Mat_Dark_Iron")
    mat.use_nodes = True
    b = mat.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.10, 0.09, 0.08, 1.0)
    b.inputs['Metallic'].default_value = 0.88
    b.inputs['Roughness'].default_value = 0.38
    return mat

def make_gem_mat(color, name):
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

mat_gold = make_uru_gold()
mat_dark = make_dark_iron()

mat_mind    = make_gem_mat((1.0, 0.84, 0.0, 1.0), "MatMind")
mat_power   = make_gem_mat((0.70, 0.05, 1.0, 1.0), "MatPower")
mat_space   = make_gem_mat((0.05, 0.55, 1.0, 1.0), "MatSpace")
mat_reality = make_gem_mat((1.0, 0.03, 0.05, 1.0), "MatReality")
mat_time    = make_gem_mat((0.05, 1.0, 0.25, 1.0), "MatTime")
mat_soul    = make_gem_mat((1.0, 0.45, 0.02, 1.0), "MatSoul")

def make_mesh_obj(name, bm, mat, subsurf_levels=1, parent=root):
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
    if subsurf_levels > 0:
        sub = obj.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = subsurf_levels
        sub.render_levels = subsurf_levels
    return obj

# 2. CORPO CONTÍNUO DA MANOPLA (ANTEBRAÇO + PULSO + PALMA/DORSO)
bm = bmesh.new()
N = 20
rings = []

profile = [
    # (z, rx, ry, off_y)
    (-1.50, 0.46, 0.36, 0.00),  # base do antebraço
    (-1.25, 0.52, 0.40, 0.01),  # crista muscular
    (-0.95, 0.48, 0.37, 0.01),
    (-0.65, 0.43, 0.33, 0.00),  # bracelete de pulso
    (-0.45, 0.41, 0.31, 0.00),  # dobra do carpo
    (-0.25, 0.45, 0.33, 0.01),  # início da mão
    ( 0.00, 0.54, 0.35, 0.02),  # centro do dorso (Joia da Mente)
    ( 0.18, 0.58, 0.33, 0.03),  # expansão para os nós dos dedos
    ( 0.34, 0.60, 0.29, 0.03),  # crista dos nós
]

for z, rx, ry, off_y in profile:
    ring = []
    for i in range(N):
        ang = 2 * math.pi * i / N
        x = rx * math.cos(ang)
        y = ry * math.sin(ang) + off_y
        ring.append(bm.verts.new((x, y, z)))
    rings.append(ring)

for r in range(len(rings) - 1):
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([rings[r][i], rings[r][ni], rings[r+1][ni], rings[r+1][i]])

bm.faces.new(rings[0]) # tampa base
make_mesh_obj("Gauntlet_Arm_and_Palm", bm, mat_gold, subsurf_levels=1)

# 3. BRAÇADEIRAS E FRISOS EM RELEVO NO PULSO (Norse Filigree Bands)
for cz, r_mult in [(-0.65, 1.04), (-0.45, 1.05)]:
    bm_c = bmesh.new()
    bmesh.ops.create_cone(bm_c, cap_ends=True, cap_tris=False, segments=N,
                          radius1=0.43 * r_mult, radius2=0.41 * r_mult, depth=0.08)
    for v in bm_c.verts:
        v.co.z += cz
        v.co.y *= 0.77
    make_mesh_obj(f"Wrist_Band_{cz}", bm_c, mat_gold, subsurf_levels=1)

# 4. OS 4 DEDOS ARTICULADOS LARGOS COM JUNTAS MECÂNICAS
def build_segmented_finger(name, base_pos, yaw_deg, lengths, widths):
    bm_f = bmesh.new()
    cur_p = list(base_pos)
    
    # Curvatura anatômica mais acentuada para frente (fechando o punho ligeiramente)
    pitches = [16.0, 24.0, 32.0]
    
    prev_ring = None
    for seg_i, (length, (wx, wy)) in enumerate(zip(lengths, widths)):
        rad_yaw = math.radians(yaw_deg)
        rad_pitch = math.radians(pitches[seg_i])
        
        # Anel base da falange
        ring_base = []
        for i in range(8):
            ang = 2 * math.pi * i / 8
            vx = cur_p[0] + (wx * 0.5) * math.cos(ang)
            vy = cur_p[1] + (wy * 0.5) * math.sin(ang)
            vz = cur_p[2]
            ring_base.append(bm_f.verts.new((vx, vy, vz)))
            
        if prev_ring:
            for i in range(8):
                ni = (i + 1) % 8
                bm_f.faces.new([prev_ring[i], prev_ring[ni], ring_base[ni], ring_base[i]])
        else:
            bm_f.faces.new(ring_base)

        # Vetor avanço
        dz = length * math.cos(rad_pitch)
        dy = -length * math.sin(rad_pitch)
        dx = length * math.sin(rad_yaw)
        next_p = [cur_p[0] + dx, cur_p[1] + dy, cur_p[2] + dz]
        
        scale_top = 0.88 if seg_i < 2 else 0.35
        ring_top = []
        for i in range(8):
            ang = 2 * math.pi * i / 8
            vx = next_p[0] + (wx * 0.5 * scale_top) * math.cos(ang)
            vy = next_p[1] + (wy * 0.5 * scale_top) * math.sin(ang)
            vz = next_p[2]
            ring_top.append(bm_f.verts.new((vx, vy, vz)))
            
        for i in range(8):
            ni = (i + 1) % 8
            bm_f.faces.new([ring_base[i], ring_base[ni], ring_top[ni], ring_top[i]])
            
        cur_p = next_p
        prev_ring = ring_top

    bm_f.faces.new(prev_ring)
    return make_mesh_obj(name, bm_f, mat_gold, subsurf_levels=1)

# 4 Dedos largos da manopla:
build_segmented_finger("Finger_Pinky", (0.37, -0.15, 0.34), yaw_deg=8,
                       lengths=[0.22, 0.18, 0.15], widths=[(0.21, 0.17), (0.18, 0.15), (0.15, 0.12)])

build_segmented_finger("Finger_Ring", (0.13, -0.20, 0.38), yaw_deg=3,
                       lengths=[0.26, 0.22, 0.17], widths=[(0.23, 0.18), (0.20, 0.15), (0.16, 0.12)])

build_segmented_finger("Finger_Middle", (-0.13, -0.20, 0.38), yaw_deg=-3,
                       lengths=[0.30, 0.25, 0.19], widths=[(0.24, 0.19), (0.21, 0.16), (0.17, 0.13)])

build_segmented_finger("Finger_Index", (-0.37, -0.15, 0.34), yaw_deg=-8,
                       lengths=[0.25, 0.21, 0.16], widths=[(0.22, 0.18), (0.19, 0.15), (0.15, 0.12)])

# 5. POLEGAR ANATÔMICO ARTICULADO (Curvado com o nó da Joia da Alma)
bm_th = bmesh.new()
thumb_points = [
    # (x, y, z, r)
    (-0.46, -0.04, 0.00, 0.15),
    (-0.55, -0.11, 0.10, 0.14), # Nó com a Joia da Alma
    (-0.52, -0.21, 0.21, 0.12),
    (-0.40, -0.26, 0.28, 0.07)  # Ponta afunilada
]
t_rings = []
for x, y, z, r in thumb_points:
    ring = []
    for i in range(8):
        ang = 2 * math.pi * i / 8
        vx = x + r * math.cos(ang)
        vy = y + r * 0.85 * math.sin(ang)
        vz = z
        ring.append(bm_th.verts.new((vx, vy, vz)))
    t_rings.append(ring)

for r in range(len(thumb_points) - 1):
    for i in range(8):
        ni = (i + 1) % 8
        bm_th.faces.new([t_rings[r][i], t_rings[r][ni], t_rings[r+1][ni], t_rings[r+1][i]])
bm_th.faces.new(t_rings[0])
bm_th.faces.new(t_rings[-1])
make_mesh_obj("Finger_Thumb", bm_th, mat_gold, subsurf_levels=1)

# 6. AS 6 JOIAS DO INFINITO EM CABOCHÃO FACETADO COM ENGASTES
def add_gem(name, loc, rx, ry, rz, gem_mat, rot=(0,0,0)):
    # 1. Bezel dourado reforçado
    bm_b = bmesh.new()
    bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=16,
                          radius1=rx * 1.35, radius2=rx * 1.15, depth=rz * 0.85)
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
    make_mesh_obj(name + "_Bezel", bm_b, mat_gold, subsurf_levels=1)

    # 2. Gema lapidada cabochão
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
    make_mesh_obj(name + "_Gem", bm_g, gem_mat, subsurf_levels=0)

    # 3. Luz pontual interna
    l = bpy.data.lights.new(name + "_Light", 'POINT')
    l.color = gem_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3]
    l.energy = 42.0
    l.shadow_soft_size = 0.04
    lo = bpy.data.objects.new(name + "_LightObj", l)
    lo.location = loc
    lo.parent = root
    col.objects.link(lo)

# 1. Joia da Mente (Grande oval cabochão central no dorso)
add_gem("Mind", (0.0, -0.34, 0.08), 0.16, 0.12, 0.08, mat_mind, rot=(math.radians(90), 0, 0))

# 4 Joias dos Nós dos Dedos
add_gem("Power",   ( 0.37, -0.20, 0.34), 0.08, 0.06, 0.05, mat_power,   rot=(math.radians(82), math.radians( 16), 0))
add_gem("Reality", ( 0.13, -0.25, 0.38), 0.08, 0.06, 0.05, mat_reality, rot=(math.radians(86), math.radians(  5), 0))
add_gem("Space",   (-0.13, -0.25, 0.38), 0.09, 0.07, 0.05, mat_space,   rot=(math.radians(86), math.radians( -5), 0))
add_gem("Time",    (-0.37, -0.20, 0.34), 0.08, 0.06, 0.05, mat_time,    rot=(math.radians(82), math.radians(-16), 0))

# Joia da Alma (Polegar)
add_gem("Soul",    (-0.55, -0.13, 0.10), 0.08, 0.06, 0.05, mat_soul,    rot=(math.radians(65), math.radians(-42), 0))

# 7. CANAIS DE ENERGIA DE NIDAVELLIR (Engraved Runes)
for tx, tz in [(0.0, 0.08), (0.37, 0.34), (0.13, 0.38), (-0.13, 0.38), (-0.37, 0.34)]:
    bm_line = bmesh.new()
    bmesh.ops.create_cube(bm_line, size=1.0)
    mid_z = (-0.25 + tz) / 2.0
    len_z = tz - (-0.25)
    for v in bm_line.verts:
        v.co.x = (tx * 0.5) + v.co.x * 0.015
        v.co.y = -0.34 + v.co.y * 0.012
        v.co.z = mid_z + v.co.z * (len_z * 0.5)
    make_mesh_obj(f"Rune_Line_{tx}", bm_line, mat_gold, subsurf_levels=0)

# 8. ILUMINAÇÃO DE ESTÚDIO CINEMATOGRÁFICO MCU
def add_l(name, ltype, loc, colr, energy):
    ld = bpy.data.lights.new(name, ltype)
    ld.color = colr
    ld.energy = energy
    if ltype in ('POINT', 'SPOT'):
        ld.shadow_soft_size = 0.15
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    col.objects.link(lo)

add_l("KeyGold", 'AREA', (1.8, -3.2, 1.4), (1.0, 0.90, 0.72), 380)
add_l("FillCyan", 'AREA', (-2.2, -2.4, 0.4), (0.15, 0.85, 1.0), 190)
add_l("RimTop", 'SPOT', (0.0, 2.6, 2.8), (1.0, 0.96, 0.90), 550)
add_l("RimBottom", 'POINT', (0.4, 2.0, -1.5), (0.8, 0.3, 1.0), 200)

# 9. CÂMERA COM ENQUADRAMENTO COMPLETO (DO ANTEBRAÇO À PONTA DOS DEDOS)
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 50 # Grande-angular média para capturar todo o modelo
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = (0.0, -4.2, -0.15)
cam.rotation_euler = (math.radians(88), 0, 0)
col.objects.link(cam)
scene.camera = cam

# Test Render
test_path = os.path.join(RES_DRAWABLE, "test_v2.png")
scene.render.filepath = test_path
bpy.ops.render.render(write_still=True)
print(f"Render V2 concluído: {test_path}")
