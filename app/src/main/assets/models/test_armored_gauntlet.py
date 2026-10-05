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

col = bpy.data.collections.new("MCU_Gauntlet_Armored")
scene.collection.children.link(col)
root = bpy.data.objects.new("Gauntlet_Root", None)
col.objects.link(root)

# 1. MATERIAIS
def make_gold():
    mat = bpy.data.materials.new("UruGold")
    mat.use_nodes = True
    b = mat.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.86, 0.60, 0.14, 1.0)
    b.inputs['Metallic'].default_value = 0.98
    b.inputs['Roughness'].default_value = 0.18
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.95
    return mat

def make_dark():
    mat = bpy.data.materials.new("DarkIron")
    mat.use_nodes = True
    b = mat.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1.0)
    b.inputs['Metallic'].default_value = 0.92
    b.inputs['Roughness'].default_value = 0.35
    return mat

def make_gem(color, name):
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
    emit.inputs['Strength'].default_value = 8.0
    mix.inputs['Fac'].default_value = 0.35

    mat.node_tree.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    mat.node_tree.links.new(emit.outputs['Emission'], mix.inputs[2])
    mat.node_tree.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return mat

mat_gold = make_gold()
mat_dark = make_dark()

mat_mind    = make_gem((1.0, 0.85, 0.0, 1.0), "MatMind")
mat_power   = make_gem((0.72, 0.05, 1.0, 1.0), "MatPower")
mat_space   = make_gem((0.05, 0.58, 1.0, 1.0), "MatSpace")
mat_reality = make_gem((1.0, 0.03, 0.05, 1.0), "MatReality")
mat_time    = make_gem((0.05, 1.0, 0.28, 1.0), "MatTime")
mat_soul    = make_gem((1.0, 0.48, 0.02, 1.0), "MatSoul")

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

# 2. CORPO ANATÔMICO CONTÍNUO (Base do antebraço até os nós)
bm_body = bmesh.new()
N = 20
rings = []
profile = [
    # (z, rx, ry, off_y)
    (-1.50, 0.48, 0.37, 0.00),
    (-1.25, 0.54, 0.42, 0.01),
    (-0.95, 0.50, 0.39, 0.01),
    (-0.65, 0.44, 0.34, 0.00),
    (-0.45, 0.42, 0.32, 0.00),
    (-0.25, 0.46, 0.34, 0.01),
    ( 0.00, 0.55, 0.36, 0.02),
    ( 0.18, 0.59, 0.34, 0.03),
    ( 0.34, 0.61, 0.30, 0.03),
]
for z, rx, ry, off_y in profile:
    ring = []
    for i in range(N):
        ang = 2 * math.pi * i / N
        ring.append(bm_body.verts.new((rx * math.cos(ang), ry * math.sin(ang) + off_y, z)))
    rings.append(ring)
for r in range(len(rings) - 1):
    for i in range(N):
        ni = (i + 1) % N
        bm_body.faces.new([rings[r][i], rings[r][ni], rings[r+1][ni], rings[r+1][i]])
bm_body.faces.new(rings[0])
bm_body.faces.new(rings[-1])
make_mesh_obj("Gauntlet_Base_Body", bm_body, mat_gold)

# Frisos metálicos do pulso
for cz, r_mult in [(-0.65, 1.04), (-0.45, 1.05)]:
    bm_c = bmesh.new()
    bmesh.ops.create_cone(bm_c, cap_ends=True, cap_tris=False, segments=N,
                          radius1=0.44 * r_mult, radius2=0.42 * r_mult, depth=0.08)
    for v in bm_c.verts:
        v.co.z += cz
        v.co.y *= 0.77
    make_mesh_obj(f"Wrist_Band_{cz}", bm_c, mat_gold)

# 3. ESCUDOS DOS NÓS DOS DEDOS (Raised Knuckle Armor Pods)
# Cada nó tem um bloco angular chanfrado onde a gema se assenta!
knuckle_data = [
    # (nome, x, y, z, rot_x, rot_y, mat_gem, rx, ry)
    ("Power",    0.37, -0.22, 0.34,  82,  16, mat_power,   0.09, 0.07),
    ("Reality",  0.13, -0.26, 0.38,  86,   5, mat_reality, 0.09, 0.07),
    ("Space",   -0.13, -0.26, 0.38,  86,  -5, mat_space,   0.10, 0.08),
    ("Time",    -0.37, -0.22, 0.34,  82, -16, mat_time,    0.09, 0.07),
]

for name, kx, ky, kz, rx_deg, ry_deg, g_mat, grx, gry in knuckle_data:
    # Bloco chanfrado da junta (Knuckle Pod)
    bm_k = bmesh.new()
    bmesh.ops.create_cube(bm_k, size=1.0)
    for v in bm_k.verts:
        v.co.x *= 0.22
        v.co.y *= 0.16
        v.co.z *= 0.14
        # Rotação
        rad_y = math.radians(ry_deg)
        x = v.co.x * math.cos(rad_y) + v.co.z * math.sin(rad_y)
        z = -v.co.x * math.sin(rad_y) + v.co.z * math.cos(rad_y)
        v.co.x, v.co.z = x, z
        v.co.x += kx
        v.co.y += ky - 0.04
        v.co.z += kz
    make_mesh_obj(f"Knuckle_Pod_{name}", bm_k, mat_gold)

    # Gema cabochão facetada
    bm_g = bmesh.new()
    bmesh.ops.create_icosphere(bm_g, subdivisions=3, radius=1.0)
    for v in bm_g.verts:
        v.co.x *= grx
        v.co.y *= gry
        v.co.z *= 0.05
        # Rotação para a face da junta
        rad_x = math.radians(rx_deg)
        y = v.co.y * math.cos(rad_x) - v.co.z * math.sin(rad_x)
        z = v.co.y * math.sin(rad_x) + v.co.z * math.cos(rad_x)
        v.co.y, v.co.z = y, z
        rad_y = math.radians(ry_deg)
        x = v.co.x * math.cos(rad_y) + v.co.z * math.sin(rad_y)
        z = -v.co.x * math.sin(rad_y) + v.co.z * math.cos(rad_y)
        v.co.x, v.co.z = x, z
        v.co.x += kx
        v.co.y += ky - 0.06
        v.co.z += kz
    make_mesh_obj(f"Gem_{name}", bm_g, g_mat, subsurf=False)

    # Luz pontual
    l = bpy.data.lights.new(f"Light_{name}", 'POINT')
    l.color = g_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3]
    l.energy = 45.0
    l.shadow_soft_size = 0.04
    lo = bpy.data.objects.new(f"LightObj_{name}", l)
    lo.location = (kx, ky - 0.06, kz)
    lo.parent = root
    col.objects.link(lo)

# 4. JOIA DA MENTE (Grande Cabochão Central do Dorso)
# Emoldurada com brasão solar ornamentado
bm_mind_crest = bmesh.new()
bmesh.ops.create_cone(bm_mind_crest, cap_ends=True, cap_tris=False, segments=16,
                      radius1=0.24, radius2=0.20, depth=0.06)
for v in bm_mind_crest.verts:
    v.co.y *= 0.75
    # Rotação 90° em X
    y = -v.co.z
    z = v.co.y
    v.co.y, v.co.z = y, z
    v.co.x += 0.0
    v.co.y += -0.36
    v.co.z += 0.08
make_mesh_obj("Mind_Crest", bm_mind_crest, mat_gold)

bm_mind_gem = bmesh.new()
bmesh.ops.create_icosphere(bm_mind_gem, subdivisions=3, radius=1.0)
for v in bm_mind_gem.verts:
    v.co.x *= 0.17
    v.co.y *= 0.12
    v.co.z *= 0.07
    y = -v.co.z
    z = v.co.y
    v.co.y, v.co.z = y, z
    v.co.x += 0.0
    v.co.y += -0.38
    v.co.z += 0.08
make_mesh_obj("Gem_Mind", bm_mind_gem, mat_mind, subsurf=False)

l_mind = bpy.data.lights.new("Light_Mind", 'POINT')
l_mind.color = (1.0, 0.85, 0.0)
l_mind.energy = 55.0
l_mind.shadow_soft_size = 0.05
lo_mind = bpy.data.objects.new("LightObj_Mind", l_mind)
lo_mind.location = (0.0, -0.38, 0.08)
lo_mind.parent = root
col.objects.link(lo_mind)

# 5. JOIA DA ALMA NO POLEGAR
bm_soul_crest = bmesh.new()
bmesh.ops.create_cone(bm_soul_crest, cap_ends=True, cap_tris=False, segments=16,
                      radius1=0.13, radius2=0.10, depth=0.05)
for v in bm_soul_crest.verts:
    v.co.x += -0.56
    v.co.y += -0.14
    v.co.z += 0.10
make_mesh_obj("Soul_Crest", bm_soul_crest, mat_gold)

bm_soul_gem = bmesh.new()
bmesh.ops.create_icosphere(bm_soul_gem, subdivisions=3, radius=1.0)
for v in bm_soul_gem.verts:
    v.co.x *= 0.09
    v.co.y *= 0.07
    v.co.z *= 0.05
    v.co.x += -0.57
    v.co.y += -0.16
    v.co.z += 0.10
make_mesh_obj("Gem_Soul", bm_soul_gem, mat_soul, subsurf=False)

# 6. DEDOS ARTICULADOS EM PLACAS ESCALONADAS (Segmented Scale Armor)
# Cada dedo tem 3 placas distintas que se sobrepõem como escamas medievais
def create_scale_finger(name, base_pos, yaw_deg, lengths, widths):
    cur_p = list(base_pos)
    pitches = [16.0, 26.0, 36.0] # curva anatômica para a frente
    
    for seg_i, (length, (wx, wy)) in enumerate(zip(lengths, widths)):
        bm_seg = bmesh.new()
        rad_yaw = math.radians(yaw_deg)
        rad_pitch = math.radians(pitches[seg_i])

        # Cria casca de armadura chanfrada com junta escura interna
        bmesh.ops.create_cone(bm_seg, cap_ends=True, cap_tris=False, segments=10,
                              radius1=wx * 0.52, radius2=wx * 0.44 if seg_i < 2 else wx * 0.20, depth=length)
        
        # Junta escura entre falanges
        bm_j = bmesh.new()
        bmesh.ops.create_icosphere(bm_j, subdivisions=2, radius=wx * 0.40)
        for v in bm_j.verts:
            v.co.x += cur_p[0]
            v.co.y += cur_p[1]
            v.co.z += cur_p[2]
        make_mesh_obj(f"{name}_Joint_{seg_i}", bm_j, mat_dark, subsurf=False)

        # Avanço do vetor
        dz = length * math.cos(rad_pitch)
        dy = -length * math.sin(rad_pitch)
        dx = length * math.sin(rad_yaw)
        mid_p = [cur_p[0] + dx * 0.5, cur_p[1] + dy * 0.5, cur_p[2] + dz * 0.5]

        for v in bm_seg.verts:
            # Achata em Y e aplica rotação
            v.co.y *= (wy / wx)
            # Rotação de pitch
            rad_p = math.radians(pitches[seg_i])
            y = v.co.y * math.cos(rad_p) - v.co.z * math.sin(rad_p)
            z = v.co.y * math.sin(rad_p) + v.co.z * math.cos(rad_p)
            v.co.y, v.co.z = y, z
            # Rotação de yaw
            x = v.co.x * math.cos(rad_yaw) + v.co.z * math.sin(rad_yaw)
            z = -v.co.x * math.sin(rad_yaw) + v.co.z * math.cos(rad_yaw)
            v.co.x, v.co.z = x, z
            # Posicionamento
            v.co.x += mid_p[0]
            v.co.y += mid_p[1]
            v.co.z += mid_p[2]

        make_mesh_obj(f"{name}_Seg_{seg_i}", bm_seg, mat_gold, subsurf=True)
        cur_p = [cur_p[0] + dx, cur_p[1] + dy, cur_p[2] + dz]

# 4 Dedos com escamas articuladas:
create_scale_finger("Finger_Pinky", (0.37, -0.16, 0.35), yaw_deg=7,
                    lengths=[0.22, 0.18, 0.15], widths=[(0.20, 0.16), (0.17, 0.14), (0.14, 0.11)])

create_scale_finger("Finger_Ring", (0.13, -0.21, 0.39), yaw_deg=2,
                    lengths=[0.26, 0.22, 0.17], widths=[(0.22, 0.17), (0.19, 0.14), (0.15, 0.11)])

create_scale_finger("Finger_Middle", (-0.13, -0.21, 0.39), yaw_deg=-2,
                    lengths=[0.30, 0.25, 0.19], widths=[(0.23, 0.18), (0.20, 0.15), (0.16, 0.12)])

create_scale_finger("Finger_Index", (-0.37, -0.16, 0.35), yaw_deg=-7,
                    lengths=[0.25, 0.21, 0.16], widths=[(0.21, 0.17), (0.18, 0.14), (0.14, 0.11)])

# Polegar
create_scale_finger("Finger_Thumb", (-0.50, -0.06, 0.05), yaw_deg=-28,
                    lengths=[0.22, 0.18, 0.14], widths=[(0.23, 0.18), (0.19, 0.15), (0.15, 0.11)])

# 7. ILUMINAÇÃO DE ESTÚDIO CINEMATOGRÁFICO MCU
def add_l(name, ltype, loc, colr, energy):
    ld = bpy.data.lights.new(name, ltype)
    ld.color = colr
    ld.energy = energy
    if ltype in ('POINT', 'SPOT'):
        ld.shadow_soft_size = 0.15
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    col.objects.link(lo)

add_l("KeyGold", 'AREA', (2.0, -3.2, 1.4), (1.0, 0.90, 0.72), 400)
add_l("FillCyan", 'AREA', (-2.4, -2.4, 0.4), (0.15, 0.85, 1.0), 200)
add_l("RimTop", 'SPOT', (0.0, 2.8, 3.0), (1.0, 0.96, 0.90), 550)
add_l("RimBottom", 'POINT', (0.4, 2.0, -1.5), (0.8, 0.3, 1.0), 220)

# Câmera perfeitamente enquadrada
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 52
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = (0.0, -4.2, -0.10)
cam.rotation_euler = (math.radians(88), 0, 0)
col.objects.link(cam)
scene.camera = cam

# Test Render
test_path = os.path.join(RES_DRAWABLE, "test_armored.png")
scene.render.filepath = test_path
bpy.ops.render.render(write_still=True)
print(f"Render Armored concluído: {test_path}")
