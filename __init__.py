#  Copyright © 2015 Nicolas Priniotakis (Nikos) - nikos@easy-logging.net
#
#  This work is free. You can redistribute it and/or modify it under the
#  terms of the Do What The Fuck You Want To Public License, Version 2,
#  as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

bl_info = {
    "name": "HDRI lighting Shortcut",
    "author": "Nicolas Priniotakis (Nikos)",
    "version": (0,0,0,1),
    "blender": (2, 7, 6, 0),
    "api": 44539,
    "category": "Render",
    "location": "Properties > World",
    "description": "Easy setup for HDRI global lightings",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",}

import bpy, pickle, getpass, os

global nodes, node_math, node_map, folder_path, pref, img_path

pref = os.path.expanduser('~/%s' % 'hdri_prefs')
if not os.path.exists(pref):
    folder_path = '//'
else:
    folder_path = pickle.load( open( pref, "rb" ) )
print("HDRI folder : " + folder_path)

img_path = None
    
# ----------------- functions --------------------
def update_pref(): 
    global folder_path
    pickle.dump((folder_path), open( 'hdri_prefs', "wb" ) )

def update_orientation(self, context):
    try :
        node_map.rotation[2] = (self.z_orientation * 0.0174533)
    except :
        pass
    
def update_strength(self, context):
    try :
        node_math.inputs[1].default_value = self.light_strength
    except :
        pass
    
def update_visible(self, context):
    cam = bpy.context.scene.world.cycles_visibility
    cam.camera = not cam.camera
    try :
        self.light_strength += 0 #dirty trick to force the viewport to update
    except :
        pass

def reset():
    try:
        bpy.context.scene.visible = False
        bpy.context.scene.world.cycles_visibility.camera = False
        bpy.context.scene.light_strength = 0.5
        bpy.context.scene.z_orientation = 0.0
    except:
        pass


def setup(img_path):
    global nodes,node_math, node_map
    bpy.context.area.type = 'NODE_EDITOR'
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.space_data.tree_type = 'ShaderNodeTree'
    bpy.context.space_data.shader_type = 'WORLD'

    nw_world = bpy.data.worlds.new("Global Lightning Shortcut")
    bpy.context.scene.world = nw_world
    bpy.context.scene.world.use_nodes = True
    
    nodes = nw_world.node_tree.nodes
    tree = nw_world.node_tree

    try:
        img = bpy.data.images.load(img_path)
    except:
        raise NameError("Cannot load image %s" % path)

    for n in nodes:
        nodes.remove(n)

    node_coo = nodes.new('ShaderNodeTexCoord')
    node_coo.location = -400,0

    node_map = nodes.new('ShaderNodeMapping')
    node_map.location = -200,0

    node_env = nodes.new('ShaderNodeTexEnvironment')
    node_env.image = img
    node_env.location = 200,0

    node_math = nodes.new('ShaderNodeMath')
    node_math.location = 400,-100
    node_math.operation = 'ADD'

    node_bkgnd = nodes.new('ShaderNodeBackground')
    node_bkgnd.location = 600,0

    node_out = nodes.new('ShaderNodeOutputWorld')
    node_out.location = 800,0

    #create links
    links = tree.links
    link0 = links.new(node_coo.outputs[0],node_map.inputs[0])
    link1 = links.new(node_map.outputs[0],node_env.inputs[0])
    link2 = links.new(node_env.outputs[0],node_bkgnd.inputs[0])
    link3 = links.new(node_env.outputs[0],node_math.inputs[0])
    link4 = links.new(node_math.outputs[0],node_bkgnd.inputs[1])
    link5 = links.new(node_bkgnd.outputs[0],node_out.inputs[0])

    bpy.context.scene.world.cycles.sample_as_light = True
    bpy.context.scene.world.cycles.sample_map_resolution = img.size[0]
    #end
    bpy.context.area.type = 'PROPERTIES'

    # ---------------------------------------

# ----------------- Custom Prop --------------------
bpy.types.Scene.z_orientation = bpy.props.FloatProperty(name="Orientation",update=update_orientation, max = 360, min = 0, default = 0)
bpy.types.Scene.light_strength = bpy.props.FloatProperty(name="Strength",update=update_strength, default = 0.5)
bpy.types.Scene.filepath = bpy.props.StringProperty(subtype='FILE_PATH')  
bpy.types.Scene.visible = bpy.props.BoolProperty(update=update_visible, name="Visible",description="Let the background being visible by the camera",default = True)

reset()

# ---------------------- GUI -----------------------
class hdri_map(bpy.types.Panel):
    bl_idname = "OBJECT_PT_sample"
    bl_label = "HDRI Lighting Shortcut"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    
    def draw(self, context):
        global img_path
        layout = self.layout
        scene = bpy.context.scene
        
        row = layout.row()      
        row.operator("nodes.img", icon="TRIA_RIGHT")
        row.prop(scene, "visible")
        if img_path is not None:
            row = layout.row()
            row.label(os.path.basename(img_path), icon='FILE_IMAGE')
            row = layout.row()
            row.prop(scene, "light_strength")
            row = layout.row()
            row.prop(scene, "z_orientation")

class OBJECT_OT_load_img(bpy.types.Operator):  
    bl_label = "Load Image"
    bl_idname = "nodes.img"
    bl_description = "Load Image"
    bl_options = {'REGISTER'}

    filter_glob = bpy.props.StringProperty(default="*.tif;*.png;*.jpeg;*.jpg", options={'HIDDEN'}) 
    filepath = bpy.props.StringProperty(name="File Path", description="Filepath used for importing files", maxlen= 1024, default= "")
    files = bpy.props.CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
        )    
        
    def execute(self,context):
        global img_path, folder_path
        img_path = self.properties.filepath
        folder_path = os.path.dirname(img_path)
        update_pref()
        setup(img_path)
        reset()
        return {'FINISHED'}

    def invoke(self, context, event):
        global folder_path
        self.filepath = folder_path+'/'
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ----------------- Registration -------------------     
def register():
    bpy.utils.register_class(hdri_map)
    bpy.utils.register_module(__name__)

 
def unregister():
    bpy.utils.unregister_class(hdri_map)

if __name__ == "__main__":
    register()
