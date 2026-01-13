from dlubal.api import rfem, common

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # Retrieve Block from the model
    block = rfem_app.get_object(rfem.structure_advanced.Block(no=1))

    # Access Block Parameters tree table
    block_parameters_tree = block.parameters
    print(f"Block parameters table:\n{block_parameters_tree}\n")

    # Get specific value from the tree (by key/path)
    length_key = 'l'
    length_val = common.tree_table.get_values_by_key(
        tree=block_parameters_tree,
        key=length_key
    )
    print(f"Length:\n{length_val}\n")

    # Modify specific value from the tree (by key/path)
    common.tree_table.set_values_by_key(
        tree=block_parameters_tree,
        key=length_key,
        values=[4.5]
    )

    # Apply changes of the block back to the model
    rfem_app.update_object(
        obj=rfem.structure_advanced.Block(
            no=1,
            parameters=block_parameters_tree
        )
    )
