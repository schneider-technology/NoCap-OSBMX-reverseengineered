# %%
from build123d import *
from ocp_vscode import show, set_port, set_defaults

set_port(3939)
set_defaults(grid=(True, True, True), axes=True, axes0=True)

# %%

d_cap = 19.50  # Outer diameter of keycap.
h_cap = 9  # Overall height of keycap.
t_cap_top = 3.50  # Thickness of top of keycap.
t_cap_walls = 1.25  # Thickness of keycap walls
r_cap_top_fillet = 2  # Fillet radius for top edge of keycap.

slop_w_shaft = 0  # Increase if stem doesn't fit into switch housing due to width.
slop_l_shaft = 0  # Increase if stem doesn't fit into switch housing due to length.

slop_t_stem = 0  # Increase if stem slot is too thin (i.e. the - of the + is too thin).
slop_l_stem = 0  # Increase if stem slot has insufficient length (i.e. the - of the + is too short).
slop_h_stem = 0.2  # Increase if stem doesn't go all the way into the stem shaft.

h_stem_slot_chamfer = 0.75 # Height of stem slot chamfer.
l_stem_slot_chamfer = 0.35 # Length of stem slot chamfer.
stem_base_height = 0.8  # Height of stem base.
stem_radius = 1.0  # Radius of stem base fillet.

'''Don't change anything after here unless you need to.'''

t_stem = 1.17 + slop_t_stem  # Thickness of stem based on Cherry MX specifications (+-0.02).
l_stem = 4.1 + slop_l_stem  # End-to-end width/length of the slot for the stem based on Cherry MX specifications (+-0.05).
h_stem = 3.6 + slop_h_stem  # Height of stem slot.

w_shaft = 4.3 - slop_w_shaft  # Outer width of stem shaft.
l_shaft = 6.1 - slop_l_shaft  # Outer length of stem shaft.
h_shaft = 4.6  # Height of stem shaft.

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
    print("Edges after hollowing out the keycap:")
    for i, edge in enumerate(cap.edges()):
        print(f"Edge {i}: {edge}")
        print(f"  Length: {edge.length}")
        print(f"  Position: {edge.position}")

    # Fillet the inside circle of the keycap by 2mm.
    inside_circle_edge = cap.edges().filter_by_position(Axis.Z, t_cap_top, t_cap_top)[0]  # Filter by Z position
    print(f"Selected edge for filleting: {inside_circle_edge}")
    fillet(inside_circle_edge, radius=2)

    # Create sketch of the stem on the inside of the keycap's top.
    cap_top_inside = cap.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-2]
    with BuildSketch(cap_top_inside) as stem_sk:
        stem_shaft = Rectangle(width=l_shaft, height=w_shaft)
        fillet(stem_shaft.vertices(), radius=stem_radius)
        Rectangle(width=t_stem, height=w_shaft, mode=Mode.SUBTRACT)
        Rectangle(width=l_stem, height=t_stem, mode=Mode.SUBTRACT)
    stem = extrude(amount=h_shaft)

    # Select and chamfer the top inner edges of the stem slot.
    stem_top_inner_edges = (
        stem.edges()
        .group_by(Axis.Z)[-1]
        .filter_by_position(Axis.X, -l_stem / 1.85, l_stem / 1.85)
        .filter_by_position(Axis.Y, -w_shaft / 2.0, w_shaft / 2.05, (False, False))
    )
    chamfer(stem_top_inner_edges, h_stem_slot_chamfer, l_stem_slot_chamfer)

    # Build a base for the stem to sit on.
    with BuildSketch(cap_top_inside) as stem_base_sk:
        stem_base_shaft = Rectangle(width=l_shaft, height=w_shaft)
        fillet(stem_base_shaft.vertices(), radius=stem_radius)
    extrude(amount=stem_base_height)

    # Cut notches in switch corner positions to prevent the walls colliding
    # with the switch.
    with BuildSketch(cap.faces().sort_by(Axis.Z)[-1]) as corner_gaps_sk:
        Rectangle(w_corner_gaps, d_cap, 45)
        mirror()
    extrude(amount=-h_corner_gaps, mode=Mode.SUBTRACT)

# Hollow out the inside circle of the stem base.
    stem_base = cap.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-3]
    with BuildSketch(stem_base) as stem_base_hollow_sk:
        Circle(d_cap / 2 - t_cap_walls)
    extrude(amount=-(stem_base_height - t_cap_top), mode=Mode.SUBTRACT)

# Fillet from the inside circle of the stem base by 2mm.
    inside_circle_edge = cap.edges().filter_by_position(Axis.Z, t_cap_top, t_cap_top)[0]  # Filter by Z position
    print(f"Selected edge for filleting: {inside_circle_edge}")
    fillet(inside_circle_edge, radius=0.799)

    # Debugging: Print out all edges and their properties
    print("Edges after hollowing out the stem base:")
    for i, edge in enumerate(cap.edges()):
        print(f"Edge {i}: {edge}")
        print(f"  Length: {edge.length}")
        print(f"  Position: {edge.position}")

    # Show the final result

show(
    cap,
    # stem_top_inner_edges,
    colors=["magenta"],
    # transparent=True,
)

export_step(cap.part, "NoCap.step")
export_stl(cap.part, "NoCap.stl")

# %%
