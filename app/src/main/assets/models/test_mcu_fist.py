import bpy
import bmesh
import math
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RES_DRAWABLE = os.path.join(MAIN_DIR, "res", "drawable-nodpi")
os.makedirs(RES_DRAWABLE, exist_ok=True)

# Configuração
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

col = bpy.data.collections.new("ThanosFist")
scene.collection.children.link(col)
root = bpy.data.objects.new("Fist_Root", None)
col.objects.link(root)

# Materiais
def make_gold():
    mat = bpy.data.materials.new("UruGold")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (0.86, 0.62, 0.16, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.96
    bsdf.inputs['Roughness'].default_value = 0.22
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.85
    return mat

def make_dark():
    mat = bpy.data.materials.new("UruDark")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (0.12, 0.11, 0.10, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.90
    bsdf.inputs['Roughness'].default_value = 0.38
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
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['IOR'].default_value = 1.77
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.92
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.92

    emit.inputs['Color'].default_value = color
    emit.inputs['Strength'].default_value = 5.0
    mix.inputs['Fac'].default_value = 0.40

    mat.node_tree.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    mat.node_tree.links.new(emit.outputs['Emission'], mix.inputs[2])
    mat.node_tree.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return mat

mat_gold = make_gold()
mat_dark = make_dark()
mat_mind = make_gem((1.0, 0.85, 0.05, 1.0), "MatMind")
mat_power = make_gem((0.70, 0.08, 1.0, 1.0), "MatPower")
mat_space = make_gem((0.08, 0.60, 1.0, 1.0), "MatSpace")
mat_reality = make_gem((1.0, 0.05, 0.08, 1.0), "MatReality")
mat_time = make_gem((0.08, 1.0, 0.35, 1.0), "MatTime")
mat_soul = make_gem((1.0, 0.50, 0.02, 1.0), "MatSoul")

def make_mesh_obj(name, bm, mat, subsurf=True):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    for p in mesh.polygons:
        p.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    col.objects.link(obj)
    obj.parent = root
    if subsurf:
        sub = obj.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = 1
        sub.render_levels = 1
    return obj

# 1. ANTEBRAÇO (Vambrace)
bm_arm = bmesh.new()
segs = 20
arm_sections = [
    # (Z, raio_x, raio_y)
    (-2.5, 0.76, 0.58),
    (-2.1, 0.80, 0.62),
    (-1.6, 0.74, 0.58),
    (-1.1, 0.70, 0.54),
    (-0.7, 0.64, 0.50),
    (-0.45, 0.62, 0.48)
]
rings = []
for z, rx, ry in arm_sections:
    ring = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        ring.append(bm_arm.verts.new((rx * math.cos(ang), ry * math.sin(ang), z)))
    rings.append(ring)
for r in range(len(arm_sections) - 1):
    for i in range(segs):
        ni = (i + 1) % segs
        bm_arm.faces.new([rings[r][i], rings[r][ni], rings[r+1][ni], rings[r+1][i]])
bm_arm.faces.new(rings[0])
make_mesh_obj("Vambrace", bm_arm, mat_gold)

# 2. PULSO ARTICULADO (Wrist Cuffs)
for idx, (z_c, r_scale) in enumerate([(-0.45, 1.02), (-0.30, 1.05), (-0.15, 1.03)]):
    bm_cuff = bmesh.new()
    bmesh.ops.create_cone(bm_cuff, cap_ends=True, cap_tris=False, segments=20,
                          radius1=0.64 * r_scale, radius2=0.62 * r_scale, depth=0.12)
    for v in bm_cuff.verts:
        v.co.z += z_c
        v.co.y *= 0.82
    make_mesh_obj(f"Wrist_Cuff_{idx}", bm_cuff, mat_gold if idx != 1 else mat_dark)

# 3. DORSO DA MÃO (Hand Dorsal Plate - Broad Titan Carapace)
bm_dorsal = bmesh.new()
dorsal_sections = [
    # (Z, raio_x, raio_y, off_y)
    (-0.15, 0.64, 0.46, 0.0),
    ( 0.08, 0.70, 0.48, 0.02),
    ( 0.32, 0.74, 0.48, 0.04), # Centro onde fica a joia da mente
    ( 0.52, 0.76, 0.46, 0.05), # Linha das juntas
]
d_rings = []
for z, rx, ry, off_y in dorsal_sections:
    ring = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        ring.append(bm_dorsal.verts.new((rx * math.cos(ang), ry * math.sin(ang) + off_y, z)))
    d_rings.append(ring)
for r in range(len(dorsal_sections) - 1):
    for i in range(segs):
        ni = (i + 1) % segs
        bm_dorsal.faces.new([d_rings[r][i], d_rings[r][ni], d_rings[r+1][ni], d_rings[r+1][i]])
bm_dorsal.faces.new(d_rings[-1])
make_mesh_obj("Hand_Dorsal", bm_dorsal, mat_gold)

# 4. GEMA CABOCHÃO COM LUZ INTERNA
def add_gem(name, loc, rx, ry, rz, mat, rot=(0,0,0)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    for v in bm.verts:
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
    gem_obj = make_mesh_obj(name, bm, mat, subsurf=False)

    # Moldura dourada esculpida ao redor da gema
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

    # Luz de ponto interna
    l = bpy.data.lights.new(name + "_Light", 'POINT')
    l.color = mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3]
    l.energy = 50.0
    l.shadow_soft_size = 0.06
    lo = bpy.data.objects.new(name + "_LightObj", l)
    lo.location = loc
    lo.parent = root
    col.objects.link(lo)
    return gem_obj

# Joia da Mente (Grande cabochão no centro do dorso)
add_gem("Mind_Stone", (0.0, -0.48, 0.28), 0.22, 0.16, 0.12, mat_mind, rot=(math.radians(90), 0, 0))

# 4 Joias dos Nós dos Dedos
add_gem("Power_Stone", (0.44, -0.38, 0.54), 0.11, 0.09, 0.08, mat_power, rot=(math.radians(78), math.radians(20), 0))
add_gem("Reality_Stone", (0.16, -0.45, 0.58), 0.11, 0.09, 0.08, mat_reality, rot=(math.radians(82), math.radians(8), 0))
add_gem("Space_Stone", (-0.12, -0.47, 0.60), 0.12, 0.10, 0.08, mat_space, rot=(math.radians(85), 0, 0))
add_gem("Time_Stone", (-0.38, -0.43, 0.56), 0.11, 0.09, 0.08, mat_time, rot=(math.radians(80), math.radians(-14), 0))
# Joia da Alma no Polegar
add_gem("Soul_Stone", (-0.68, -0.16, 0.12), 0.11, 0.09, 0.08, mat_soul, rot=(math.radians(55), math.radians(-48), 0))

# 5. DEDOS FECHADOS EM PUNHO PODEROSO (Curled Titan Fist Armor)
# Em vez de apontar para cima, os dedos dobram para FRENTE e para BAIXO, fechando a mão!
def add_fist_finger(name, base_pos, yaw, seg_lengths, thicks):
    bm = bmesh.new()
    cur_p = list(base_pos)
    
    # Ângulos de flexão para cada uma das 3 falanges:
    # 1ª falange: dobra para frente (pitch -35°)
    # 2ª falange: dobra mais para baixo (pitch -85°)
    # 3ª falange: dobra para dentro da palma (pitch -135°)
    pitches = [-35, -85, -135]
    
    for seg_i, (length, thick, pitch_deg) in enumerate(zip(seg_lengths, thicks, pitches)):
        rad_pitch = math.radians(pitch_deg)
        rad_yaw = math.radians(yaw)

        # Junta escura
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=thick * 0.98)
        for v in bm.verts[-42:]:
            v.co.x += cur_p[0]
            v.co.y += cur_p[1]
            v.co.z += cur_p[2]

        # Vetor avanço
        # Frente é Y negativo, baixo é Z negativo
        dy = length * math.sin(rad_pitch) * math.cos(rad_yaw)
        dz = length * math.cos(rad_pitch)
        dx = length * math.sin(rad_yaw)

        next_p = [cur_p[0] + dx, cur_p[1] + dy, cur_p[2] + dz]
        mid_p = [(cur_p[0] + next_p[0])/2.0, (cur_p[1] + next_p[1])/2.0, (cur_p[2] + next_p[2])/2.0]

        # Casco de armadura largo com formato trapezoidal
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                              radius1=thick * 1.15, radius2=thick * 0.90, depth=length * 1.05)
        for v in bm.verts[-26:]:
            v.co.x *= 1.25 # placa larga
            v.co.x += mid_p[0]
            v.co.y += mid_p[1]
            v.co.z += mid_p[2]

        cur_p = next_p

    make_mesh_obj(name, bm, mat_gold)

# 4 Dedos dobrados em punho imponente
add_fist_finger("Finger_Pinky_Fist", (0.44, -0.36, 0.54), yaw=12, seg_lengths=[0.26, 0.22, 0.18], thicks=[0.12, 0.10, 0.08])
add_fist_finger("Finger_Ring_Fist", (0.16, -0.42, 0.58), yaw=4, seg_lengths=[0.30, 0.26, 0.20], thicks=[0.13, 0.11, 0.09])
add_fist_finger("Finger_Middle_Fist", (-0.12, -0.44, 0.60), yaw=-2, seg_lengths=[0.32, 0.28, 0.22], thicks=[0.14, 0.12, 0.095])
add_fist_finger("Finger_Index_Fist", (-0.38, -0.40, 0.56), yaw=-8, seg_lengths=[0.29, 0.25, 0.20], thicks=[0.13, 0.11, 0.09])

# Polegar dobrado sobre a lateral dos dedos (como um punho real)
bm_th = bmesh.new()
t_nodes = [
    [-0.66, -0.14, 0.10],
    [-0.68, -0.36, 0.24],
    [-0.56, -0.52, 0.36],
    [-0.34, -0.56, 0.42]
]
for i in range(len(t_nodes)-1):
    p1 = t_nodes[i]
    p2 = t_nodes[i+1]
    bmesh.ops.create_cone(bm_th, cap_ends=True, cap_tris=False, segments=12,
                          radius1=0.16 - i*0.03, radius2=0.13 - i*0.03, depth=0.26)
    mx = (p1[0]+p2[0])/2.0
    my = (p1[1]+p2[1])/2.0
    mz = (p1[2]+p2[2])/2.0
    for v in bm_th.verts[-26:]:
        v.co.x += mx
        v.co.y += my
        v.co.z += mz
make_mesh_obj("Finger_Thumb_Fist", bm_th, mat_gold)

# Iluminação
def add_l(name, ltype, loc, colr, energy):
    ld = bpy.data.lights.new(name, ltype)
    ld.color = colr
    ld.energy = energy
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    col.objects.link(lo)

add_l("KeyGold", 'AREA', (2.2, -3.5, 1.8), (1.0, 0.92, 0.75), 450)
add_l("FillCyan", 'AREA', (-2.6, -2.8, 0.5), (0.1, 0.88, 1.0), 220)
add_l("RimTop", 'SPOT', (0.0, 3.0, 3.2), (1.0, 0.95, 0.85), 600)
add_l("RimBottom", 'POINT', (0.5, 2.4, -2.0), (0.8, 0.3, 1.0), 250)

# Câmera
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 75
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = (0.0, -4.6, 0.05)
cam.rotation_euler = (math.radians(91.5), 0, 0)
col.objects.link(cam)
scene.camera = cam

# Test Render
test_img_path = os.path.join(RES_DRAWABLE, "test_fist.png")
scene.render.filepath = test_img_path
bpy.ops.render.render(write_still=True)
print(f"Test render concluído em: {test_img_path}")
