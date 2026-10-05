import bpy
import bmesh
import math
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RES_DRAWABLE = os.path.join(MAIN_DIR, "res", "drawable-nodpi")
os.makedirs(RES_DRAWABLE, exist_ok=True)

# 1. Reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Configuração de Render (Cycles)
scene.render.engine = 'CYCLES'
try:
    scene.cycles.device = 'GPU'
except:
    scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.resolution_x = 500
scene.render.resolution_y = 500

col = bpy.data.collections.new("AuthenticGauntlet")
scene.collection.children.link(col)
root = bpy.data.objects.new("GauntletRoot", None)
col.objects.link(root)

# 2. Materiais PBR de Alta Fidelidade

# Uru Metal Dourado com Ranhuras e Pátina Antiga nos Sulcos
def create_uru_metal_material():
    mat = bpy.data.materials.new("Mat_Uru_Forged_Gold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)

    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = (0.94, 0.72, 0.22, 1.0)
    principled.inputs['Metallic'].default_value = 0.96
    principled.inputs['Roughness'].default_value = 0.22

    # Textura de Ruído Procedural para Metal Escovado/Forjado de Nidavellir
    tex_noise = nodes.new('ShaderNodeTexNoise')
    tex_noise.location = (-400, 100)
    tex_noise.inputs['Scale'].default_value = 85.0
    tex_noise.inputs['Detail'].default_value = 6.0
    tex_noise.inputs['Roughness'].default_value = 0.6

    bump = nodes.new('ShaderNodeBump')
    bump.location = (-100, 100)
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.05
    links.new(tex_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])

    # Variação de cor sutil (dourado rico nos topos, bronze escuro nas ranhuras)
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-100, -150)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.62, 0.42, 0.12, 1.0) # Bronze escuro
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.96, 0.75, 0.24, 1.0) # Ouro Uru brilhante
    links.new(tex_noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], principled.inputs['Base Color'])

    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Metal Escuro / Articulações
def create_dark_metal_material():
    mat = bpy.data.materials.new("Mat_Uru_Dark")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Base Color'].default_value = (0.12, 0.11, 0.10, 1.0)
    principled.inputs['Metallic'].default_value = 0.88
    principled.inputs['Roughness'].default_value = 0.38
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Joias Cósmicas com Vidro Refrativo + Centro Emissivo Intenso
def create_gem_material(name, rgb, emission_boost=10.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (500, 0)

    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 150)
    principled.inputs['Base Color'].default_value = (*rgb, 1.0)
    principled.inputs['Roughness'].default_value = 0.02
    principled.inputs['IOR'].default_value = 1.77
    if 'Transmission Weight' in principled.inputs:
        principled.inputs['Transmission Weight'].default_value = 0.92
    elif 'Transmission' in principled.inputs:
        principled.inputs['Transmission'].default_value = 0.92

    emission = nodes.new('ShaderNodeEmission')
    emission.location = (0, -150)
    emission.inputs['Color'].default_value = (*rgb, 1.0)
    emission.inputs['Strength'].default_value = emission_boost

    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (250, 0)
    mix.inputs['Fac'].default_value = 0.40 # Mistura brilho interno e reflexo de vidro
    links.new(principled.outputs['BSDF'], mix.inputs[1])
    links.new(emission.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], output.inputs['Surface'])
    return mat

mat_gold = create_uru_metal_material()
mat_dark = create_dark_metal_material()

# As 6 Joias Canônicas do MCU
mat_mind    = create_gem_material("Mat_Mind",    (1.00, 0.85, 0.05), emission_boost=12.0) # Amarela (Mente - Dorso)
mat_power   = create_gem_material("Mat_Power",   (0.75, 0.10, 1.00), emission_boost=10.0) # Roxa (Poder - Indicador)
mat_space   = create_gem_material("Mat_Space",   (0.05, 0.65, 1.00), emission_boost=10.0) # Azul (Espaço - Médio)
mat_reality = create_gem_material("Mat_Reality", (1.00, 0.04, 0.08), emission_boost=10.0) # Vermelha (Realidade - Anelar)
mat_soul    = create_gem_material("Mat_Soul",    (1.00, 0.48, 0.02), emission_boost=10.0) # Laranja (Alma - Mínimo)
mat_time    = create_gem_material("Mat_Time",    (0.05, 1.00, 0.35), emission_boost=10.0) # Verde (Tempo - Polegar)

# Helper para gerar malha
def make_mesh_obj(name, bm, mat, subsurf=0, shade_smooth=True):
    mesh = bpy.data.meshes.new(name + "_M")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    if shade_smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    col.objects.link(obj)
    obj.parent = root
    if subsurf > 0:
        sub = obj.modifiers.new("Sub", 'SUBSURF')
        sub.levels = subsurf
        sub.render_levels = subsurf
    return obj

# =========================================================================
# 3. CONSTRUÇÃO DO ANTEBRAÇO TÁTICO E ARTICULADO (BRACER & CUFF)
# =========================================================================
# O antebraço é um cone facetado largo no cotovelo e afilado no punho,
# com placas de blindagem sobrepostas e vincos no dorso.

def create_forearm():
    bm = bmesh.new()
    # Criamos os anéis transversais do antebraço
    # Coordenadas: Z vertical, X lateral, Y profundidade (dorso para frente -Y, palma para trás +Y)
    levels = [
        # (z, rx_back, rx_front, ry_back, ry_front)
        (-1.60, 0.58, 0.52, 0.45, 0.40), # Borda superior do cotovelo
        (-1.40, 0.56, 0.50, 0.44, 0.39),
        (-1.10, 0.52, 0.47, 0.42, 0.37),
        (-0.80, 0.47, 0.43, 0.39, 0.34),
        (-0.50, 0.42, 0.39, 0.36, 0.31), # Início do punho
        (-0.35, 0.40, 0.37, 0.34, 0.29), # Fim do antebraço
    ]
    
    rings = []
    num_pts = 16
    for z, rxb, rxf, ryb, ryf in levels:
        ring = []
        for i in range(num_pts):
            ang = 2 * math.pi * i / num_pts
            # Deforma para ter crista no dorso (-Y) e aspecto de armadura anatômica
            rx = rxf if math.sin(ang) < 0 else rxb
            ry = ryf if math.sin(ang) < 0 else ryb
            x = rx * math.cos(ang)
            y = ry * math.sin(ang)
            # Crista dorsal no centro
            if -0.3 < x < 0.3 and y < 0:
                y -= 0.05 * (1.0 - abs(x) / 0.3)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
        
    for r in range(len(levels) - 1):
        for i in range(num_pts):
            ni = (i + 1) % num_pts
            bm.faces.new([rings[r][i], rings[r][ni], rings[r+1][ni], rings[r+1][i]])
            
    # Borda chanfrada aberta na base (cotovelo)
    bm.faces.new(rings[0])
    make_mesh_obj("Forearm_Base", bm, mat_gold, subsurf=1)

    # Borda do Cotovelo (Flared Cuff Rim)
    bm_rim = bmesh.new()
    bmesh.ops.create_cone(bm_rim, cap_ends=True, cap_tris=False, segments=24,
                          radius1=0.62, radius2=0.59, depth=0.10)
    for v in bm_rim.verts:
        v.co.z -= 1.58
        v.co.y *= 0.82
    make_mesh_obj("Elbow_Rim", bm_rim, mat_gold, subsurf=1)

    # 3 Placas Articuladas do Punho (Wrist Lames) sobrepostas
    wrist_z_steps = [-0.34, -0.24, -0.14]
    wrist_radii   = [(0.43, 0.36), (0.46, 0.38), (0.49, 0.40)]
    for idx, (wz, (wrx, wry)) in enumerate(zip(wrist_z_steps, wrist_radii)):
        bm_w = bmesh.new()
        bmesh.ops.create_cone(bm_w, cap_ends=True, cap_tris=False, segments=20,
                              radius1=wrx, radius2=wrx * 0.94, depth=0.08)
        for v in bm_w.verts:
            v.co.z += wz
            v.co.y *= (wry / wrx)
        make_mesh_obj(f"Wrist_Lame_{idx}", bm_w, mat_gold, subsurf=1)

create_forearm()

# =========================================================================
# 4. DORSO DA MÃO (PALM & METACARPAL SHIELD) COM ENGASTE DA MENTE
# =========================================================================
def create_hand_shield():
    # Placa do dorso da mão em formato trapezoidal de escudo com espessura
    bm = bmesh.new()
    hand_levels = [
        # (z, rx, ry, off_y)
        (-0.10, 0.50, 0.38, -0.02),
        ( 0.08, 0.54, 0.37, -0.03),
        ( 0.26, 0.57, 0.35, -0.04),
        ( 0.42, 0.60, 0.31, -0.05), # Crista dos nós dos dedos
    ]
    rings = []
    num_pts = 16
    for z, rx, ry, off_y in hand_levels:
        ring = []
        for i in range(num_pts):
            ang = 2 * math.pi * i / num_pts
            vx = rx * math.cos(ang)
            vy = ry * math.sin(ang) + off_y
            # Acentua a elevação dorsal para receber o engaste da Joia da Mente
            if vy < 0:
                vy -= 0.06 * (1.0 - min(1.0, abs(vx)/0.4))
            ring.append(bm.verts.new((vx, vy, z)))
        rings.append(ring)
        
    for r in range(len(hand_levels) - 1):
        for i in range(num_pts):
            ni = (i + 1) % num_pts
            bm.faces.new([rings[r][i], rings[r][ni], rings[r+1][ni], rings[r+1][i]])
            
    bm.faces.new(rings[-1]) # Fecha topo dos nós
    make_mesh_obj("Hand_Shield", bm, mat_gold, subsurf=1)

    # Moldura Solar da Joia da Mente (Sunburst Teardrop Bezel)
    bm_sun = bmesh.new()
    bmesh.ops.create_cone(bm_sun, cap_ends=True, cap_tris=False, segments=16,
                          radius1=0.22, radius2=0.18, depth=0.06)
    for v in bm_sun.verts:
        v.co.y *= 1.25 # Alongada na vertical
        v.co.x += 0.0
        v.co.y += -0.42
        v.co.z += 0.12
    make_mesh_obj("Mind_Bezel", bm_sun, mat_gold, subsurf=1)

    # Barra Robusta dos Nós dos Dedos (Knuckle Ridge Arch)
    bm_k = bmesh.new()
    bmesh.ops.create_cube(bm_k, size=1.0)
    for v in bm_k.verts:
        v.co.x *= 1.05
        v.co.y *= 0.18
        v.co.z *= 0.14
        # Curva o arco dos nós acompanhando a mão
        v.co.y -= 0.08 * (1.0 - (v.co.x / 0.55)**2)
        v.co.z += 0.44
        v.co.y -= 0.32
    make_mesh_obj("Knuckle_Bar", bm_k, mat_gold, subsurf=1)

create_hand_shield()

# =========================================================================
# 5. AS 6 JOIAS DO INFINITO (MODELAGEM FACETADA & CRISTALINA COM LUZ)
# =========================================================================
def add_cosmic_stone(name, loc, rx, ry, rz, rot_euler, mat_gem, light_color, energy=60.0):
    # Engaste Dourado (Bezel Socket)
    bm_b = bmesh.new()
    bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=12,
                          radius1=max(rx, ry) * 1.35, radius2=max(rx, ry) * 1.15, depth=rz * 1.1)
    for v in bm_b.verts:
        v.co.x *= (rx / max(rx, ry))
        v.co.y *= (ry / max(rx, ry))
        # Rotação
        vx, vy, vz = v.co.x, v.co.y, v.co.z
        if rot_euler[0] != 0:
            rad = rot_euler[0]
            vy, vz = vy * math.cos(rad) - vz * math.sin(rad), vy * math.sin(rad) + vz * math.cos(rad)
        if rot_euler[1] != 0:
            rad = rot_euler[1]
            vx, vz = vx * math.cos(rad) + vz * math.sin(rad), -vx * math.sin(rad) + vz * math.cos(rad)
        v.co.x, v.co.y, v.co.z = vx + loc[0], vy + loc[1], vz + loc[2]
    make_mesh_obj(name + "_Bezel", bm_b, mat_gold, subsurf=1)

    # Gema Facetada (Icosphere cabochon facetada)
    bm_g = bmesh.new()
    bmesh.ops.create_icosphere(bm_g, subdivisions=2, radius=1.0)
    for v in bm_g.verts:
        v.co.x *= rx
        v.co.y *= ry
        v.co.z *= rz
        # Rotação
        vx, vy, vz = v.co.x, v.co.y, v.co.z
        if rot_euler[0] != 0:
            rad = rot_euler[0]
            vy, vz = vy * math.cos(rad) - vz * math.sin(rad), vy * math.sin(rad) + vz * math.cos(rad)
        if rot_euler[1] != 0:
            rad = rot_euler[1]
            vx, vz = vx * math.cos(rad) + vz * math.sin(rad), -vx * math.sin(rad) + vz * math.cos(rad)
        v.co.x, v.co.y, v.co.z = vx + loc[0], vy + loc[1], vz + loc[2]
    # Pedras são facetadas com sombreamento plano/sharp nos reflexos
    make_mesh_obj(name + "_Gem", bm_g, mat_gem, subsurf=0, shade_smooth=True)

    # Luz de Brilho Cósmico Interno
    light_data = bpy.data.lights.new(name + "_Light", 'POINT')
    light_data.color = light_color
    light_data.energy = energy
    light_data.shadow_soft_size = 0.05
    light_obj = bpy.data.objects.new(name + "_LightObj", light_data)
    light_obj.location = (loc[0], loc[1] - 0.03, loc[2])
    light_obj.parent = root
    col.objects.link(light_obj)

# 1. Joia da Mente (Grande, Central no Dorso)
add_cosmic_stone("Mind", (0.0, -0.44, 0.12), rx=0.13, ry=0.17, rz=0.08,
                 rot_euler=(math.radians(90), 0, 0), mat_gem=mat_mind,
                 light_color=(1.0, 0.85, 0.0), energy=80.0)

# 2. Joias dos Nós dos Dedos (Power, Space, Reality, Soul)
# Posições canônicas de Infinity War:
# Indicador: Roxa (Power) | Médio: Azul (Space) | Anelar: Vermelha (Reality) | Mínimo: Laranja (Soul)
add_cosmic_stone("Power",   (-0.38, -0.32, 0.44), rx=0.075, ry=0.065, rz=0.055,
                 rot_euler=(math.radians(65), math.radians(-16), 0), mat_gem=mat_power,
                 light_color=(0.75, 0.10, 1.0), energy=50.0)

add_cosmic_stone("Space",   (-0.13, -0.36, 0.47), rx=0.080, ry=0.070, rz=0.060,
                 rot_euler=(math.radians(70), math.radians(-5), 0), mat_gem=mat_space,
                 light_color=(0.05, 0.65, 1.0), energy=55.0)

add_cosmic_stone("Reality", ( 0.13, -0.36, 0.47), rx=0.080, ry=0.070, rz=0.060,
                 rot_euler=(math.radians(70), math.radians(5), 0), mat_gem=mat_reality,
                 light_color=(1.00, 0.04, 0.08), energy=55.0)

add_cosmic_stone("Soul",    ( 0.38, -0.32, 0.44), rx=0.075, ry=0.065, rz=0.055,
                 rot_euler=(math.radians(65), math.radians(16), 0), mat_gem=mat_soul,
                 light_color=(1.00, 0.48, 0.02), energy=50.0)

# 3. Joia do Tempo no Polegar (Verde)
add_cosmic_stone("Time",    (-0.55, -0.18, 0.12), rx=0.075, ry=0.065, rz=0.055,
                 rot_euler=(math.radians(50), math.radians(-45), 0), mat_gem=mat_time,
                 light_color=(0.05, 1.00, 0.35), energy=55.0)


# =========================================================================
# 6. DEDOS ARTICULADOS DE TITÃ (ARMORED PHALANX PLATES & POWER CLAW POSE)
# =========================================================================
# Em vez de tubos finos verticais, cada dedo é composto por 3 placas de armadura
# sobrepostas (lames), largas, musculosas, curvadas para frente (-Y) e para baixo (-Z)
# em uma imponente garra semifechada que mostra simultaneamente as placas e as joias!

def create_armored_finger(name, knuckle_root, yaw_deg, lengths, widths):
    # knuckle_root: (x, y, z) de partida no topo do nó
    cur_x, cur_y, cur_z = knuckle_root

    # Ângulos de curvatura anatômica para a frente/baixo (Titânico/Poderoso)
    # A falange 1 projeta-se para a frente (-Y) com leve descida
    # A falange 2 dobra para baixo (-Z)
    # A falange 3 curva como uma garra afiada
    pitches = [math.radians(55), math.radians(95), math.radians(130)]
    yaw = math.radians(yaw_deg)

    for seg_idx, (seg_len, (wx, wy)) in enumerate(zip(lengths, widths)):
        bm_seg = bmesh.new()
        pitch = pitches[seg_idx]

        # Vetor de direção do segmento da falange
        dx = seg_len * math.sin(yaw) * 0.3
        dy = -seg_len * math.sin(pitch)
        dz = -seg_len * math.cos(pitch)

        # Construímos o casco da placa da armadura da falange (seção D chanfrada)
        # 8 vértices no anel base
        base_verts = []
        tip_verts  = []
        taper = 0.85 if seg_idx < 2 else 0.40 # Ponta afilada na última falange (garra)

        # Construção da placa
        for i in range(8):
            ang = 2 * math.pi * i / 8
            # Forma facetada de armadura: mais achatada na palma (+Y), chanfrada no dorso (-Y)
            rx = wx * 0.5 * math.cos(ang)
            ry = wy * 0.5 * math.sin(ang)
            if math.sin(ang) < 0: # Dorso da falange tem vinco
                ry *= 1.25

            # Ponto na base do segmento
            base_verts.append(bm_seg.verts.new((cur_x + rx, cur_y + ry, cur_z)))

            # Ponto na ponta do segmento
            tip_verts.append(bm_seg.verts.new((cur_x + dx + rx * taper,
                                               cur_y + dy + ry * taper,
                                               cur_z + dz)))

        # Faces laterais
        for i in range(8):
            ni = (i + 1) % 8
            bm_seg.faces.new([base_verts[i], base_verts[ni], tip_verts[ni], tip_verts[i]])

        bm_seg.faces.new(base_verts)
        bm_seg.faces.new(tip_verts)

        # Junta esférica metálica escura no nó da articulação
        bm_joint = bmesh.new()
        bmesh.ops.create_icosphere(bm_joint, subdivisions=2, radius=wx * 0.45)
        for v in bm_joint.verts:
            v.co.x += cur_x
            v.co.y += cur_y
            v.co.z += cur_z
        make_mesh_obj(f"{name}_Joint_{seg_idx}", bm_joint, mat_dark, subsurf=1)

        make_mesh_obj(f"{name}_Seg_{seg_idx}", bm_seg, mat_gold, subsurf=1)

        # Atualiza a posição para o próximo segmento
        cur_x += dx
        cur_y += dy
        cur_z += dz

# 4 Dedos maciços com proporções imponentes de Titã
# Indicador
create_armored_finger("Finger_Index",  knuckle_root=(-0.38, -0.27, 0.44), yaw_deg=-8,
                      lengths=[0.26, 0.22, 0.18], widths=[(0.23, 0.20), (0.20, 0.17), (0.16, 0.14)])

# Médio (Mais longo e robusto)
create_armored_finger("Finger_Middle", knuckle_root=(-0.13, -0.30, 0.47), yaw_deg=-2,
                      lengths=[0.29, 0.25, 0.20], widths=[(0.24, 0.21), (0.21, 0.18), (0.17, 0.15)])

# Anelar
create_armored_finger("Finger_Ring",   knuckle_root=( 0.13, -0.30, 0.47), yaw_deg=2,
                      lengths=[0.27, 0.23, 0.19], widths=[(0.24, 0.21), (0.20, 0.17), (0.16, 0.14)])

# Mínimo
create_armored_finger("Finger_Pinky",  knuckle_root=( 0.38, -0.27, 0.44), yaw_deg=8,
                      lengths=[0.23, 0.19, 0.16], widths=[(0.22, 0.19), (0.18, 0.15), (0.15, 0.13)])

# Polegar Poderoso com Placa Articulada e Pose de Oposição
def create_armored_thumb():
    bm_t = bmesh.new()
    # 4 anéis ao longo da curvatura do polegar
    t_pts = [
        # (x, y, z, rx, ry)
        (-0.46, -0.05, 0.05, 0.18, 0.15), # Base do metacarpo
        (-0.56, -0.16, 0.12, 0.17, 0.14), # Nós com engaste da joia do tempo
        (-0.52, -0.32, 0.10, 0.15, 0.12), # Falange intermediária
        (-0.38, -0.42, 0.06, 0.11, 0.09), # Garra distal curvando para dentro
    ]
    rings = []
    for x, y, z, rx, ry in t_pts:
        ring = []
        for i in range(8):
            ang = 2 * math.pi * i / 8
            ring.append(bm_t.verts.new((x + rx * math.cos(ang), y + ry * math.sin(ang), z)))
        rings.append(ring)

    for r in range(len(t_pts) - 1):
        for i in range(8):
            ni = (i + 1) % 8
            bm_t.faces.new([rings[r][i], rings[r][ni], rings[r+1][ni], rings[r+1][i]])

    bm_t.faces.new(rings[0])
    bm_t.faces.new(rings[-1])
    make_mesh_obj("Thumb_Armor", bm_t, mat_gold, subsurf=1)

create_armored_thumb()

# =========================================================================
# 7. ESTÚDIO DE ILUMINAÇÃO CINEMATOGRÁFICO
# =========================================================================
def add_light(name, ltype, loc, color, energy, size=0.2):
    ld = bpy.data.lights.new(name, ltype)
    ld.color = color
    ld.energy = energy
    if ltype in ('POINT', 'SPOT', 'AREA'):
        ld.shadow_soft_size = size
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    col.objects.link(lo)
    return lo

# Key Light Dourada Quente (Frontal/Superior)
add_light("Key_Gold", 'AREA', (2.5, -4.0, 2.0), (1.0, 0.94, 0.82), 650.0, size=0.6)

# Fill Light Fria / Azulada Cósmica (Lateral)
add_light("Fill_Cosmic", 'AREA', (-3.0, -3.0, 0.5), (0.25, 0.75, 1.0), 300.0, size=0.8)

# Rim Light de Silhueta Metálica Intensa (Atrás/Cima)
add_light("Rim_Top", 'SPOT', (0.0, 3.2, 3.5), (1.0, 0.98, 0.92), 900.0, size=0.1)

# Kicker Light Inferior (Roxo / Titã Glow)
add_light("Kicker_Bottom", 'POINT', (1.2, 2.2, -1.8), (0.85, 0.35, 1.0), 350.0, size=0.3)

# =========================================================================
# 8. CÂMERA DINÂMICA HERO 3D (3/4 PERSPECTIVE)
# =========================================================================
cam_data = bpy.data.cameras.new("HeroCamera")
cam_data.lens = 65 # Teleobjetiva média para evitar distorção de grande-angular
cam = bpy.data.objects.new("HeroCamera", cam_data)

# Posiciona a câmera para enquadrar a manopla inteira de forma gloriosa:
# O antebraço na parte inferior, o dorso com a Joia da Mente no centro,
# e os nós dos dedos curvados para a frente com as 4 joias e o polegar visíveis.
cam.location = (0.0, -4.5, -0.30)
cam.rotation_euler = (math.radians(85), 0, 0)
col.objects.link(cam)
scene.camera = cam

# Ajuste fino da rotação da raiz para ângulo 3/4 heroico
root.rotation_euler = (math.radians(-10), math.radians(12), math.radians(-15))

# =========================================================================
# 9. RENDER DE TESTE
# =========================================================================
test_output = os.path.join(RES_DRAWABLE, "test_authentic.png")
scene.render.filepath = test_output
print(f"Iniciando Render de Teste em: {test_output}")
bpy.ops.render.render(write_still=True)
print("Render Concluído com Sucesso!")
