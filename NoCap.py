# %%
from build123d import *
from ocp_vscode import show, set_port, set_defaults

set_port(3939)
set_defaults(grid=(True, True, True), axes=True, axes0=True)

# %%

d_cap = 19.50  # Outer diameter of keycap.
h_cap = 4.5  # Overall height of keycap.
t_cap_top = 2.0  # Thickness of top of keycap.
t_cap_walls = 1.25  # Thickness of keycap walls
r_cap_top_fillet = 2  # Fillet radius for top edge of keycap.

slop_w_shaft = 0  # Increase if stem doesn't fit into switch housing due to width.
slop_l_shaft = 0  # Increase if stem doesn't fit into switch housing due to length.

slop_t_stem = 0.1  # Increase if stem slot is too thin (i.e. the - of the + is too thin).
slop_l_stem = 0  # Increase if stem slot has insufficient length (i.e. the - of the + is too short).
slop_h_stem = 0.2  # Increase if stem doesn't go all the way into the stem shaft.

slop_stem_base_h = 1.5  # Increase if stem base is too short.

#h_stem_slot_chamfer = 0.75 # Height of stem slot chamfer.
#l_stem_slot_chamfer = 0.35 # Length of stem slot chamfer.


stem_base_height_fillet = 0.8  # Fillet radius for stem base.
stem_radius = 0.5  # Radius of stem base fillet.
inside_radius = 2  # Radius of inside keycap fillet.

'''Don't change anything after here unless you need to.'''

t_stem = 1.17 + slop_t_stem  # Thickness of stem based on Cherry MX specifications (+-0.02).
l_stem = 4.1 + slop_l_stem  # End-to-end width/length of the slot for the stem based on Cherry MX specifications (+-0.05).
h_stem = 3.6 + slop_h_stem  # Height of stem slot.

w_shaft = 4.3 - slop_w_shaft  # Outer width of stem shaft.
l_shaft = 6.1 - slop_l_shaft  # Outer length of stem shaft.
h_shaft = 4.6  # Height of stem shaft.

stem_base_height = 0.8 + slop_stem_base_h # Height of stem base.

w_corner_gaps = 5  # Width of the gaps that give clearance to the corners of the switch when pressed.
h_corner_gaps = h_cap - (h_shaft + t_cap_top)  # Height of the switch corner gaps.

with BuildPart() as cap:
    # Create the main body of the keycap.
    with BuildSketch() as cap_sk:
        Circle(d_cap / 2)
    extrude(amount=h_cap)
    fillet(cap.edges().sort_by(Axis.Z)[0], radius=r_cap_top_fillet)

    # Hollow out the body of the keycap.
    with BuildSketch(cap.faces().sort_by(Axis.Z)[-1]) as cap_hollow_sk:
        Circle(d_cap / 2 - t_cap_walls)
    extrude(amount=-(h_cap - t_cap_top), mode=Mode.SUBTRACT)

    # Debugging: Print out all edges and their properties
#     print("Edges after hollowing out the keycap:")
#     for i, edge in enumerate(cap.edges()):
#             print(f"Edge {i}: {edge}")
#             print(f"geometry type: {edge.geom_type}")
#             print(f"  Length: {edge.length}")
#             print(f"  Position: {edge.position}")

    fakestembase = stem_base_height/2
    print(f"fakestembase: {fakestembase}")

    #Create a quadratic prebase for the stems to sit on.
    #prebase = cap.faces().filter_by(Axis.Z)[-1]
    #with BuildSketch(prebase) as prebase_sk:
    #    Rectangle(width=w_shaft*2, height=w_shaft*2, align=(Align.CENTER, Align.CENTER))
    #extrude(amount=fakestembase)
    
    curve_slot_height = 2
    total_slot_height = stem_base_height + curve_slot_height

    #Create first part of the stem slot on the positive X axis
    cap_top_inside = cap.faces().filter_by(Axis.Z)[-1]
    with BuildSketch(cap_top_inside) as stem_sk:
        Rectangle(width=w_shaft / 2, height=w_shaft, align=(Align.MIN, Align.CENTER))
        Rectangle(width=(t_stem-slop_t_stem)*2, height=w_shaft, mode=Mode.SUBTRACT, align=(Align.CENTER, Align.CENTER))
        Rectangle(width=w_shaft, height=t_stem, mode=Mode.SUBTRACT, align=(Align.MIN, Align.CENTER))
    extrude(amount=total_slot_height)  

    print("Edges")
    for i, edge in enumerate(cap.edges()):
            print(f"Edge {i}: {edge}")
            print(f"geometry type: {edge.geom_type}")
            print(f"  Length: {edge.length}")
            print(f"  Position: {edge.position}")

    # Fillet inside edges of the stem slot which have 1.565 length on Z 2.0 and X on 1.075
    stem_top_inner_edges = [edge for edge in cap.edges() if edge.position.Z == t_cap_top and abs(edge.length - 1.515) < 0.01 and edge.position.X < 1]
    
    # fillet max radius possible
    fillet(stem_top_inner_edges, radius=total_slot_height-0.01)

# This will be relevant for the new stem slot
                #Line((0, 0), (length, 0))
                #Line((length, 0), (length, width))
                #ThreePointArc((length / 2, width * 1.5), (length, width), (0, width))
                #Line((0, width), (0, 0))


    #Remove the prebase
    prebase = cap.faces().filter_by(Axis.Z)[0]
    with BuildSketch(prebase):
        Rectangle(width=w_shaft*2, height=w_shaft*2, align=(Align.CENTER, Align.CENTER))
    extrude(amount=fakestembase+1, mode=Mode.SUBTRACT)

    #Create second part of the stem slot on the negative X axis
    #cap_top_inside2 = cap.faces().filter_by(Axis.Z)[-2]
    #with BuildSketch(cap_top_inside2) as stem_sk:     
      #  Rectangle(width=w_shaft / 2, height=w_shaft, align=(Align.MAX, Align.CENTER))
      #  Rectangle(width=(t_stem-slop_t_stem)*2, height=w_shaft, mode=Mode.SUBTRACT, align=(Align.CENTER, Align.CENTER))
      #  Rectangle(width=w_shaft, height=t_stem, mode=Mode.SUBTRACT, align=(Align.MAX, Align.CENTER))
    #extrude(amount=total_slot_height)
    


# Calculate the circumference of the inside circle
    inside_circle_circumference = 2 * 3.141592653589793 * (d_cap / 2 - t_cap_walls)

   # Fillet the inside circle of the keycap by 2mm.
    inside_circle_edge = next(edge for edge in cap.edges() if edge.position.Z == t_cap_top and abs(edge.length - inside_circle_circumference) < 0.01)
    #print(f"Selected edge for filleting: {inside_circle_edge}")
    fillet(inside_circle_edge, radius=2)

    #Add stem_base
    stem_base = cap.faces().filter_by(Axis.Z)[0]
    with BuildSketch(stem_base) as stem_base_sk:
        Rectangle(width=w_shaft, height=w_shaft, align=(Align.CENTER, Align.CENTER))
    extrude(amount=stem_base_height)
    #define stem_badge_edges which are the edges where the length = w_shaft and Z = 2

    stem_base_edges = [edge for edge in cap.edges() if edge.length == w_shaft] and [edge for edge in cap.edges() if edge.position.Z == 2]
    #fillet
    fillet(stem_base_edges, radius=stem_base_height_fillet)

 #Build a base for the stem to sit on.

with BuildPart() as stem_base:
    with BuildSketch() as stem_base_sk:
        Rectangle(width=w_shaft, height=w_shaft, align=(Align.CENTER, Align.CENTER))
 #       fillet(stem_base_shaft.vertices(), radius=stem_radius)
    extrude(amount=t_cap_top+stem_base_height)
    

with BuildPart() as plus:
    # create plus sign
    with BuildSketch() as sk:
        Rectangle(width=l_stem, height=1.17, align=(Align.CENTER, Align.CENTER))
        Rectangle(width=1.17, height=l_stem, align=(Align.CENTER, Align.CENTER))
    extrude(amount=t_cap_top+stem_base_height+4)    
    
BaseZ = -15.5
arc_start_x = -3
arc_end_x = 0
arc_height_z = -17
#MiddleX = StartX-((StartX+EndX)/2)

#Add Rectangle to the top of the keycap height of t_cap_top and width of d_cap
with BuildPart() as cap_top:    
        Box(30, 15.5, 1 , align=(Align.MAX, Align.CENTER))
        plane = Plane(cap_top.faces().group_by(Axis.Y)[0][0])
        #with BuildSketch(plane) as sk:
        with BuildSketch(plane) as sk:
            with BuildLine(plane) as arc_ln:
                Line((arc_start_x, BaseZ), (arc_end_x, BaseZ))
                ThreePointArc((arc_end_x, BaseZ), ((arc_start_x + arc_end_x) / 2, arc_height_z), (arc_start_x, BaseZ))
            make_face()
        extrude(amount=-15.5)
        
        #extrude(amount=-19.5)


    # Combine parts into a single compound shape

combined_part = Compound([cap.part, cap_top.part])

    

    # Show the final result
show(
        cap, cap_top, #stem_base, #plus,
        # stem_top_inner_edges,
        colors=["magenta"],
        # transparent=True,
    )

export_step(combined_part, "NoCap.step")
export_stl(combined_part, "NoCap.stl")

# %%
