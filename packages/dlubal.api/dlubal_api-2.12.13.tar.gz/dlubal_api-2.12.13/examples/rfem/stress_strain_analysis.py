from dlubal.api import rfem

with rfem.Application() as rfem_app:

    # Activate stress-strain analysis add-on
    base_data_update = rfem_app.get_base_data()
    base_data_update.addons.stress_strain_analysis_active = True
    rfem_app.set_base_data(base_data=base_data_update)

    # Create line welded joint
    rfem_app.create_object(
        rfem.types_for_lines.LineWeldedJoint(
            no=1,
            weld_type=rfem.types_for_lines.LineWeldedJoint.WeldType.WELD_TYPE_SINGLE_FILLET,
            joint_type=rfem.types_for_lines.LineWeldedJoint.JointType.JOINT_TYPE_TEE_JOINT,
            longitudinal_arrangement=rfem.types_for_lines.LineWeldedJoint.LONGITUDINAL_ARRANGEMENT_CONTINUOUS,
            weld_size_a1=0.004, #[m],
        )
    )

    # Assign line welded joint to line and surfaces
    rfem_app.update_object_list(
        objs = [
            rfem.structure_core.Line(
                no=89,
                line_weld_assignment=rfem.structure_core.Line.LineWeldAssignmentTable(
                    rows=[
                        rfem.structure_core.Line.LineWeldAssignmentRow(
                            no=1,
                            weld=1,
                            surface1=16,
                            surface2=1,
                            surface3=2
                        )
                    ]
                )
            ),
        ]
    )

    # Assign objects to stress-strain analysis
    rfem_app.update_object_list(
        objs = [
            rfem.stress_analysis_objects.LineWeldedJointConfiguration(
                no=1,
                assigned_to_line_welded_joints=[1],
            ),
            rfem.stress_analysis_objects.SurfaceConfiguration(
                no=1,
                assigned_to_surfaces=[1,2,16],
            ),
        ]
    )

    # Calculate the analysis
    rfem_app.calculate_all(skip_warnings=True)


    # Retrieves results of line weld stresses
    line_weld_stresses = rfem_app.get_results(
        results_type=rfem.results.STRESS_STRAIN_ANALYSIS_LINE_WELDS_STRESSES
    ).data
    print(f"\nLine Weld Stresses:\n{line_weld_stresses}")
    line_weld_stresses.to_csv('line_weld_stresses.csv', index=False)

    # Retrieves results of surface stresses
    surface_stresses = rfem_app.get_results(
        results_type=rfem.results.STRESS_STRAIN_ANALYSIS_SURFACES_STRESSES
    ).data
    print(f"\nSurface Stresses:\n{surface_stresses}")
    surface_stresses.to_csv('surface_stresses.csv', index=False)


    # Get maximum design ratio of surface stresses
    surface_stresses_max = surface_stresses.loc[surface_stresses['design_ratio'].idxmax()]
    print(f"\nSurface Stresses | Maximum:\n{surface_stresses_max}")


    # Get details for maximum design ratio of surface stresses
    surface_stresses_details_id = surface_stresses_max['design_check_details_id']
    surface_stresses_max_details = rfem_app.get_results(
        results_type=rfem.results.STRESS_STRAIN_ANALYSIS_DESIGN_CHECK_DETAILS,
        filters=[rfem.results.ResultsFilter(
            column_id="design_check_details_id",
            filter_expression=str(surface_stresses_details_id))],
    ).data
    print(f"\nSurface Stresses | Maximum - Details:\n{surface_stresses_max_details}")
    # surface_stresses_max_details.to_csv('surface_stresses_max_details.csv', index=False)
    surface_stresses_max_details.to_excel('surface_stresses_max_details.xlsx', index=False, engine='openpyxl')






