from dlubal.api import rfem, common

# -------------------------------------------------------
# This example demonstrates how to modify a design global
# settings in the model by using helper functions to interact
# with the tree table data structure.
# -------------------------------------------------------

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # Retrieve a design global settings
    design_settings_tree: rfem.GlobalSettingsTreeTable = rfem_app.get_design_settings(
        addon=rfem.DesignAddons.STEEL_DESIGN
    )
    print(f"DESIGN SETTINGS_TREE:\n{design_settings_tree}")

    # Get value/s for the key (there can be multiple occurrences)
    member_slenderness_key = 'member_slendernesses_compression_ec3'
    member_slendernesses_val = common.get_values_by_key(
        tree=design_settings_tree,
        key=member_slenderness_key
    )
    print(f"\nMember slendernesses: {member_slendernesses_val}")

    # Modify the value from the tree by the key
    common.set_values_by_key(
        tree=design_settings_tree,
        key=member_slenderness_key,
        values=[150],
    )
    # Apply the updated design settings to the model
    rfem_app.set_design_settings(
        addon=rfem.DesignAddons.STEEL_DESIGN,
        global_settings_tree_table=design_settings_tree
    )

