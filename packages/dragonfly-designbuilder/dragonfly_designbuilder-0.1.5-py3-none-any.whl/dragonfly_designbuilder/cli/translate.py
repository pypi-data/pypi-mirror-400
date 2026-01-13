"""dragonfly designbuilder translation commands."""
import click
import sys
import logging
import base64

from dragonfly.model import Model
from dragonfly_designbuilder.writer import model_to_dsbxml as writer_model_to_dsbxml
from dragonfly_designbuilder.writer import model_to_dsbxml_file as writer_model_to_dsbxml_file

_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating Dragonfly files to DesignBuilder.')
def translate():
    pass


@translate.command('model-to-dsbxml')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--multiplier/--full-geometry', ' /-fg', help='Flag to note if the '
    'multipliers on each Building story will be passed along to the '
    'generated Honeybee Room objects or if full geometry objects should be '
    'written for each story in the building.', default=True, show_default=True)
@click.option(
    '--plenum/--no-plenum', '-p/-np', help='Flag to indicate whether '
    'ceiling/floor plenum depths assigned to Room2Ds should generate '
    'distinct 3D Rooms in the translation.', default=True, show_default=True)
@click.option(
    '--ceil-adjacency/--no-ceil-adjacency', '-a/-na', help='Flag to indicate '
    'whether adjacencies should be solved between interior stories when '
    'Room2Ds perfectly match one another in their floor plate. This ensures '
    'that Surface boundary conditions are used instead of Adiabatic ones. '
    'Note that this input has no effect when the object-per-model is Story.',
    default=True, show_default=True)
@click.option(
    '--merge-method', '-m', help='Text to describe how the Room2Ds should '
    'be merged into individual Rooms during the translation. Specifying a '
    'value here can be an effective way to reduce the number of Room '
    'volumes in the resulting Model and, ultimately, yield a faster simulation '
    'time with less results to manage. Choose from: None, Zones, PlenumZones, '
    'Stories, PlenumStories.', type=str, default='None', show_default=True)
@click.option(
    '--xml-template', '-t', help='Text for the type of template file to be used '
    'to write the dsbXML. Different templates contain different amounts of default '
    'assembly library data, which may be needed in order to import the '
    'dsbXML into older versions of DesignBuilder. However, this data can '
    'greatly increase the size of the resulting dsbXML file. Choose from '
    'the following options.', type=str, default='Default', show_default=True)
@click.option(
    '--program-name', '-pn', help='Optional text to set the name of the '
    'software that will appear under under a comment in the XML to identify where '
    'it is being exported from. This can be set things like "Ladybug '
    'Tools" or "Pollination" or some other software in which this DsbXML '
    'export capability is being run. If unspecified, no comment will appear.',
    type=str, default=None, show_default=True)
@click.option(
    '--output-file', '-o', help='Optional dsbXML file path to output the dsbXML string '
    'of the translation. By default this will be printed out to stdout.',
    type=click.File('wb'), default='-', show_default=True)
def model_to_dsbxml_cli(
    model_file, multiplier, plenum, ceil_adjacency, merge_method,
    xml_template, program_name, output_file
):
    """Translate a Dragonfly Model file to a DsbXML file.

    \b
    Args:
        model_file: Full path to a Dragonfly Model JSON or Pkl file.
    """
    try:
        full_geometry = not multiplier
        no_plenum = not plenum
        no_ceil_adjacency = not ceil_adjacency
        model_to_dsbxml(
            model_file, full_geometry, no_plenum, no_ceil_adjacency, merge_method,
            xml_template, program_name, output_file
        )
    except Exception as e:
        _logger.exception('Model translation failed.\n{}\n'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def model_to_dsbxml(
    model_file, full_geometry=False, no_plenum=False, no_ceil_adjacency=False,
    merge_method='None', xml_template='Default', program_name=None, output_file=None,
    multiplier=True, plenum=True, ceil_adjacency=True
):
    """Translate a Dragonfly Model to an DsbXML file.

    Args:
        model_file: Full path to a Model JSON file (DFJSON) or a Model pkl (DFpkl) file.
        full_geometry: Boolean to note if the multipliers on each Building story
            will be passed along to the generated Honeybee Room objects or if
            full geometry objects should be written for each story in the
            building. (Default: False).
        no_plenum: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should generate distinct 3D Rooms in the
            translation. (Default: False).
        ceil_adjacency: Boolean to indicate whether adjacencies should be solved
            between interior stories when Room2Ds perfectly match one another
            in their floor plate. This ensures that Surface boundary conditions
            are used instead of Adiabatic ones. Note that this input has no
            effect when the object-per-model is Story. (Default: False).
        merge_method: An optional text string to describe how the Room2Ds should
            be merged into individual Rooms during the translation. Specifying a
            value here can be an effective way to reduce the number of Room
            volumes in the resulting Model and, ultimately, yield a faster simulation
            time with less results to manage. Note that Room2Ds will only be merged if
            they form a contiguous volume. Otherwise, there will be multiple Rooms per
            zone or story, each with an integer added at the end of their
            identifiers. Choose from the following options:

            * None - No merging will occur
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
            or some other software in which this DsbXML export capability is being
            run. If None, no comment will appear. (Default: None).
        output_file: Optional dsbXML file path to output the dsbXML string of the
            translation. If None, the string will be returned from this function.
    """
    # re-serialize the Model to Python
    model = Model.from_file(model_file)
    multiplier = not full_geometry
    ceil_adjacency = not no_ceil_adjacency

    # write out the dsbXML file
    if isinstance(output_file, str):
        writer_model_to_dsbxml_file(
            model, output_file, multiplier, no_plenum, ceil_adjacency, merge_method,
            xml_template=xml_template, program_name=program_name
        )
    else:
        dsbxml_str = writer_model_to_dsbxml(
            model, multiplier, no_plenum, ceil_adjacency, merge_method,
            xml_template=xml_template, program_name=program_name)
        f_contents = dsbxml_str.encode('iso-8859-15')
        if output_file is None:
            b = base64.b64encode(f_contents)
            base64_string = b.decode('utf-8')
            return base64_string
        else:
            output_file.write(f_contents)
