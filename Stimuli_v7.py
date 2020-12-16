import bpy, bmesh
from math import *
from mathutils import Vector
import random
import bpy
from bpy import context
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
from itertools import accumulate
import numpy as np
import time
import math

# import os
# os.chdir("users/mark/documents/uci/research/239")
# exec(open('Stimuli_v7.py').read())



def getAllCoords(obj):
    coords = [(obj.matrix_world @ v.co) for v in obj.data.vertices]
    print(coords)
    
# Create a BVH tree and return bvh and vertices in world coordinates 
def BVHTreeAndVerticesInWorldFromObj( obj ):
    mWorld = obj.matrix_world
    vertsInWorld = [mWorld @ v.co for v in obj.data.vertices]
    bvh = BVHTree.FromPolygons( vertsInWorld, [p.vertices for p in obj.data.polygons] )
    return bvh, vertsInWorld

def createVertices(NUMVERTS=4):
    rsum = 0
    rands = [random.randrange(2,5,1) for _ in range (NUMVERTS)]
    rsum = sum(rands)
    dphis = [(2*pi*rands[i])/rsum for i in range(NUMVERTS)]
    Dphis = np.cumsum(dphis)
    
    #calculate x,y coordinate pairs
    #coords = [(cos(i*dphis[i]),sin(i*dphis[i]),0) for i in range(NUMVERTS)]
    coords = [(cos(Dphis[i]),sin(Dphis[i]),0) for i in range(NUMVERTS)]

    bm = bmesh.new()
    for v in coords:
        bm.verts.new(v)

    # think of this new vertices as bottom of the extruded shape
    bottom = bm.faces.new(bm.verts)

    # next we create top via extrude operator, note it doesn't move the new face
    # we make our 1 face into a list so it can be accepted to geom
    top = bmesh.ops.extrude_face_region(bm, geom=[bottom])

    # here we move all vertices returned by the previous extrusion
    # filter the "geom" list for vertices using list constructor
    bmesh.ops.translate(bm, vec=Vector((0,0,1)), verts=[v for v in top["geom"] if isinstance(v,bmesh.types.BMVert)])
    bm.normal_update()

    me = bpy.data.meshes.new("cube")
    bm.to_mesh(me)
    

    # add bmesh to scene
    ob = bpy.data.objects.new("cube",me)
    # bpy.context.scene.objects.link(ob)
    # bpy.context.scene.update()
    layer = bpy.context.view_layer
    layer.update()
    bpy.context.collection.objects.link(ob)
    
    ob.rotation_euler = (random.random()*radians(90), random.random()*radians(90), random.random()*radians(90)) #MARK COMMENTED THESE OUT
    #bpy.context.scene.update()   # MARK COMMENTED THESE OUT
    layer = bpy.context.view_layer
    layer.update()
    # rotate_obj(ob, 1)
    # rotate_obj(ob, 2)

    
    coords_all = []
    for verts in bm.verts:
        #print("verts:",verts,"coords:", ob.matrix_world @ verts.co)
        coords_all.append(ob.matrix_world @ verts.co)
        
    # for edge in bm.edges:
    #     print("edge vertices:", edge.verts[0].index, edge.verts[1].index)
    
    N=NUMVERTS*2 # because mirroring across plane. 
    conn=[]
    # for j in range(1,N):
    #     for i in range(1,N-j+1):
    #         print ("search for:", i-1,i+j-1)
    #         F=0
    #         for edge in bm.edges:
    #             if (edge.verts[0].index == i-1 and edge.verts[1].index == i+j-1) or (edge.verts[0].index == i+j-1 and edge.verts[1].index == i-1):
    #                 print ("Y:",edge.verts[0].index, edge.verts[1].index)
    #                 F=1
    #         conn.append(F) 

    for delta in range(1, N):
        start = 0
        while start + delta < N:
            index1 = start
            index2 = start + delta
            #print ("search for:", index1,index2)
            F = 0
            for edge in bm.edges:
                if (edge.verts[0].index == index1 and edge.verts[1].index == index2) or (edge.verts[0].index == index2 and edge.verts[1].index == index1):
                    #print ("Y:",edge.verts[0].index, edge.verts[1].index)
                    F = 1
            conn.append(F)
            start += 1

  
    # print("conn vec", conn, "len: ", len(conn))    
            
    # print("std dev of all angles: ", np.std(dphis), "\n")
    # print("\n")

    faces = []
    for edge in bm.faces:
        faces += [[v.index for v in edge.verts]]

    print(faces)

    return ob, dphis, np.std(dphis),coords_all, conn


def get_visible_conn_matrix(ob, vverts):
    me = ob.data
    # Get a BMesh representation
    bm = bmesh.new()  # create an empty BMesh
    bm.from_mesh(me)  # fill it in from a Mesh

    conn = []
    N = len(vverts)
    vert_id = []

    for v in bm.verts:
        if v.select == True:
            # print("vertex index:", v.index)
            vert_id.append(v.index)

    for delta in range(1, N):
        start = 0
        while start + delta < N:
            index1 = vert_id[start]
            index2 = vert_id[start + delta]
            #print ("search for:", index1,index2)
            F = 0
            for edge in bm.edges:
                if (edge.verts[0].index == index1 and edge.verts[1].index == index2) or (edge.verts[0].index == index2 and edge.verts[1].index == index1):
                    #print ("Y:",edge.verts[0].index, edge.verts[1].index)
                    F = 1
            
            conn.append(F)
            start += 1

    #bpy.ops.object.mode_set(mode='OBJECT')
    return conn

def compute_edge_angles_degrees(ob, ids):
    me = ob.data
    # Get a BMesh representation
    bm = bmesh.new()  # create an empty BMesh
    bm.from_mesh(me)  # fill it in from a Mesh
    all_angles = []
    all_degrees = np.zeros_like(ids)

    for i, id in enumerate(ids):
        edges = []
        prev_edge = 0
        # print("Searching all edges for vert: ", id)

        for edge in bm.edges:
            if (edge.verts[0].index == id or edge.verts[1].index == id):
                # print("edge found:", edge)
                edges.append(edge)
                if (isVisibleEdge(edge, ids)):
                    all_degrees[i] += 1
            else:
                continue

        for edge in edges:
            if (prev_edge == 0):
                prev_edge = edge
                continue
            # print("edge pair: ", prev_edge, edge) #edge.verts[0].index
            v00 = edge.verts[0]
            v01 = edge.verts[1]
            v10 = prev_edge.verts[0]
            v11 = prev_edge.verts[1]
            v0 = Vector(v00.co) - Vector(v01.co)
            v1 = Vector(v10.co) - Vector(v11.co)
            # print("Angle: ", math.degrees(v0.angle(v1)))
            all_angles.append(v0.angle(v1))
            prev_edge = edge

    # print("All degrees: ",all_degrees)
    return all_angles, all_degrees

def isVisibleEdge(e, vv_ids):
    if (e.verts[0].index in vv_ids and e.verts[1].index in vv_ids):
        # print("edge visible:", e)
        return True
    else:
        # print("edge not visible", e)
        return False


def createNObjects(N=10, num_angles = 7):
    data = []
    for i in range(N):
        # delete all objects
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()
        ob, dphis, sda, coords, conn  = createVertices(NUMVERTS)
        scene = bpy.context.scene
        cam = bpy.context.scene.camera #bpy.data.objects['Camera']
        for k in range(num_angles):
            visible_vertices, vvid, projected_verts = getVisibleVertices(ob, cam, scene)
            #print("vvids = ", vvid)
            visible_conn = get_visible_conn_matrix(ob, visible_vertices)
            #print(visible_vertices)
            #k = len(visible_vertices)
            #print("visible conn len should be {}, but is actually {}".format(k*(k-1)/2, len(visible_conn)))
            angles, degrees = compute_edge_angles_degrees(ob, vvid)

            ####
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            visible_faces = get_visible_faces(bm, vvid)
            #print("visible faces = ", visible_faces)
            ####
            pv = get_pv(cam, visible_vertices)
            # obj = np.asarray(coords)
            # print(obj)
            # nv = obj.shape[0]
            # print(obj.shape)
            # obj=(obj.T.reshape(3,nv))
            # visible_conn = np.tile(visible_conn, (3,1))
            # data.append(np.concatenate((obj,conn), axis=1))   
            data.append(i) # i is an object id 
            data.append(visible_vertices)
            data.append(visible_faces)
            #data.append(projected_verts)
            data.append(pv)
            data.append(visible_conn)
            data.append(degrees)
            data.append(angles)
            data.append(np.std(angles)) 
            ob.rotation_euler = (random.random()*radians(180), random.random()*radians(180), random.random()*radians(180)) #MARK COMMENTED THESE OUT
            bpy.data.scenes.update()
            bpy.context.view_layer.update()
        #time.sleep(.5)

    return data    


def vvid_to_inds(vvid):
    translation_dict = {}
    for i, vertid in enumerate(vvid):
        translation_dict[vertid] = i
    return translation_dict

def get_visible_faces(bm, vvid):
    new_faces = []
    translation_dict = vvid_to_inds(vvid)
    ########################### 
    #temporary
    # faces = []
    # for edge in bm.faces:
    #     faces += [[v.index for v in edge.verts]]
    # print(faces)
    #############################
    for face in bm.faces:
        face_verts = []
        for v in face.verts:
            try:
                face_verts += [translation_dict[v.index]]
            except KeyError:
                break
        else:
            new_faces += [face_verts]
    return new_faces

def get_pv(cam, vverts):
    camI = cam.rotation_euler.to_matrix().copy()
    camI.invert()
    from_cam_to_vert = [Vector(v) - cam.location for v in vverts]
    new_verts = [camI @ v for v in from_cam_to_vert]
    return [[v.x, v.y, v.z] for v in new_verts]



def getVisibleVertices(obj, cam, scene):    
    # In world coordinates, get a bvh tree and vertices
    bvh, vertices = BVHTreeAndVerticesInWorldFromObj( obj )
    visible_vertices = []
    visible_vertices_id = []
    projected_verts = []
    for i, v in enumerate( vertices ):
        #print("vertex #")
        #print(i)
        # Get the 2D projection of the vertex
        co2D = world_to_camera_view( scene, cam, v )
        # print(co2D)
        # print("\n")
        # By default, deselect it
        obj.data.vertices[i].select = False
        # If inside the camera view
        if 0.0 <= co2D.x <= 1.0 and 0.0 <= co2D.y <= 1.0: 
            #print(i,"this vertex is inside camera view")
            # Try a ray cast, in order to test the vertex visibility from the camera
            location, normal, index, distance = bvh.ray_cast( cam.location, (v - cam.location).normalized() )
            mindists = []
            loc = None
            for _ in range(1000):
                direction_vector = ((v - cam.location).normalized() + Vector((random.gauss(0,.01),random.gauss(0,.01),random.gauss(0,.01)))).normalized()
                location, normal, index, distance = bvh.ray_cast( cam.location, direction_vector )
                if location:
                    #break
                    mindists.append((v - location).length)
            # print("cam.location, (v - cam.location).normalized() , location, normal, index, distance")
            # print(cam.location, (v - cam.location).normalized() , location, normal, index, distance)
            # # If the ray hits something and if this hit is close to the vertex, we assume this is the vertex
            # print("LOCATION=", location)
            # if location:
            #     print("DISTANCE = ", (v - location).length)

            #if location and (v - location).length < limit:
            if mindists and min(mindists) < limit:# and (v - location).length < limit:
                obj.data.vertices[i].select = True
                #print("distance from ray cast = ", min(mindists))
                #print("selected vertex is:", i)
                #print(getCoords(obj.data.vertices[i])) 
                #[ob.matrix_world @ v.co for v in ob.data.vertices]
                visible_vertices.append([v.x,v.y,v.z])
                #v_global = obj.matrix_world @ obj.data.vertices[i].co
                projected_verts.append([co2D.x, co2D.y, co2D.z]) # shoot you messed up.
                #projected_verts.append([v_global.x, v_global.y, v_global.z])
                visible_vertices_id.append(i)

        #print("\n\n")        
    #print("#verts:", NUMVERTS, " #visible vertices:", len(visible_vertices))
    del bvh
    #print("visible vertices:",visible_vertices)
    return visible_vertices, visible_vertices_id, projected_verts


# def camera_shots(a):
#     cam = bpy.data.objects['Camera']
#     origin = bpy.data.objects['cube']

#     step_count = 3

#     for step in range(0, step_count):
#         origin.rotation_euler[a] = radians(step * (360.0 / step_count))
#         #print(math.degrees(origin.rotation_euler[2]))
#         bpy.data.scenes["Scene"].render.filepath = PATH + 'rot_xyz_%d_%d_%d.png' % (math.degrees(origin.rotation_euler[0]), math.degrees(origin.rotation_euler[1]), math.degrees(origin.rotation_euler[2]))
#         bpy.ops.render.render( write_still=True )

#PATH="/Users/pmishra/Library/Mobile Documents/com~apple~CloudDocs/blender_scripts/3D vision/Pilot Test Stimuli/New Obj/"
NUMVERTS = 4
PATH = ""
# Threshold to test if ray cast corresponds to the original vertex
limit = .1    
data = createNObjects(500)

#print(data)

#camera_shots(0)
#camera_shots(1)
#camera_shots(2)



import pickle
with open(PATH + 'dataARCO5.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(list(data), f)

# bpy.ops.object.select_by_type(type='MESH')
# bpy.ops.object.delete()
# obj, dphis, sda, coords, conn  = createVertices(NUMVERTS)
# scene = bpy.context.scene
# cam = bpy.context.scene.camera #bpy.data.objects['Camera']
# vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
# co2D = world_to_camera_view( scene, cam, vertices[0] )
# co2D
# scene.camera.rotation_euler[0] = 0
# scene.camera.rotation_euler[1] = 0
# scene.camera.rotation_euler[2] = math.pi/2
# scene.camera.location = Vector([0,0,5])
