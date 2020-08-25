import re   #regular expression operations
import math
import sys  #system-specific parameters and functions
import os   #miscellaneous operating system read/write files, manipulate paths

# command-line input
help_text = """Usage: makeBMD.py <file> <hex size [m]> [expand_factor] """

try:    #try block lets you test a block of code for errors
    if len(sys.argv) < 3:   #sys.argv the list of commend arguments passed to a Python script
        raise ValueError

    file_name = sys.argv[1]
    cell_size = float(sys.argv[2])  #18000

    if len(sys.argv) > 3:
        expand_factor = float(sys.argv[3])
    else:
        expand_factor = 1.001
except:     #expect block lets you handel the error
    print (sys.argv)
    print (help_text)
    sys.exit()      #exit from python, cleanup the actions action specified by finally clauses of try statements

# format of vertex files:       #stl-standard triangle language
#    vertex  7.758358e-03  2.144992e-02  1.539336e-02
#    vertex  7.761989e-03  2.167315e-02  1.525611e-02
#    vertex  7.767175e-03  2.167225e-02  1.551236e-02

# a regular expression to match a beginning of a vertex line in STL file
#re.compile(pattern,flags=0) compile a regular expression pattern into a regular expression object
#which can be used for matching using its match(),search()
vertex_re = re.compile('\s+vertex.+')   #for unicode(str)patterns

vertex_max = [-1e+12, -1e+12, -1e+12]
vertex_min = [ 1e+12,  1e+12,  1e+12]

# stroll through the file and find points with highest/lowest coordinates
with open(sys.argv[1], 'r') as f:   #open for reading
    for line in f:
        m = vertex_re.match(line)

        if m:
            n = line.split()    #split a string into a list
            v = [float(n[i]) for i in range(1, 4)]

            vertex_max = [max([vertex_max[i], v[i]]) for i in range(3)]
            vertex_min = [min([vertex_min[i], v[i]]) for i in range(3)]

# scale the blockmesh by a small factor
# achtung, scale around object center, not coordinate origin!
for i in range(3):
    center = (vertex_max[i] + vertex_min[i])/2
    size = vertex_max[i] - vertex_min[i]

    vertex_max[i] = center + size/2*expand_factor
    vertex_min[i] = center - size/2*expand_factor

# find out number of elements that will produce desired cell size
sizes = [vertex_max[i] - vertex_min[i] for i in range(3)]
num_elements = [int(math.ceil(sizes[i]/cell_size)) for i in range(3)]


print ("max: {}".format(vertex_max))
print ("min: {}".format(vertex_min))
print ("sizes: {}".format(sizes))
print ("number of elements: {}".format(num_elements))
print ("expand factor: {}".format(expand_factor))

# write a blockMeshDict file
bm_file = """
/*--------------------------------*- C++ -*----------------------------------*\
    =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  6
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

x_min {v_min[0]};
x_max {v_max[0]};

y_min {v_min[1]};
y_max {v_max[1]};

z_min {v_min[2]};
z_max {v_max[2]};

n_x {n[0]};
n_y {n[1]};
n_z {n[2]};

vertices
(
    ($x_min $y_min $z_min) //0
    ($x_max $y_min $z_min) //1
    ($x_max $y_max $z_min) //2
    ($x_min $y_max $z_min) //3
    ($x_min $y_min $z_max) //4
    ($x_max $y_min $z_max) //5
    ($x_max $y_max $z_max) //6
    ($x_min $y_max $z_max) //7
);


blocks ( hex (0 1 2 3 4 5 6 7) ($n_x $n_y $n_z) simpleGrading (1 1 1) );

edges ( );
//patches ( );
//mergePatchPairs ( );
boundary
(
    allBoundary
    {{
        type patch;
        faces
        (
            (3 7 6 2)
            (0 4 7 3)
            (2 6 5 1)
            (1 5 4 0)
            (0 3 2 1)
            (4 5 6 7)
        );
    }}
);

// ************************************************************************* //
"""
#os.path.join()return the concatenation of path and any number of *path with exactly one directory separator 
with open(os.path.join('system', 'blockMeshDict'), 'w') as mesh_file:
    mesh_file.write(
        bm_file.format(v_min=vertex_min, v_max=vertex_max, n=num_elements)
    )

print ("done.")