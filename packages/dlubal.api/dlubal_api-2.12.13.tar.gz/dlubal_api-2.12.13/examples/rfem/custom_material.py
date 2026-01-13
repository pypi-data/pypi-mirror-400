from dlubal.api import rfem
from dlubal.api import common
import pprint

# -------------------------------------------------------
# This example shows how to create and modify a custom material
# in the model by using helper functions to interact with the
# tree table data structure in efficient way.
# -------------------------------------------------------


# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # Initialize model
    rfem_app.create_model(name="custom_material")

    base_data = rfem_app.get_base_data()
    base_data.addons.concrete_design_active = True
    rfem_app.set_base_data(base_data=base_data)

    rfem_app.delete_all_objects()


    # Create a new material
    rfem_app.create_object(rfem.structure_core.Material(
        no=1, name="C30/37"
    ))

    # Retrieve the material
    material:rfem.structure_core.Material = rfem_app.get_object(
        rfem.structure_core.Material(no=1)
    )

    # Update material values tree table for default temperatue (row=0)
    material_values_tree = material.material_values.rows[0].material_values_tree

    common.tree_table.set_values_by_key(
        tree=material_values_tree,
        key='rho',                              # Mass density
        values=[2400.0]
    )
    common.tree_table.set_values_by_key(
        tree=material_values_tree,
        key='gamma',                            # Specific weight
        values=[24000.0]
    )

    # Update material standard parameters tree table
    standard_params_tree = material.standard_parameters
    common.tree_table.set_values_by_key(
        tree=standard_params_tree,
        key='class',
        values=[5]                              # Structural class S5
    )

    c_min_dur = common.tree_table.get_values_by_key(
        tree=standard_params_tree,
        key='c_min_dur',
        return_paths=True
    )
    pprint.pprint(c_min_dur)

    common.tree_table.set_values_by_key(
        tree=standard_params_tree,
        key='c_min_dur',
        values=[0.075],
        path=[
            '4_durability_and_concrete_cover',
            '4_4_1_minimum_concrete_cover',
            'table_4_4n_values_of_minimum_cover_c_min_dur_requirements_with_regard_to_durability_for_reinforcement_steel',
            'values_of_minimum_cover_for_structural_class_s5'
        ],
        occurrence=4                            # Minimum cover for XC4
    )


    # Apply modified material back to the model
    rfem_app.update_object(
        obj=rfem.structure_core.Material(
            no=1,
            user_defined=True,
            material_values=material.material_values,
            standard_parameters=material.standard_parameters
        )
    )
