This code is designed to compute various dimension characteristics of bat shelters. Below is a short step by step description of how it works.

1. The code accept raster images with 2D maps of bat shelters as an input. The images must be placed in a specific directory; the user will be asked to indicate the full address to the directory (Windows OS is assumed to be used here) and the format of the images (.jpg or .png). The directory may contain other files, however, the program will try to analyze all the files of the indicated format.

2. The program reads image files in RGB format, that is, it creates a two dimensional array with RGB coordinate vectors and entries and works with this array. The image files must be prepared in advance. They must contain:
  - the map of the shelter; each pixel of the map must have color different from white (that is, RGB coordinate vector must be different from [255,255,255]).
  - the entrances marked by a specific color; this color should not occur anywhere else on the image.
  - the scale line: a horizontal line outside of the map indicating the 1 meter distance. The pixels of the line must be of a specific color that does not occur anywhere else.

3. After the working directory address and the format of the files were received, the program starts analyzing all the files in the working directory one by one. Each time it finds a file it tries to find a .pkl file inside the directory "WorkingDirectory\\Pickles\\" with the same name as the image file. The .pkl file is supposed to store the results of the computations applied to this image file previously; if the program finds the .pkl file, it will suggest to use it; after the computations are done, the program will create a .pkl file or rewrite the existing one. If the .pkl file is found, but the data in this file is incomplete, the program will make the necessary computations.

4. From now on let's assume that .pkl file was not found, the program then proceeds with calculations. It will ask for the following additional input:
  - color error: this is the error which is accepted when comparing the colors. Say, color error is equal to 2, then (using the RGB format) [0,0,0] and [1,0,1] and [2,0,0] are assumed to be the same colors, while [0,0,0] and [1,1,1] are different.
  - the color with which the entrances are marked.
  - the color used to draw the scale line.

5. The program will find the entrances and the scale line. In both cases it checks all the pixels one by one; once a pixel of the correct color is found, it discovers all the pixels that are connected with this one by a lattice path of this color (it is allowed to go along the diagonals) and treats this collection of pixels as an entrance marking/the scale line. In the case of an entrance the program puts an entrance in the center of mass of these pixels and proceed, in the case of a scale the program computes the horizontal width of the scale line and use the inverse of it as the scaling coefficient for getting the real distances out of the distances between pixels.

6. Next the program will determine which pixels are inside the map of the shelter. To this end, it will take the position of the first entrance and discover all the pixels that can be reached from this position via a lattice path with no white pixels.

7. Next, the program will find the boundary, that is, the pixels inside the map that have white pixels neighboring them. Note that the boundary can be disconnected (e.g. if there is a pillar in the middle of the shelter). The program will find all the connected components of it.

8. Next, the program will compute the area; this is just the number of pixels inside the map rescaled by the scaling coefficient squared.

9. Next, the program will compute various lengths, including the perimeter. First, let us briefly describe the general approach here. The program has a function getdist(data, seed, bdry, isinside), where
  - data is the array with pixel colors;
  - seed is a point inside the map;
  - bdry is the bool array indicating whether the pixel is on the boundary;
  - isinside is the bool array indicating whether the pixel is inside the map.
This function precomputes the distances from the seed to all the other points inside the map and returns two arrays [dist, traj] where
  - dist is a numeric array with the precomputed distances;
  - traj is an array containing the shortest trajectory to each point from the seed.

10. The perimeter. To compute the perimeter the program uses the auxiliary function bdry_comp_length(data, bdry_comp). This function picks the boundary component, makes a small cut at a given point and then uses the getdist function to precompute distances from this point to all the points inside this component with a cut. The largest distance is then (almost) the perimeter (one adds the diameter of the cut to be more precise).

11. The distances from the entrances. The program now will precompute the distances from each entrance to all the pixels inside the map using the getdist function. This usually consumes quit a bit of time. The program then goes through the pixels one by one find the one which is the farthest from the entrances, as well as the number of the nearest entrance.

12. After the computations were done the program will start creating an edited file with the map. First, it will draw the trajectory from the farthest point to the entrances, then it will highlight the boundary (mostly for testing purposes). Finally, the program will label the entrances with numbers (the label of the nearest entrance will be indicated in the output table then). The edited map is saved in the file edited_MapFileName.jpg. The program will also save the .pkl file (replacing the existing one if there was any).

13. The program will run through all the files of the indicated format inside the indicated directory. After the program finishes it outputs an .xlsx file with the results of the computations: for each map the file contains the area, the perimeter and the distance to the farthest point.





