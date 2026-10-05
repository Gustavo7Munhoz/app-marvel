import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RES_DRAWABLE = os.path.join(MAIN_DIR, "res", "drawable-nodpi")
os.makedirs(RES_DRAWABLE, exist_ok=True)

# 1. Reset da cena
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Configuração de Render (Cycles com Denoising)
scene.render.engine = 'CYCLES'
try:
    scene.cycles.device = 'GPU'
except:
    scene.cycles.device = 'CPU'
scene.cycles.samples = 28
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.resolution_x = 512
scene.render.resolution_y = 512

col = bpy.data.collections.new("GauntletCollection")
scene.collection.children.link(col)
root = bpy.data.objects.new("GauntletRoot", None)
col.objects.link(root)

# 2. Materiais PBR
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
    bsdf.inputs['Base Color'].default_value = (0.22, 0.16, 0.10, 1.0)
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
    mix.inputs['Fac'].default_value = 0.32 # Brilho interno cósmico rico
    links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    links.new(emit.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return mat

mat_gold  = create_uru_gold_mat()
mat_dark  = create_dark_joint_mat()

mat_mind    = create_infinity_gem_mat("Gem_Mind",    (1.00, 0.65, 0.00), 3.5) # Âmbar Solar Intenso
mat_power   = create_infinity_gem_mat("Gem_Power",   (0.75, 0.02, 1.00), 2.8) # Violeta Cósmica
mat_space   = create_infinity_gem_mat("Gem_Space",   (0.00, 0.68, 1.00), 2.8) # Azul Elétrico
mat_reality = create_infinity_gem_mat("Gem_Reality", (1.00, 0.01, 0.05), 2.8) # Carmesim
mat_soul    = create_infinity_gem_mat("Gem_Soul",    (1.00, 0.38, 0.00), 2.8) # Laranja Fogo
mat_time    = create_infinity_gem_mat("Gem_Time",    (0.00, 1.00, 0.28), 2.8) # Verde Esmeralda

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

# =========================================================================
# 3. CORPO ANATÔMICO PROPORCIONAL (TITAN GAUNTLET SILHOUETTE)
# =========================================================================
def build_gauntlet_hull():
    bm = bmesh.new()
    N = 20

    # Chassi base contínuo (antebraço majestoso até a base dos nós)
    rings_spec = [
        # (z, rx, ry, off_y, dorsal_crest)
        (-1.15, 0.60, 0.44,  0.02, 0.04), # Borda larga do cotovelo
        (-0.95, 0.55, 0.41,  0.02, 0.05),
        (-0.70, 0.49, 0.37,  0.01, 0.05), # Meio do antebraço
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
            if math.sin(ang) < 0: # Dorso com crista
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

    # 2. Placa Central Saliente do Antebraço com Crista (Dorsal Spine Armor Plate)
    bm_spine = bmesh.new()
    bmesh.ops.create_cube(bm_spine, size=1.0)
    for v in bm_spine.verts:
        # Prisma chanfrado da armadura
        v.co.x *= (0.22 - (v.co.z + 0.5) * 0.06)
        v.co.y *= 0.09
        v.co.z *= 0.70
        if v.co.y < 0:
            v.co.y -= 0.03 * (1.0 - abs(v.co.x / 0.12))
        v.co.z -= 0.65
        v.co.y -= 0.38
    mesh_from_bm("Forearm_Dorsal_Armor", bm_spine, mat_gold, sub=0, smooth=True)

    # 3. Placas de Blindagem Lateral do Antebraço (Chanfradas, sem arredondar)
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

    # 4. Três Placas Laminadas Articuladas do Punho (Laminar Wrist Plates)
    for idx, z_wrist in enumerate([-0.24, -0.14, -0.04]):
        bm_w = bmesh.new()
        bmesh.ops.create_cone(bm_w, cap_ends=True, cap_tris=False, segments=24,
                              radius1=0.48 + idx * 0.03, radius2=0.45 + idx * 0.03, depth=0.07)
        for v in bm_w.verts:
            v.co.z += z_wrist
            v.co.y *= 0.82
        mesh_from_bm(f"Wrist_Lame_{idx}", bm_w, mat_gold, sub=1)

    # 5. Ponte Robusta dos Nós dos Dedos (Arco Transversal Superior)
    bm_kb = bmesh.new()
    bmesh.ops.create_cube(bm_kb, size=1.0)
    for v in bm_kb.verts:
        v.co.x *= 1.12
        v.co.y *= 0.22
        v.co.z *= 0.14
        v.co.y -= 0.08 * (1.0 - (v.co.x / 0.60)**2)
        v.co.z += 0.38
        v.co.y -= 0.34
    mesh_from_bm("Knuckle_Bridge_Bar", bm_kb, mat_gold, sub=1)

build_gauntlet_hull()

# =========================================================================
# 4. ENGASTES ESCULPIDOS E AS 6 JOIAS DO INFINITO (MCU LAYOUT)
# =========================================================================
def place_stone(name, pos, rx, ry, rz, rot_euler, gem_mat, light_rgb, energy=16.0):
    pos_v = Vector(pos)
    mat_rot = Euler(rot_euler, 'XYZ').to_matrix().to_4x4()

    # Engaste Dourado Saliente com Chanfro
    bm_b = bmesh.new()
    bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=16,
                          radius1=max(rx, ry) * 1.45, radius2=max(rx, ry) * 1.18, depth=rz * 1.3)
    for v in bm_b.verts:
        v.co.x *= (rx / max(rx, ry))
        v.co.y *= (ry / max(rx, ry))
        v.co = mat_rot @ v.co + pos_v
    mesh_from_bm(name + "_Bezel", bm_b, mat_gold, sub=1)

    # Joia Facetada Lapidada com Refração Translúcida
    bm_g = bmesh.new()
    bmesh.ops.create_icosphere(bm_g, subdivisions=2, radius=1.0)
    for v in bm_g.verts:
        v.co.x *= rx
        v.co.y *= ry
        v.co.z *= rz
        # Leve elevação do cabochão
        v.co = mat_rot @ v.co + pos_v
    mesh_from_bm(name + "_Gem", bm_g, gem_mat, sub=0, smooth=True)

    # Luz Cósmica Suave (não satura/estoura em branco)
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
    v.co.y *= 1.34 # Formato de lágrima/marquise
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

# 1. Joia da Mente (Grande, Âmbar Cristalino, Centro do Dorso)
place_stone("Mind", (0.0, -0.48, 0.12), rx=0.13, ry=0.17, rz=0.075,
            rot_euler=(math.radians(90), 0, 0), gem_mat=mat_mind,
            light_rgb=(1.0, 0.85, 0.05), energy=18.0)

# 2. Joias dos Nós dos Dedos (Proeminentes, 100% Desobstruídas, Anguladas para a Câmera)
# Indicador: Poder (Roxa / Violeta)
place_stone("Power",   (-0.37, -0.46, 0.42), rx=0.080, ry=0.070, rz=0.060,
            rot_euler=(math.radians(58), math.radians(-12), 0), gem_mat=mat_power,
            light_rgb=(0.78, 0.10, 1.0), energy=22.0)

# Médio: Espaço (Azul Cósmico Tesseract)
place_stone("Space",   (-0.13, -0.50, 0.44), rx=0.085, ry=0.075, rz=0.060,
            rot_euler=(math.radians(62), math.radians(-4), 0), gem_mat=mat_space,
            light_rgb=(0.05, 0.70, 1.0), energy=24.0)

# Anelar: Realidade (Vermelho Éter Carmesim)
place_stone("Reality", ( 0.13, -0.50, 0.44), rx=0.085, ry=0.075, rz=0.060,
            rot_euler=(math.radians(62), math.radians(4), 0), gem_mat=mat_reality,
            light_rgb=(1.00, 0.05, 0.10), energy=24.0)

# Mínimo: Alma (Laranja Fogo de Vormir)
place_stone("Soul",    ( 0.37, -0.46, 0.42), rx=0.080, ry=0.070, rz=0.060,
            rot_euler=(math.radians(58), math.radians(12), 0), gem_mat=mat_soul,
            light_rgb=(1.00, 0.50, 0.02), energy=22.0)

# 3. Polegar: Tempo (Verde Esmeralda - Frontal/Lateral, Totalmente Visível)
place_stone("Time",    (-0.54, -0.28, 0.16), rx=0.080, ry=0.070, rz=0.060,
            rot_euler=(math.radians(40), math.radians(-32), 0), gem_mat=mat_time,
            light_rgb=(0.05, 1.00, 0.35), energy=22.0)

# =========================================================================
# 5. DEDOS ARTICULADOS DE TITÃ (ARMORED SEGMENTS & POWER CLAW)
# =========================================================================
def build_phalanx_mesh(bm, length, width_x, width_y, taper=0.88, is_claw=False):
    num_pts = 8
    base_v = []
    tip_v  = []

    for i in range(num_pts):
        ang = 2 * math.pi * i / num_pts
        vx = width_x * 0.5 * math.cos(ang)
        vy = width_y * 0.5 * math.sin(ang)
        if math.sin(ang) < 0: # Dorso facetado de armadura
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

        # Articulação mecânica escura
        bm_j = bmesh.new()
        bmesh.ops.create_icosphere(bm_j, subdivisions=2, radius=wx * 0.36)
        for v in bm_j.verts:
            v.co = cur_mat @ v.co
        mesh_from_bm(f"{name}_Joint_{seg_idx}", bm_j, mat_dark, sub=1)

        # Placa Dourada
        bm_seg = bmesh.new()
        is_claw = (seg_idx == len(lengths) - 1)
        taper = 0.55 if is_claw else 0.88
        build_phalanx_mesh(bm_seg, length, wx, wy, taper=taper, is_claw=is_claw)
        for v in bm_seg.verts:
            v.co = cur_mat @ v.co
        mesh_from_bm(f"{name}_Plate_{seg_idx}", bm_seg, mat_gold, sub=1)

        cur_mat = cur_mat @ Matrix.Translation(Vector((0, 0, length)))

# Pose Imponente: Dedos começam ligeiramente atrás dos nós e curvam para a frente
finger_pitches = [52.0, 42.0, 36.0]

# Indicador
create_finger_kinematic("Index",  root_pos=(-0.37, -0.28, 0.36), yaw_deg=-8,
                        pitch_angles=finger_pitches, lengths=[0.24, 0.20, 0.16],
                        widths=[(0.23, 0.19), (0.20, 0.16), (0.16, 0.13)])

# Médio
create_finger_kinematic("Middle", root_pos=(-0.13, -0.32, 0.38), yaw_deg=-2,
                        pitch_angles=finger_pitches, lengths=[0.27, 0.23, 0.18],
                        widths=[(0.24, 0.20), (0.21, 0.17), (0.17, 0.14)])

# Anelar
create_finger_kinematic("Ring",   root_pos=( 0.13, -0.32, 0.38), yaw_deg=2,
                        pitch_angles=finger_pitches, lengths=[0.25, 0.21, 0.17],
                        widths=[(0.24, 0.20), (0.21, 0.17), (0.17, 0.14)])

# Mínimo
create_finger_kinematic("Pinky",  root_pos=( 0.37, -0.28, 0.36), yaw_deg=8,
                        pitch_angles=finger_pitches, lengths=[0.21, 0.18, 0.14],
                        widths=[(0.22, 0.18), (0.19, 0.15), (0.15, 0.12)])

# Polegar Poderoso com Placas de Armadura Articuladas e Joia do Tempo em Destaque
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

# =========================================================================
# 6. ESTÚDIO DE LUZ CINEMATOGRÁFICO (WARM GOLD STUDIO LIGHTING)
# =========================================================================
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

# Key Light Frontal/Superior (Ouro Quente e Brilhante)
create_studio_light("L_Key", 'AREA', (2.6, -4.0, 1.8), (1.0, 0.96, 0.88), 750.0, size=0.8)

# Fill Light Lateral Quente/Champagne (Evita qualquer tom verde no ouro)
create_studio_light("L_Fill", 'AREA', (-3.0, -3.2, 0.4), (1.0, 0.92, 0.82), 420.0, size=0.9)

# Rim Light de Contorno Superior (Branco Quente de Destaque)
create_studio_light("L_RimTop", 'SPOT', (0.0, 3.2, 3.8), (1.0, 0.98, 0.95), 900.0, size=0.1)

# Rim Light de Base (Realce do Antebraço)
create_studio_light("L_RimBottom", 'POINT', (1.5, 2.2, -1.8), (1.0, 0.85, 0.65), 350.0, size=0.3)

# =========================================================================
# 7. CÂMERA DINÂMICA HERO COM TARGET TRACKING
# =========================================================================
target_empty = bpy.data.objects.new("CamTarget", None)
target_empty.location = (0.0, -0.15, -0.35) # Centro exato da manopla completa
col.objects.link(target_empty)

cam_data = bpy.data.cameras.new("HeroCamera")
cam_data.lens = 62
cam = bpy.data.objects.new("HeroCamera", cam_data)
# Câmera afastada para enquadramento completo com margens confortáveis
cam.location = (0.0, -4.8, 0.15)
col.objects.link(cam)
scene.camera = cam

track = cam.constraints.new('TRACK_TO')
track.target = target_empty
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# Rotação da Manopla para Ângulo 3/4 Heroico e Imponente
root.rotation_euler = (math.radians(-6), math.radians(12), math.radians(-14))

# =========================================================================
# 8. RENDER DE TESTE
# =========================================================================
test_output = os.path.join(RES_DRAWABLE, "test_gauntlet_pro.png")
scene.render.filepath = test_output
print(f"Renderizando imagem de teste: {test_output}")
bpy.ops.render.render(write_still=True)
print("Render de Teste Concluído!")
