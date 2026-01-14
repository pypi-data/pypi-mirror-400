from typing import Any, Mapping
from ...pv.design.design import (
    ArrayDesign,
    GridDesign,
    InverterDesign,
    ModuleDesign,
    FixedStructureDesign,
    RigidDesign,
    TrackerStructureDesign,
    TransformerDesign,
)
from pvlib.location import Location


def make_array_design(input: Mapping[str, Any], location: Location) -> ArrayDesign:
    hub_module = input['moduleDesign']
    module = ModuleDesign(
        rated_module_power=hub_module['nameplatePower'],
        long_side=hub_module['longSide'],
        short_side=hub_module['shortSide'],
        bifaciality_factor=hub_module['bifacialityFactor'],
        id='module',
    )
    inverter = InverterDesign(
        rated_inverter_power_ac=input['invDesign']['nameplateNominalPower'],
        module=module,
        strings_per_inverter=input['stringCount'],
        modules_per_string=input['modulesPerString'],
    )

    hub_structure = input['structure']
    structure = None
    if hub_structure['structureType'] == 'fixed':
        structure = FixedStructureDesign(
            azimuth=180 if location.latitude > 0 else 0,
            tilt=hub_structure['tilt'] if not hub_structure['hasTiltByLatitude'] else location.latitude,
            module=module,
            module_placement=hub_structure['placementType'],
        )
    elif hub_structure['structureType'] == 'tracker':
        structure = TrackerStructureDesign(
            max_tracking_angle=hub_structure['trackingAngle'],
            module=module,
            module_placement=hub_structure['placementType'],
        )
        if 'nightStowAngle' in hub_structure:
            structure.night_stow_angle = float(hub_structure['nightStowAngle'])
    else:
        raise ValueError(f'Unknown structure type: {hub_structure["structureType"]}')

    # rated_dc_power = input['modulesPerString'] * input['stringCount'] * module.rated_module_power

    return ArrayDesign(
        inverter_count=input['invCount'],
        structure=structure,
        inverter=inverter,
        ground_cover_ratio=input['layout']['groundCoverRatio'],
    )


def make_site_design(hub_design: Mapping[str, Any], location: Location) -> RigidDesign:
    array_designs = [make_array_design(array, location) for array in hub_design['subarrays']]
    grid = GridDesign(id='grid')
    if 'gridLimit' in hub_design['grid']:
        grid.grid_limit = hub_design['grid']['gridLimit']

    design = RigidDesign(
        arrays=array_designs,
        transformer=TransformerDesign(
            id='transformer',
        ),
        grid=grid,
    )
    design.register_nodes()
    return design
