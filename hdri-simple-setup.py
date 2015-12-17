import bpy

global nodes, node_math, node_map

# good

def update_orientation(self, context):
    node_map.rotation[2] = self.z_orientation
    print("orientation")
    
def update_strength(self, context):
    node_math.inputs[1].default_value = self.light_strength
    
def update_visible(self, context):
    cam = bpy.context.scene.world.cycles_visibility
    cam.camera = not cam.camera
 
bpy.types.Scene.z_orientation = bpy.props.FloatProperty(name="Orientation",update=update_orientation)
bpy.types.Scene.light_strength = bpy.props.FloatProperty(name="Strength",update=update_strength)
bpy.types.Scene.filepath = bpy.props.StringProperty(subtype='FILE_PATH')  
bpy.types.Scene.visible = bpy.props.BoolProperty(update=update_visible, name="Visible",description="Let the background being visible by the camera",default = False)

def setup(img_path):
    global nodes,node_math, node_map
    bpy.context.area.type = 'NODE_EDITOR'
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.space_data.tree_type = 'ShaderNodeTree'
    bpy.context.space_data.shader_type = 'WORLD'

    nw_world = bpy.data.worlds.new("custom_hdri_setup")
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
    node_math.operation = 'MULTIPLY'

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

class hdri_map(bpy.types.Panel):
    bl_idname = "OBJECT_PT_sample"
    bl_label = "Global Lightning Setup"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    
    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        
        row = layout.row()      
        row.operator("nodes.img", icon="TRIA_RIGHT")
        row.prop(scene, "visible")
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
        global img_path
        img_path = self.properties.filepath
        setup(img_path)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.directory = "//"
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
        #return {'FINISHED'}
        
def register():
    bpy.utils.register_class(hdri_map)
    bpy.utils.register_module(__name__)
 
def unregister():
    bpy.utils.unregister_class(hdri_map)

if __name__ == "__main__":
    register()



