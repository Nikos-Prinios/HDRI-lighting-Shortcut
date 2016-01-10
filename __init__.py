#  2015 Nicolas Priniotakis (Nikos) - nikos@easy-logging.net
#
#  This work is free. You can redistribute it and/or modify it under the
#  terms of the Do What The Fuck You Want To Public License, Version 2,
#  as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

bl_info = {
    "name": "HDRI lighting Shortcut",
    "author": "Nicolas Priniotakis (Nikos)",
    "version": (1,1,0,0),
    "blender": (2, 7, 6, 0),
    "api": 44539,
    "category": "Render",
    "location": "Properties > World",
    "description": "Easy setup for HDRI global lightings",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",}

import bpy, pickle, getpass, os

global nodes, node_math, node_map, folder_path, pref, img_path, real_HDR, node_bkgnd

pref = os.path.expanduser('~/%s' % 'hdri_prefs')
if not os.path.exists(pref):
    folder_path = '//'
else:
    folder_path = pickle.load( open( pref, "rb" ) )
print("HDRI folder : " + folder_path)

img_path = None
    
# ----------------- functions --------------------

def img_exists(img):
    for index, i in enumerate(bpy.data.images):
        if i.name == img :
            return True
    return False

def img_index(img):
    for index, i in enumerate(bpy.data.images):
        if i.name == img :
            return index
    return None

def current_bkgnd():
    nodes = bpy.context.scene.world.node_tree.nodes
    for node in nodes:
        if node.name == "HLS_ENV":
            return node.image.name
    
    
def node_exists(n):
    nodes = bpy.context.scene.world.node_tree.nodes
    for node in nodes:
        if node.name == n:   
            return True
    return False

def node_tree_ok():
    #bpy.context.area.type = 'NODE_EDITOR'
    #bpy.context.space_data.tree_type = 'ShaderNodeTree'
    #bpy.context.space_data.shader_type = 'WORLD'

    current_world = bpy.context.scene.world
    if current_world.name == "HDRI Lighting Shortcut":
        if node_exists("HLS_ENV"): 
            if node_exists("HLS_MAPPING"):
                return True
    return False


def update_pref(): 
    global folder_path
    try:
        pickle.dump((folder_path), open( 'hdri_prefs', "wb" ) )
    except:
        folder_path = '//'

def update_orientation(self, context):
    try :
        node_map.rotation[2] = (self.z_orientation * 0.0174533)
    except :
        pass
    
def update_strength(self, context):
    global real_HDR
    #try :
    if not real_HDR:
        node_math.inputs[1].default_value = self.light_strength
    else:
        node_bkgnd.inputs[1].default_value = self.light_strength
    #except :
    #    pass
    
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
        bpy.context.scene.light_strength = 1.0
        bpy.context.scene.z_orientation = 0.0
    except:
        pass

def clear_node_tree():
    try:
        nodes = bpy.context.scene.world.node_tree.nodes
        for node in nodes:
            nodes.remove(node)
    except:
        pass

def node_tree_exists(world_name):
    for w in bpy.data.worlds:
        if w.name == world_name:
            return True
    return False

def world_num(world_name):
    for index, w in enumerate(bpy.data.worlds):
        if w.name == world_name:
            return index

def setup(img_path):
    global nodes,node_math, node_bkgnd, node_map,real_HDR
    
    bpy.context.area.type = 'NODE_EDITOR'
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.space_data.tree_type = 'ShaderNodeTree'
    bpy.context.space_data.shader_type = 'WORLD'
    tree_name = "HDRI Lighting Shortcut"
    
    # Create the new world if it doesn't exists
    if node_tree_exists(tree_name):
        bpy.context.scene.world.use_nodes = True
        nw_world = bpy.data.worlds[world_num(tree_name)]
        bpy.context.scene.world = nw_world
        clear_node_tree()
    else:
        nw_world = bpy.data.worlds.new(tree_name)
        bpy.context.scene.world = nw_world
        bpy.context.scene.world.use_nodes = True

    nodes = nw_world.node_tree.nodes
    tree = nw_world.node_tree
    img = os.path.basename(img_path)
    real_HDR = False
    if img.endswith(".hdr") or img.endswith(".exr"):
        real_HDR = True
    
    try:
        if not img_exists(img):
            img = bpy.data.images.load(img_path)
        else:
            img = bpy.data.images[img_index(img)]
    except:
        raise NameError("Cannot load image %s" % path)

    for n in nodes:
        nodes.remove(n)

    node_coo = nodes.new('ShaderNodeTexCoord')
    node_coo.location = -400,0

    node_map = nodes.new('ShaderNodeMapping')
    node_map.name = "HLS_MAPPING"
    node_map.location = -200,0

    node_env = nodes.new('ShaderNodeTexEnvironment')
    node_env.name = "HLS_ENV"
    node_env.image = img
    node_env.location = 200,0

    if not real_HDR:
        node_math = nodes.new('ShaderNodeMath')
        node_math.name = "HLS_MATH"
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
    if not real_HDR:
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
bpy.types.Scene.light_strength = bpy.props.FloatProperty(name="Strength",update=update_strength, default = 1)
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
        try:
            img = current_bkgnd()
        except:
            img = ''
        layout = self.layout
        scene = bpy.context.scene
        
        row = layout.row()      
        row.operator("nodes.img", icon="TRIA_RIGHT")
        
        #if img_path is not None:
        if node_tree_ok():
            row.prop(scene, "visible")
            row = layout.row()
            row.label(os.path.basename(img), icon='FILE_IMAGE')
            row = layout.row()
            row.prop(scene, "light_strength")
            row = layout.row()
            row.prop(scene, "z_orientation")

class OBJECT_OT_load_img(bpy.types.Operator):  
    bl_label = "Load Image"
    bl_idname = "nodes.img"
    bl_description = "Load Image"
    bl_options = {'REGISTER'}

    filter_glob = bpy.props.StringProperty(default="*.tif;*.png;*.jpeg;*.jpg;*.exr;*.hdr", options={'HIDDEN'}) 
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
