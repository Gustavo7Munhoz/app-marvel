import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math
import os
import shutil

print("=========================================================")
print("GERANDO MODELO 3D CANÔNICO DA MANOPLA DO THANOS (MCU)")
print(f"Blender: {bpy.app.version_string}")
print("=========================================================")

# 1. Configuração de Diretórios
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RES_DRAWABLE = os.path.join(MAIN_DIR, "res", "drawable-nodpi")
USER_DOCS_BLENDER = os.path.expanduser(r"~\Documents\Blender")
PROJECT_ROOT = os.path.abspath(os.path.join(MAIN_DIR, "..", ".."))

os.makedirs(RES_DRAWABLE, exist_ok=True)
os.makedirs(USER_DOCS_BLENDER, exist_ok=True)
os.makedirs(SCRIPT_DIR, exist_ok=True)

# 2. Reset de Fábrica
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Configuração de Render (Cycles com Denoising)
scene.render.engine = 'CYCLES'
try:
    scene.cycles.device = 'GPU'
except:
    scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.resolution_x = 400
scene.render.resolution_y = 400

col = bpy.data.collections.new("AuthenticThanosGauntlet")
scene.collection.children.link(col)
root = bpy.data.objects.new("GauntletRoot", None)
col.objects.link(root)

# 3. Materiais PBR de Alta Fidelidade MCU
def create_uru_gold_mat():
    mat = bpy.data.materials.new("Mat_Uru_Gold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (800, 0)

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (400, 0)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.17

    tex_noise = nodes.new('ShaderNodeTexNoise')
    tex_noise.location = (-400, 200)
    tex_noise.inputs['Scale'].default_value = 65.0
    tex_noise.inputs['Detail'].default_value = 4.0
    tex_noise.inputs['Roughness'].default_value = 0.50

    tex_voronoi = nodes.new('ShaderNodeTexVoronoi')
    tex_voronoi.location = (-400, -100)
    tex_voronoi.voronoi_dimensions = '3D'
    tex_voronoi.feature = 'DISTANCE_TO_EDGE'
    tex_voronoi.inputs['Scale'].default_value = 14.0

    mix_bump = nodes.new('ShaderNodeMix')
    mix_bump.location = (-150, 100)
    mix_bump.data_type = 'FLOAT'
    mix_bump.inputs[0].default_value = 0.35
    links.new(tex_noise.outputs['Fac'], mix_bump.inputs[4])
    links.new(tex_voronoi.outputs['Distance'], mix_bump.inputs[5])

    bump = nodes.new('ShaderNodeBump')
    bump.location = (100, 100)
    bump.inputs['Strength'].default_value = 0.09
    bump.inputs['Distance'].default_value = 0.02
    links.new(mix_bump.outputs['Result'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, -180)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.76, 0.54, 0.15, 1.0)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = (1.00, 0.82, 0.28, 1.0)
    links.new(tex_noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_dark_joint_mat():
    mat = bpy.data.materials.new("Mat_Joint_Dark")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.20, 0.15, 0.10, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.88
    bsdf.inputs['Roughness'].default_value = 0.32
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_infinity_gem_mat(name, color_rgb, emissive_boost=3.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (500, 0)

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 120)
    bsdf.inputs['Base Color'].default_value = (*color_rgb, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.03
    bsdf.inputs['IOR'].default_value = 1.77
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.35
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.35

    emit = nodes.new('ShaderNodeEmission')
    emit.location = (0, -120)
    emit.inputs['Color'].default_value = (*color_rgb, 1.0)
    emit.inputs['Strength'].default_value = emissive_boost

    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (250, 0)
    mix.inputs['Fac'].default_value = 0.32
    links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    links.new(emit.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return mat

mat_gold  = create_uru_gold_mat()
mat_dark  = create_dark_joint_mat()

mat_mind    = create_infinity_gem_mat("Gem_Mind",    (1.00, 0.65, 0.00), 3.5)
mat_power   = create_infinity_gem_mat("Gem_Power",   (0.75, 0.02, 1.00), 2.8)
mat_space   = create_infinity_gem_mat("Gem_Space",   (0.00, 0.68, 1.00), 2.8)
mat_reality = create_infinity_gem_mat("Gem_Reality", (1.00, 0.01, 0.05), 2.8)
mat_soul    = create_infinity_gem_mat("Gem_Soul",    (1.00, 0.38, 0.00), 2.8)
mat_time    = create_infinity_gem_mat("Gem_Time",    (0.00, 1.00, 0.28), 2.8)

def mesh_from_bm(name, bm, mat, sub=0, smooth=True):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    col.objects.link(obj)
    obj.parent = root
    if sub > 0:
        mod = obj.modifiers.new("Sub", 'SUBSURF')
        mod.levels = sub
        mod.render_levels = sub
    return obj

# 4. Construção do Casco e Blindagem do Antebraço
def build_gauntlet_hull():
    bm = bmesh.new()
    N = 20

    rings_spec = [
        # (z, rx, ry, off_y, dorsal_crest)
        (-1.15, 0.60, 0.44,  0.02, 0.04), # Cotovelo
        (-0.95, 0.55, 0.41,  0.02, 0.05),
        (-0.70, 0.49, 0.37,  0.01, 0.05), # Antebraço
        (-0.45, 0.44, 0.33,  0.00, 0.05), # Punho
        (-0.25, 0.42, 0.32,  0.00, 0.05),
        (-0.10, 0.44, 0.34, -0.01, 0.05), # Articulação do punho
        ( 0.04, 0.49, 0.36, -0.02, 0.06), # Palma
        ( 0.16, 0.55, 0.37, -0.03, 0.08), # Dorso (Joia da Mente)
        ( 0.28, 0.59, 0.35, -0.04, 0.07), # Ponte
        ( 0.38, 0.61, 0.30, -0.04, 0.04), # Topo dos nós
    ]

    all_rings = []
    for z, rx, ry, off_y, crest in rings_spec:
        ring = []
        for i in range(N):
            ang = 2 * math.pi * i / N
            x = rx * math.cos(ang)
            y = ry * math.sin(ang) + off_y
            if math.sin(ang) < 0:
                dist = abs(math.cos(ang))
                y -= crest * (1.0 - dist)
            ring.append(bm.verts.new((x, y, z)))
        all_rings.append(ring)

    for r in range(len(rings_spec) - 1):
        for i in range(N):
            ni = (i + 1) % N
            bm.faces.new([all_rings[r][i], all_rings[r][ni], all_rings[r+1][ni], all_rings[r+1][i]])

    bm.faces.new(all_rings[0])
    bm.faces.new(all_rings[-1])
    mesh_from_bm("Gauntlet_Base_Hull", bm, mat_gold, sub=1)

    # 1. Borda Flared do Cotovelo com Bisel Robusto
    bm_cuff = bmesh.new()
    bmesh.ops.create_cone(bm_cuff, cap_ends=True, cap_tris=False, segments=24,
                          radius1=0.65, radius2=0.60, depth=0.12)
    for v in bm_cuff.verts:
        v.co.z -= 1.13
        v.co.y *= 0.82
    mesh_from_bm("Elbow_Cuff_Rim", bm_cuff, mat_gold, sub=1)

    # 2. Placa Central Saliente do Antebraço com Crista
    bm_spine = bmesh.new()
    bmesh.ops.create_cube(bm_spine, size=1.0)
    for v in bm_spine.verts:
        v.co.x *= (0.22 - (v.co.z + 0.5) * 0.06)
        v.co.y *= 0.09
        v.co.z *= 0.70
        if v.co.y < 0:
            v.co.y -= 0.03 * (1.0 - abs(v.co.x / 0.12))
        v.co.z -= 0.65
        v.co.y -= 0.38
    mesh_from_bm("Forearm_Dorsal_Armor", bm_spine, mat_gold, sub=0, smooth=True)

    # 3. Placas de Blindagem Lateral do Antebraço
    for side in [-1, 1]:
        bm_lat = bmesh.new()
        bmesh.ops.create_cube(bm_lat, size=1.0)
        for v in bm_lat.verts:
            v.co.x *= 0.14
            v.co.y *= 0.28
            v.co.z *= 0.68
            v.co.x += side * 0.44
            v.co.z -= 0.65
            v.co.y -= 0.04
        mesh_from_bm(f"Forearm_SideArmor_{side}", bm_lat, mat_gold, sub=0, smooth=True)

    # 4. Três Placas Laminadas Articuladas do Punho
    for idx, z_wrist in enumerate([-0.24, -0.14, -0.04]):
        bm_w = bmesh.new()
        bmesh.ops.create_cone(bm_w, cap_ends=True, cap_tris=False, segments=24,
                              radius1=0.48 + idx * 0.03, radius2=0.45 + idx * 0.03, depth=0.07)
        for v in bm_w.verts:
            v.co.z += z_wrist
            v.co.y *= 0.82
        mesh_from_bm(f"Wrist_Lame_{idx}", bm_w, mat_gold, sub=1)

    # 5. Ponte Robusta dos Nós dos Dedos
    bm_kb = bmesh.new()
    bmesh.ops.create_cube(bm_kb, size=1.0)
    for v in bm_kb.verts:
        v.co.x *= 1.12
        v.co.y *= 0.20
        v.co.z *= 0.14
        v.co.y -= 0.08 * (1.0 - (v.co.x / 0.60)**2)
        v.co.z += 0.38
        v.co.y -= 0.34
    mesh_from_bm("Knuckle_Bridge_Bar", bm_kb, mat_gold, sub=1)

build_gauntlet_hull()

# 5. As 6 Joias do Infinito e Engastes Dourados
def place_stone(name, pos, rx, ry, rz, rot_euler, gem_mat, light_rgb, energy=16.0):
    pos_v = Vector(pos)
    mat_rot = Euler(rot_euler, 'XYZ').to_matrix().to_4x4()

    bm_b = bmesh.new()
    bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=16,
                          radius1=max(rx, ry) * 1.45, radius2=max(rx, ry) * 1.18, depth=rz * 1.3)
    for v in bm_b.verts:
        v.co.x *= (rx / max(rx, ry))
        v.co.y *= (ry / max(rx, ry))
        v.co = mat_rot @ v.co + pos_v
    mesh_from_bm(name + "_Bezel", bm_b, mat_gold, sub=1)

    bm_g = bmesh.new()
    bmesh.ops.create_icosphere(bm_g, subdivisions=2, radius=1.0)
    for v in bm_g.verts:
        v.co.x *= rx
        v.co.y *= ry
        v.co.z *= rz
        v.co = mat_rot @ v.co + pos_v
    mesh_from_bm(name + "_Gem", bm_g, gem_mat, sub=0, smooth=True)

    l_data = bpy.data.lights.new(name + "_Light", 'POINT')
    l_data.color = light_rgb
    l_data.energy = energy
    l_data.shadow_soft_size = 0.04
    l_obj = bpy.data.objects.new(name + "_LightObj", l_data)
    l_obj.location = pos_v
    l_obj.parent = root
    col.objects.link(l_obj)

# Moldura Estelar em Alto-Relevo da Joia da Mente
bm_mind_plate = bmesh.new()
bmesh.ops.create_cone(bm_mind_plate, cap_ends=True, cap_tris=False, segments=24,
                      radius1=0.25, radius2=0.22, depth=0.06)
for v in bm_mind_plate.verts:
    v.co.y *= 1.34
    v.co.z, v.co.y = -v.co.y, v.co.z
    v.co.y -= 0.44
    v.co.z += 0.12
mesh_from_bm("Mind_Star_Plate", bm_mind_plate, mat_gold, sub=1)

# Raios de Filigrana Dourada em torno da Joia da Mente
for ray_i in range(8):
    ang = 2 * math.pi * ray_i / 8
    bm_ray = bmesh.new()
    bmesh.ops.create_cube(bm_ray, size=1.0)
    for v in bm_ray.verts:
        v.co.x *= 0.022
        v.co.y *= 0.18
        v.co.z *= 0.025
        vx = v.co.x * math.cos(ang) - v.co.y * math.sin(ang)
        vy = v.co.x * math.sin(ang) + v.co.y * math.cos(ang)
        v.co.x = vx + 0.20 * math.cos(ang)
        v.co.z = vy + 0.20 * math.sin(ang) + 0.12
        v.co.y = -0.45
    mesh_from_bm(f"Mind_Ray_{ray_i}", bm_ray, mat_gold, sub=1)

# 1. Joia da Mente (Centro do Dorso)
place_stone("Mind", (0.0, -0.48, 0.12), rx=0.13, ry=0.17, rz=0.075,
            rot_euler=(math.radians(90), 0, 0), gem_mat=mat_mind,
            light_rgb=(1.0, 0.85, 0.05), energy=18.0)

# 2. Joias dos Nós dos Dedos (100% Desobstruídas no Topo)
place_stone("Power",   (-0.37, -0.46, 0.42), rx=0.080, ry=0.070, rz=0.060,
            rot_euler=(math.radians(58), math.radians(-12), 0), gem_mat=mat_power,
            light_rgb=(0.78, 0.10, 1.0), energy=20.0)

place_stone("Space",   (-0.13, -0.50, 0.44), rx=0.085, ry=0.075, rz=0.060,
            rot_euler=(math.radians(62), math.radians(-4), 0), gem_mat=mat_space,
            light_rgb=(0.05, 0.70, 1.0), energy=22.0)

place_stone("Reality", ( 0.13, -0.50, 0.44), rx=0.085, ry=0.075, rz=0.060,
            rot_euler=(math.radians(62), math.radians(4), 0), gem_mat=mat_reality,
            light_rgb=(1.00, 0.05, 0.10), energy=22.0)

place_stone("Soul",    ( 0.37, -0.46, 0.42), rx=0.080, ry=0.070, rz=0.060,
            rot_euler=(math.radians(58), math.radians(12), 0), gem_mat=mat_soul,
            light_rgb=(1.00, 0.50, 0.02), energy=20.0)

# 3. Joia do Tempo no Polegar
place_stone("Time",    (-0.54, -0.28, 0.16), rx=0.080, ry=0.070, rz=0.060,
            rot_euler=(math.radians(40), math.radians(-32), 0), gem_mat=mat_time,
            light_rgb=(0.05, 1.00, 0.35), energy=20.0)

# 6. Dedos Articulados de Titã
def build_phalanx_mesh(bm, length, width_x, width_y, taper=0.88, is_claw=False):
    num_pts = 8
    base_v = []
    tip_v  = []

    for i in range(num_pts):
        ang = 2 * math.pi * i / num_pts
        vx = width_x * 0.5 * math.cos(ang)
        vy = width_y * 0.5 * math.sin(ang)
        if math.sin(ang) < 0:
            vy *= 1.25
        base_v.append(bm.verts.new((vx, vy, 0.0)))
        tip_v.append(bm.verts.new((vx * taper, vy * taper, length)))

    for i in range(num_pts):
        ni = (i + 1) % num_pts
        bm.faces.new([base_v[i], base_v[ni], tip_v[ni], tip_v[i]])

    bm.faces.new(base_v)
    if is_claw:
        claw_tip = bm.verts.new((0, -width_y * 0.15, length + 0.06))
        for i in range(num_pts):
            ni = (i + 1) % num_pts
            bm.faces.new([tip_v[i], tip_v[ni], claw_tip])
    else:
        bm.faces.new(tip_v)

def create_finger_kinematic(name, root_pos, yaw_deg, pitch_angles, lengths, widths):
    cur_mat = Matrix.Translation(Vector(root_pos)) @ Matrix.Rotation(math.radians(yaw_deg), 4, 'Z')

    for seg_idx, (p_angle, length, (wx, wy)) in enumerate(zip(pitch_angles, lengths, widths)):
        cur_mat = cur_mat @ Matrix.Rotation(math.radians(p_angle), 4, 'X')

        bm_j = bmesh.new()
        bmesh.ops.create_icosphere(bm_j, subdivisions=2, radius=wx * 0.36)
        for v in bm_j.verts:
            v.co = cur_mat @ v.co
        mesh_from_bm(f"{name}_Joint_{seg_idx}", bm_j, mat_dark, sub=1)

        bm_seg = bmesh.new()
        is_claw = (seg_idx == len(lengths) - 1)
        taper = 0.55 if is_claw else 0.88
        build_phalanx_mesh(bm_seg, length, wx, wy, taper=taper, is_claw=is_claw)
        for v in bm_seg.verts:
            v.co = cur_mat @ v.co
        mesh_from_bm(f"{name}_Plate_{seg_idx}", bm_seg, mat_gold, sub=1)

        cur_mat = cur_mat @ Matrix.Translation(Vector((0, 0, length)))

finger_pitches = [52.0, 42.0, 36.0]

create_finger_kinematic("Index",  root_pos=(-0.37, -0.28, 0.36), yaw_deg=-8,
                        pitch_angles=finger_pitches, lengths=[0.24, 0.20, 0.16],
                        widths=[(0.23, 0.19), (0.20, 0.16), (0.16, 0.13)])

create_finger_kinematic("Middle", root_pos=(-0.13, -0.32, 0.38), yaw_deg=-2,
                        pitch_angles=finger_pitches, lengths=[0.27, 0.23, 0.18],
                        widths=[(0.24, 0.20), (0.21, 0.17), (0.17, 0.14)])

create_finger_kinematic("Ring",   root_pos=( 0.13, -0.32, 0.38), yaw_deg=2,
                        pitch_angles=finger_pitches, lengths=[0.25, 0.21, 0.17],
                        widths=[(0.24, 0.20), (0.21, 0.17), (0.17, 0.14)])

create_finger_kinematic("Pinky",  root_pos=( 0.37, -0.28, 0.36), yaw_deg=8,
                        pitch_angles=finger_pitches, lengths=[0.21, 0.18, 0.14],
                        widths=[(0.22, 0.18), (0.19, 0.15), (0.15, 0.12)])

def create_thumb_kinematic():
    thumb_mat = Matrix.Translation(Vector((-0.46, -0.10, 0.10))) @ \
                Matrix.Rotation(math.radians(-25), 4, 'Z') @ \
                Matrix.Rotation(math.radians(25), 4, 'Y') @ \
                Matrix.Rotation(math.radians(28), 4, 'X')

    thumb_pitches = [26.0, 36.0]
    thumb_lens    = [0.24, 0.20]
    thumb_widths  = [(0.25, 0.20), (0.20, 0.15)]

    cur_m = thumb_mat
    for seg_idx, (pitch, length, (wx, wy)) in enumerate(zip(thumb_pitches, thumb_lens, thumb_widths)):
        cur_m = cur_m @ Matrix.Rotation(math.radians(pitch), 4, 'X')

        bm_j = bmesh.new()
        bmesh.ops.create_icosphere(bm_j, subdivisions=2, radius=wx * 0.36)
        for v in bm_j.verts:
            v.co = cur_m @ v.co
        mesh_from_bm(f"Thumb_Joint_{seg_idx}", bm_j, mat_dark, sub=1)

        bm_seg = bmesh.new()
        is_claw = (seg_idx == len(thumb_lens) - 1)
        taper = 0.50 if is_claw else 0.85
        build_phalanx_mesh(bm_seg, length, wx, wy, taper=taper, is_claw=is_claw)
        for v in bm_seg.verts:
            v.co = cur_m @ v.co
        mesh_from_bm(f"Thumb_Plate_{seg_idx}", bm_seg, mat_gold, sub=1)

        cur_m = cur_m @ Matrix.Translation(Vector((0, 0, length)))

create_thumb_kinematic()

# 7. Iluminação de Estúdio Dourado (Warm Studio Lighting)
def create_studio_light(name, ltype, loc, color, energy, size=0.25):
    ld = bpy.data.lights.new(name, ltype)
    ld.color = color
    ld.energy = energy
    if ltype in ('POINT', 'SPOT', 'AREA'):
        ld.shadow_soft_size = size
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    col.objects.link(lo)
    return lo

create_studio_light("L_Key", 'AREA', (2.6, -4.0, 1.8), (1.0, 0.96, 0.88), 750.0, size=0.8)
create_studio_light("L_Fill", 'AREA', (-3.0, -3.2, 0.4), (1.0, 0.92, 0.82), 420.0, size=0.9)
create_studio_light("L_RimTop", 'SPOT', (0.0, 3.2, 3.8), (1.0, 0.98, 0.95), 900.0, size=0.1)
create_studio_light("L_RimBottom", 'POINT', (1.5, 2.2, -1.8), (1.0, 0.85, 0.65), 350.0, size=0.3)

# 8. Câmera com Target Tracking
target_empty = bpy.data.objects.new("CamTarget", None)
target_empty.location = (0.0, -0.15, -0.35)
col.objects.link(target_empty)

cam_data = bpy.data.cameras.new("HeroCamera")
cam_data.lens = 62
cam = bpy.data.objects.new("HeroCamera", cam_data)
cam.location = (0.0, -4.8, 0.15)
col.objects.link(cam)
scene.camera = cam

track = cam.constraints.new('TRACK_TO')
track.target = target_empty
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# 9. Salvar Arquivo .BLEND no Computador do Usuário e no Projeto
blend_user_docs = os.path.join(USER_DOCS_BLENDER, "Manopla_Thanos.blend")
blend_project = os.path.join(SCRIPT_DIR, "manopla_thanos.blend")

bpy.ops.wm.save_as_mainfile(filepath=blend_project)
print(f"Salvo arquivo .blend do projeto: {blend_project}")
bpy.ops.wm.save_as_mainfile(filepath=blend_user_docs)
print(f"Salvo arquivo .blend para o usuário em: {blend_user_docs}")

# 10. Exportar GLB (GLTF Binário)
glb_path = os.path.join(SCRIPT_DIR, "manopla_thanos.glb")
try:
    bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', export_yup=True)
    print(f"Exportado GLB com sucesso em: {glb_path}")
except Exception as e:
    print(f"Aviso GLB: {e}")

# 11. Renderizar os 24 Frames 360° para o App Android
NUM_FRAMES = 24
print(f"\nIniciando renderização de {NUM_FRAMES} frames da rotação 360°...")
scene.render.resolution_x = 360
scene.render.resolution_y = 360

for f in range(NUM_FRAMES):
    angle_deg = f * (360.0 / NUM_FRAMES)
    root.rotation_euler = (math.radians(-6), math.radians(6), math.radians(angle_deg))

    frame_name = f"manopla_3d_{f:02d}.png"
    frame_path = os.path.join(RES_DRAWABLE, frame_name)
    scene.render.filepath = frame_path

    bpy.ops.render.render(write_still=True)
    print(f"Frame {f+1:02d}/{NUM_FRAMES} ({angle_deg:.0f}°) -> {frame_name}")

# 12. Renderizar Frame Hero de Alta Resolução (720x720)
print("\nRenderizando frame Hero em alta resolução...")
scene.render.resolution_x = 720
scene.render.resolution_y = 720
root.rotation_euler = (math.radians(-6), math.radians(12), math.radians(-14))
hero_path = os.path.join(RES_DRAWABLE, "manopla_hero_3d.png")
scene.render.filepath = hero_path
bpy.ops.render.render(write_still=True)
print(f"Hero render concluído -> {hero_path}")

print("\n=======================================================")
print("PROCESSO CONCLUÍDO COM SUCESSO TOTAL!")
print(f"1. .blend salvo em: {blend_user_docs}")
print(f"2. 24 Frames 360° em: {RES_DRAWABLE}")
print(f"3. Hero Banner em: {hero_path}")
print("=======================================================")
