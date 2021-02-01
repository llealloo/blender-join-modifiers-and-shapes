bl_info = {
    "name": "Join Modifiers and Shapes",
    "author": "llealloo",
    "version": (1, 00),
    "blender": (2, 83, 0),
    "location": "View3D > Object Mode > Tool",
    "description": "Join and apply modifiers to selected objects including their shape keys",
    "warning": "",
    "doc_url": "https://github.com/llealloo/join-modifiers-and-shapes/",
    "category": "Object",
}

import bpy

class join_modifiers_shape_keys(bpy.types.Operator):
    """Join selected objects with modifiers applied and shape keys intact"""
    bl_idname = "object.join_modifiers_shape_keys"
    bl_label = "Crunchitize"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj)
    
    def execute(self, context):
        
        nl = ['L','Left','left']
        nr = ['R','Right','right']
        
        ol = bpy.context.selected_objects
        td = []                                                         # to do list
        
        def addToDo(sn, mf, ob):                                             # shape name (string), mirror flag (bool), object (ref)
            for t in td:
                if sn == t[0]:
                    t.append(ob)
                    t[1]
                    return
            td.append([sn, mf, ob])
            return
        
        # Duplicate selected objects (user must include object dependencies with shape keys)
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.duplicate(linked=False)
        dl = bpy.context.selected_objects                           # store duplicates in list
        
        
        for o in ol:                                                # hide original objects
            o.hide_set(True)
        
        
        
        # Build todo list of shape keys (merge matched name shape key directives)
        for o in dl:
            print(o.name)
            bpy.ops.object.select_all(action="DESELECT")
            bpy.context.view_layer.objects.active = o
            o.select_set(True)
            if o.type == "MESH":         
                print("it's a mesh!!")
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.object.mode_set(mode="OBJECT")
            #return {"FINISHED"}
            o.show_only_shape_key = True
            try:                                                    
                for s in o.data.shape_keys.key_blocks[:]:
                    addToDo(s.name, False, o)
                    
                    # Find and create asymmetric shape keys
                    i = -1 
                    for x in nl:                            # return index of suffix match if found in list, else return -1
                        if s.name.endswith(x):
                            i = nl.index(x)
                            break
                    if i==-1:
                        continue  
                    nn = s.name[:-len(nl[i])] + nr[i]                              # new name
                    si = o.data.shape_keys.key_blocks[:].index(s)                      # current shape key index
                    o.active_shape_key_index = si                                  # set active shape key for duplication
                    nk = o.shape_key_add(name=nn, from_mix=True)                   # duplicate to new shape key (added last)
                    o.active_shape_key_index = len(o.data.shape_keys.key_blocks[:])-1  # set last shape key to active
                    while o.active_shape_key_index > si+1:
                        bpy.ops.object.shape_key_move(type="UP")                    # move the new shape key under current
                    addToDo(nk.name, True, o)
            except AttributeError:                             #if no shape keys, then add a Basis and add a task
                bpy.ops.object.shape_key_add(from_mix=False)
                addToDo("Basis", False, o)
                pass
            for m in o.modifiers:                                   
                if m.type == "ARMATURE":
                    armature_apply = True
                    try:
                        armature_link = m.object
                    except:
                        pass
                    
        print(td)
        
        # Iterate through todo list
        sl = []
        for t in td:                                        # reset all to basis shape keys
            print("")
            print("task: "+t[0])
            print("mirrored: "+str(t[1]))
            for o in dl:
                print(" setting "+o.name+" to sk index 0")
                o.active_shape_key_index = 0
            sn = t[0]
            mf = t[1]                                       # mirror flag for asymmetric shape key
            ao = t[2:]                                      # affected object
            
            for o in ao:                                    # set all objects shape keys to todo list key
                sk = o.data.shape_keys.key_blocks
                print(" setting "+o.name+" to sk index "+str(sk[:].index(sk[sn])))
                o.active_shape_key_index = sk[:].index(sk[sn])
                
            
            
            tl = []                                         # temp list of objects
            for o in dl:
                mp = False                                  # look for mirror modifiers
                for m in o.modifiers:
                    if m.type == "MIRROR":
                        mp = True
                        break
                
                if mp and mf:                               # if mirror modifier found and mirror flag true
                    pass                                    # placeholder pass
                bpy.ops.object.select_all(action="DESELECT")
                o.select_set(True)
                bpy.context.view_layer.objects.active = o
                
                bpy.ops.object.duplicate(linked=False)
                no = bpy.context.object                     # the new object
                no.name = no.name + sn
                print(" created: "+no.name)
                
                try:
                    sk = no.data.shape_keys.key_blocks[:]     # delete all shape keys except active one if object has shape keys
                    #print(str(len(sk))+" shape keys")
                    no.active_shape_key_index = 0
                    if o in ao:                                 # if object is affected in this task
                        while len(no.data.shape_keys.key_blocks[:]) > 0:
                            #print("  num shape keys > 0")
                            s = no.data.shape_keys.key_blocks[no.active_shape_key_index]
                            #print("  "+s.name)
                            if s.name != sn:
                                bpy.ops.object.shape_key_remove(all=False)
                            else:
                                no.active_shape_key_index = (no.active_shape_key_index+1)%len(no.data.shape_keys.key_blocks[:])
                                if no.active_shape_key_index == 0:
                                    print("  "+no.data.shape_keys.key_blocks[no.active_shape_key_index].name)
                                    bpy.ops.object.shape_key_remove(all=False)
                                    break
                    else:
                        bpy.ops.object.shape_key_remove(all=True)            # if object is unaffected, delete all shape keys
                except AttributeError:
                    pass                                    # pass if no shape keys
                
                # apply all modifiers
                for m in o.modifiers:
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=m.name)
                
                tl.append(bpy.context.object)               # append to temp object list
                
            # Join the shape's objects
            bpy.ops.object.select_all(action="DESELECT")
            bpy.context.view_layer.objects.active = tl[0]
            nm = []                                                     # list of non mesh objects
            for o in tl:
                o.select_set(True)
                if o.type != "MESH":
                    nm.append(o)
            bpy.ops.object.delete({"selected_objects": nm})             # delete non-mesh objects
            if len(tl)>1:
                bpy.ops.object.join()
            bpy.context.object.name = "Joined_"+str(td.index(t))+"_"+sn
            sl.append(bpy.context.object)
        
        
        #return {'FINISHED'}
        
        # Join generated shape meshes as shapekeys
        fo = sl[0]                                                  # final output object
        print("Starting Verts: "+str(len(fo.data.vertices)))
        bpy.context.view_layer.objects.active = fo
        for so in sl[1:]:
            print(so.name)
            print(" Verts: "+str(len(so.data.vertices)))
            bpy.ops.object.select_all(action="DESELECT")
            bpy.context.view_layer.objects.active = fo
            fo.select_set(True)
            so.select_set(True)
            #return {'FINISHED'}
            bpy.ops.object.join_shapes()
            
        fo.name = "Bake_Output"
        try:
            sk = fo.data.shape_keys.key_blocks[:]
            for s in sk:
                s.name = td[sk.index(s)][0]                             # rename shape keys
        except AttributeError:
            print("object has no shape keys")
            
            
        
        bpy.ops.object.delete({"selected_objects": sl[1:]})         # clean up
        bpy.ops.object.delete({"selected_objects": dl})             # clean up
        for b in bpy.data.meshes:                                   # clean up
            if b.users == 0:
                bpy.data.meshes.remove(b)
        #if armature_apply == True and armature_link is not None:
        #    bpy.ops.object.modifier_add(type='ARMATURE')
        #    ob.modifiers[0].object = armature_link
                
            
                
                
                
                
        
        
        
        return {'FINISHED'}

class OBJECT_PT_join_modifiers_shape_keys_panel(bpy.types.Panel):
    """Creates a Sub-Panel in the Property Area of the 3D View"""
    bl_label = "Join Modifiers & Shapes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_context = "objectmode"

    def draw(self, context):
        try:
            kn = len(context.object.data.shape_keys.key_blocks)
        except AttributeError:
            kn = 0

        layout = self.layout
        layout.separator()
        row = layout.row()
        row.operator(join_modifiers_shape_keys.bl_idname)
        layout.separator()

def register():
    bpy.utils.register_class(join_modifiers_shape_keys)
    bpy.utils.register_class(OBJECT_PT_join_modifiers_shape_keys_panel)


def unregister():
    bpy.utils.unregister_class(join_modifiers_shape_keys)
    bpy.utils.unregister_class(OBJECT_PT_join_modifiers_shape_keys_panel)


if __name__ == "__main__":
    register()
