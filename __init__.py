bl_info = {
    "name": "HDRI-lighting-Shortcut",
    "author": "Nicolas Priniotakis (Nikos) and Riccardo Giovanetti",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "category": "Lighting",
    "location": "Properties > World",
    "description": "Easy setup for HDRI global lightings",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
}

import bpy
import os
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import BoolProperty, FloatProperty, PointerProperty

# Update functions
def update_mirror(self, context):
    if context.scene.world and context.scene.world.use_nodes:
        nodes = context.scene.world.node_tree.nodes
        env_node = next((n for n in nodes if n.type == 'TEX_ENVIRONMENT'), None)
        if env_node:
            env_node.projection = 'MIRROR_BALL' if self.mirror else 'EQUIRECTANGULAR'

def update_orientation(self, context):
    if context.scene.world and context.scene.world.use_nodes:
        nodes = context.scene.world.node_tree.nodes
        mapping_node = next((n for n in nodes if n.type == 'MAPPING'), None)
        if mapping_node:
            mapping_node.inputs['Rotation'].default_value[2] = self.orientation

def update_strength(self, context):
    if context.scene.world and context.scene.world.use_nodes:
        nodes = context.scene.world.node_tree.nodes
        background_node = next((n for n in nodes if n.type == 'BACKGROUND'), None)
        if background_node:
            background_node.inputs['Strength'].default_value = self.light_strength

def update_hue_sat(self, context):
    if context.scene.world and context.scene.world.use_nodes:
        nodes = context.scene.world.node_tree.nodes
        hue_sat_node = next((n for n in nodes if n.type == 'HUE_SAT'), None)
        if hue_sat_node:
            hue_sat_node.inputs['Hue'].default_value = self.hue
            hue_sat_node.inputs['Saturation'].default_value = self.sat


def update_visibility(self, context):
    """Met à jour la visibilité de l'environnement HDRI pour la caméra."""
    if context.scene.world and context.scene.world.use_nodes:
        nodes = context.scene.world.node_tree.nodes
        links = context.scene.world.node_tree.links

        # Trouver les nœuds
        output_node = next((n for n in nodes if n.type == 'OUTPUT_WORLD'), None)
        background = next((n for n in nodes if n.type == 'BACKGROUND' and n.inputs[0].is_linked), None)
        dark_background = next((n for n in nodes if n.type == 'BACKGROUND' and not n.inputs[0].is_linked), None)
        mix_shader = next((n for n in nodes if n.type == 'MIX_SHADER'), None)
        light_path = next((n for n in nodes if n.type == 'LIGHT_PATH'), None)

        # Supprimer les connexions existantes vers le World Output
        for link in links:
            if link.to_node == output_node:
                links.remove(link)

        if self.visible:
            # Si visible, connecter le background HDRI directement au World Output
            links.new(background.outputs['Background'], output_node.inputs['Surface'])
        else:
            # Si non visible, configurer le Mix Shader
            links.new(background.outputs['Background'], mix_shader.inputs[1])      # HDRI sur le premier plot
            links.new(dark_background.outputs['Background'], mix_shader.inputs[2]) # Fond sombre sur le deuxième plot
            links.new(light_path.outputs['Is Camera Ray'], mix_shader.inputs[0])  # Light Path au Fac
            links.new(mix_shader.outputs['Shader'], output_node.inputs['Surface'])

# Properties
class HDRI_Properties(PropertyGroup):
    mirror: BoolProperty(
        name="Mirror Ball",
        description="Sets the Environment Texture to use the Mirror Ball projection",
        default=False,
        update=update_mirror
    )

    orientation: FloatProperty(
        name="Rotation",
        description="Rotates the HDRI",
        min=0.0,
        max=360.0,  # Changed to degrees instead of radians
        default=0.0,
        update=update_orientation
    )

    sat: FloatProperty(
        name="Saturation",
        description="Sets the Saturation level",
        min=0.0,
        max=2.0,
        default=1.0,
        precision=2,
        update=update_hue_sat
    )

    hue: FloatProperty(
        name="Hue",
        description="Sets the Hue level",
        min=-1.0,
        max=1.0,
        default=0.5,
        precision=2,
        update=update_hue_sat
    )

    light_strength: FloatProperty(
        name="Light Strength",
        description="Sets the Light Strength",
        min=0.0,
        max=5.0,
        default=1.0,
        precision=3,
        update=update_strength
    )

    visible: BoolProperty(
        name="Adjustments",
        description="Show/hide adjustment controls",
        default=True,
        update=update_visibility
    )

# Node setup
def create_node_setup():
    """Crée et configure les nœuds HDRI."""
    world = bpy.context.scene.world
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    nodes.clear()

    # Création des nœuds
    coord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    env_tex = nodes.new(type='ShaderNodeTexEnvironment')
    hue_sat = nodes.new(type='ShaderNodeHueSaturation')
    light_path = nodes.new(type='ShaderNodeLightPath')
    mix_shader = nodes.new(type='ShaderNodeMixShader')
    background = nodes.new(type='ShaderNodeBackground')
    dark_background = nodes.new(type='ShaderNodeBackground')
    output = nodes.new(type='ShaderNodeOutputWorld')

    # Configuration des nœuds
    coord.location = (-1200, 0)
    mapping.location = (-900, 0)
    env_tex.location = (-600, 0)
    hue_sat.location = (-300, 0)
    light_path.location = (-300, 300)
    mix_shader.location = (0, 0)
    background.location = (-300, 0)
    dark_background.location = (-300, -200)
    dark_background.inputs[0].default_value = (0.1, 0.1, 0.1, 1)  # Couleur gris foncé
    output.location = (600, 0)

    # Connexions entre les nœuds
    links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
    links.new(env_tex.outputs['Color'], hue_sat.inputs['Color'])
    links.new(hue_sat.outputs['Color'], background.inputs['Color'])

    # Par défaut, connecter directement le background au world output
    links.new(background.outputs['Background'], output.inputs['Surface'])

    return {
        'coord': coord,
        'mapping': mapping,
        'env_tex': env_tex,
        'hue_sat': hue_sat,
        'light_path': light_path,
        'mix_shader': mix_shader,
        'background': background,
        'dark_background': dark_background,
        'output': output
    }

# Operators
class HDRI_OT_Setup(Operator):
    bl_idname = "hdri.setup"
    bl_label = "Setup HDRI World"
    bl_description = "Setup the HDRI world node system"

    def execute(self, context):
        create_node_setup()
        return {'FINISHED'}

class HDRI_OT_LoadImage(Operator):
    bl_idname = "hdri.load_image"
    bl_label = "Load HDRI"
    bl_description = "Load an HDRI image"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        env_node = create_node_setup()['env_tex']
        image = bpy.data.images.load(self.filepath, check_existing=True)
        image.colorspace_settings.name = 'Linear Rec.709'
        env_node.image = image
        self.report({'INFO'}, f"Loaded HDRI: {os.path.basename(self.filepath)}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Panel
class HDRI_PT_Panel(Panel):
    bl_label = "HDRI Lighting Shortcut"
    bl_idname = "HDRI_PT_main"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        hdri_props = scene.hdri_props

        # Setup and Load buttons in a row
        row = layout.row()
        row.operator("hdri.setup", text="Setup HDRI World")
        row.operator("hdri.load_image", text="Load HDRI")

        # Light sources section
        box = layout.box()
        box.label(text="Light sources")

        row = box.row()
        split = row.split(factor=0.5)
        col1 = split.column()
        col2 = split.column()

        # Left column
        col1.prop(hdri_props, "light_strength", text="Exposure")


        # Right column
        col2.prop(hdri_props, "orientation", text="Orientation")
        col2.prop(hdri_props, "mirror", text="Mirror Ball", icon='CHECKBOX_HLT' if hdri_props.mirror else 'CHECKBOX_DEHLT')

        # Adjustments section
        box = layout.box()
        row = box.row()
        row.prop(hdri_props, "visible", text="Visible")

        row = box.row()
        split = row.split(factor=0.5)
        col1 = split.column()
        col2 = split.column()

        col1.prop(hdri_props, "sat", text="Saturation")
        col2.prop(hdri_props, "hue", text="Hue")


# Register/unregister
def register():
    bpy.utils.register_class(HDRI_Properties)
    bpy.utils.register_class(HDRI_OT_Setup)
    bpy.utils.register_class(HDRI_OT_LoadImage)
    bpy.utils.register_class(HDRI_PT_Panel)
    bpy.types.Scene.hdri_props = PointerProperty(type=HDRI_Properties)

def unregister():
    bpy.utils.unregister_class(HDRI_PT_Panel)
    bpy.utils.unregister_class(HDRI_OT_LoadImage)
    bpy.utils.unregister_class(HDRI_OT_Setup)
    bpy.utils.unregister_class(HDRI_Properties)
    del bpy.types.Scene.hdri_props

if __name__ == "__main__":
    register()
