from dlubal.api import rfem, common


# -------------------------------------------------------
# This example demonstrates how to modify a design configuration
# in the model by using helper functions to interact with the
# tree table data structure, either by key or by path.
# -------------------------------------------------------

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # --- Get/Set value by key ---

    # Retrieve a design configuration
    steel_uls_config: rfem.steel_design_objects.SteelDesignUlsConfiguration = rfem_app.get_object(
        obj=rfem.steel_design_objects.SteelDesignUlsConfiguration(no=1)
    )

    # Get specific tree table from the configuration
    settings_ec3_uls_tree = steel_uls_config.settings_ec3
    print(f"\nSTEEL_SETTINGS_EC3_ULS_TREE:\n{settings_ec3_uls_tree}")

    # Get value/s for the key (there can be multiple occurrences)
    elastic_design_key = 'options_elastic_design'
    elastic_design_val = common.tree_table.get_values_by_key(
        tree=settings_ec3_uls_tree,
        key=elastic_design_key
    )
    print(f"\nElastic Design (key-based search): {elastic_design_val}")

    # Modify the value from the tree by the key
    common.tree_table.set_values_by_key(
        tree=settings_ec3_uls_tree,
        key=elastic_design_key,
        values=[True]
    )

    # Apply the updated configuration to the model
    rfem_app.update_object(
        obj=rfem.steel_design_objects.SteelDesignUlsConfiguration(
            no=1,
            settings_ec3=settings_ec3_uls_tree
        )
    )


    # --- Get/Set value by path ---

    # Retrieve a design configuration
    steel_sls_config: rfem.steel_design_objects.SteelDesignSlsConfiguration = rfem_app.get_object(
        obj=rfem.steel_design_objects.SteelDesignSlsConfiguration(no=1)
    )

    # Get specific tree table from the configuration
    settings_ec3_sls_tree = steel_sls_config.settings_ec3
    print(f"\nSTEEL_SETTINGS_EC3_SLS_TREE:\n{settings_ec3_sls_tree}")

    # Get specific value from the tree by its path
    beam_rel_deflection_limit_path=[
        "serviceability_limits",
        "sl_check_limit_characteristic",
        "sl_check_deformation_z_or_resulting_axis_characteristic",
        "l_", # Beam | Relative limit
    ]
    beam_rel_deflection_limit_val = common.get_value_by_path(
        tree=settings_ec3_sls_tree,
        path=beam_rel_deflection_limit_path
    )
    print(f"\nBeam | Relative deflection limit: L/{beam_rel_deflection_limit_val}")

    # Modify the value by path
    common.tree_table.set_value_by_path(
        tree=settings_ec3_sls_tree,
        path=beam_rel_deflection_limit_path,
        value=250
    )

    # Apply the updated configuration to the model
    rfem_app.update_object(
        obj=rfem.steel_design_objects.SteelDesignSlsConfiguration(
            no=1,
            settings_ec3=settings_ec3_sls_tree
        )
    )
