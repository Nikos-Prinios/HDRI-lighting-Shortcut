#  2015 - 2017 Nicolas Priniotakis (Nikos) - nikos@easy-logging.net


# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "HDRI-lighting-Shortcut",
    "author": "Nicolas Priniotakis (Nikos) and Riccardo Giovanetti",
    "version": (1, 3, 3),
    "blender": (2, 80, 0),
    "category": "Lighting",
    "location": "Properties > World",
    "description": "Easy setup for HDRI global lightings",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "", }

### IMPORTS & VARIABLES ---------------------------------------------
import bpy
import os
from bpy.types import Operator, AddonPreferences
global nodes, folder_path, pref, img_path, adjustments
global node_coo, node_map, node_rgb, node_add, node_sat, node_env, node_math, node_math_add
global node_bkgnd, node_out, node_light_path, node_rflx_math, node_rflx_math_add
adjustments = False
img_path = None

import bpy
import os

### GLOBAL VARIABLES ---------------------------------------------
nodes = None
folder_path = None
img_path = None
adjustments = False
node_coo = None
node_map = None
node_rgb = None
node_add = None
node_sat = None
node_env = None
node_math = None
node_math_add = None
node_bkgnd = None
node_out = None
node_light_path = None
node_reflexion = None
node_rflx_math = None
node_rflx_math_add = None
node_blur_noise = None
node_blur_coordinate = None
node_blur_mix_1 = None
node_blur_mix_2 = None
node_blur_math_sub = None
node_blur_math_add = None


### FUNCTIONS ------------------------------------------------------
def img_exists(img):
    for index, i in enumerate(bpy.data.images):
        if i.name == img:
            return True
    return False


def img_index(img):
    for index, i in enumerate(bpy.data.images):
        if i.name == img:
            return index
    return None


def current_bkgnd():
    global nodes
    for node in nodes:
        if node.name == "ENVIRONMENT":
            return node.image.name


def node_exists(n):
    global nodes
    for node in nodes:
        if node.name == n:
            return True
    return False


def node_attrib():
    global nodes, node_coo, node_map, node_rgb, node_add, node_sat, node_env, node_math
    global node_math_add, node_bkgnd, node_out, node_light_path, node_reflexion
    global node_rflx_math, node_rflx_math_add, node_blur_noise, node_blur_coordinate
    global node_blur_mix_1, node_blur_mix_2, node_blur_math_sub, node_blur_math_add

    nodes = bpy.context.scene.world.node_tree.nodes

    for node in nodes:
        if node.name == 'COORDINATE':
            node_coo = node
        elif node.name == 'MAPPING':
            node_map = node
        elif node.name == 'COMBINE':
            node_rgb = node
        elif node.name == 'RGB_ADD':
            node_add = node
        elif node.name == 'SATURATION':
            node_sat = node
        elif node.name == 'ENVIRONMENT':
            node_env = node
        elif node.name == 'HLS_MATH':
            node_math = node
        elif node.name == 'HLS_MATH_ADD':
            node_math_add = node
        elif node.name == 'BACKGROUND':
            node_bkgnd = node
        elif node.name == 'OUTPUT':
            node_out = node
        elif node.name == "LIGHT_PATH":
            node_light_path = node
        elif node.name == 'REFLEXION':
            node_reflexion = node
        elif node.name == "RFLX_MATH":
            node_rflx_math = node
        elif node.name == "RFLX_MATH_ADD":
            node_rflx_math_add = node
        elif node.name == "BLUR_NOISE":
            node_blur_noise = node
        elif node.name == "BLUR_COORDINATE":
            node_blur_coordinate = node
        elif node.name == "BLUR_MIX_1":
            node_blur_mix_1 = node
        elif node.name == "BLUR_MIX_2":
            node_blur_mix_2 = node
        elif node.name == "BLUR_MATH_ADD":
            node_blur_math_add = node
        elif node.name == "BLUR_MATH_SUB":
            node_blur_math_sub = node


def node_tree_ok():
    try:
        current_world = bpy.context.scene.world
        if current_world.name == "HDRI Lighting Shortcut":
            if node_exists("COORDINATE") and node_exists("MAPPING") and node_exists("COMBINE") and \
               node_exists("RGB_ADD") and node_exists("SATURATION") and node_exists("ENVIRONMENT") and \
               node_exists("BACKGROUND") and node_exists("LIGHT_PATH") and node_exists('REFLEXION') and \
               node_exists('RFLX_MATH') and node_exists('RFLX_MATH_ADD') and node_exists('HLS_MATH') and \
               node_exists('HLS_MATH_ADD') and node_exists('REF_MIX') and node_exists('BLUR_NOISE') and \
               node_exists('BLUR_COORDINATE') and node_exists('BLUR_MIX_1') and node_exists('BLUR_MIX_2') and \
               node_exists('BLUR_MATH_ADD') and node_exists('BLUR_MATH_SUB') and node_exists("OUTPUT"):
                node_attrib()
                return True
    except:
        pass
    return False


def update_mirror(self, context):
    global node_env
    try:
        if self.mirror:
            node_env.projection = 'MIRROR_BALL'
        else:
            node_env.projection = 'EQUIRECTANGULAR'
    except:
        pass


def update_orientation(self, context):
    try:
        node_map.inputs[2].default_value = (self.orientation, 0, 0)
    except Exception as e:
        print(e)
        pass


def update_sat(self, context):
    try:
        node_sat.inputs[1].default_value = self.sat
    except:
        pass


def update_hue(self, context):
    try:
        node_sat.inputs[0].default_value = self.hue
    except:
        pass


def update_strength(self, context):
    try:
        node_math_add.inputs[1].default_value = self.light_strength
        if not bpy.context.scene.adjustments_prop:
            node_rflx_math_add.inputs[1].default_value = self.light_strength
            self.reflexion = self.light_strength
    except:
        pass


def update_main_strength(self, context):
    try:
        node_math.inputs[1].default_value = self.main_light_strength
    except:
        pass


def update_visible(self, context):
    if self.visible:
        self.world.cycles_visibility.camera = True
    else:
        self.world.cycles_visibility.camera = False
    try:
        self.light_strength += 0  # dirty trick to force the viewport to update
    except:
        pass


def check_visible():
    scene = bpy.context.scene
    cam = scene.world.cycles_visibility
    if scene.visible:
        cam.camera = False
        scene.visible = True
    else:
        cam.camera = True
        scene.visible = False
    try:
        scene.light_strength += 0  # stupid trick (2) to force the viewport to update
    except:
        pass


def update_reflexion(self, context):
    try:
        node_rflx_math_add.inputs[1].default_value = self.reflexion
    except:
        pass


def reset():
    self = bpy.context.scene
    self.visible = True
    self.adjustments_prop = False
    self.mirror = False
    self.world.cycles_visibility.camera = False
    self.light_strength = 0.5
    self.main_light_strength = 0.1
    self.orientation = 0.0
    self.sat = 0.0
    self.hue = 0.0
    self.reflexion = 0.5
    self.reflexion_intensity = 0.5


def do_it():
    global folder_path, img_path, adjustments, node_env
    if folder_path is not None:
        bpy.ops.image.open(filepath=img_path)
        nodes['ENVIRONMENT'].image = bpy.data.images[os.path.basename(img_path)]
    adjustments = True
    bpy.ops.render.render(write_still=True)


def adjust():
    global adjustments, node_rgb, node_add, node_sat, node_coo, node_map, node_env, node_math, node_math_add
    global node_bkgnd, node_light_path, node_reflexion, node_rflx_math, node_rflx_math_add, node_blur_noise
    global node_blur_coordinate, node_blur_mix_1, node_blur_mix_2, node_blur_math_sub, node_blur_math_add
    if adjustments:
        node_coo.location.x = 0
        node_coo.location.y = 800
        node_map.location.x = 200
        node_map.location.y = 800
        node_rgb.location.x = 400
        node_rgb.location.y = 800
        node_add.location.x = 600
        node_add.location.y = 800
        node_sat.location.x = 800
        node_sat.location.y = 800
        node_env.location.x = 1000
        node_env.location.y = 800
        node_math.location.x = 1000
        node_math.location.y = 600
        node_math_add.location.x = 1000
        node_math_add.location.y = 400
        node_bkgnd.location.x = 1000
        node_bkgnd.location.y = 200
        node_light_path.location.x = 1000
        node_light_path.location.y = 0
        node_reflexion.location.x = 800
        node_reflexion.location.y = 0
        node_rflx_math.location.x = 600
        node_rflx_math.location.y = 0
        node_rflx_math_add.location.x = 400
        node_rflx_math_add.location.y = 0
        node_blur_noise.location.x = 200
        node_blur_noise.location.y = 0
        node_blur_coordinate.location.x = 0
        node_blur_coordinate.location.y = 0
        node_blur_mix_1.location.x = -200
        node_blur_mix_1.location.y = 0
        node_blur_mix_2.location.x = -400
        node_blur_mix_2.location.y = 0
        node_blur_math_sub.location.x = -600
        node_blur_math_sub.location.y = 0
        node_blur_math_add.location.x = -800
        node_blur_math_add.location.y = 0
        adjustments = False


### REGISTER/UNREGISTER --------------------------------------------
class HDRI_Properties(bpy.types.PropertyGroup):
    mirror: bpy.props.BoolProperty(
        name="Mirror Ball",
        description="Sets the Environment Texture to use the Mirror Ball projection",
        default=False,
        update=update_mirror
    )

    orientation: bpy.props.FloatProperty(
        name="Rotation",
        description="Rotates the HDRI",
        min=-1.57,
        max=1.57,
        default=0.0,
        update=update_orientation
    )

    sat: bpy.props.FloatProperty(
        name="Saturation",
        description="Sets the Saturation level",
        min=0.0,
        max=2.0,
        default=0.0,
        update=update_sat
    )

    hue: bpy.props.FloatProperty(
        name="Hue",
        description="Sets the Hue level",
        min=-1.0,
        max=1.0,
        default=0.0,
        update=update_hue
    )

    light_strength: bpy.props.FloatProperty(
        name="Light Strength",
        description="Sets the Light Strength",
        min=0.0,
        max=2.0,
        default=0.5,
        update=update_strength
    )

    main_light_strength: bpy.props.FloatProperty(
        name="Main Light Strength",
        description="Sets the Main Light Strength",
        min=0.0,
        max=2.0,
        default=0.1,
        update=update_main_strength
    )

    visible: bpy.props.BoolProperty(
        name="Visible",
        description="Sets the visibility of the HDRI",
        default=True,
        update=update_visible
    )

    reflexion: bpy.props.FloatProperty(
        name="Reflexion",
        description="Sets the amount of light that is reflected",
        min=0.0,
        max=1.0,
        default=0.5,
        update=update_reflexion
    )


class HDRI_UIPanel(bpy.types.Panel):
    bl_label = "HDRI Lighting Shortcut"
    bl_idname = "HDRI_PT_ui"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"

    @classmethod
    def poll(cls, context):
        return context.world is not None

    def draw(self, context):
        layout = self.layout
        self.world = context.scene.world
        row = layout.row()
        row.prop(self.world.HDRI_props, "mirror")
        row = layout.row()
        row.prop(self.world.HDRI_props, "orientation")
        row = layout.row()
        row.prop(self.world.HDRI_props, "sat")
        row = layout.row()
        row.prop(self.world.HDRI_props, "hue")
        row = layout.row()
        row.prop(self.world.HDRI_props, "light_strength")
        row = layout.row()
        row.prop(self.world.HDRI_props, "main_light_strength")
        row = layout.row()
        row.prop(self.world.HDRI_props, "visible")
        row = layout.row()
        row.prop(self.world.HDRI_props, "reflexion")
        row = layout.row()
        row.operator("hdri.open")
        row = layout.row()
        row.operator("hdri.reset")


class HDRI_Open(bpy.types.Operator):
    bl_label = "Open HDRI"
    bl_idname = "hdri.open"

    def execute(self, context):
    global folder_path, img_path
    folder_path = bpy.context.scene.render.filepath
    original_filepath = bpy.context.scene.render.filepath  # Store the original filepath

    bpy.context.scene.render.filepath = "//"  # Set the filepath to the blend file's directory
    bpy.context.scene.render.use_file_extension = True  # Ensure file extensions are used

    try:
        bpy.ops.image.open()  # Open the file dialog
        selected_image = bpy.context.window_manager.fileselect_add
        if selected_image:  # Check if an image is selected
            img_path = selected_image[0].name  # Get the filepath of the selected image
            bpy.ops.image.open(filepath=img_path)  # Open the selected image
    except Exception as e:
        print("Error:", e)
    finally:
        bpy.context.scene.render.filepath = original_filepath  # Restore the original filepath

    return {'FINISHED'}



class HDRI_Reset(bpy.types.Operator):
    bl_label = "Reset HDRI"
    bl_idname = "hdri.reset"

    def execute(self, context):
        reset()
        return {'FINISHED'}


### REGISTER -------------------------------------------------------
def register():
    bpy.utils.register_class(HDRI_Properties)
    bpy.types.World.HDRI_props = bpy.props.PointerProperty(type=HDRI_Properties)
    bpy.utils.register_class(HDRI_UIPanel)
    bpy.utils.register_class(HDRI_Open)
    bpy.utils.register_class(HDRI_Reset)


def unregister():
    bpy.utils.unregister_class(HDRI_Properties)
    del bpy.types.World.HDRI_props
    bpy.utils.unregister_class(HDRI_UIPanel)
    bpy.utils.unregister_class(HDRI_Open)
    bpy.utils.unregister_class(HDRI_Reset)


if __name__ == "__main__":
    register()

