# Recovery Of An Object's 3D Geometry From a 2D Projection

## Introduction
The conversion of 2D retinal input to 3D representation of the world is one of the most important capabilities of the human visual system. This conversion is both quick and accurate, and many behavioral experiments have been performed to identify the limits of human performance(e.g. 1,2). These studies tend to focus on monocular or binocular reconstruction. Binocular reconstruction consistently produces better 3D shape inference (Pizlo) than monocular reconstruction, but accurate monocular 3D shape perception is still possible. That monocular reconstruction is possible at all is notable in that there are an infinite number of 3D scenes that could produce any given 2D retinal image. Therefore, the process of inverting the projection of 3D scene onto the 2D retina is ill-posed and difficult. Despite the difficulty, the brain achieves some level of monocular 3D reconstruction accuracy by applying constraints that reflect regularities in our physical world (Pizlo). For instance, many objects in the natural world are symmetrical, and so the brain may select the 3D object consistent with the 2D input that is maximally symmetrical. In computer vision, implementation of these constraints is typically done using an optimization approach that can be accurate, but is slow and biologically implausible. Mishra & Helie (2020) began to address the speed and biological plausibility issues by using a deep convolutional neural network trained to monocularly reconstruct simple polyhedral objects that had minimally varying 3D angles. The constraint of minimum standard deviation of 3D angles (MSDA) was shown by Marill (1989) to generate accurate 3D reconstructions for some polyhedral shapes. Leclerc and Fischler (1992) demonstrated that the constraint of minimum standard deviation of angles in conjunction with a constraint requiring planar faces produced even better 3D reconstructions. This project builds on Mishra & Helie’s approach by changing the underlying neural network architecture, training the network on a slightly larger class of objects, and adding a planarity constraint as defined by Fischler and Leclerc. 

## Methods
### Data Generation
Three dimensional cuboid objects were generated algorithmically in the software Blender. Each cuboid was generated at the origin of a global coordinate system, and then rotated a random amount about the x,y and z axes. A camera coordinate system was then defined. The location of each of the cuboids visible vertices was measured in the camera coordinate system by the equation <img src="https://render.githubusercontent.com/render/math?math=V = U^{-1}W">, where U is the set of orthonormal basis vectors defining the x,y,z axes of the camera coordinate system and W is the set of vectors defining the distance from camera coordinate system origin to visible vertex. The Blender UI and camera and global coordinate systems are shown in figure 1.

<img src="https://github.com/mabeers-arco/3DVision/blob/main/Blender.png" height="400" />

Figure 1: Blender UI with an example cuboid 

Blender outputs a file containing the x,y,z values of the visible vertices in the camera coordinate system and a connection matrix describing which vertices share an edge, as shown in figure 2. 

<img src="https://github.com/mabeers-arco/3DVision/blob/main/network_input.png" height="400" />

Figure 2: Description of Blender output. This image taken from Mishra and Helie (2020).

A visual summary of the objects the network was trained on is provided in figure 3. Objects are basically an arbitrary quadrilateral extruded in the direction normal to the plane the quadrilateral rests in. This results in four perfectly rectangular sides and two sides of any shape. 

<img src="https://github.com/mabeers-arco/3DVision/blob/main/object_list.png" height="400" />

Figure 3: A set of randomly selected 2D images the network was trained and tested on. 

### Network Architecture and Training
The neural network architecture used in this work is very similar to LeNet. The network takes in three channels of data. The first channel describes the x coordinates of the object vertices in the camera coordinate system. The second channel describes the y coordinates of the object vertices. The third channel describes the connection matrix as shown in figure 2. The output of the final layer of the network is an estimate of the depth values for each (x,y) pair. 

The LeNet architecture mirrored in this work includes several fully connected layers. The size of the output from Blender changes depending on how many vertices are visible, so the Blender output is padded before being passed to the network so that the output dimensions of the early convolutional layers are the correct size. The architecture is presented in figure 4. 

*********************FIGURE 4 GOES HERE**************************

Figure 4: LeNet architecture employed for this project

After depth estimates for each (x,y) pair are produced by the network, we refer to the connection matrix and compute the appropriate edges. In other words, if vertex 0 is connected to vertex 1, we take the difference of the (x,y,z) coordinates of vertex 0 and vertex 1 to get E01. Once all edges that exist in the connection matrix are computed, the angles between connected edges are computed using the formula <img src="https://render.githubusercontent.com/render/math?math=a\dot b = \Vert a\Vert \Vert b\Vert cos(\theta)">. Once all the relevant 3D angles are computed, we take the standard devation. This quantity becomes one part of the forward function output. The second part of the output corresponds to a planarity constraint. A planar polygon with n sides has sum of internal angles equal to <img src="https://render.githubusercontent.com/render/math?math=(n - 2)\pi">. If the polygon is non-planar the sum of its internal angles will be different. For each visible face of our object, we compute the absolute value of the difference between the sum of internal angles and <img src="https://render.githubusercontent.com/render/math?math=(n - 2)\pi">. The sum of these differences, added to the standard deviation of 3D angles is the forward function's output during training. During training, the loss is defined as the absolute value of the difference between the network output and the true standard deviation of the same angles computed within the network. The true object has perfectly planar sides, so comparing network output to true SDA is identical to comparing network output to true SDA plus a deviation from planarity penalty. 

The network takes about 150 epochs for the loss to asymptote, and this asymptote occurs at around 1 to 2 degrees difference between true SDA and network output. The Adam optimizer was used and training for 150 epochs takes about 20 minutes on the CPU runtime of a Google Colab with a training dataset of 1000 cuboids and a batch size of 10. As the loss has some reasonable interpretation, I have included a plot of it below. 

########################## FIGURE 5 LOSS FUNCTION ###########################


## Results
There is no objectively best way to compare the shape of a reconstruction to the true shape of an object so quantification of network performance is hard. I have instead provided a number of figures that summarize performance. In particular, for a test set of 100 objects, I have provided a histogram of differences between the true angle and estimated angle for every angle in each of the 100 test shapes. I have also provided a histogram of the distances between the true vertex location and estimated vertex location. 


######################## FIGURE 6 GOES HERE #######################################

Figure 5: Summary of differences between angles and distances in test set

In addition, I have provided a gif of a "good" reconstruction and a "bad" reconstruction from the same network. I also provided a detailed numerical summary of the good reconstruction. As a final summary, an unscientific visual inspection of the 100 test reconstructions yielded X "good" reconstructions and Y "bad" reconstructions. 

## Future Work 


## References

## Good Reconstruction

------------------------------------------------------
ANGLES
     Vertices  Actual Angle Estimated Angle
1   [1, 0, 3]     90.000000         93.2955
2   [0, 1, 2]     81.818184         83.9141
3   [0, 1, 4]     89.999977         86.2022
4   [2, 1, 4]     89.999962         86.1603
5   [1, 2, 5]     90.000015         93.6117
6   [4, 3, 0]     90.000053          85.519
7   [4, 3, 6]     65.454559          64.023
8   [0, 3, 6]     90.000000         87.6224
9   [3, 4, 5]     81.818192         84.4609
10  [3, 4, 1]     89.999985         94.9735
11  [5, 4, 1]     89.999977         94.2701
12  [4, 5, 6]    114.545471         113.399
13  [4, 5, 2]     90.000046         85.9579
14  [6, 5, 2]     89.999992         91.5402
15  [5, 6, 3]     98.181793         97.8369
------------------------------------------------------
SDA + PLANARITY
                          Estimated     Actual
SDA                       10.311151  10.004722
Deviation from Planarity   0.269958   0.000000
Total Loss                10.581109  10.004722
------------------------------------------------------
XYZ
          X         Y   Actual Z  Estimated Z
0  0.981972  0.198792 -11.286680    -0.560142
1 -0.737786  0.630276 -10.879275    -0.278223
2 -0.927186 -0.319611 -11.359913    -0.690502
3  1.074211 -0.265353 -10.405737     0.340475
4 -0.645546  0.166130  -9.998331     0.581059
5 -0.834946 -0.783756 -10.478970     0.177497
6  0.050477 -1.289798 -10.838299    -0.154359
------------------------------------------------------
FACE [3, 4, 5, 6]
        Vertices Actual Angle Estimated Angle
0      [3, 4, 5]      81.8182         84.4609
1      [4, 5, 6]      114.545         113.399
2      [5, 6, 3]      98.1818         97.8369
3      [6, 3, 4]      65.4546          64.023
Total        NaN          360          359.72
------------------------------------------------------
FACE [1, 2, 5, 4]
        Vertices Actual Angle Estimated Angle
0      [1, 2, 5]           90         93.6117
1      [2, 5, 4]           90         85.9579
2      [5, 4, 1]           90         94.2701
3      [4, 1, 2]           90         86.1603
Total        NaN          360             360
------------------------------------------------------
FACE [0, 1, 4, 3]
        Vertices Actual Angle Estimated Angle
0      [0, 1, 4]           90         86.2022
1      [1, 4, 3]           90         94.9735
2      [4, 3, 0]      90.0001          85.519
3      [3, 0, 1]           90         93.2955
Total        NaN          360          359.99
------------------------------------------------------
  Verts in Edge Actual Distance Estimated Distance
0        (0, 1)         1.81926            1.79533
1        (0, 3)               1            1.01737
2        (1, 2)         1.08128            1.05268
3        (1, 4)               1           0.980972
4        (2, 5)               1           0.988615
5        (3, 4)         1.81926            1.78931
6        (3, 6)          1.5115            1.53048
7        (4, 5)         1.08128            1.04929
8        (5, 6)         1.08128            1.07247
------------------------------------------------------
