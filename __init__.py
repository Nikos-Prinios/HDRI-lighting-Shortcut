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
    "category": "Material",
    "location": "Properties > World",
    "description": "Easy setup for HDRI global lightings",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",}

import bpy, pickle, getpass, os

global nodes,folder_path, pref, img_path, real_HDR, color_correc
global node_coo,nod_map,node_rgb,node_add,node_sat,node_env,node_math,node_bkgnd,node_out,node_light_path
real_HDR = False
pref = os.path.expanduser('~/%s' % 'hdri_prefs')
if not os.path.exists(pref):
    folder_path = '//'
else:
    folder_path = pickle.load( open( pref, "rb" ) )
print("HDRI folder : " + folder_path)
color_correc = False
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

    
def node_attrib():
    global node_coo,nod_map,node_rgb,node_add,node_sat,node_env,node_math,node_bkgnd,node_out,node_light_path,node_reflexion
    nodes = bpy.context.scene.world.node_tree.nodes
    for node in nodes:
        if node.name == 'coordinate':
            node_coo = node
        if node.name == 'HLS_MAPPING':
            node_map = node
        if node.name == 'Color_correction':
            node_rgb = node
        if node.name == 'RGB_ADD':
            node_add = node
        if node.name == 'saturation':
            node_sat = node
        if node.name == 'HLS_ENV':
            node_env = node
        if node.name == 'HLS_MATH':
            node_math = node
        if node.name == 'bkgnd':
            node_bkgnd = node
        if node.name == 'output':
            node_out = node
        if node.name == 'light_path':
            node_light_path = node
        if node.name == 'reflexion':
            node_reflexion = node

def node_tree_ok():
    #bpy.context.area.type = 'NODE_EDITOR'
    #bpy.context.space_data.tree_type = 'ShaderNodeTree'
    #bpy.context.space_data.shader_type = 'WORLD'

    current_world = bpy.context.scene.world
    if current_world.name == "HDRI Lighting Shortcut":
        if node_exists("coordinate"):
            if node_exists("HLS_MAPPING"):
                if node_exists("Color_correction"):
                    if node_exists("RGB_ADD"):
                        if node_exists("saturation"):
                            if node_exists("HLS_ENV"):
                                if node_exists("bkgnd"):
                                    if node_exists("light_path"):
                                        if node_exists('reflexion'):
                                            if node_exists("output"):
                                                node_attrib()
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

def update_r(self, context):
    try :
        node_rgb.inputs[0].default_value = ((self.color_r * 100)/255)/100
    except :
        pass

def update_sat(self, context):
    try :
        node_sat.inputs[1].default_value = self.sat
    except :
        pass

def update_hue(self, context):
    try :
        node_sat.inputs[0].default_value = self.hue
    except :
        pass

def update_g(self, context):
    try :
        node_rgb.inputs[1].default_value = ((self.color_g * 100)/255)/100
    except :
        pass

def update_b(self, context):
    try :
        node_rgb.inputs[2].default_value = ((self.color_b * 100)/255)/100
    except :
        pass

def update_strength(self, context):
    global real_HDR
    try :
        if not real_HDR:
            node_math.inputs[1].default_value = self.light_strength
        else:
            node_bkgnd.inputs[1].default_value = self.light_strength
    except :
        pass
    
def update_visible(self, context):
    cam = bpy.context.scene.world.cycles_visibility
    cam.camera = not cam.camera
    try :
        self.light_strength += 0 #dirty trick to force the viewport to update
    except :
        pass

def update_reflexion(self, context):
    node_reflexion.inputs[1].default_value = self.reflexion

def reset():
    try:
        bpy.context.scene.visible = False
        bpy.context.scene.colcor = False
        bpy.context.scene.world.cycles_visibility.camera = False
        bpy.context.scene.light_strength = 1.0
        bpy.context.scene.z_orientation = 0.0
        bpy.context.scene.color_r = 0
        bpy.context.scene.color_g = 0
        bpy.context.scene.color_b = 0
        bpy.context.scene.sat = 1
        bpy.context.scene.hue = .5
    except:
        pass

def clear_node_tree():
    try:
        nodes = bpy.context.scene.world.node_tree.nodes
        for node in nodes:
            nodes.remove(node)
    except:
        pass

def update_colcor(self,context):
    global color_correc
    color_correc = not color_correc
    

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
    global nodes,node_math, node_bkgnd, node_map,real_HDR, node_rgb, node_sat,node_reflexion,node_light_path
    
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
    node_coo.name = 'coordinate'

    node_map = nodes.new('ShaderNodeMapping')
    node_map.name = "HLS_MAPPING"
    node_map.location = -200,0

    node_rgb = nodes.new("ShaderNodeCombineRGB")
    node_rgb.name = 'Color_correction'
    node_rgb.location = 200,200

    node_add = nodes.new("ShaderNodeMixRGB")
    node_add.blend_type = 'ADD'
    node_add.inputs[0].default_value = 1
    node_add.location = 400,400
    node_add.name = 'RGB_ADD'

    node_sat = nodes.new("ShaderNodeHueSaturation")
    node_sat.location = 400,200
    node_sat.name = 'saturation'

    node_env = nodes.new('ShaderNodeTexEnvironment')
    node_env.name = "HLS_ENV"
    node_env.image = img
    node_env.location = 200,0

    #if not real_HDR:
    node_math = nodes.new('ShaderNodeMath')
    node_math.name = "HLS_MATH"
    node_math.location = 400,-100
    node_math.operation = 'ADD'

    node_bkgnd = nodes.new('ShaderNodeBackground')
    node_bkgnd.location = 600,0
    node_bkgnd.name = 'bkgnd'

    node_reflexion = nodes.new('ShaderNodeBackground')
    node_reflexion.location = 600,-200
    node_reflexion.name = 'reflexion'

    node_light_path = nodes.new('ShaderNodeLightPath')
    node_light_path.location = 600,400
    node_light_path.name = 'light_path'

    node_ref_mix = nodes.new('ShaderNodeMixShader')
    node_ref_mix.location = 800,0
    node_ref_mix.name = 'ref_mix'

    node_out = nodes.new('ShaderNodeOutputWorld')
    node_out.location = 1000,0
    node_out.name = 'output'

    #create links
    links = tree.links
    link0 = links.new(node_coo.outputs[0],node_map.inputs[0])
    link1 = links.new(node_map.outputs[0],node_env.inputs[0])
    link2 = links.new(node_rgb.outputs[0],node_add.inputs[1])
    link3 = links.new(node_env.outputs[0],node_sat.inputs[4])
    link4 = links.new(node_sat.outputs[0],node_add.inputs[2])
    link5 = links.new(node_add.outputs[0],node_reflexion.inputs[0])
    link6 = links.new(node_add.outputs[0],node_bkgnd.inputs[0])
    link7 = links.new(node_light_path.outputs[3],node_ref_mix.inputs[0])
    if not real_HDR:
        link8 = links.new(node_env.outputs[0],node_math.inputs[0])
        link9 = links.new(node_math.outputs[0],node_bkgnd.inputs[1])
    link10 = links.new(node_bkgnd.outputs[0],node_ref_mix.inputs[1])
    link11 = links.new(node_reflexion.outputs[0],node_ref_mix.inputs[2])
    link12 = links.new(node_ref_mix.outputs[0],node_out.inputs[0])

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
bpy.types.Scene.color_r = bpy.props.IntProperty(name="R",update=update_r, max = 255, min = 0, default = 0)
bpy.types.Scene.color_g = bpy.props.IntProperty(name="G",update=update_g, max = 255, min = 0, default = 0)
bpy.types.Scene.color_b = bpy.props.IntProperty(name="B",update=update_b, max = 255, min = 0, default = 0)
bpy.types.Scene.sat = bpy.props.FloatProperty(name="Saturation",update=update_sat, max = 2, min = 0, default = 1)
bpy.types.Scene.hue = bpy.props.FloatProperty(name="Hue",update=update_hue, max = 1, min = 0, default = .5)
bpy.types.Scene.reflexion = bpy.props.FloatProperty(name="Reflexion Intensity",update=update_reflexion, default = 1)
bpy.types.Scene.colcor = bpy.props.BoolProperty(name="Adjustments",update=update_colcor, default = False)



reset()

# ---------------------- GUI -----------------------
class hdri_map(bpy.types.Panel):
    bl_idname = "OBJECT_PT_sample"
    bl_label = "HDRI Lighting Shortcut"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    
    def draw(self, context):
        global color_correc
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
            
            self.layout.operator("remove.setup")

            box = layout.box()
            row = box.row() 
            row.label(os.path.basename(img), icon='FILE_IMAGE')
            row.prop(scene, "visible")
            row = box.row()
            row.prop(scene, "light_strength")
            #row = layout.row()
            row.prop(scene, "z_orientation")
            row = box.row()
            row.prop(scene, "colcor")
            if color_correc == True:
                row = box.row()
                row.prop(scene, "sat")
                row.prop(scene, "hue")
                row = box.row()
                row.prop(scene, "color_r")
                row.prop(scene, "color_g")
                row.prop(scene, "color_b")
                row = box.row()
                row.prop(scene,'reflexion')


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

class OBJECT_OT_Remove_setup(bpy.types.Operator):
    bl_idname = "remove.setup"
    bl_label = "Delete"
 
    def execute(self, context):
        tree_name = "HDRI Lighting Shortcut"
        if node_tree_exists(tree_name):
            nw_world = bpy.data.worlds[world_num(tree_name)]
            bpy.context.scene.world = nw_world
            clear_node_tree()
            # stupid trick to force cycles to update the viewport
            bpy.context.scene.world.light_settings.use_ambient_occlusion = not bpy.context.scene.world.light_settings.use_ambient_occlusion
            bpy.context.scene.world.light_settings.use_ambient_occlusion = not bpy.context.scene.world.light_settings.use_ambient_occlusion
        return{'RUNNING_MODAL'}    

# ----------------- Registration -------------------     
def register():
    bpy.utils.register_class(hdri_map)
    bpy.utils.register_module(__name__)

 
def unregister():
    bpy.utils.unregister_class(hdri_map)
    bpy.utils.unregister_class(OBJECT_OT_load_img)
    bpy.utils.unregister_class(OBJECT_OT_Remove_setup)

if __name__ == "__main__":
    register()
