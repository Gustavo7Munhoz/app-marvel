import bpy
import bmesh
import math
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RES_DRAWABLE = os.path.join(MAIN_DIR, "res", "drawable-nodpi")

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

col = bpy.data.collections.new("CurledGauntlet")
scene.collection.children.link(col)
root = bpy.data.objects.new("Root", None)
col.objects.link(root)

# Materiais
mat_gold = bpy.data.materials.new("Gold")
mat_gold.use_nodes = True
b = mat_gold.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (0.86, 0.60, 0.14, 1.0)
b.inputs['Metallic'].default_value = 0.98
b.inputs['Roughness'].default_value = 0.18

mat_dark = bpy.data.materials.new("Dark")
mat_dark.use_nodes = True
b = mat_dark.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1.0)
b.inputs['Metallic'].default_value = 0.88
b.inputs['Roughness'].default_value = 0.35

def make_gem(colr, name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    bsdf = nodes['Principled BSDF']
    emit = nodes.new('ShaderNodeEmission')
    mix = nodes.new('ShaderNodeMixShader')
    bsdf.inputs['Base Color'].default_value = colr
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['IOR'].default_value = 1.77
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.95
    emit.inputs['Color'].default_value = colr
    emit.inputs['Strength'].default_value = 7.0
    mix.inputs['Fac'].default_value = 0.35
    m.node_tree.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    m.node_tree.links.new(emit.outputs['Emission'], mix.inputs[2])
    m.node_tree.links.new(mix.outputs['Shader'], nodes['Material Output'].inputs['Surface'])
    return m

mat_mind = make_gem((1.0, 0.85, 0.0, 1.0), "G_Mind")
mat_power = make_gem((0.70, 0.05, 1.0, 1.0), "G_Power")
mat_space = make_gem((0.05, 0.55, 1.0, 1.0), "G_Space")
mat_reality = make_gem((1.0, 0.03, 0.05, 1.0), "G_Reality")
mat_time = make_gem((0.05, 1.0, 0.25, 1.0), "G_Time")
mat_soul = make_gem((1.0, 0.45, 0.02, 1.0), "G_Soul")

def make_obj(name, bm, mat, sub=1):
    mesh = bpy.data.meshes.new(name + "_M")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    for p in mesh.polygons:
        p.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    col.objects.link(obj)
    obj.parent = root
    if sub > 0:
        s = obj.modifiers.new("Sub", 'SUBSURF')
        s.levels = sub
        s.render_levels = sub
    return obj

# 1. CORPO DA MANOPLA (Antebraço e Palma contínuos)
bm = bmesh.new()
N = 20
levels = [
    # (z, rx, ry, off_y)
    (-1.40, 0.45, 0.35, 0.00),
    (-1.15, 0.52, 0.40, 0.01),
    (-0.85, 0.48, 0.37, 0.01),
    (-0.55, 0.43, 0.33, 0.00),
    (-0.35, 0.41, 0.31, 0.00),
    (-0.15, 0.45, 0.33, 0.01),
    ( 0.08, 0.54, 0.35, 0.02),
    ( 0.25, 0.58, 0.33, 0.03),
    ( 0.40, 0.60, 0.28, 0.03), # crista dos nós
]
r_verts = []
for z, rx, ry, off_y in levels:
    ring = []
    for i in range(N):
        ang = 2 * math.pi * i / N
        ring.append(bm.verts.new((rx * math.cos(ang), ry * math.sin(ang) + off_y, z)))
    r_verts.append(ring)
for r in range(len(levels) - 1):
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([r_verts[r][i], r_verts[r][ni], r_verts[r+1][ni], r_verts[r+1][i]])
bm.faces.new(r_verts[0])
bm.faces.new(r_verts[-1])
make_obj("Body", bm, mat_gold)

# Frisos do pulso
for cz in [-0.55, -0.35]:
    bm_c = bmesh.new()
    bmesh.ops.create_cone(bm_c, cap_ends=True, cap_tris=False, segments=N,
                          radius1=0.45, radius2=0.43, depth=0.08)
    for v in bm_c.verts:
        v.co.z += cz
        v.co.y *= 0.77
    make_obj(f"Wrist_{cz}", bm_c, mat_gold)

# 2. JOIAS E ENGASTES
def add_gem(name, loc, rx, ry, rz, g_mat, rot):
    bm_b = bmesh.new()
    bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=16,
                          radius1=rx * 1.35, radius2=rx * 1.15, depth=rz * 0.85)
    for v in bm_b.verts:
        v.co.y *= (ry / rx)
        # Rot
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
    make_obj(name + "_B", bm_b, mat_gold)

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
    make_obj(name + "_G", bm_g, g_mat, sub=0)

    l = bpy.data.lights.new(name + "_L", 'POINT')
    l.color = g_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3]
    l.energy = 45.0
    l.shadow_soft_size = 0.04
    lo = bpy.data.objects.new(name + "_LO", l)
    lo.location = loc
    lo.parent = root
    col.objects.link(lo)

add_gem("Mind", (0.0, -0.34, 0.08), 0.16, 0.12, 0.08, mat_mind, (math.radians(90), 0, 0))
add_gem("Power",   ( 0.37, -0.20, 0.40), 0.08, 0.06, 0.05, mat_power,   (math.radians(75), math.radians( 16), 0))
add_gem("Reality", ( 0.13, -0.25, 0.43), 0.08, 0.06, 0.05, mat_reality, (math.radians(78), math.radians(  5), 0))
add_gem("Space",   (-0.13, -0.25, 0.43), 0.09, 0.07, 0.05, mat_space,   (math.radians(78), math.radians( -5), 0))
add_gem("Time",    (-0.37, -0.20, 0.40), 0.08, 0.06, 0.05, mat_time,    (math.radians(75), math.radians(-16), 0))
add_gem("Soul",    (-0.55, -0.13, 0.10), 0.08, 0.06, 0.05, mat_soul,    (math.radians(65), math.radians(-42), 0))

# 3. DEDOS CURVADOS EM GARRA PODEROSA PARA A FRENTE (TITAN CLAW POSE)
# Cada falange curva fortemente para frente e para baixo
def create_curled_finger(name, base_pos, yaw_deg, lengths, widths):
    bm_f = bmesh.new()
    cur_p = list(base_pos)
    
    # Falanges curvam para frente (-Y) e depois para baixo (-Z)
    pitches = [38.0, 75.0, 110.0]
    
    prev_ring = None
    for seg_i, (length, (wx, wy)) in enumerate(zip(lengths, widths)):
        rad_yaw = math.radians(yaw_deg)
        rad_pitch = math.radians(pitches[seg_i])

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

        # Avanço do osso da falange
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
    return make_obj(name, bm_f, mat_gold, sub=1)

# 4 Dedos curvados para a frente em pose de poder
create_curled_finger("F_Pinky",  ( 0.37, -0.15, 0.40), yaw_deg=8,
                     lengths=[0.24, 0.20, 0.16], widths=[(0.22, 0.18), (0.19, 0.15), (0.15, 0.12)])

create_curled_finger("F_Ring",   ( 0.13, -0.20, 0.43), yaw_deg=3,
                     lengths=[0.28, 0.24, 0.18], widths=[(0.24, 0.19), (0.21, 0.16), (0.17, 0.13)])

create_curled_finger("F_Middle", (-0.13, -0.20, 0.43), yaw_deg=-3,
                     lengths=[0.31, 0.26, 0.20], widths=[(0.25, 0.20), (0.22, 0.17), (0.18, 0.14)])

create_curled_finger("F_Index",  (-0.37, -0.15, 0.40), yaw_deg=-8,
                     lengths=[0.26, 0.22, 0.17], widths=[(0.23, 0.18), (0.20, 0.16), (0.16, 0.13)])

# Polegar curvado para dentro
bm_th = bmesh.new()
t_nodes = [
    [-0.46, -0.04, 0.00, 0.15],
    [-0.55, -0.12, 0.10, 0.14],
    [-0.52, -0.25, 0.18, 0.12],
    [-0.38, -0.34, 0.22, 0.07]
]
t_rings = []
for x, y, z, r in t_nodes:
    ring = []
    for i in range(8):
        ang = 2 * math.pi * i / 8
        ring.append(bm_th.verts.new((x + r*math.cos(ang), y + r*0.85*math.sin(ang), z)))
    t_rings.append(ring)
for r in range(len(t_nodes)-1):
    for i in range(8):
        ni = (i+1)%8
        bm_th.faces.new([t_rings[r][i], t_rings[r][ni], t_rings[r+1][ni], t_rings[r+1][i]])
bm_th.faces.new(t_rings[0])
bm_th.faces.new(t_rings[-1])
make_obj("F_Thumb", bm_th, mat_gold, sub=1)

# Iluminação
def add_l(name, ltype, loc, colr, energy):
    ld = bpy.data.lights.new(name, ltype)
    ld.color = colr
    ld.energy = energy
    if ltype in ('POINT', 'SPOT'):
        ld.shadow_soft_size = 0.15
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    col.objects.link(lo)

add_l("KeyGold", 'AREA', (2.0, -3.2, 1.8), (1.0, 0.90, 0.72), 420)
add_l("FillCyan", 'AREA', (-2.4, -2.4, 0.5), (0.15, 0.85, 1.0), 200)
add_l("RimTop", 'SPOT', (0.0, 2.8, 3.2), (1.0, 0.96, 0.90), 600)
add_l("RimBottom", 'POINT', (0.4, 2.0, -1.5), (0.8, 0.3, 1.0), 240)

# Câmera apontando ligeiramente de cima para baixo (Hero 3D Perspective)
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 55
cam = bpy.data.objects.new("Cam", cam_data)
# Câmera a Z=+0.40 olhando para Z=0.0 (inclinação de 15° para ver o dorso e as gemas)
cam.location = (0.0, -4.0, 0.40)
cam.rotation_euler = (math.radians(77), 0, 0)
col.objects.link(cam)
scene.camera = cam

test_path = os.path.join(RES_DRAWABLE, "test_claw.png")
scene.render.filepath = test_path
bpy.ops.render.render(write_still=True)
print(f"Render concluído: {test_path}")
