import bpy
import bmesh
import math
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RES_DRAWABLE = os.path.join(MAIN_DIR, "res", "drawable-nodpi")
os.makedirs(RES_DRAWABLE, exist_ok=True)

# 1. Cena limpa e setup
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

col = bpy.data.collections.new("MCU_Gauntlet_V3")
scene.collection.children.link(col)
root = bpy.data.objects.new("Gauntlet_Root", None)
col.objects.link(root)

# 2. Materiais
def make_gold_material():
    mat = bpy.data.materials.new("Mat_Uru_Gold")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    # Tom rico de ouro envelhecido do MCU (Avengers: Infinity War)
    bsdf.inputs['Base Color'].default_value = (0.84, 0.58, 0.12, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.20
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.85
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.85
    return mat

def make_dark_joint_material():
    mat = bpy.data.materials.new("Mat_Dark_Joints")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (0.12, 0.10, 0.08, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.35
    return mat

def make_gem_material(color, name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    out = nodes['Material Output']
    bsdf = nodes['Principled BSDF']
    emit = nodes.new('ShaderNodeEmission')
    mix = nodes.new('ShaderNodeMixShader')

    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.03
    bsdf.inputs['IOR'].default_value = 1.77
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.94
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.94

    emit.inputs['Color'].default_value = color
    emit.inputs['Strength'].default_value = 6.0
    mix.inputs['Fac'].default_value = 0.35

    mat.node_tree.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    mat.node_tree.links.new(emit.outputs['Emission'], mix.inputs[2])
    mat.node_tree.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return mat

mat_gold = make_gold_material()
mat_dark = make_dark_joint_material()

mat_mind    = make_gem_material((1.0, 0.85, 0.0, 1.0), "MatMind")
mat_power   = make_gem_material((0.68, 0.05, 1.0, 1.0), "MatPower")
mat_space   = make_gem_material((0.05, 0.55, 1.0, 1.0), "MatSpace")
mat_reality = make_gem_material((1.0, 0.03, 0.05, 1.0), "MatReality")
mat_time    = make_gem_material((0.05, 1.0, 0.25, 1.0), "MatTime")
mat_soul    = make_gem_material((1.0, 0.45, 0.02, 1.0), "MatSoul")

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

# 3. ANTEBRAÇO E BRACELETE CONTINUOS (SEM BURACOS)
# Construído como anéis contínuos de baixo (-2.2) até o pulso (-0.4)
bm_arm = bmesh.new()
segs = 24
arm_rings_data = [
    # (z, rx, ry, off_y)
    (-2.2, 0.72, 0.52, 0.02),
    (-1.8, 0.75, 0.55, 0.03), # crista muscular do antebraço
    (-1.4, 0.72, 0.53, 0.02),
    (-1.0, 0.68, 0.50, 0.01),
    (-0.7, 0.64, 0.48, 0.00),
    (-0.45, 0.61, 0.46, 0.00) # encontro perfeito com o pulso
]
arm_v_rings = []
for z, rx, ry, off_y in arm_rings_data:
    ring = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        x = rx * math.cos(ang)
        y = ry * math.sin(ang) + off_y
        ring.append(bm_arm.verts.new((x, y, z)))
    arm_v_rings.append(ring)

for r in range(len(arm_rings_data) - 1):
    for i in range(segs):
        ni = (i + 1) % segs
        bm_arm.faces.new([arm_v_rings[r][i], arm_v_rings[r][ni], arm_v_rings[r+1][ni], arm_v_rings[r+1][i]])
bm_arm.faces.new(arm_v_rings[0]) # tampa inferior
make_mesh_obj("Gauntlet_Vambrace", bm_arm, mat_gold)

# Frisos metálicos sobrepostos no pulso (interlocked armor cuffs)
for cuff_z, scale in [(-0.60, 1.03), (-0.45, 1.05)]:
    bm_cuff = bmesh.new()
    bmesh.ops.create_cone(bm_cuff, cap_ends=True, cap_tris=False, segments=segs,
                          radius1=0.63 * scale, radius2=0.61 * scale, depth=0.10)
    for v in bm_cuff.verts:
        v.co.z += cuff_z
        v.co.y *= 0.82
    make_mesh_obj(f"Cuff_{cuff_z}", bm_cuff, mat_dark if cuff_z == -0.60 else mat_gold, subsurf=True)

# 4. PALMA E DORSO DA MÃO (Hand Metacarpal Carapace)
# Conecta diretamente do pulso (-0.45) até a base dos nós dos dedos (+0.40)
bm_hand = bmesh.new()
hand_rings_data = [
    # (z, rx, ry, off_y)
    (-0.45, 0.61, 0.46, 0.00), # encaixe exato no pulso
    (-0.25, 0.65, 0.48, 0.02),
    ( 0.00, 0.72, 0.50, 0.04), # centro do dorso
    ( 0.20, 0.76, 0.48, 0.05), # nível da joia da mente
    ( 0.40, 0.78, 0.44, 0.06), # crista dos 4 nós dos dedos
]
hand_v_rings = []
for z, rx, ry, off_y in hand_rings_data:
    ring = []
    for i in range(segs):
        ang = 2 * math.pi * i / segs
        x = rx * math.cos(ang)
        y = ry * math.sin(ang) + off_y
        ring.append(bm_hand.verts.new((x, y, z)))
    hand_v_rings.append(ring)

for r in range(len(hand_rings_data) - 1):
    for i in range(segs):
        ni = (i + 1) % segs
        bm_hand.faces.new([hand_v_rings[r][i], hand_v_rings[r][ni], hand_v_rings[r+1][ni], hand_v_rings[r+1][i]])
bm_hand.faces.new(hand_v_rings[-1]) # topo dos nós
make_mesh_obj("Gauntlet_Hand_Body", bm_hand, mat_gold)

# 5. AS 6 JOIAS DO INFINITO EM CABOCHÃO FACETADO COM ENGASTES DOURADOS
def add_cabochon_gem(name, loc, rx, ry, rz, mat, rot=(0,0,0)):
    # Gema cabochão
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
    make_mesh_obj(name, bm_g, mat, subsurf=False)

    # Moldura / Engaste de ouro esculpido
    bm_b = bmesh.new()
    bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=16,
                          radius1=rx * 1.30, radius2=rx * 1.10, depth=rz * 0.8)
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
    make_mesh_obj(name + "_Bezel", bm_b, mat_gold, subsurf=True)

    # Luz de ponto para emitir o reflexo cósmico colorido no metal Uru
    l = bpy.data.lights.new(name + "_Light", 'POINT')
    l.color = mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3]
    l.energy = 55.0
    l.shadow_soft_size = 0.05
    lo = bpy.data.objects.new(name + "_LightObj", l)
    lo.location = loc
    lo.parent = root
    col.objects.link(lo)

# 5.1 Joia da Mente (Grande oval cabochão central no dorso)
add_cabochon_gem("Gem_Mind", (0.0, -0.44, 0.18), 0.22, 0.16, 0.10, mat_mind, rot=(math.radians(90), 0, 0))

# 5.2 4 Joias dos Nós dos Dedos (Alinhadas perfeitamente na crista dos nós)
add_cabochon_gem("Gem_Power",   ( 0.44, -0.34, 0.42), 0.10, 0.08, 0.07, mat_power,   rot=(math.radians(80), math.radians( 18), 0))
add_cabochon_gem("Gem_Reality", ( 0.15, -0.39, 0.46), 0.10, 0.08, 0.07, mat_reality, rot=(math.radians(85), math.radians(  6), 0))
add_cabochon_gem("Gem_Space",   (-0.15, -0.40, 0.46), 0.11, 0.09, 0.07, mat_space,   rot=(math.radians(85), math.radians( -6), 0))
add_cabochon_gem("Gem_Time",    (-0.44, -0.35, 0.42), 0.10, 0.08, 0.07, mat_time,    rot=(math.radians(80), math.radians(-18), 0))

# 5.3 Joia da Alma (Lateral do Polegar)
add_cabochon_gem("Gem_Soul",    (-0.64, -0.16, 0.05), 0.11, 0.09, 0.07, mat_soul,    rot=(math.radians(65), math.radians(-45), 0))

# 6. DEDOS ARTICULADOS ROBUSTOS DE TITÃ (Largos, contíguos e levemente flexionados)
# Largura dos dedos: ~0.28 cada um, para encostarem lado a lado sem vãos feios!
def create_robust_finger(name, base_pos, yaw_deg, lengths, widths):
    bm = bmesh.new()
    cur_p = list(base_pos)
    
    # 3 falanges anatômicas com curvatura suave e imponente para frente
    curvatures = [18.0, 22.0, 25.0] # inclina para frente (-Y) e sobe suavemente
    
    for seg_i, (length, (wx, wy)) in enumerate(zip(lengths, widths)):
        # Placa de armadura esculpida
        rad_yaw = math.radians(yaw_deg)
        rad_pitch = math.radians(sum(curvatures[:seg_i+1]))
        
        # Vetor avanço ao longo do dedo
        # Dedo aponta para cima (+Z) com leve flexão para frente (-Y)
        dz = length * math.cos(rad_pitch)
        dy = -length * math.sin(rad_pitch)
        dx = length * math.sin(rad_yaw)
        
        next_p = [cur_p[0] + dx, cur_p[1] + dy, cur_p[2] + dz]
        mid_p = [(cur_p[0] + next_p[0])/2.0, (cur_p[1] + next_p[1])/2.0, (cur_p[2] + next_p[2])/2.0]
        
        # Cria segmento de armadura chanfrada com topo abobadado
        w_top = wx * (0.85 if seg_i < 2 else 0.45) # afunila em garra elegante na ponta
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                              radius1=wx * 0.5, radius2=w_top * 0.5, depth=length * 1.02)
        
        # Achata em Y e alinha com a junta
        for v in bm.verts[-26:]:
            v.co.y *= (wy / wx)
            v.co.x += mid_p[0]
            v.co.y += mid_p[1]
            v.co.z += mid_p[2]
            
        cur_p = next_p

    make_mesh_obj(name, bm, mat_gold, subsurf=True)

# 4 Dedos largos da manopla: encostam uns nos outros formando uma mão maciça de titã
# Mínimo (Pinky)
create_robust_finger("Finger_Pinky", (0.44, -0.30, 0.42), yaw_deg=8,
                     lengths=[0.24, 0.20, 0.17], widths=[(0.26, 0.22), (0.23, 0.19), (0.20, 0.16)])

# Anelar (Ring)
create_robust_finger("Finger_Ring", (0.15, -0.34, 0.46), yaw_deg=3,
                     lengths=[0.30, 0.25, 0.20], widths=[(0.28, 0.23), (0.25, 0.20), (0.21, 0.17)])

# Médio (Middle) - Mais longo e dominante
create_robust_finger("Finger_Middle", (-0.15, -0.35, 0.46), yaw_deg=-2,
                     lengths=[0.34, 0.28, 0.22], widths=[(0.29, 0.24), (0.26, 0.21), (0.22, 0.17)])

# Indicador (Index)
create_robust_finger("Finger_Index", (-0.44, -0.31, 0.42), yaw_deg=-7,
                     lengths=[0.29, 0.24, 0.19], widths=[(0.27, 0.23), (0.24, 0.20), (0.20, 0.16)])

# Polegar Poderoso de Titã (Curvado na lateral da mão)
bm_thumb = bmesh.new()
t_nodes = [
    [-0.64, -0.10, 0.05],
    [-0.68, -0.22, 0.18],
    [-0.62, -0.34, 0.30],
    [-0.50, -0.40, 0.38]
]
for i in range(len(t_nodes)-1):
    p1 = t_nodes[i]
    p2 = t_nodes[i+1]
    bmesh.ops.create_cone(bm_thumb, cap_ends=True, cap_tris=False, segments=12,
                          radius1=0.17 - i*0.03, radius2=0.14 - i*0.03, depth=0.22)
    mx = (p1[0]+p2[0])/2.0
    my = (p1[1]+p2[1])/2.0
    mz = (p1[2]+p2[2])/2.0
    for v in bm_thumb.verts[-26:]:
        v.co.x += mx
        v.co.y += my
        v.co.z += mz
make_mesh_obj("Finger_Thumb", bm_thumb, mat_gold, subsurf=True)

# 7. ILUMINAÇÃO DE CINEMA MCU
def add_light(name, ltype, loc, color, energy):
    ldata = bpy.data.lights.new(name, ltype)
    ldata.color = color
    ldata.energy = energy
    if ltype in ('POINT', 'SPOT'):
        ldata.shadow_soft_size = 0.15
    lobj = bpy.data.objects.new(name, ldata)
    lobj.location = loc
    col.objects.link(lobj)

add_light("KeyLight_Gold", 'AREA', (2.2, -3.4, 1.6), (1.0, 0.90, 0.72), 420)
add_light("FillLight_Cyan", 'AREA', (-2.5, -2.6, 0.4), (0.1, 0.85, 1.0), 200)
add_light("RimLight_Top", 'SPOT', (0.0, 2.8, 3.2), (1.0, 0.95, 0.88), 650)
add_light("RimLight_Bottom", 'POINT', (0.5, 2.2, -1.8), (0.7, 0.3, 1.0), 240)

# Câmera com enquadramento perfeito (Sem cortar e sem perspectiva distorcida)
cam_data = bpy.data.cameras.new("Gauntlet_Camera")
cam_data.lens = 68
cam = bpy.data.objects.new("Gauntlet_Camera", cam_data)
cam.location = (0.0, -4.4, -0.40)
cam.rotation_euler = (math.radians(88), 0, 0)
col.objects.link(cam)
scene.camera = cam

# Test render
test_img_path = os.path.join(RES_DRAWABLE, "test_gauntlet_v3.png")
scene.render.filepath = test_img_path
bpy.ops.render.render(write_still=True)
print(f"Render V3 concluído: {test_img_path}")
