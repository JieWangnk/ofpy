#prepare your STL files and edit this script to match their names and directories and move to ./constant/triSurgace
python3 mergestl.py

# create a background mesh from the prepared model
python3 blockMesh.py constant/triSurface/aorta_merged.stl 1 1.002

# edges and other features; system/surfaceFeatureExtractDict must be defined
#surfaceFeatures

# background mesh
# meshing in parallel: system/decomposeParDict must be defined;
#decomposePar -force
#mpirun -np 4 snappyHexMesh -parallel
#reconstructParMesh -latestTime

foamCleanPolyMesh && blockMesh && snappyHexMesh -overwrite

# check and see
checkMesh
#paraFoam

#pyFoamRunner.py icoFoam
icoFoam


