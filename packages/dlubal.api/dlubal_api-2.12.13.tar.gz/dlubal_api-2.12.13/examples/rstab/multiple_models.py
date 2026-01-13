from dlubal.api import rstab, common

# -------------------------------------------------------
# This example demonstrates how to interact with multiple RSTAB models
# using the RSTAB API. The script includes creating, updating,
# and querying model object/s in two separate models in one script.
# -------------------------------------------------------

# Function to create, update, and query model object/s
def create_update_and_query_objects(rstab_app, model_id=None):

    # Create a list of objects
    rstab_app.create_object_list(
        objs=[
            rstab.structure_core.Node(no=1, coordinate_1=0.0),
            rstab.structure_core.Node(no=2, coordinate_1=2.0),
            rstab.structure_core.Node(no=3, coordinate_1=3.0),
            rstab.structure_core.Material(no=1, name='S235'),
            rstab.structure_core.CrossSection(no=1, name='IPE 200', material=1)
        ],
        model_id=model_id
    )

    # Create a single object
    rstab_app.create_object(
        obj=rstab.structure_core.Member(no=1, cross_section_start=1, node_start=1, node_end=3),
        model_id=model_id
    )

    # Update a list of objects
    rstab_app.update_object_list(
        objs=[
            rstab.structure_core.Node(no=1, coordinate_2=1.0),
            rstab.structure_core.Node(no=2, coordinate_2=1.0),
            rstab.structure_core.Node(no=3, coordinate_2=1.0),
        ],
        model_id=model_id
    )

    # Update a single object
    rstab_app.update_object(
        obj=rstab.structure_core.Node(
            no=2,
            type=rstab.structure_core.Node.TYPE_ON_MEMBER,
            on_member_reference_member=1,
            distance_from_start_absolute=2.0
        ),
        model_id=model_id
    )

    # Retrieve a list of objects
    node_list = rstab_app.get_object_list(
        objs=[rstab.structure_core.Node()],
        model_id=model_id
    )
    for node in node_list:
        print(f"{node.DESCRIPTOR.name}: {node.no} [X={node.coordinate_1}, Y={node.coordinate_2}] | Type: {node.type}")

    # Retrieve a single objects
    member = rstab_app.get_object(
        obj=rstab.structure_core.Member(no=1)
    )
    print(f"{member.DESCRIPTOR.name}: {member.no},  Length: {member.length} [m]")


# --- MAIN SCRIPT ---

# Connect to the RSTAB application
with rstab.Application() as rstab_app:

    rstab_app.close_all_models(save_changes=False)

    # Create two separate models and store their model IDs
    model_1: common.ModelId = rstab_app.create_model(name="model_1")
    model_2: common.ModelId = rstab_app.create_model(name="model_2")
    model_list = rstab_app.get_model_list()
    print(f"\nModel list:\n {model_list}")

    # Make operations on currently active model (default is model_2)
    active_model = rstab_app.get_active_model()
    print(f"\nCurrently active model_2:\n {active_model}")
    create_update_and_query_objects(rstab_app)  # Use default active model

    # Perform operations on model_1 by passing its model ID
    print(f"\nSwitching to model_1 (by ID):\n {model_1}")
    create_update_and_query_objects(rstab_app, model_id=model_1)

    # Set model_1 as the active model
    rstab_app.set_active_model(model_id=model_1)
    active_model = rstab_app.get_active_model()
    print(f"\nSetting model_1 as active:\n {active_model}")