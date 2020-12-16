# COPIED AND PASTED FROM PLAY WITH INPUT DATA JUPYTER NOTEBOOK
import matplotlib
import torch
import torch.nn as nn
import numpy as np
import pickle
import matplotlib.pyplot as plt
import sys
import plotly 
import collections
#import chart_studio.plotly as py
import plotly.graph_objs as go
# from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
# init_notebook_mode(connected=False)
import math
import pylab

def get_edge_vert_pairs_from(conn):
    N = math.ceil(math.sqrt(len(conn.squeeze())*2))
    pairs = []
    count = 0
    for delta in range(1, N):
        start = 0
        while start + delta < N:
            index1 = start
            index2 = start + delta
            #print(index1, index2)
            #print ("search for:", index1,index2)
            if conn.squeeze()[count] == 1:
                pairs.append((index1, index2))
            start += 1
            count += 1
    return pairs


def read_in_object_data(fpath, device):
    with open(fpath, 'rb') as f:
        data = pickle.load(f)
        print(len(data)/7)
        object_list = []
        for i in range(len(data)):
            if(i%7 > 0): # why do we take every fifth object? 
                continue
            object_summary = object_data(label = data[i],
                                         xyz = data[i+1],
                                         xyz_proj = data[i+2],
                                         conn = data[i+3], 
                                         deg = data[i+4], 
                                         angs = data[i+5],
                                         sda = data[i+6], 
                                         device = device)
            object_list.append(object_summary)

    return object_list


def get_data_set(object_list, xyz_transform, conn_transform):
    if not xyz_transform:
        xyz_transform = lambda x: x
    if not conn_transform:
        conn_transform = lambda x: x
    dataset = torch.utils.data.TensorDataset(torch.stack([xyz_transform(obj.xyz_proj) for obj in object_list]), 
                                           torch.stack([conn_transform(obj.conn) for obj in object_list]), 
                                           torch.tensor([obj.sda for obj in object_list]))
    return dataset


def number_of_visible_verts(obj):
    return len(obj.xyz[0])

def summarize(object_list):
    counts = [number_of_visible_verts(ob) for ob in object_list]
    counts = collections.Counter(counts)
    # histogram of counts. 
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (18, 5))
    fig.suptitle('Summary of Object List')
    ax1.bar(list(counts.keys()), counts.values(), color='g')
    ax1.set_xlabel("Number of Visible Vertices")
    ax1.set_ylabel("Frequency")
    ax2.hist([obj.sda.tolist()[0] for obj in object_list])
    ax2.set_xlabel("SDA")
    ax2.set_ylabel("Frequency")

def get_objects_with_id(label, object_list):
    return [ob for ob in object_list if ob.label == label]
    
    
def show_list_of_objects2d(object_list, save=False):
    n = math.ceil(math.sqrt(len(object_list)))
    fig, axs = plt.subplots(n, n, figsize = (14, 9))
    counter = 0
    for i in range(n):
        for j in range(n):
            if counter == len(object_list):
                break
            ob = object_list[counter]
            pairs = get_edge_vert_pairs_from(ob.conn)
            lines = []
            for p in pairs:
                x0 = ob.xyz_proj[0, p[0]]
                y0 = ob.xyz_proj[1, p[0]]
                x1 = ob.xyz_proj[0, p[1]]
                y1 = ob.xyz_proj[1, p[1]]
                lines.append([(x0,y0), (x1, y1)])

            lc = matplotlib.collections.LineCollection(lines, color = "orange", linewidths=1)
            axs[i, j].add_collection(lc)
            axs[i, j].scatter(ob.xyz_proj[0,:], ob.xyz_proj[1,:])
            axs[i, j].set_xlim(-2,2)
            axs[i, j].set_ylim(-2,2)
            counter += 1

    if save:
        fig.savefig("object_list.png")



class object_data():
    def __init__(self, label, xyz, xyz_proj, conn, deg, angs, sda, device):
        self.label = label
        self.xyz = torch.tensor(xyz, dtype=torch.float32).to(device).transpose(0,1)
        self.conn = torch.tensor(conn, dtype=torch.float32).unsqueeze(0).to(device) 
        self.deg = torch.tensor(deg, dtype=torch.float32).to(device) 
        self.angs = torch.tensor(angs, dtype=torch.float32).unsqueeze(0).to(device) 
        self.sda = torch.tensor(sda, dtype=torch.float32).unsqueeze(0).to(device) 
        self.xyz_proj = torch.tensor(xyz_proj, dtype=torch.float32).to(device).transpose(0,1)
        self.device = device

    def show(self, projected = False):
        #credit: https://stackoverflow.com/questions/42301481/adding-specific-lines-to-a-plotly-scatter3d-plot
        pairs = get_edge_vert_pairs_from(self.conn)
        if projected:
            X = self.xyz_proj[0]
            Y = self.xyz_proj[1]
            Z = self.xyz_proj[2]
        else:
            X = self.xyz[0]
            Y = self.xyz[1]
            Z = self.xyz[2]
            
            
        trace1 = go.Scatter3d(
            x=X,
            y=Y,
            z=Z,
            mode='markers',
            name='Vertices'
        )

        x_lines = list()
        y_lines = list()
        z_lines = list()

        #create the coordinate list for the lines
        for p in pairs:
            for i in range(2):
                x_lines.append(X[p[i]])
                y_lines.append(Y[p[i]])
                z_lines.append(Z[p[i]])
            x_lines.append(None)
            y_lines.append(None)
            z_lines.append(None)

        trace2 = go.Scatter3d(
            x=x_lines,
            y=y_lines,
            z=z_lines,
            mode='lines',
            name='Edges'
        )

        fig = go.Figure(data=[trace1, trace2])
        fig.show()
    #     plotly.offline.iplot(fig, filename='simple-3d-scatter')
    #     print(self.xyz.transpose(0,1))
    #     fig = go.Figure(data=go.Scatter3d(x=self.xyz[0], y=self.xyz[1], z=self.xyz[2], mode='markers'))
    #     fig.show()
    
    def show2d(self):
        pairs = get_edge_vert_pairs_from(self.conn)
        lines = []
        for p in pairs:
            x0 = self.xyz_proj[0, p[0]]
            y0 = self.xyz_proj[1, p[0]]
            x1 = self.xyz_proj[0, p[1]]
            y1 = self.xyz_proj[1, p[1]]
            lines.append([(x0,y0), (x1, y1)])

        lc = matplotlib.collections.LineCollection(lines, color = "orange", linewidths=1)
        fig, ax = pylab.subplots(figsize = (8, 4.5))
        ax.add_collection(lc)
        ax.scatter(self.xyz_proj[0,:], self.xyz_proj[1,:])
        matplotlib.pyplot.xlim(0,1)
        matplotlib.pyplot.ylim(0,1)
        plt.show()




class pad_xyz(object):
    def __init__(self, nverts):
        self.nverts = nverts      

    def __call__(self, xyz):
        vv = xyz.shape[1]
        pad = self.nverts - vv
        m = nn.ZeroPad2d((0, pad, 0, 0)) #padding(left,right,top,bottom)
        return m(xyz)

class restructure_conn(object):
    def __init__(self, nverts):
        self.nverts = nverts
        
    def __call__(self, conn):
        pairs = get_edge_vert_pairs_from(conn = conn.squeeze())
        count = 0
        new_conn = []
        for delta in range(1, self.nverts):
            start = 0
            
            while start + delta < self.nverts:
                index1 = start
                index2 = start + delta
                if (index1, index2) in pairs:
                    new_conn.append(1)
                else:
                    new_conn.append(0)
                start += 1
                count += 1
        return torch.tensor(new_conn)




