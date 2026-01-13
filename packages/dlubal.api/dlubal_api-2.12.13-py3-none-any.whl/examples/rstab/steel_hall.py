
from dlubal.api import rstab, common
import math

# -------------------------------------------------------
# This example demonstrates how to modelling parametric
# steel hall with help of manipulation functions like move
# or rotate including the copy option. The idea is to reduce
# manual modeling by leveraging symmetry and transformations.
# -------------------------------------------------------

# Editable parameters (SI units)
FRAME_SPACING = 5.0
FRAME_COUNT = 5
FRAME_WIDTH = 11.0
FRAME_HEIGHT_MIN = 4.5
FRAME_HEIGHT_MAX = 6.0
RAFTER_SLOPE_LENGTH = 0.75
PURLIN_FIELDS = 4
PURLIN_OFFSET_ON_TOP = 0.25

STEEL_GRADE = "S235 | EN 10025-2:2004-11"
CROSS_SECTION_COLUMN = "IPE 300"
CROSS_SECTION_RAFTER = "I 0.3/0.11/0.006/0.014/0/0/H"
CROSS_SECTION_RAFTER_TAPPERED = "I 0.6/0.11/0.006/0.014/0/0/H"
CROSS_SECTION_PURLINS = "CHC 139.7x8.0"
CROSS_SECTION_BRACING = "R 20"


def build_half_portal_frame() -> list:

    inf = float('inf')

    portal_frame = [
        rstab.structure_core.Material(no=1, name=STEEL_GRADE),
        rstab.structure_core.CrossSection(no=1, name=CROSS_SECTION_COLUMN, material=1),
        rstab.structure_core.CrossSection(no=2, name=CROSS_SECTION_RAFTER, material=1),
        rstab.structure_core.CrossSection(no=3, name=CROSS_SECTION_RAFTER_TAPPERED, material=1),
    ]

    portal_frame.append(rstab.structure_core.Node(no=1))
    portal_frame.append(rstab.structure_core.Node(no=2, coordinate_3=-FRAME_HEIGHT_MIN))

    node_no = 3
    rafter_length = math.sqrt((FRAME_HEIGHT_MAX - FRAME_HEIGHT_MIN)**2 + (FRAME_WIDTH / 2)**2)
    purlin_offset = (rafter_length - PURLIN_OFFSET_ON_TOP) / PURLIN_FIELDS

    for j in range(1, PURLIN_FIELDS+1):
        portal_frame.append(
            rstab.structure_core.Node(
                no=node_no,
                type=rstab.structure_core.Node.TYPE_ON_MEMBER,
                on_member_reference_member=2,
                distance_from_start_is_defined_as_relative=False,
                distance_from_start_absolute=purlin_offset*j,
            )
        )
        node_no += 1

    portal_frame.append(rstab.structure_core.Node(no=node_no, coordinate_1=FRAME_WIDTH/2, coordinate_3=-FRAME_HEIGHT_MAX))

    # Members
    portal_frame.append(rstab.structure_core.Member(
        no=1, node_start=1,  node_end=2, cross_section_start=1,
        type=rstab.structure_core.Member.TYPE_BEAM))
    portal_frame.append(rstab.structure_core.Member(
        no=2, node_start=2, node_end=node_no, cross_section_start=3,
        type=rstab.structure_core.Member.TYPE_BEAM,
    ))

    # Nodal support (hinge)
    portal_frame.append(rstab.types_for_nodes.NodalSupport(
        no=1, nodes=[1],
        spring_x=inf, spring_y=inf, spring_z=inf,
        rotational_restraint_z=inf
    ))

    return portal_frame


def enhance_rafters_with_tapering() -> list:

    tapered_members = []

    for rafter_no in (2, 4):

        tapered_members.append(
            rstab.structure_core.Member(
                no=rafter_no,
                cross_section_end=2,
                cross_section_distribution_type=rstab.structure_core.Member.CROSS_SECTION_DISTRIBUTION_TYPE_TAPERED_AT_START_OF_MEMBER,
                cross_section_distance_from_start_is_defined_as_relative=False,
                section_distance_from_start_absolute=RAFTER_SLOPE_LENGTH
            )
        )

    return tapered_members


def build_purlins_in_first_bay_half() -> list:

    nodes_per_frame = 7 + 2* (PURLIN_FIELDS)

    purlins = [
        rstab.structure_core.CrossSection(no=4, name=CROSS_SECTION_PURLINS, material=1),
    ]

    for purlin in range(1, PURLIN_FIELDS+2):

        purlin_no = (4 * FRAME_COUNT) + purlin
        purlin_node_start = 2 + (purlin - 1)
        purlin_node_end = 2 + (purlin - 1) + nodes_per_frame

        purlins.append(rstab.structure_core.Member(
            no=purlin_no, cross_section_start=4,
            node_start= purlin_node_start, node_end= purlin_node_end,
            type=rstab.structure_core.Member.TYPE_TRUSS)
        )

    return purlins


def build_bracing_in_first_bay_half() -> list:

    nodes_per_frame = 7 + 2* (PURLIN_FIELDS)
    bracing_no = (4 * FRAME_COUNT) + 2*(PURLIN_FIELDS+1)*(FRAME_COUNT-1) + 1

    bracing = [
        rstab.structure_core.CrossSection(no=5, name=CROSS_SECTION_BRACING, material=1)
    ]

    for i in range(1, PURLIN_FIELDS + 2):
        for j in range(2):
            bracing.append(rstab.structure_core.Member(
                no=bracing_no + j, cross_section_start=5,
                node_start= i + j, node_end= nodes_per_frame + i - j + 1,
                type=rstab.structure_core.Member.TYPE_TRUSS_ONLY_N
            ))
        bracing_no += 2

    return bracing


def get_members_by_type(rstab_app, member_type) -> list:

    member_list = rstab_app.get_object_list(
        objs=[
            rstab.structure_core.Member()
        ]
    )

    member_list_filtered = []

    for member in member_list:
        if member.type is member_type:
            member_list_filtered.append(member)

    return member_list_filtered


# --- MAIN SCRIPT ---

# Connect to the RFEM application
with rstab.Application() as rstab_app:

    rstab_app.close_all_models(save_changes=False)
    model_id = rstab_app.create_model(name='steel_hall_parametric')
    rstab_app.delete_all_objects()

    # Build the half of the portal frame
    portal_frame = build_half_portal_frame()
    rstab_app.create_object_list(
        objs=portal_frame
    )

    # Rotate the half of the portal frame as copy to its mirrored position
    rstab_app.rotate_objects(
        objs=portal_frame,
        rotation_angle=math.pi,
        point_1=common.Vector3d(x=FRAME_WIDTH/2,y=0,z=-FRAME_HEIGHT_MAX),
        axis=rstab.manipulation.COORDINATE_AXIS_Z,
        rotation_axis=rstab.manipulation.ROTATION_AXIS_SPECIFICATION_TYPE_POINT_AND_PARALLEL_AXIS,
        create_copy=True,
        number_of_steps=1
    )

    # Enhance the rafters with tapering
    tapered_rafter = enhance_rafters_with_tapering()
    rstab_app.update_object_list(
        objs=tapered_rafter
    )

    # Move the frame to create multiple frames by applying a vector displacement
    rstab_app.move_objects(
        objs=rstab_app.get_object_list(
            objs=[
                rstab.structure_core.Node(),
                rstab.structure_core.Member(),
            ]
        ),
        create_copy=True,
        number_of_steps=FRAME_COUNT-1,
        direction_through=rstab.manipulation.DIRECTION_THROUGH_DISPLACEMENT_VECTOR,
        displacement_vector=common.Vector3d(x=0.0, y=FRAME_SPACING, z=0.0)
    )

    # Model purlins between the first two frames, on one symmetric half of the hall
    purlins = build_purlins_in_first_bay_half()
    rstab_app.create_object_list(objs=purlins)

    # Rotate purlins to symmetric half of the hall
    rstab_app.rotate_objects(
        objs=purlins,
        rotation_angle=math.pi - 2*math.atan((FRAME_HEIGHT_MAX - FRAME_HEIGHT_MIN) / (FRAME_WIDTH / 2)),
        point_1=common.Vector3d(x=FRAME_WIDTH/2,y=0,z=-FRAME_HEIGHT_MAX),
        axis=rstab.manipulation.COORDINATE_AXIS_Y,
        rotation_axis=rstab.manipulation.ROTATION_AXIS_SPECIFICATION_TYPE_POINT_AND_PARALLEL_AXIS,
        create_copy=True,
        number_of_steps=1
    )

    # Copy the purlins parallel to the axis for the remaining bays
    rstab_app.move_objects(
        objs=get_members_by_type(
            rstab_app, rstab.structure_core.Member.TYPE_TRUSS
        ),
        create_copy=True,
        number_of_steps=FRAME_COUNT-2,
        direction_through=rstab.manipulation.DIRECTION_THROUGH_PARALLEL_TO_AXIS,
        axis=rstab.manipulation.COORDINATE_AXIS_Y,
        spacing=FRAME_SPACING
    )

    # Model bracing between the first two frames, on one symmetric half of the hall
    bracing = build_bracing_in_first_bay_half()
    rstab_app.create_object_list(objs=bracing)

    # Mirror the bracing to symetric half of the hall
    rstab_app.rotate_objects(
        objs=get_members_by_type(
            rstab_app, rstab.structure_core.Member.TYPE_TRUSS_ONLY_N
        ),
        rotation_angle=math.pi,
        point_1=common.Vector3d(x=FRAME_WIDTH/2,y=FRAME_SPACING/2,z=-FRAME_HEIGHT_MAX),
        axis=rstab.manipulation.COORDINATE_AXIS_Z,
        rotation_axis=rstab.manipulation.ROTATION_AXIS_SPECIFICATION_TYPE_POINT_AND_PARALLEL_AXIS,
        create_copy=True,
        number_of_steps=1
    )
