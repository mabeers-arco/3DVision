# Recovery Of An Object's 3D Geometry From a 2D Projection

## Introduction
The conversion of 2D retinal input to 3D representation of the world is one of the most important capabilities of the human visual system. This conversion is both quick and accurate, and many behavioral experiments have been performed to identify the limits of human performance(e.g. Rock & DiVita, 1987; ). These studies tend to focus on monocular or binocular reconstruction. Binocular reconstruction consistently produces better 3D shape inference (Li et al. 2011) than monocular reconstruction, but accurate monocular 3D shape perception is still possible. That monocular reconstruction is possible at all is notable in that there are an infinite number of 3D scenes that could produce any given 2D retinal image. Therefore, the process of inverting the projection of 3D scene onto the 2D retina is ill-posed and difficult. Despite the difficulty, the brain achieves some level of monocular 3D reconstruction accuracy by applying constraints that reflect regularities in our physical world (Pizlo & Stevenson, 1999). For instance, many objects in the natural world are symmetrical, and so the brain may select the 3D object consistent with the 2D input that is maximally symmetrical. In computer vision, implementation of these constraints is typically done using an optimization approach that can be accurate, but is slow and biologically implausible. Mishra & Helie (2020) began to address the speed and biological plausibility issues by using a deep convolutional neural network trained to monocularly reconstruct simple polyhedral objects that had minimally varying 3D angles. The constraint of minimum standard deviation of 3D angles (MSDA) was shown by Marill (1989) to generate accurate 3D reconstructions for some polyhedral shapes. Leclerc and Fischler (1992) demonstrated that MSDA in conjunction with a constraint requiring planar faces produced even better 3D reconstructions. This project builds on Mishra & Helie’s approach by changing the underlying neural network architecture, training the network on a slightly larger class of objects, and adding a planarity constraint as defined by Leclerc and Fischler. 

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

**Figure 4:** LeNet architecture employed for this project

After depth estimates for each (x,y) pair are produced by the network, we refer to the connection matrix and compute the appropriate edges. In other words, if vertex 0 is connected to vertex 1, we take the difference of the (x,y,z) coordinates of vertex 0 and vertex 1 to get E01. Once all edges that exist in the connection matrix are computed, the angles between connected edges are computed using the formula <img src="https://render.githubusercontent.com/render/math?math=a \cdot b = \Vert a\Vert \Vert b\Vert cos(\theta)">. Once all the relevant 3D angles are computed, we take the standard devation. This quantity becomes one part of the forward function output. The second part of the output corresponds to a planarity constraint. A planar polygon with n sides has sum of internal angles equal to <img src="https://render.githubusercontent.com/render/math?math=(n - 2)\pi">. If the polygon is non-planar the sum of its internal angles will be different. For each visible face of our object, we compute the absolute value of the difference between the sum of internal angles and <img src="https://render.githubusercontent.com/render/math?math=(n - 2)\pi">. The sum of these differences, added to the standard deviation of 3D angles is the forward function's output during training. During training, the loss is defined as the absolute value of the difference between the network output and the true standard deviation of the same angles computed within the network. The true object has perfectly planar sides, so comparing network output to true SDA is identical to comparing network output to true SDA plus a deviation from planarity penalty. 

The network takes about 150 epochs for the loss to asymptote, and this asymptote occurs at around 1 to 2 degrees difference between true SDA and network output. The Adam optimizer was used and training for 150 epochs takes about 20 minutes on the CPU runtime of a Google Colab with a training dataset of 1000 cuboids and a batch size of 10. As the loss has some reasonable interpretation, a plot of it as been included below. 

<img src="https://github.com/mabeers-arco/3DVision/blob/main/network_loss_12_16.png" height="400" />


## Results
There is no objectively best way to compare the shape of a reconstruction to the true shape of an object so quantification of network performance is hard. However, a number of figures that summarize performance have been provided. In particular, in figure 5 there is a histogram of differences between the true angle and estimated angle for every angle in each of 100 test shapes. Figure 5 also contains a histogram of the differences between actual edge lengths and estimated edge lengths. 

<img src="https://github.com/mabeers-arco/3DVision/blob/main/deviations.png" height="400" />

**Figure 5:** Summary of angle estimation errors and edge length estimation errors in test set

In addition, an example of a "good" reconstruction and a "bad" reconstruction from the same network are provided in figures six and seven. These examples were selected by hand and are intended to provide an intuition for the spectrum of reconstructions this algorithm may produce. The network reconstructions are always centered around z = 0, so the actual object is shifted to the origin in figures six and seven for easier comparison. In the section at the very bottom, a detailed numerical summary of the good and bad reconstructions can be found. 

<img src="https://github.com/mabeers-arco/3DVision/blob/main/good_ortho.gif" height="600" />

**Figure 6:** Orthographic Projection of A "Good" Reconstruction

<img src="https://github.com/mabeers-arco/3DVision/blob/main/bad_ortho.gif" height="600" />

**Figure 7:** Orthographic Projection of A "Bad" Reconstruction


## Discussion and Future Work 
The network was able to, in some cases, achieve 3D reconstructions that were visually similar to the actual 3D shape.  These successes were achieved despite the fact that the network employed was relatively small. 

## References
Rock, I., & DiVita,J. (1987). A case of viewer-centered object perception. Cognitive Psychology, 19,280-293.

Li, Y., Sawada, T., Shi, Y., Kwon, T., & Pizlo, Z. (2011). A Bayesian model of binocular perception of 3D mirror symmetrical polyhedra. Journal of Vision, 11(4), 11–11. https://doi.org/10.1167/11.4.11

Pizlo, Z., & Stevenson, A. K. (1999). Shape constancy from novel views. Perception and Psychophysics, 61(7), 1299–1307. https://doi.org/10.3758/BF03206181

Marill, T. (1991). Emulating the human interpretation of line-drawings as three-dimensional objects. International Journal of Computer Vision, 6(2), 147–161. https://doi.org/10.1007/BF00128154

Leclerc, Y. G., & Fischler, M. A. (1992). An optimization-based approach to the interpretation of single line drawings as 3D wire frames. International Journal of Computer Vision, 9(2), 113–136. https://doi.org/10.1007/BF00129683

Mishra, P., & Hélie, S. (2020). 3D shape estimation in a constraint optimization neural network. Vision Research, 177, 118–129. https://doi.org/10.1016/j.visres.2020.08.010



## Numerical Summary of "Good" Reconstruction

 ANGLES
|    | Vertices   |   Actual Angle |   Estimated Angle |
|---:|:-----------|---------------:|------------------:|
|  1 | [1, 0, 4]  |        90      |           88.1462 |
|  2 | [0, 1, 2]  |        96.9231 |           93.5675 |
|  3 | [0, 1, 5]  |        90      |           89.7126 |
|  4 | [2, 1, 5]  |        90      |           89.0361 |
|  5 | [1, 2, 6]  |        90      |           91.2656 |
|  6 | [4, 3, 6]  |        83.0769 |           88.937  |
|  7 | [3, 4, 5]  |        96.9231 |           94.2513 |
|  8 | [3, 4, 0]  |        90.0001 |           93.8838 |
|  9 | [5, 4, 0]  |        90      |           90.7987 |
| 10 | [4, 5, 6]  |        96.9231 |           94.1894 |
| 11 | [4, 5, 1]  |        90      |           91.3177 |
| 12 | [6, 5, 1]  |        90      |           90.7192 |
| 13 | [5, 6, 3]  |        83.0769 |           82.3388 |
| 14 | [5, 6, 2]  |        90      |           88.9755 |
| 15 | [3, 6, 2]  |        90      |           95.3882 |

 SDA + PLANARITY
|                          |   Estimated |   Actual |
|:-------------------------|------------:|---------:|
| SDA                      |    3.29307  |  4.10966 |
| Deviation from Planarity |    0.255249 |  0       |
| Total Loss               |   42.1053   |  4.10966 |

 XYZ
|    |         X |          Y |   Actual Z |   Estimated Z |
|---:|----------:|-----------:|-----------:|--------------:|
|  0 |  0.823482 |  0.608837  |  -11.3435  |     -0.680864 |
|  1 | -0.140282 |  0.611278  |  -10.4324  |      0.346926 |
|  2 | -0.871164 | -0.355916  |  -10.9702  |     -0.221901 |
|  3 |  0.828853 | -1.03717   |  -11.5661  |     -0.782476 |
|  4 |  1.3274   | -0.0693889 |  -10.8086  |     -0.162777 |
|  5 |  0.363631 | -0.0669473 |   -9.89753 |      0.814419 |
|  6 | -0.367251 | -1.03414   |  -10.4354  |      0.233913 |

 [3, 4, 5, 6]
|       | Vertices   |   Actual Angle |   Estimated Angle |
|:------|:-----------|---------------:|------------------:|
| 0     | [3, 4, 5]  |        96.9231 |           94.2513 |
| 1     | [4, 5, 6]  |        96.9231 |           94.1894 |
| 2     | [5, 6, 3]  |        83.0769 |           82.3388 |
| 3     | [6, 3, 4]  |        83.0769 |           88.937  |
| Total | nan        |       360      |          359.716  |

 [0, 1, 5, 4]
|       | Vertices   |   Actual Angle |   Estimated Angle |
|:------|:-----------|---------------:|------------------:|
| 0     | [0, 1, 5]  |             90 |           89.7126 |
| 1     | [1, 5, 4]  |             90 |           91.3177 |
| 2     | [5, 4, 0]  |             90 |           90.7987 |
| 3     | [4, 0, 1]  |             90 |           88.1462 |
| Total | nan        |            360 |          359.975  |

 [1, 2, 6, 5]
|       | Vertices   |   Actual Angle |   Estimated Angle |
|:------|:-----------|---------------:|------------------:|
| 0     | [1, 2, 6]  |             90 |           91.2656 |
| 1     | [2, 6, 5]  |             90 |           88.9755 |
| 2     | [6, 5, 1]  |             90 |           90.7192 |
| 3     | [5, 1, 2]  |             90 |           89.0361 |
| Total | nan        |            360 |          359.996  |

 EDGE LENGTHS
|    | Verts in Edge   |   Actual Distance |   Estimated Distance |
|---:|:----------------|------------------:|---------------------:|
|  0 | (0, 1)          |           1.32625 |             1.40897  |
|  1 | (0, 4)          |           1       |             0.991127 |
|  2 | (1, 2)          |           1.32625 |             1.33911  |
|  3 | (1, 5)          |           1       |             0.965643 |
|  4 | (2, 6)          |           1       |             0.960044 |
|  5 | (3, 4)          |           1.32624 |             1.25267  |
|  6 | (3, 6)          |           1.64597 |             1.56962  |
|  7 | (4, 5)          |           1.32625 |             1.3725   |
|  8 | (5, 6)          |           1.32625 |             1.34411  |

## Numerical Summary of "Bad" Reconstruction

 ANGLES
|    | Vertices   |   Actual Angle |   Estimated Angle |
|---:|:-----------|---------------:|------------------:|
|  1 | [1, 0, 3]  |        83.0769 |           77.2399 |
|  2 | [1, 0, 4]  |        90      |           91.8834 |
|  3 | [3, 0, 4]  |        90      |           95.6095 |
|  4 | [0, 1, 2]  |       110.769  |           91.1015 |
|  5 | [0, 1, 5]  |        90      |           86.6993 |
|  6 | [2, 1, 5]  |        90      |           83.2484 |
|  7 | [1, 2, 3]  |        96.9231 |          104.665  |
|  8 | [1, 2, 6]  |        90      |           95.3371 |
|  9 | [3, 2, 6]  |        90      |          100.014  |
| 10 | [2, 3, 0]  |        69.2307 |           84.5634 |
| 11 | [5, 4, 0]  |        90      |           88.5687 |
| 12 | [4, 5, 6]  |       110.769  |           93.7145 |
| 13 | [4, 5, 1]  |        90      |           92.8329 |
| 14 | [6, 5, 1]  |        90      |           95.9965 |
| 15 | [5, 6, 2]  |        90      |           85.3602 |

 SDA + PLANARITY
|                          |   Estimated |   Actual |
|:-------------------------|------------:|---------:|
| SDA                      |     7.02745 |  9.86039 |
| Deviation from Planarity |     2.35614 |  0       |
| Total Loss               |    42.1053  |  9.86039 |

 XYZ
|    |         X |         Y |   Actual Z |   Estimated Z |
|---:|----------:|----------:|-----------:|--------------:|
|  0 |  0.841719 |  0.586704 |   -11.2283 |     0.166276  |
|  1 |  0.268573 | -0.205915 |   -10.3327 |    -0.915897  |
|  2 | -0.527554 | -0.554268 |   -10.6624 |    -0.267202  |
|  3 | -0.473085 |  0.183514 |   -12.1327 |     0.716905  |
|  4 |  1.33915  | -0.195908 |   -11.6026 |     0.520003  |
|  5 |  0.766008 | -0.988528 |   -10.7069 |    -0.528132  |
|  6 | -0.030119 | -1.33688  |   -11.0366 |     0.0768143 |

 [0, 3, 2, 1]
|       | Vertices   |   Actual Angle |   Estimated Angle |
|:------|:-----------|---------------:|------------------:|
| 0     | [0, 3, 2]  |        69.2307 |           84.5634 |
| 1     | [3, 2, 1]  |        96.9231 |          104.665  |
| 2     | [2, 1, 0]  |       110.769  |           91.1015 |
| 3     | [1, 0, 3]  |        83.0769 |           77.2399 |
| Total | nan        |       360      |          357.57   |

 [1, 2, 6, 5]
|       | Vertices   |   Actual Angle |   Estimated Angle |
|:------|:-----------|---------------:|------------------:|
| 0     | [1, 2, 6]  |             90 |           95.3371 |
| 1     | [2, 6, 5]  |             90 |           85.3602 |
| 2     | [6, 5, 1]  |             90 |           95.9965 |
| 3     | [5, 1, 2]  |             90 |           83.2484 |
| Total | nan        |            360 |          359.942  |

 [0, 1, 5, 4]
|       | Vertices   |   Actual Angle |   Estimated Angle |
|:------|:-----------|---------------:|------------------:|
| 0     | [0, 1, 5]  |             90 |           86.6993 |
| 1     | [1, 5, 4]  |             90 |           92.8329 |
| 2     | [5, 4, 0]  |             90 |           88.5687 |
| 3     | [4, 0, 1]  |             90 |           91.8834 |
| Total | nan        |            360 |          359.984  |

 EDGE LENGTHS
|    | Verts in Edge   |   Actual Distance |   Estimated Distance |
|---:|:----------------|------------------:|---------------------:|
|  0 | (0, 1)          |          1.32625  |             1.45871  |
|  1 | (0, 3)          |          1.64597  |             1.48137  |
|  2 | (0, 4)          |          1        |             0.992495 |
|  3 | (1, 2)          |          0.929446 |             1.08442  |
|  4 | (1, 5)          |          1        |             1.00513  |
|  5 | (2, 3)          |          1.64597  |             1.23116  |
|  6 | (2, 6)          |          1        |             0.989076 |
|  7 | (4, 5)          |          1.32625  |             1.43364  |
|  8 | (5, 6)          |          0.929447 |             1.05883  |
