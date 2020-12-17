# Recovery Of An Object's 3D Geometry From a 2D Projection

## Introduction
The conversion of 2D retinal input to 3D representation of the world is one of the most important capabilities of the human visual system. This conversion is both quick and accurate, and many behavioral experiments have been performed to identify the limits of human performance(e.g. 1,2). These studies tend to focus on monocular or binocular reconstruction. Binocular reconstruction consistently produces better 3D shape inference (Pizlo) than monocular reconstruction, but accurate monocular 3D shape perception is still possible. That monocular reconstruction is possible at all is notable in that there are an infinite number of 3D scenes that could produce any given 2D retinal image. Therefore, the process of inverting the projection of 3D scene onto the 2D retina is ill-posed and difficult. Despite the difficulty, the brain achieves some level of monocular 3D reconstruction accuracy by applying constraints that reflect regularities in our physical world (Pizlo). For instance, many objects in the natural world are symmetrical, and so the brain may select the 3D object consistent with the 2D input that is maximally symmetrical. In computer vision, implementation of these constraints is typically done using an optimization approach that can be accurate, but is slow and biologically implausible. Mishra & Helie (2020) began to address the speed and biological plausibility issues by using a deep convolutional neural network trained to monocularly reconstruct simple polyhedral objects that had minimally varying 3D angles. The constraint of minimum standard deviation of 3D angles (MSDA) was shown by Marill (1989) to generate accurate 3D reconstructions for some polyhedral shapes. Leclerc and Fischler (1992) demonstrated that MSDA in conjunction with a constraint requiring planar faces produced even better 3D reconstructions. This project builds on Mishra & Helie’s approach by changing the underlying neural network architecture, training the network on a slightly larger class of objects, and adding a planarity constraint as defined by Leclerc and Fischler. 

## Methods
### Data Generation
Three dimensional cuboid objects were generated algorithmically in the software Blender. Each cuboid was generated at the origin of a global coordinate system, and then rotated a random amount about the x,y and z axes. A camera coordinate system was then defined. The location of each of the cuboids visible vertices was measured in the camera coordinate system by the equation <img src="https://render.githubusercontent.com/render/math?math=V = U^{-1}W">, where U is the set of orthonormal basis vectors defining the x,y,z axes of the camera coordinate system and W is the set of vectors defining the distance from camera coordinate system origin to visible vertex. The Blender UI and camera and global coordinate systems are shown in figure 1.

<img src="https://github.com/mabeers-arco/3DVision/blob/main/Blender.png" height="400" />

**Figure 1:** Blender UI with an example cuboid 


Blender outputs a file containing the x,y,z values of the visible vertices in the camera coordinate system and a connection matrix describing which vertices share an edge, as shown in Figure 2.

<img src="https://github.com/mabeers-arco/3DVision/blob/main/network_input.png" height="400" />

**Figure 2:** Description of Blender output. This image taken from Mishra and Helie (2020).

A random sample of the objects the network was trained on is provided in figure 3. Each object can be constructed by extruding an arbitrary convex quadrilateral in the direction normal to the plane the quadrilateral rests in. This results in four perfectly rectangular sides and two sides that are some convex quadrilateral. 

<img src="https://github.com/mabeers-arco/3DVision/blob/main/object_list.png" height="400" />

**Figure 3:** A set of randomly selected 2D images the network was trained and tested on. 

### Network Architecture and Training
The neural network architecture used in this work is very similar to LeNet. The network takes in three channels of data. The first channel describes the x coordinates of the object vertices in the camera coordinate system. The second channel describes the y coordinates of the object vertices. The third channel describes the connection matrix as shown in figure 2. The output of the final layer of the network is an estimate of the depth values for each (x,y) pair. 

The LeNet architecture mirrored in this work includes several fully connected layers. The size of the output from Blender changes depending on how many vertices are visible, so the Blender output is padded before being passed to the network so that the output dimensions of the early convolutional layers are the correct size. The architecture used in this project is shown in figure 4. 

<img src="https://github.com/mabeers-arco/3DVision/blob/main/Arch.png" height="400" />

***Figure 4:*** LeNet architecture employed for this project

After depth estimates for each (x,y) pair are produced by the network, we refer to the connection matrix and compute the appropriate edges. In other words, if vertex 0 is connected to vertex 1, we take the difference of the (x,y,z) coordinates of vertex 0 and vertex 1 to get E01. Once all edges that exist in the connection matrix are computed, the angles between connected edges are computed using the formula <img src="https://render.githubusercontent.com/render/math?math=a \cdot b = \Vert a\Vert \Vert b\Vert cos(\theta)">. Once all the relevant 3D angles are computed, we take the standard devation. This quantity becomes one part of the forward function output. The second part of the output corresponds to a planarity constraint. A planar polygon with n sides has sum of internal angles equal to <img src="https://render.githubusercontent.com/render/math?math=(n - 2)\pi">. If the polygon is non-planar the sum of its internal angles will be different. For each visible face of our object, we compute the absolute value of the difference between the sum of internal angles and <img src="https://render.githubusercontent.com/render/math?math=(n - 2)\pi">. The sum of these differences, added to the standard deviation of 3D angles is the forward function's output during training. During training, the loss is defined as the absolute value of the difference between the network output and the true standard deviation of the same angles computed within the network. The true object has perfectly planar sides, so comparing network output to true SDA is identical to comparing network output to true SDA plus a deviation from planarity penalty. 

The network takes about 150 epochs for the loss to asymptote, and this asymptote occurs at around 1 to 2 degrees difference between true SDA and network output. The Adam optimizer was used and training for 150 epochs takes about 20 minutes on the CPU runtime of a Google Colab with a training dataset of 1000 cuboids and a batch size of 10. As the loss has some reasonable interpretation, I have included a plot of it below. 

<img src="https://github.com/mabeers-arco/3DVision/blob/main/network_loss_12_16.png" height="400" />


## Results
There is no objectively best way to compare the shape of a reconstruction to the true shape of an object so quantification of network performance is hard. I have  provided a number of figures that summarize performance. In particular, for a test set of 100 objects, I have provided a histogram of differences between the true angle and estimated angle for every angle in each of the 100 test shapes. I have also provided a histogram of the difference between actual edge lengths and estimated edge lengths. 

<img src="https://github.com/mabeers-arco/3DVision/blob/main/deviations.png" height="400" />
**Figure 5:** Summary of angle estimation errors and edge length estimation errors in test set

In addition, I have provided gifs of a "good" reconstruction and a "bad" reconstruction from the same network. The network reconstructions are always centered around z = 0, so the actual object is shifted to the origin for the reconstructions. In the section at the very bottom, a detailed numerical summary of the good and bad reconstructions can be found. 

<img src="https://github.com/mabeers-arco/3DVision/blob/main/good.gif" height="600" />
**Figure 6:** "Good" Reconstruction

<img src="https://github.com/mabeers-arco/3DVision/blob/main/bad.gif" height="600" />
**Figure 7:** "Bad" Reconstruction


## Future Work 


## References

## Numerical Summaries of "Good" and "Bad" Reconstructions

<img src="https://github.com/mabeers-arco/3DVision/blob/main/num_sum.png" height="800" />

