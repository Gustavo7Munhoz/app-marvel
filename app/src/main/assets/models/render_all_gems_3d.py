import bpy
import bmesh
import math
import os
import sys

# Output paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
RES_DRAWABLE = os.path.join(MAIN_DIR, "res", "drawable-nodpi")
MODELS_DIR = SCRIPT_DIR

os.makedirs(RES_DRAWABLE, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

print(f"Target drawable folder: {RES_DRAWABLE}")
print(f"Target models folder: {MODELS_DIR}")

# Factory reset
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 10
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.resolution_x = 300
scene.render.resolution_y = 300

# World ambient
world = bpy.data.worlds.new("World")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs['Color'].default_value = (0.01, 0.01, 0.02, 1.0)
    bg.inputs['Strength'].default_value = 0.4
scene.world = world

# Geometry: UPRIGHT STANDING ("DE PÉ") 16-facet cushion cut gem
mesh = bpy.data.meshes.new("GemMesh")
bm = bmesh.new()

# Proportions:
# X is width (left to right)
# Z is height (up and down, standing upright!)
# Y is depth (front to back)
rx = 0.92
rz = 1.20

# 1. Front Table (facing -Y toward camera)
t_verts = []
for i in range(8):
    a = 2 * math.pi * i / 8
    t_verts.append(bm.verts.new((0.35 * rx * math.cos(a), -0.38, 0.35 * rz * math.sin(a))))
bm.faces.new(t_verts)

# 2. Star facets
star_verts = []
for i in range(8):
    a = 2 * math.pi * (i + 0.5) / 8
    star_verts.append(bm.verts.new((0.65 * rx * math.cos(a), -0.28, 0.65 * rz * math.sin(a))))

for i in range(8):
    ni = (i + 1) % 8
    bm.faces.new([t_verts[i], t_verts[ni], star_verts[i]])

# 3. Kite facets
kite_verts = []
for i in range(8):
    a = 2 * math.pi * i / 8
    kite_verts.append(bm.verts.new((0.92 * rx * math.cos(a), -0.15, 0.92 * rz * math.sin(a))))

for i in range(8):
    prev_star = (i - 1 + 8) % 8
    bm.faces.new([t_verts[i], star_verts[i], kite_verts[i]])
    bm.faces.new([t_verts[i], kite_verts[i], star_verts[prev_star]])

# 4. Girdle Front
g_front = []
for i in range(16):
    a = 2 * math.pi * i / 16
    g_front.append(bm.verts.new((1.02 * rx * math.cos(a), -0.04, 1.02 * rz * math.sin(a))))

for i in range(8):
    k_idx = 2 * i
    s_idx = 2 * i + 1
    next_k = (2 * i + 2) % 16
    bm.faces.new([kite_verts[i], g_front[k_idx], g_front[s_idx]])
    bm.faces.new([kite_verts[i], g_front[s_idx], star_verts[i]])
    bm.faces.new([star_verts[i], g_front[s_idx], g_front[next_k]])
    bm.faces.new([star_verts[i], g_front[next_k], kite_verts[(i + 1) % 8]])

# 5. Girdle Back
g_back = []
for i in range(16):
    a = 2 * math.pi * i / 16
    g_back.append(bm.verts.new((1.02 * rx * math.cos(a), 0.04, 1.02 * rz * math.sin(a))))

for i in range(16):
    ni = (i + 1) % 16
    bm.faces.new([g_front[i], g_front[ni], g_back[ni], g_back[i]])

# 6. Pavilion
p_mid = []
for i in range(8):
    a = 2 * math.pi * (i + 0.5) / 8
    p_mid.append(bm.verts.new((0.55 * rx * math.cos(a), 0.38, 0.55 * rz * math.sin(a))))

for i in range(8):
    b1 = 2 * i
    b2 = 2 * i + 1
    b3 = (2 * i + 2) % 16
    bm.faces.new([g_back[b1], g_back[b2], p_mid[i]])
    bm.faces.new([g_back[b2], g_back[b3], p_mid[i]])
    bm.faces.new([g_back[b1], p_mid[i], p_mid[(i - 1 + 8) % 8]])

# 7. Culet
culet = bm.verts.new((0, 0.60, 0))
for i in range(8):
    ni = (i + 1) % 8
    bm.faces.new([p_mid[i], culet, p_mid[ni]])

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()

gem_obj = bpy.data.objects.new("InfinityStone", mesh)
bpy.context.collection.objects.link(gem_obj)

for f in mesh.polygons:
    f.use_smooth = False

bev = gem_obj.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.015
bev.segments = 2
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(25)

# Outer Crystal Material
mat_gem = bpy.data.materials.new("GemMaterial")
mat_gem.use_nodes = True
g_nodes = mat_gem.node_tree.nodes
g_nodes.clear()

glass_node = g_nodes.new(type='ShaderNodeBsdfGlass')
glass_node.inputs['Roughness'].default_value = 0.012
glass_node.inputs['IOR'].default_value = 1.95

emit_node = g_nodes.new(type='ShaderNodeEmission')
emit_node.inputs['Strength'].default_value = 2.2

mix1 = g_nodes.new(type='ShaderNodeMixShader')
mix1.inputs['Fac'].default_value = 0.20
mat_gem.node_tree.links.new(glass_node.outputs['BSDF'], mix1.inputs[1])
mat_gem.node_tree.links.new(emit_node.outputs['Emission'], mix1.inputs[2])

glossy_node = g_nodes.new(type='ShaderNodeBsdfGlossy')
glossy_node.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
glossy_node.inputs['Roughness'].default_value = 0.015

fresnel_node = g_nodes.new(type='ShaderNodeFresnel')
fresnel_node.inputs['IOR'].default_value = 1.6

mix2 = g_nodes.new(type='ShaderNodeMixShader')
mat_gem.node_tree.links.new(fresnel_node.outputs['Fac'], mix2.inputs['Fac'])
mat_gem.node_tree.links.new(mix1.outputs['Shader'], mix2.inputs[1])
mat_gem.node_tree.links.new(glossy_node.outputs['BSDF'], mix2.inputs[2])

out_node = g_nodes.new(type='ShaderNodeOutputMaterial')
mat_gem.node_tree.links.new(mix2.outputs['Shader'], out_node.inputs['Surface'])
gem_obj.data.materials.append(mat_gem)

# Inner Singularity Core
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.22, location=(0, 0, 0))
core = bpy.context.active_object
core.name = "SingularityCore"
core.scale = (0.5 * rx, 0.40, 0.5 * rz)

mat_core = bpy.data.materials.new("CoreEmission")
mat_core.use_nodes = True
cn = mat_core.node_tree.nodes
cn.clear()
core_emit_node = cn.new(type='ShaderNodeEmission')
core_emit_node.inputs['Strength'].default_value = 16.0
c_out = cn.new(type='ShaderNodeOutputMaterial')
mat_core.node_tree.links.new(core_emit_node.outputs['Emission'], c_out.inputs['Surface'])
core.data.materials.append(mat_core)
core.parent = gem_obj

# Lighting Rig
# Key light (Front top left)
l1 = bpy.data.lights.new("Key", 'AREA')
l1.energy = 240.0
l1.size = 2.5
l1.color = (1.0, 0.98, 0.95)
o1 = bpy.data.objects.new("Key", l1)
bpy.context.collection.objects.link(o1)
o1.location = (2.2, -3.2, 2.0)

# Cyan Tactical Rim Light (Back right)
l2 = bpy.data.lights.new("RimCyan", 'AREA')
l2.energy = 280.0
l2.size = 1.8
l2.color = (0.0, 0.9, 1.0)
o2 = bpy.data.objects.new("RimCyan", l2)
bpy.context.collection.objects.link(o2)
o2.location = (-2.5, 2.5, 1.5)

# Gem Rim Light (Back left)
l3 = bpy.data.lights.new("RimGem", 'AREA')
l3.energy = 190.0
l3.size = 1.8
o3 = bpy.data.objects.new("RimGem", l3)
bpy.context.collection.objects.link(o3)
o3.location = (2.0, 2.5, -1.0)

# Camera: Framed directly facing upright gem
cam = bpy.data.cameras.new("Cam")
cam.lens = 52
cam_o = bpy.data.objects.new("Cam", cam)
bpy.context.collection.objects.link(cam_o)
scene.camera = cam_o
cam_o.location = (0, -4.5, 0.25)
cam_o.rotation_euler = (math.radians(87.0), 0, 0)

# Save Master .blend file
blend_file = os.path.join(MODELS_DIR, "infinity_gems.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)
print(f"Master Blender file saved to: {blend_file}")

# Export GLB 3D model
glb_file = os.path.join(MODELS_DIR, "infinity_gem.glb")
bpy.ops.export_scene.gltf(filepath=glb_file, export_format='GLB')
print(f"Master GLB 3D model exported to: {glb_file}")

# 6 Infinity Stones configuration
GEMS = [
    {
        "id": "power",
        "index": 0,
        "glass_color": (0.25, 0.0, 0.85, 1.0),
        "emit_color": (0.55, 0.0, 1.0, 1.0),
        "core_color": (1.0, 0.7, 1.0, 1.0),
        "rim_color": (0.7, 0.05, 1.0),
    },
    {
        "id": "space",
        "index": 1,
        "glass_color": (0.0, 0.18, 0.90, 1.0),
        "emit_color": (0.0, 0.40, 1.0, 1.0),
        "core_color": (0.7, 0.9, 1.0, 1.0),
        "rim_color": (0.0, 0.5, 1.0),
    },
    {
        "id": "reality",
        "index": 2,
        "glass_color": (0.85, 0.01, 0.01, 1.0),
        "emit_color": (1.0, 0.05, 0.05, 1.0),
        "core_color": (1.0, 0.7, 0.7, 1.0),
        "rim_color": (1.0, 0.15, 0.15),
    },
    {
        "id": "mind",
        "index": 3,
        "glass_color": (0.88, 0.60, 0.0, 1.0),
        "emit_color": (1.0, 0.78, 0.0, 1.0),
        "core_color": (1.0, 0.95, 0.7, 1.0),
        "rim_color": (1.0, 0.85, 0.1),
    },
    {
        "id": "time",
        "index": 4,
        "glass_color": (0.0, 0.75, 0.18, 1.0),
        "emit_color": (0.0, 0.95, 0.28, 1.0),
        "core_color": (0.7, 1.0, 0.8, 1.0),
        "rim_color": (0.1, 0.95, 0.35),
    },
    {
        "id": "soul",
        "index": 5,
        "glass_color": (0.90, 0.30, 0.0, 1.0),
        "emit_color": (1.0, 0.45, 0.0, 1.0),
        "core_color": (1.0, 0.80, 0.5, 1.0),
        "rim_color": (1.0, 0.55, 0.1),
    },
]

NUM_FRAMES = 24

for gem in GEMS:
    print(f"\n--- RENDERIZANDO JOIA DE PÉ 360°: {gem['id'].upper()} ({gem['index'] + 1}/6) ---")
    glass_node.inputs['Color'].default_value = gem['glass_color']
    emit_node.inputs['Color'].default_value = gem['emit_color']
    core_emit_node.inputs['Color'].default_value = gem['core_color']
    l3.color = gem['rim_color']

    for f in range(NUM_FRAMES):
        angle_deg = f * (360.0 / NUM_FRAMES)
        # Rotação 360° em torno do eixo Z (vertical) para a joia em pé!
        gem_obj.rotation_euler = (0, 0, math.radians(angle_deg))

        frame_name = f"gem_{gem['id']}_{f:02d}.png"
        frame_path = os.path.join(RES_DRAWABLE, frame_name)
        scene.render.filepath = frame_path

        bpy.ops.render.render(write_still=True)
        print(f"[{gem['id']}] Frame {f+1}/{NUM_FRAMES} (angle {angle_deg:.1f}°) -> {frame_name}")

print("\n=======================================================")
print("TODAS AS 6 JOIAS EM PÉ FORAM RENDERIZADAS EM 360° COM SUCESSO!")
print("=======================================================")
