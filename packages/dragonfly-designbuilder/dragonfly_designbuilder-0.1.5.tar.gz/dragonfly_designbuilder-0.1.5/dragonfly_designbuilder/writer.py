# coding: utf-8
"""Write an inp file from a Dragonfly model."""
from __future__ import division
import os

from honeybee_designbuilder.writer import model_to_dsbxml as hb_model_to_dsbxml


def model_to_dsbxml(
    model, use_multiplier=True, exclude_plenums=False, solve_ceiling_adjacencies=True,
    merge_method='None', xml_template='Default', program_name=None
):
    """Generate an dsbXML string for a Model.

    The resulting string will include all geometry (Rooms, Faces, Apertures,
    Doors, Shades), all fully-detailed constructions + materials, all fully-detailed
    schedules, and the room properties. It will also include the simulation
    parameters. Essentially, the string includes everything needed to simulate
    the model.

    Args:
        model: A dragonfly Model for which an INP representation will be returned.
        use_multiplier: Boolean to note if the multipliers on each Building
            story will be passed along to the generated Honeybee Room objects
            or if full geometry objects should be written for each story in the
            building. (Default: True).
        exclude_plenums: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should generate distinct 3D Rooms in the
            translation. (Default: False).
        solve_ceiling_adjacencies: Boolean to indicate whether adjacencies should
            be solved between interior stories when Room2Ds perfectly match one
            another in their floor plate. This ensures that Surface boundary
            conditions are used instead of Adiabatic ones. (Default: True).
        merge_method: An optional text string to describe how the Room2Ds should
            be merged into individual Rooms during the translation. Specifying a
            value here can be an effective way to reduce the number of Room volumes
            in the resulting Model and, ultimately, yield a faster simulation time
            with less results to manage. Note that Room2Ds will only be merged if they
            form a contiguous volume across their solved adjacencies. Otherwise,
            there will be multiple Rooms per zone or story, each with an integer
            added at the end of their identifiers. Choose from the following options:

            * None - No merging of Room2Ds will occur
            * Zones - Room2Ds in the same zone will be merged
            * PlenumZones - Only plenums in the same zone will be merged
            * Stories - Rooms in the same story will be merged
            * PlenumStories - Only plenums in the same story will be merged

        xml_template: Text for the type of template file to be used to write the
            dsbXML. Different templates contain different amounts of default
            assembly library data, which may be needed in order to import the
            dsbXML into older versions of DesignBuilder. However, this data can
            greatly increase the size of the resulting dsbXML file. Choose from
            the following options.

            * Default - a minimal file that imports into the latest versions
            * Assembly - the Default plus an AssemblyLibrary with typical objects
            * Full - a large file with all libraries that can be imported to version 7.3

        program_name: Optional text to set the name of the software that will
            appear under a comment in the XML to identify where it is being exported
            from. This can be set things like "Ladybug Tools" or "Pollination"
            or some other software in which this dsbXML export capability is being
            run. If None, no comment will appear. (Default: None).

    Usage:

    .. code-block:: python

        import os
        from ladybug_geometry.geometry3d import Point3D, Face3D
        from dragonfly.model import Model
        from dragonfly.building import Building
        from dragonfly.story import Story
        from dragonfly.room2d import Room2D
        from dragonfly.roof import RoofSpecification
        from dragonfly.windowparameter import SimpleWindowRatio
        from honeybee.config import folders

        # Crate an input Model
        pts1 = (Point3D(0, 0, 0), Point3D(10, 0, 0),
                Point3D(10, 10, 0), Point3D(0, 10, 0))
        pts2 = (Point3D(10, 0, 0), Point3D(20, 0, 0),
                Point3D(20, 10, 0), Point3D(10, 10, 0))
        pts3 = (Point3D(0, 0, 3.25), Point3D(20, 0, 3.25),
                Point3D(20, 5, 5), Point3D(0, 5, 5))
        pts4 = (Point3D(0, 5, 5), Point3D(20, 5, 5),
                Point3D(20, 10, 3.25), Point3D(0, 10, 3.25))
        room2d_full = Room2D(
            'R1-full', floor_geometry=Face3D(pts1), floor_to_ceiling_height=4,
            is_ground_contact=True, is_top_exposed=True)
        room2d_plenum = Room2D(
            'R2-plenum', floor_geometry=Face3D(pts2), floor_to_ceiling_height=4,
            is_ground_contact=True, is_top_exposed=True)
        room2d_plenum.ceiling_plenum_depth = 1.0
        roof = RoofSpecification([Face3D(pts3), Face3D(pts4)])
        story = Story('S1', [room2d_full, room2d_plenum])
        story.roof = roof
        story.solve_room_2d_adjacency(0.01)
        story.set_outdoor_window_parameters(SimpleWindowRatio(0.4))
        building = Building('Office_Building_1234', [story])
        model = Model('NewDevelopment1', [building])

        # create the dsbXML string for the model
        xml_str = model.to.dsbxml(model)

        # write the final string into an dsbXML
        dsbxml = os.path.join(folders.default_simulation_folder, 'test_file', 'in.xml')
        with open(dsbxml, 'wb') as fp:
            fp.write(xml_str.encode('iso-8859-15'))
    """
    # convert the Dragonfly Model to Honeybee
    hb_model = model.to_honeybee(
        'District', use_multiplier=use_multiplier, exclude_plenums=exclude_plenums,
        solve_ceiling_adjacencies=solve_ceiling_adjacencies, merge_method=merge_method,
        enforce_adj=False, enforce_solid=True
    )[0]

    # assign the floor geometry to the Honeybee Rooms from Dragonfly
    df_flr_geos = {}  # dictionary to hold the DesignBuilder floor geometry
    for df_room in model.room_2ds:
        df_flr_geos[df_room.identifier] = df_room.floor_geometry
    for hb_room in hb_model.rooms:
        try:
            hb_room.properties.designbuilder.floor_geometry = \
                df_flr_geos[hb_room.identifier]
        except KeyError:  # possibly a 3D Room that has no Room2D geometry
            pass

    # patch missing adjacencies to adiabatic in case the models is a sub-selection
    hb_model.properties.energy.missing_adjacencies_to_adiabatic()

    # translate the Honeybee Model to dsbXML
    dsbxml_str = hb_model_to_dsbxml(
        hb_model, xml_template=xml_template, program_name=program_name)
    return dsbxml_str


def model_to_dsbxml_file(
    model, output_file, use_multiplier=True, exclude_plenums=False,
    solve_ceiling_adjacencies=True, merge_method='None', xml_template='Default',
    program_name=None
):
    """Write an dsbXML file from a Dragonfly Model.

    Note that this method also ensures that the resulting dsbXML file uses the
    ISO-8859-15 encoding that is used by DesignBuilder.

    Args:
        model: A dragonfly Model for which an dsbXML file will be written.
        output_file: The path to the XML file that will be written from the model.
        use_multiplier: Boolean to note if the multipliers on each Building
            story will be passed along to the generated Honeybee Room objects
            or if full geometry objects should be written for each story in the
            building. (Default: True).
        exclude_plenums: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should generate distinct 3D Rooms in the
            translation. (Default: False).
        solve_ceiling_adjacencies: Boolean to indicate whether adjacencies should
            be solved between interior stories when Room2Ds perfectly match one
            another in their floor plate. This ensures that Surface boundary
            conditions are used instead of Adiabatic ones. (Default: True).
        merge_method: An optional text string to describe how the Room2Ds should
            be merged into individual Rooms during the translation. Specifying a
            value here can be an effective way to reduce the number of Room volumes
            in the resulting Model and, ultimately, yield a faster simulation time
            with less results to manage. Note that Room2Ds will only be merged if they
            form a contiguous volume across their solved adjacencies. Otherwise,
            there will be multiple Rooms per zone or story, each with an integer
            added at the end of their identifiers. Choose from the following options:

            * None - No merging of Room2Ds will occur
            * Zones - Room2Ds in the same zone will be merged
            * PlenumZones - Only plenums in the same zone will be merged
            * Stories - Rooms in the same story will be merged
            * PlenumStories - Only plenums in the same story will be merged

        xml_template: Text for the type of template file to be used to write the
            dsbXML. Different templates contain different amounts of default
            assembly library data, which may be needed in order to import the
            dsbXML into older versions of DesignBuilder. However, this data can
            greatly increase the size of the resulting dsbXML file. Choose from
            the following options.

            * Default - a minimal file that imports into the latest versions
            * Assembly - the Default plus an AssemblyLibrary with typical objects
            * Full - a large file with all libraries that can be imported to version 7.3

        program_name: Optional text to set the name of the software that will
            appear under a comment in the XML to identify where it is being exported
            from. This can be set things like "Ladybug Tools" or "Pollination"
            or some other software in which this dsbXML export capability is being
            run. If None, no comment will appear. (Default: None).
    """
    # make sure the directory exists where the file will be written
    dir_name = os.path.dirname(os.path.abspath(output_file))
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    # get the string of the dsbXML file
    xml_str = model_to_dsbxml(
        model, use_multiplier, exclude_plenums, solve_ceiling_adjacencies,
        merge_method, xml_template, program_name
    )
    # write the string into the file and encode it in ISO-8859-15
    with open(output_file, 'wb') as fp:
        fp.write(xml_str.encode('iso-8859-15'))
    return output_file
