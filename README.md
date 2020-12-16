# Recovery Of An Object's 3D Geometry From a 2D Projection

## Introduction
The conversion of 2D retinal input to 3D representation of the world is one of the most important capabilities of the human visual system. This conversion is both quick and accurate, and many behavioral experiments have been performed to identify the limits of human performance(e.g. 1,2). These studies tend to focus on monocular or binocular reconstruction. Binocular reconstruction consistently produces better 3D shape inference (Pizlo) than monocular reconstruction, but accurate monocular 3D shape perception is still possible. That monocular reconstruction is possible at all is notable in that there are an infinite number of 3D scenes that could produce any given 2D retinal image. Therefore, the process of inverting the projection of 3D scene onto the 2D retina is ill-posed and difficult. Despite the difficulty, the brain achieves some level of monocular 3D reconstruction accuracy by applying constraints that reflect regularities in our physical world (Pizlo). For instance, many objects in the natural world are symmetrical, and so the brain may select the 3D object consistent with the 2D input that is maximally symmetrical. In computer vision, implementation of these constraints is typically done using an optimization approach that can be accurate, but is slow and biologically implausible. Mishra & Helie (2020) began to address the speed and biological plausibility issues by using a deep convolutional neural network trained to monocularly reconstruct simple polyhedral objects that had minimally varying 3D angles. The constraint of minimum standard deviation of 3D angles (MSDA) was shown by Marill (1989) to generate accurate 3D reconstructions for some polyhedral shapes. Leclerc and Fischler (1992) demonstrated that the constraint of minimum standard deviation of angles in conjunction with a constraint requiring planar faces produced even better 3D reconstructions. This project builds on Mishra & Helie’s approach by changing the underlying neural network architecture, training the network on a slightly larger class of objects, and adding a planarity constraint as defined by Fischler and Leclerc. 

## Methods
### Data Generation
Three dimensional cuboid objects were generated algorithmically in the software *Blender*. Each cuboid was generated at the origin of a global coordinate system, and then rotated a random amount about the x,y and z axes. A camera coordinate system was then defined. The location of each of the cuboids visible vertices was measured in the camera coordinate system by the equation <img src="https://render.githubusercontent.com/render/math?math=V = U^{-1}W">, where U is the set of orthonormal basis vectors defining the x,y,z axes of the camera coordinate system and W is the set of vectors defining the distance from camera coordinate system origin to visible vertex. The Blender UI and camera and global coordinate systems are shown in Figure 1.

<img src="https://github.com/mabeers-arco/3dReconstruction/blob/main/Blender.png" height="400" />

Figure 1: Blender UI with an example cuboid 

Blender outputs a file containing the x,y,z values of the visible vertices in the camera coordinate system and a connection matrix describing which vertices share an edge. The connection matrix, shown in Figure 2 along with a sample figure, 

### Network Architecture and Training

## Results

## Discussion

## References


