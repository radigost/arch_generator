import datetime
import math

import bpy
import mathutils

import yaml

with open('params.yml', 'r') as f:
    data = list(yaml.load_all(f, Loader=yaml.SafeLoader))
print()

def clean_scene():
    bpy.ops.object.delete()

def raize_floor():
    # open floor plan and extrude it
    # Go to edit mode, face selection mode and select all faces
    bpy.ops.import_scene.gltf(filepath=data[0]["files"]["floor"])
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0, 0, 3)}
    )
    bpy.ops.object.mode_set(mode='OBJECT')
    first_floor = bpy.context.active_object
    eul = mathutils.Euler((0.0, (math.radians(90.0)), 0.0), 'XYZ')
    # eul.to_matrix is 3x3 but we need 4x4 to multiply with matrix_world
    R = eul.to_matrix().to_4x4()
    mw = first_floor.matrix_world
    mw @= R


    # create material
    mat = bpy.data.materials.new(name='Material')
    mat.use_nodes = True
    mat_nodes = mat.node_tree.nodes
    mat_links = mat.node_tree.links

    first_floor.data.materials.append(mat)

    # metallic
    mat_nodes['Principled BSDF'].inputs['Metallic'].default_value = 1.0
    mat_nodes['Principled BSDF'].inputs['Base Color'].default_value = (
        0.005634391214698553, 0.01852927729487419, 0.8000000715255737, 1.0
    )
    mat_nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.167

def assemble_windows():
    bpy.ops.import_scene.gltf(filepath=data[0]["files"]["basic_window"])

    context = bpy.context
    home = bpy.data.objects["Home"]

    for i in range(0, 5):
        new_obj = home.copy()
        new_obj.data = home.data.copy()
        new_obj.animation_data_clear()
        new_obj.location.x += 3.0
        context.collection.objects.link(new_obj)
        home = new_obj

def export_home():
    date = datetime.datetime.now()
    bpy.ops.export_scene.gltf(export_format='GLB', filepath=f'output/blender_{date}.glb')

clean_scene()
raize_floor()
assemble_windows()
export_home()
