from __future__ import annotations

from dataclasses import MISSING, dataclass, field, fields
from abc import abstractmethod
from typing import Annotated, Any, Literal, List, Mapping, Optional, cast, override
from pydantic import Field
from pvlib.location import Location
import math
import pandas as pd
import warnings
import sympy as sp
from sympy.core.relational import Relational
from sympy.logic.boolalg import BooleanTrue, BooleanFalse

from .component_graph import ComponentGraph, DesignComponent
from .design_types import ComponentType
from ...display.object_tree_print import TreePrintable


StructureType = Literal['fixed', 'tracker']
ModuleOrientation = Literal['horizontal', 'vertical']
ModuleConstruction = Literal['glass_glass', 'glass_polymer']


# =============================================================================
# Helpers
# =============================================================================


def get_azimuth_by_location(location: Location) -> float:
    return 180 if location.latitude > 0 else 0


def sin_deg(angle_deg: float) -> float:
    """
    The sine of an angle given in degrees.
    """
    angle_rad = math.radians(angle_deg)  # Convert degrees to radians
    return math.sin(angle_rad)


# =============================================================================
# Design Classes
# =============================================================================


@dataclass(kw_only=True)
class ModuleDesign(DesignComponent, TreePrintable):
    @property
    @override
    def component_type(self) -> ComponentType:
        return 'module'

    rated_module_power: float = 400  # VARIABLE
    """The power of the module under standard-test conditions (STC): 25°C and 1000
    W/m^2"""

    short_side: float = 1
    """The length of the short side of the module [m]"""

    long_side: float = 2
    """The length of the long side of the module [m]"""

    bifaciality_factor: float = 0
    """A unit-less factor with values between 0 and 1 that describes the ratio of
    the efficiency of the rear side of the module and the efficiency of the front
    side. Bifacial modules typically have a bifaciality factor or 0.7, monofacial
    modules have a bifaciality factor of zero."""

    degradation_rate: float = 0
    """The rate of power reduction over time [%/year]"""

    temperature_coefficient_power: float = -0.003
    """The temperature coefficient of the maximum power point [1/°C]"""

    cell_string_count: int = 3
    """The number of parallel strings into which all cells of the module are
    divided [dimensionless]."""

    half_cell: bool = False
    """True: half-cell module, False: full-cell module."""

    module_construction: ModuleConstruction = 'glass_polymer'
    """Choose between 'glass_polymer' and 'glass_glass'"""

    module_eff_value: float = 0.22
    """The datasheet efficiency of the module [fraction]"""

    manufacturer: Optional[str] = None
    """Module manufacturer."""

    model: Optional[str] = None
    """Module model name."""

    temperature_coefficient_isc: Optional[float] = None
    """Temperature coefficient of short-circuit current [1/°C]."""

    temperature_coefficient_voc: Optional[float] = None
    """Temperature coefficient of open-circuit voltage [1/°C]."""

    nominal_operating_cell_temp: Optional[float] = None
    """Nominal operating cell temperature [°C]."""

    cells_per_cell_string: Optional[int] = None
    """Number of cells per cell string [count]."""

    mpp_voltage_stc: Optional[float] = None
    """Voltage at maximum-power point under STC [V]."""

    mpp_current_stc: Optional[float] = None
    """Current at maximum-power point under STC [A]."""

    open_circuit_voltage_stc: Optional[float] = None
    """Open-circuit voltage under STC [V]."""

    short_circuit_current_stc: Optional[float] = None
    """Short-circuit current under STC [A]."""

    bandgap_energy: Optional[float] = None
    """Material bandgap energy [eV]."""

    bandgap_energy_temp_coef: Optional[float] = None
    """Temperature coefficient of the bandgap energy [1/°C]."""

    back_transmission_loss_factor: Optional[float] = None
    """Fraction of irradiance on the back surface that does not reach the
    module's cells due to module features such as busbars, junction box,
    etc."""

    @property
    def surface_area(self) -> float:
        """The surface area of the module [m^2]."""
        return self.short_side * self.long_side


# ----------------------------- STRUCTURE -----------------------------
@dataclass(kw_only=True)
class StructureDesign(DesignComponent, TreePrintable):
    @property
    @override
    def component_type(self) -> ComponentType:
        return 'structure'

    module: ModuleDesign
    """The PV modules mounted on the structure."""

    rear_side_shading_factor: float = 0.1
    """Fraction of rear-side irradiance blocked by mechanical components behind
    the module, reducing effective light contribution to energy generation."""

    module_placement: Annotated[str, Field('2v', pattern=r'^\d[vh]$')] = '2v'
    """A string identifying the arrangement of modules on the structure. For example,
    '2v' indicates two vertically oriented (portrait) modules in the cross-section of
    the structure, with their short sides aligned with the structure's main axis.
    Conversely, '3h' indicates three horizontally oriented (landscape) modules, with
    their long sides aligned with the structure's main axis."""

    modules_per_structure: int = 84
    """The number of modules installed per structure. Typically this number is a
    multiple of the number of modules per string."""

    axis_tilt: float = 0
    """Tilt of the main structure axis relative to the horizontal plane [degrees].
    Values must be >= 0 and <= 45 degrees."""

    back_shading_loss_factor: float = 0.02
    """Fraction of irradiance on the back surface that does not reach the
    module's cells due to module features such as busbars, junction box,
    etc."""

    back_mismatch_loss_factor: Optional[float] = None
    """Additional fractional loss on the back-side irradiance due to electrical
    mismatch effects between cells or strings, typically caused by non-uniform
    rear-side illumination (e.g. partial shading, structural elements, or
    albedo heterogeneity)."""

    @property
    @abstractmethod
    def axis_height(self) -> float:
        """The distance between the main structure axis and the ground [m]."""

    @property
    @abstractmethod
    def axis_azimuth(self) -> float:
        """The angle between the main structure axis and a line oriented toward true north
        [degrees]. Values must be >=0 and <=90. A value of 0 means the main structure axis is
        oriented north-south. A value of 90 means the main structure axis is oriented
        east-west."""

    collector_to_axis_offset: float = 0
    """The vertical distance between the collector and the main structure axis [m]."""

    @property
    def structure_type(self) -> StructureType:
        """The type of structure: fixed or tracker"""
        return cast(StructureType, self.subtype)

    @property
    def module_orientation(self) -> ModuleOrientation:
        """The orientation of the long side of the module
        Two options: horizontal, vertical"""
        orientation_char = self.module_placement[1]
        if orientation_char == 'v':
            return 'vertical'
        else:
            return 'horizontal'

    @property
    def number_modules_cross_section(self) -> int:
        """The number of modules in the cross-section of the structure."""
        return int(self.module_placement[0])

    @property
    def collector_width(self) -> float:
        """The width of the rectangle formed by the PV modules placed on top of the structure [m]."""
        if self.module_orientation == 'horizontal':
            return self.number_modules_cross_section * self.module.short_side
        else:
            return self.number_modules_cross_section * self.module.long_side

    @property
    @abstractmethod
    def collector_height(self) -> float:
        """The height of the center of the rectangle formed by the PV modules placed on top of the structure [m]."""

    @property
    @abstractmethod
    def module_clearance(self) -> float:
        """The shortest distance (at any moment of the day) between the lower edge of any PV module and the ground [m]."""


# ----------------------------- FIXED-TILT STRUCTURE -----------------------------
@dataclass(kw_only=True)
class FixedStructureDesign(StructureDesign, DesignComponent):
    subtype: Optional[str] = 'fixed'

    tilt: float
    """The tilt angle of the module surface / collector [degrees]. A value of 0 means modules
    are facing up. A Value of 90 means modules are facing the horizon. Values must
    be >= 0 and <= 90."""

    azimuth: float = 180
    """The azimuth angle of the module surface / collector. A value of 0 means modules are facing
    north [degrees] In the northern hemisphere fixed-tilt structures are typically
    oriented towards the south (azimuth = 180 degrees), while in the southern
    hemisphere they are typically oriented towards the north (azimuth = 0 degrees).
    Values must be >= 0 and <= 360.
    """

    module_clearance: float = 1  # pyright: ignore[reportIncompatibleMethodOverride]

    use_azimuth_by_location: bool = True
    """If True, then after assigning the location to the site, the azimuth will be automatically
    adjusted based on location"""

    @property
    @override
    def axis_height(self) -> float:
        return self.collector_height - self.collector_to_axis_offset

    @property
    @override
    def axis_azimuth(self) -> float:
        return self.azimuth + 90

    @property
    @override
    def structure_type(self) -> StructureType:
        return 'fixed'

    @property
    @override
    def collector_height(self) -> float:
        return self.module_clearance + 0.5 * self.collector_width * sin_deg(self.tilt)


@dataclass(kw_only=True)
class TrackerStructureDesign(StructureDesign, DesignComponent):
    subtype: Optional[str] = 'tracker'

    axis_height: float = 1.5
    """The distance between the axis of rotation and the ground [m]."""

    axis_azimuth: float = 0
    """The angle between the tracker axis and a line oriented toward true north
    [degrees]. Values must be >=0 and <=90. A value of 0 means the tracker axis is
    oriented north-south. A value of 90 means the tracker axis is oriented
    east-west."""

    axis_tilt: float = 0
    """The angle between the axis of rotation and a flat horizontal surface
    [degrees]. Values must be >= 0 and <= 45 degrees."""

    max_tracking_angle: float = 60
    """The maximum possible rotation angle [degrees]. Commercial
    horizontal-single-axis-trackers (HSAT) allow tracking angles up to 50-60
    degrees. Values must be >= 0 and <= 90 degrees."""

    night_stow_angle: float = 0
    """The angle at which the tracker is stowed at night [degrees]. Values must
    be >= 0 and <= 90 degrees."""

    backtracking: bool = True
    """True: backtracking enabled, False: No backtracking"""

    @property
    @override
    def structure_type(self) -> StructureType:
        return 'tracker'

    axis_height: float = 1.5  # pyright: ignore[reportIncompatibleMethodOverride]
    """The distance between the axis of rotation and the ground [m]."""

    axis_azimuth: float = 0  # pyright: ignore[reportIncompatibleMethodOverride]
    """The angle between the axis of rotation and a line oriented toward true north
    [degrees]. Values must be >=0 and <=90. A value of 0 means the axis of rotation is
    oriented north-south. A value of 90 means the tracker axis of rotationis oriented
    east-west."""

    @property
    @override
    def collector_height(self) -> float:
        return self.axis_height + self.collector_to_axis_offset

    @property
    @override
    def module_clearance(self) -> float:
        return self.collector_height - 0.5 * self.collector_width * sin_deg(self.max_tracking_angle)


# ----------------------------- INVERTER -----------------------------------------
@dataclass(kw_only=True)
class InverterDesign(DesignComponent, TreePrintable):
    @property
    @override
    def component_type(self) -> ComponentType:
        return 'inverter'

    subtype: Optional[str] = 'tracker'

    module: ModuleDesign
    """The PV modules connected to the inverter."""

    rated_inverter_power_ac: float  # VARIABLE
    """The rated AC power output of the inverter [W]. From Datasheet."""

    modules_per_string: int  # VARIABLE
    """The number of modules per string."""

    strings_per_inverter: int  # VARIABLE
    """The number of strings connected to the inveter."""

    nominal_efficiency: float = 0.98
    """The nominal DC to AC conversion efficiency of the inverter [fraction]."""

    @property
    def modules_per_inverter(self) -> int:
        """The total number of modules connected to the inverer (all strings)."""
        return self.modules_per_string * self.strings_per_inverter

    @property
    def rated_inverter_power_dc(self) -> float:
        """The total DC power of all strings/modules connected to the inverter at STC conditions [W].
        Also referred to as DC capacity."""
        return self.modules_per_inverter * self.module.rated_module_power


# ----------------------------- ARRAY --------------------------------------------
@dataclass(kw_only=True)
class ArrayDesign(DesignComponent, TreePrintable):
    @property
    @override
    def component_type(self) -> ComponentType:
        return 'array'

    structure: StructureDesign
    """Modules are either mounted on a rigid structure with a fixed tilt angle or
    on a Horizontal-Single-Axis-Tracker (HSAT), following the sun from east to west."""

    inverter: InverterDesign
    """The inverter transforming DC to AC power."""

    inverter_count: int  # VARIABLE
    """The number of inverters belonging to this array."""

    ground_cover_ratio: float  # VARIABLE
    """The ratio between the collector width and the structure pitch."""

    structures_per_structure_line: int = 1
    """The number of structures connected to lines for efficient robotic cleaning."""

    albedo_value: float = 0.2
    """A single value describing the albedo of the ground below the modules [fraction].
    The default value is 0.2 meaning that 20% of the incoming irradiance is reflected
    (in all directions)."""

    ground_slope_tilt: float = 0
    """The angle of the slope (ground) containing the tracker axes, relative to horizontal
    [degrees]. The default is zero degrees (flat surface)."""

    ground_cross_axis_slope: float = 0
    """The angle of the ground slope perpendicular to the tracker axis direction,
    measured relative to a horizontal surface [degrees]. A value of 0 corresponds
    to no cross-axis slope (flat ground)"""

    ground_slope_azimuth: float = 0
    """Direction of the normal to the ground slope containing the tracker axes, when
    projected on the horizontal [degrees]. The default is zero degrees (flat ground)."""

    @property
    def rated_array_power_dc(self) -> float:  # VARIABLE
        """The rated DC power of the array [Wp]. Also called the DC capacity."""
        return self.inverter_count * self.inverter.rated_inverter_power_dc

    @property
    def rated_array_power_ac(self) -> float:  # VARIABLE
        """The nominal ac power of the array [W]. Also called the AC capacity."""
        return self.inverter_count * self.inverter.rated_inverter_power_ac

    @property
    def dc_ac_ratio(self) -> float:  # VARIABLE
        """The ratio between the nominal dc and the nominal ac power [fraction]."""
        return self.rated_array_power_dc / self.rated_array_power_ac

    @property
    def pitch(self) -> float:  # VARIABLE
        """The distance between the axes of two adjacent structures [m]."""
        return self.structure.collector_width / self.ground_cover_ratio

    # --- Properties ---

    @property
    def module_count(self) -> float:
        """The number of PV modules in this array."""
        return self.inverter_count * self.inverter.modules_per_inverter

    @property
    def string_count(self) -> float:
        """The number of PV modules in this array."""
        return self.inverter_count * self.inverter.strings_per_inverter

    @property
    def structure_count(self) -> float:
        """The number of structures in this array."""
        return self.module_count / self.structure.modules_per_structure

    @property
    def total_module_surface_area(self) -> float:  # pvsyst: area_sizing
        """The tota surface area of all modules in this array [m^2]."""
        return self.module_count * self.structure.module.surface_area


# ----------------------------- TRANSFORMER --------------------------------------
@dataclass(kw_only=True)
class TransformerDesign(DesignComponent, TreePrintable):
    @property
    @override
    def component_type(self) -> ComponentType:
        return 'transformer'

    no_load_loss: float = 0.2 / 100
    """The constant losses experienced by a transformer, even when the transformer is not under load.
    % of transformer rating [fraction]."""

    full_load_loss: float = 0.7 / 100
    """The load dependent losses experienced by the transformer. % of transformer rating [fraction]."""


# ----------------------------- GRID ---------------------------------------------
@dataclass(kw_only=True)
class GridDesign(DesignComponent, TreePrintable):
    @property
    @override
    def component_type(self) -> ComponentType:
        return 'grid'

    grid_limit: float | pd.Series | None = None


# ----------------------------- SITE ----------------------------------------
@dataclass
class RigidDesign(ComponentGraph, TreePrintable):
    arrays: List[ArrayDesign]
    transformer: TransformerDesign  # ac
    grid: GridDesign
    selected_array: int = 0

    nodes: list[DesignComponent] = field(default_factory=list)
    edges: list[tuple[DesignComponent, DesignComponent]] = field(default_factory=list)

    @property
    def array(self) -> ArrayDesign:
        if not self.arrays:
            raise ValueError('No arrays defined in the design')
        if isinstance(self.arrays, ArrayDesign):
            return self.arrays
        else:
            return self.arrays[self.selected_array]

    def _make_base_design_spec(self) -> dict[str, Any]:
        return dict(
            rated_module_power=self.array.structure.module.rated_module_power,
            dc_capacity=self.array.rated_array_power_dc,
            dc_ac_ratio=self.array.dc_ac_ratio,
            module_placement=self.array.structure.module_placement,
            ground_cover_ratio=self.array.ground_cover_ratio,
            grid_limit=self.grid.grid_limit,
        )

    # FIXME: add missing fields
    def to_tracker_design_spec(self) -> dict[str, Any]:
        s = self.array.structure
        assert isinstance(s, TrackerStructureDesign), 'Site design must have a tracker structure'
        return dict(
            **self._make_base_design_spec(),
            axis_height=s.axis_height,
            axis_azimuth=s.axis_azimuth,
            axis_tilt=s.axis_tilt,
            max_tracking_angle=s.max_tracking_angle,
            night_stow_angle=s.night_stow_angle,
            backtracking=s.backtracking,
        )

    # FIXME: add missing fields
    def to_fixed_design_spec(self) -> dict[str, Any]:
        s = self.array.structure
        assert isinstance(s, FixedStructureDesign), 'Site design must have a fixed structure'
        return dict(
            **self._make_base_design_spec(),
            tilt=s.tilt,
            azimuth=s.azimuth,
            clearance=s.module_clearance,
        )

    def register_nodes(self) -> None:
        assert len(self.arrays) == 1, (
            f'automatic design.register_nodes() only supports single-array designs, got {len(self.arrays)} arrays'
        )
        main_array = self.arrays[0]
        self.add_node(main_array)
        self.add_node(main_array.structure)
        self.add_node(main_array.structure.module)
        self.add_node(main_array.inverter)
        self.add_node(self.transformer)
        self.add_node(self.grid)


# =============================================================================
# Solver
# =============================================================================


class EquationSystem:
    """
    Defines:
      - which parameters exist as symbols
      - which parameters may be solved for (variables)
      - which relations participate in solving (equations)

    Symbols are created ONCE and reused everywhere.
    """

    def __init__(self) -> None:
        # ------------------------------------------------------------------
        # Symbol registry
        # ------------------------------------------------------------------
        self.symbols: dict[str, sp.Symbol] = {
            # module / inverter
            'rated_module_power': sp.Symbol('rated_module_power'),
            'modules_per_string': sp.Symbol('modules_per_string'),
            'strings_per_inverter': sp.Symbol('strings_per_inverter'),
            'modules_per_inverter': sp.Symbol('modules_per_inverter'),
            'rated_inverter_power_dc': sp.Symbol('rated_inverter_power_dc'),
            'rated_inverter_power_ac': sp.Symbol('rated_inverter_power_ac'),
            # array
            'inverter_count': sp.Symbol('inverter_count'),
            'rated_array_power_dc': sp.Symbol('rated_array_power_dc'),
            'rated_array_power_ac': sp.Symbol('rated_array_power_ac'),
            'dc_ac_ratio': sp.Symbol('dc_ac_ratio'),
            'module_count': sp.Symbol('module_count'),
            'string_count': sp.Symbol('string_count'),
            # layout
            'collector_width': sp.Symbol('collector_width'),
            'ground_cover_ratio': sp.Symbol('ground_cover_ratio'),
            'pitch': sp.Symbol('pitch'),
        }

        S = self.symbols  # shorthand

        # ------------------------------------------------------------------
        # Variables for automatic solving
        # - variables must appear in one of the equations
        # - not all symbols used in equtions must be variables
        # ------------------------------------------------------------------
        self.variables: set[str] = {
            'modules_per_string',
            'strings_per_inverter',
            'modules_per_inverter',
            'rated_inverter_power_dc',
            'rated_inverter_power_ac',
            'inverter_count',
            'rated_array_power_dc',
            'rated_array_power_ac',
            'dc_ac_ratio',
            'ground_cover_ratio',
            'pitch',
            'module_count',
            'string_count',
        }

        # ------------------------------------------------------------------
        # Equations (relations to be solved)
        # ------------------------------------------------------------------
        self.equations: list = [
            sp.Eq(S['modules_per_inverter'], S['modules_per_string'] * S['strings_per_inverter'], evaluate=False),  # type: ignore
            sp.Eq(S['rated_inverter_power_dc'], S['modules_per_inverter'] * S['rated_module_power'], evaluate=False),  # type: ignore
            sp.Eq(S['rated_array_power_dc'], S['inverter_count'] * S['rated_inverter_power_dc'], evaluate=False),  # type: ignore
            sp.Eq(S['rated_array_power_ac'], S['inverter_count'] * S['rated_inverter_power_ac'], evaluate=False),  # type: ignore
            sp.Eq(S['dc_ac_ratio'], S['rated_array_power_dc'] / S['rated_array_power_ac'], evaluate=False),  # type: ignore
            sp.Eq(S['pitch'], S['collector_width'] / S['ground_cover_ratio'], evaluate=False),  # type: ignore
            sp.Eq(S['module_count'], S['inverter_count'] * S['modules_per_inverter'], evaluate=False),  # type: ignore
            sp.Eq(S['string_count'], S['inverter_count'] * S['strings_per_inverter'], evaluate=False),  # type: ignore
        ]

    def sym(self, name: str) -> sp.Symbol:
        return self.symbols[name]

    def required_symbol_names(self) -> set[str]:
        return {str(s) for eq in self.equations for s in eq.free_symbols}

    def required_constant_names(self) -> set[str]:
        return self.required_symbol_names() - self.variables

    def lhs_symbol_names(self) -> set[str]:
        """
        Names of symbols that appear on the left-hand side of equations.
        These are considered 'used' if provided by the user.
        """
        lhs = set()
        for eq in self.equations:
            if isinstance(eq, sp.Equality):
                lhs.add(str(eq.lhs))
        return lhs


def _iterative_solve(
    *,
    equations: list[Relational],
    known_eq: dict[str, float],
    symbols: dict[str, sp.Symbol],
) -> dict[str, float]:
    """
    Iteratively solve equations that contain exactly one unknown.
    known_eq: subset of known values that are part of equation system
    """
    known = dict(known_eq)

    progress = True

    while progress:
        progress = False

        for eq in equations:
            if not isinstance(eq, sp.Equality):
                continue

            # substitute known values
            subs = {symbols[k]: v for k, v in known.items()}
            lhs = eq.lhs.subs(subs)  # type: ignore
            rhs = eq.rhs.subs(subs)  # type: ignore

            free = lhs.free_symbols | rhs.free_symbols

            # exactly one unknown → solvable
            if len(free) == 1:
                sym = next(iter(free))
                name = str(sym)

                if name in known:
                    continue

                sol = sp.solve(sp.Eq(lhs, rhs, evaluate=False), sym, dict=True)

                if sol:
                    expr = sol[0][sym]
                    expr = sp.simplify(expr)

                    if not expr.free_symbols:
                        known[name] = float(expr)
                        progress = True

    return known


def detect_equation_contradictions(
    *,
    system: EquationSystem,
    equations_substituted: list[Relational],
    known_values: Mapping[str, float | int],
    residual_tolerance: float = 1e-9,
) -> None:
    """
    Detect conflicting equations and raise a detailed ValueError.

    Shows:
      - symbolic equation
      - evaluated LHS value
      - RHS factor values and numeric result
    """

    contradictions: list[str] = []
    conflicting_vars: set[str] = set()

    for orig, eq in zip(system.equations, equations_substituted):
        if not isinstance(orig, sp.Equality):
            continue

        # Hard symbolic contradiction
        if isinstance(eq, BooleanFalse):
            contradictions.append(sp.sstr(orig))
            for s in orig.free_symbols:
                name = str(s)
                if name in known_values:
                    conflicting_vars.add(name)
            continue

        if isinstance(eq, BooleanTrue):
            continue

        if isinstance(eq, sp.Equality):
            lhs = eq.lhs
            rhs = eq.rhs

            if lhs.is_number and rhs.is_number:
                lhs_val = float(lhs)  # type: ignore
                rhs_val = float(rhs)  # type: ignore

                if abs(lhs_val - rhs_val) > residual_tolerance:
                    # --- build detailed RHS breakdown ---
                    rhs_syms = orig.rhs.free_symbols
                    rhs_parts = []
                    for s in sorted(rhs_syms, key=lambda x: str(x)):
                        name = str(s)
                        if name in known_values:
                            rhs_parts.append(f'{name}({known_values[name]}')

                    rhs_detail = ' × '.join(rhs_parts)
                    if rhs_detail:
                        rhs_detail += f' = {rhs_val}'
                    else:
                        rhs_detail = str(rhs_val)

                    contradictions.append(f'{sp.sstr(orig)}\n    LHS = {lhs_val}\n    RHS = {rhs_detail}')

                    for s in orig.free_symbols:
                        name = str(s)
                        if name in known_values:
                            conflicting_vars.add(name)

    if contradictions:
        warn_lines = ['Conflicting inputs detected.']

        if conflicting_vars:
            warn_lines.append('Conflicting variables: ' + ', '.join(sorted(conflicting_vars)))

        warn_lines.append('Conflicting equations:')
        for c in contradictions:
            warn_lines.append('  - ' + c.replace('\n', '\n    '))

        warnings.warn(
            '\n'.join(warn_lines),
            category=UserWarning,
            stacklevel=3,
        )

        raise ValueError('\n'.join(warn_lines))


def solve_equation_system(
    *,
    system: EquationSystem,
    known_values: Mapping[str, float | int],
) -> dict[str, float]:
    # ------------------------------------------------------------
    # 1. Check required constants
    # ------------------------------------------------------------
    missing = [name for name in system.required_constant_names() if name not in known_values]
    if missing:
        raise ValueError('Missing required constants: ' + ', '.join(missing))

    # ------------------------------------------------------------
    # 2. Substitute known values
    # ------------------------------------------------------------
    subs = {system.sym(name): float(val) for name, val in known_values.items() if name in system.symbols}

    eqs_sub: list[Relational] = []
    for eq in system.equations:
        if isinstance(eq, sp.Equality):
            lhs = sp.simplify(eq.lhs.subs(subs))  # type: ignore
            rhs = sp.simplify(eq.rhs.subs(subs))  # type: ignore

            # keep as Equality
            eqs_sub.append(sp.Eq(lhs, rhs, evaluate=False))  # type: ignore
        else:
            eqs_sub.append(sp.simplify(eq.subs(subs)))

    # ------------------------------------------------------------
    # 3. Detect contradictions (with variable attribution)
    # ------------------------------------------------------------
    detect_equation_contradictions(
        system=system,
        equations_substituted=eqs_sub,
        known_values=known_values,
    )

    # ------------------------------------------------------------
    # 4. Unknowns = variables without values
    # ------------------------------------------------------------
    unknown_syms = [system.sym(name) for name in system.variables if name not in known_values]

    if not unknown_syms:
        return {k: float(v) for k, v in known_values.items()}

    # ------------------------------------------------------------
    # 5. Detect underconstrained equations (diagnostics)
    # ------------------------------------------------------------
    undefined_equations: list[Relational] = []

    unknown_sym_set = set(unknown_syms)

    for orig, eq in zip(system.equations, eqs_sub):
        if isinstance(eq, sp.Equality):
            free = eq.lhs.free_symbols | eq.rhs.free_symbols  # type: ignore
            if free & unknown_sym_set:
                undefined_equations.append(orig)

    # ------------------------------------------------------------
    # 6. Iterative solve (single-variable elimination)
    # ------------------------------------------------------------

    # Split known values between those that are in and not in equation system
    known_eq = {k: v for k, v in known_values.items() if k in system.symbols}
    known_other = {k: v for k, v in known_values.items() if k not in system.symbols}

    known_after = _iterative_solve(
        equations=eqs_sub,
        known_eq=known_eq,  # type: ignore
        symbols=system.symbols,
    )

    # ------------------------------------------------------------
    # 7. Verify solver did not change user-provided values
    # ------------------------------------------------------------
    mismatches: list[str] = []

    for name, user_val in known_values.items():
        if name not in system.symbols:
            continue
        if name not in known_after:
            continue

        solved_val = known_after[name]

        # numeric comparison
        residual_tolerance = 1e-9
        if abs(float(solved_val) - float(user_val)) > residual_tolerance * max(
            1.0, abs(float(user_val)), abs(float(solved_val))
        ):
            mismatches.append(f'{name}: user={float(user_val)} solved={float(solved_val)}')

    if mismatches:
        lines = [
            'Solver modified user-provided inputs.',
            'The following inputs do not match the solved results:',
        ]
        for m in mismatches:
            lines.append('  - ' + m)

        raise ValueError('\n'.join(lines))

    # ------------------------------------------------------------
    # 8. Detect unresolved variables and undefined equations
    # ------------------------------------------------------------
    unresolved = {name for name in system.variables if name not in known_after}

    undefined_equations: list[Relational] = []

    subs_final = {system.sym(k): v for k, v in known_after.items() if k in system.symbols}

    for eq in system.equations:
        if not isinstance(eq, sp.Equality):
            continue

        lhs = eq.lhs.subs(subs_final)  # type: ignore
        rhs = eq.rhs.subs(subs_final)  # type: ignore

        free = lhs.free_symbols | rhs.free_symbols
        if free:
            undefined_equations.append(eq)

    if unresolved:
        # warning (diagnostics)
        warn_lines = ['Underconstrained system detected.']
        warn_lines.append('Unresolved variables: ' + ', '.join(sorted(unresolved)))

        if undefined_equations:
            warn_lines.append('Undefined equations:')
            for eq in undefined_equations:
                warn_lines.append(f'  - {sp.sstr(eq)}')

        warnings.warn(
            '\n'.join(warn_lines),
            category=UserWarning,
            stacklevel=3,
        )

        # hard error
        raise ValueError('\n'.join(warn_lines))

    return {**known_after, **known_other}


# =============================================================================
# Helpers for factories
# =============================================================================


def filter_kwargs_for_dataclass(cls: type, values: Mapping[str, Any]) -> dict[str, Any]:
    names = {f.name for f in fields(cls)}
    return {k: v for k, v in values.items() if k in names and v is not None}


def extract_dataclass_values(obj) -> dict[str, Any]:
    if obj is None:
        return {}
    return {f.name: getattr(obj, f.name) for f in fields(obj) if getattr(obj, f.name) is not None}


DESIGN_CLASSES = (
    ModuleDesign,
    StructureDesign,
    FixedStructureDesign,
    TrackerStructureDesign,
    InverterDesign,
    ArrayDesign,
    TransformerDesign,
    GridDesign,
)


def collect_all_attribute_names() -> set[str]:
    names: set[str] = set()

    for cls in DESIGN_CLASSES:
        # dataclass fields (inputs, constants)
        names |= {f.name for f in fields(cls)}

        # properties defined directly on the class
        names |= {name for name, attr in cls.__dict__.items() if isinstance(attr, property)}

    return names


# =============================================================================
# Factory methods
# =============================================================================


def make_array_design(
    *,
    # -----------------
    # ---- DESIGNS ----
    module: ModuleDesign | None = None,
    structure: StructureDesign | None = None,
    structure_type: StructureType,
    inverter: InverterDesign | None = None,
    # -----------------
    # --- VARIABLES ---
    modules_per_string: int | None = None,
    strings_per_inverter: int | None = None,
    modules_per_inverter: int | None = None,
    inverter_count: int | None = None,
    module_count: int | None = None,
    string_count: int | None = None,
    rated_inverter_power_ac: float | None = None,
    rated_inverter_power_dc: float | None = None,
    rated_array_power_dc: float | None = None,
    rated_array_power_ac: float | None = None,
    dc_ac_ratio: float | None = None,
    ground_cover_ratio: float | None = None,
    pitch: float | None = None,
    # -----------------
    # --- CONSTANTS ---
    **constants,
) -> ArrayDesign:
    # ------------------------------------------------------------
    # 1. Collect user inputs
    # ------------------------------------------------------------
    user_explicit: dict[str, float | int | None] = {
        'modules_per_string': modules_per_string,
        'strings_per_inverter': strings_per_inverter,
        'modules_per_inverter': modules_per_inverter,
        'inverter_count': inverter_count,
        'module_count': module_count,
        'string_count': string_count,
        'rated_inverter_power_ac': rated_inverter_power_ac,
        'rated_inverter_power_dc': rated_inverter_power_dc,
        'rated_array_power_dc': rated_array_power_dc,
        'rated_array_power_ac': rated_array_power_ac,
        'dc_ac_ratio': dc_ac_ratio,
        'ground_cover_ratio': ground_cover_ratio,
        'pitch': pitch,
        **constants,
    }

    # ------------------------------------------------------------
    # 2. Build module and structure.
    # ------------------------------------------------------------
    if module is None:
        module_kwargs = filter_kwargs_for_dataclass(ModuleDesign, user_explicit)
        module = ModuleDesign(**module_kwargs)

    if structure is None:
        if structure_type == 'tracker':
            structure_kwargs = filter_kwargs_for_dataclass(TrackerStructureDesign, user_explicit)
            structure = TrackerStructureDesign(module=module, **structure_kwargs)
        else:
            structure_kwargs = filter_kwargs_for_dataclass(FixedStructureDesign, user_explicit)
            # if user_explicit.get('module_clearance') is not None:
            #     structure_kwargs['clearance'] = user_explicit['module_clearance']
            structure = FixedStructureDesign(module=module, **structure_kwargs)

    # ------------------------------------------------------------
    # 3. Collect defaults from Design classes
    # ------------------------------------------------------------
    defaults: dict[str, float | int | None] = {}

    for cls in (InverterDesign, ArrayDesign):
        for f in fields(cls):
            if f.default is not MISSING:
                if f.default is not None:
                    defaults[f.name] = f.default
            elif f.default_factory is not MISSING:  # type: ignore
                if f.default_factory is not None:
                    defaults[f.name] = f.default_factory()  # type: ignore

    # ------------------------------------------------------------
    # 4. Collect fields from module and structure
    # ------------------------------------------------------------
    module_parameters = extract_dataclass_values(module)
    module_parameters['surface_area'] = module.surface_area

    structure_parameters = extract_dataclass_values(structure)
    structure_parameters['number_modules_cross_section'] = structure.number_modules_cross_section
    structure_parameters['collector_height'] = structure.collector_height
    structure_parameters['collector_width'] = structure.collector_width
    structure_parameters['module_clearance'] = structure.module_clearance

    # ------------------------------------------------------------
    # 5. Known values = defaults overwritten by user inputs
    # ------------------------------------------------------------
    known_values: dict[str, Any] = dict(defaults)

    for k, v in user_explicit.items():
        if v is not None:
            known_values[k] = v

    known_values.update(module_parameters)
    known_values.update(structure_parameters)

    # ------------------------------------------------------------
    # 6. Validate known values against design attribute namespace
    # ------------------------------------------------------------
    ALL_ATTRIBUTE_NAMES = collect_all_attribute_names()
    invalid = {
        name for name in known_values if (name not in ALL_ATTRIBUTE_NAMES and name not in {'module', 'structure', 'inverter'})
    }

    if invalid:
        warnings.warn(
            'Invalid design parameters ignored: ' + ', '.join(sorted(invalid)),
            stacklevel=2,
        )

    # ------------------------------------------------------------
    # 7. Solve
    # ------------------------------------------------------------
    system = EquationSystem()
    solver_known_values = {k: v for k, v in known_values.items() if k in system.symbols}
    solved = solve_equation_system(system=system, known_values=solver_known_values)

    # ------------------------------------------------------------
    # 8. Build Inverter and Array (only one!)
    # ------------------------------------------------------------
    design_inputs = dict(known_values)
    design_inputs['module'] = module
    design_inputs['structure'] = structure
    design_inputs.update(solved)

    if inverter is None:
        inverter_kwargs = filter_kwargs_for_dataclass(InverterDesign, design_inputs)
        inverter = InverterDesign(**inverter_kwargs)
        design_inputs['inverter'] = inverter

    array_kwargs = filter_kwargs_for_dataclass(ArrayDesign, design_inputs)
    array = ArrayDesign(**array_kwargs)

    return array


def make_site_design(
    *,
    # -----------------
    # ---- DESIGNS ----
    module: ModuleDesign | None = None,
    structure: StructureDesign | None = None,
    structure_type: StructureType | None = None,
    inverter: InverterDesign | None = None,
    arrays: ArrayDesign | list[ArrayDesign] | None = None,
    grid: GridDesign | None = None,
    transformer: TransformerDesign | None = None,
    # -----------------
    # --- VARIABLES ---
    modules_per_string: int | None = None,
    strings_per_inverter: int | None = None,
    modules_per_inverter: int | None = None,
    inverter_count: int | None = None,
    module_count: int | None = None,
    string_count: int | None = None,
    rated_inverter_power_ac: float | None = None,
    rated_inverter_power_dc: float | None = None,
    rated_array_power_dc: float | None = None,
    rated_array_power_ac: float | None = None,
    dc_ac_ratio: float | None = None,
    ground_cover_ratio: float | None = None,
    pitch: float | None = None,
    # -----------------
    # --- CONSTANTS ---
    **constants,
):
    if not arrays:
        if structure_type is None:
            raise ValueError('If arrays is not provided, structure_type must be defined.')
        arrays = [
            make_array_design(
                module=module,
                structure=structure,
                structure_type=structure_type,
                inverter=inverter,
                modules_per_string=modules_per_string,
                strings_per_inverter=strings_per_inverter,
                modules_per_inverter=modules_per_inverter,
                inverter_count=inverter_count,
                module_count=module_count,
                string_count=string_count,
                rated_inverter_power_ac=rated_inverter_power_ac,
                rated_inverter_power_dc=rated_inverter_power_dc,
                rated_array_power_dc=rated_array_power_dc,
                rated_array_power_ac=rated_array_power_ac,
                dc_ac_ratio=dc_ac_ratio,
                ground_cover_ratio=ground_cover_ratio,
                pitch=pitch,
                **constants,
            )
        ]
    elif isinstance(arrays, ArrayDesign):
        arrays = [arrays]

    if grid is None:
        grid_kwargs = filter_kwargs_for_dataclass(GridDesign, constants)
        grid = GridDesign(**grid_kwargs)

    if transformer is None:
        transformer_kwargs = filter_kwargs_for_dataclass(TransformerDesign, constants)
        transformer = TransformerDesign(**transformer_kwargs)

    site_design = RigidDesign(
        arrays=arrays,
        transformer=transformer,
        grid=grid,
    )
    site_design.register_nodes()
    return site_design


def make_fixed_design(
    *,
    # structure parameters
    tilt: float = 20,
    azimuth: Optional[float] = None,
    clearance: float = 1,
    module_clearance: Optional[float] = None,  # clearance renamed to module_clearance
    #
    # common design parameters
    module_rated_power: float = 400,
    rated_module_power: Optional[float] = None,  # module_rated_power renamed to rated_module_power
    dc_capacity: float = 100 * 1e6,  # 100 MW
    rated_array_power_dc: Optional[float] = None,  # dc_capacity renamed to rated_array_power_dc
    dc_ac_ratio: float = 1.2,
    module_placement='2v',
    grid_limit: Optional[float] = None,
    ground_cover_ratio: float = 0.35,
    strings_per_inverter: int = 10,  # added to make new design solvable
    modules_per_string: int = 28,  # added to make new design solvable
    **kwargs,
):
    """
    Create a fixed-tilt single-array design
    """

    # --- legacy alias handling ---
    if rated_module_power is not None:
        module_rated_power = rated_module_power

    if rated_array_power_dc is not None:
        dc_capacity = rated_array_power_dc  #

    if module_clearance is not None:
        clearance = module_clearance

    # --- azimuth logic ---
    use_azimuth_by_location = azimuth is None
    azimuth = azimuth if azimuth is not None else 180

    site_design = make_site_design(
        structure_type='fixed',
        tilt=tilt,
        azimuth=azimuth,
        module_clearance=clearance,
        use_azimuth_by_location=use_azimuth_by_location,
        rated_module_power=module_rated_power,
        rated_array_power_dc=dc_capacity,
        dc_ac_ratio=dc_ac_ratio,
        module_placement=module_placement,
        grid_limit=grid_limit,
        ground_cover_ratio=ground_cover_ratio,
        strings_per_inverter=strings_per_inverter,
        modules_per_string=modules_per_string,
        **kwargs,
    )
    return site_design


def make_tracker_design(
    *,
    # structure parameters
    axis_height: float = 1.5,
    axis_azimuth: float = 0,
    axis_tilt: float = 0,
    max_tracking_angle: float = 60,
    night_stow_angle: float = 0,
    backtracking: bool = True,
    #
    # common design parameters
    module_rated_power: float = 400,
    rated_module_power: Optional[float] = None,  # legacy
    dc_capacity: float = 100 * 1e6,  # 100 MW
    rated_array_power_dc: Optional[float] = None,  # legacy
    dc_ac_ratio: float = 1.2,
    module_placement='1v',
    grid_limit: Optional[float] = None,
    ground_cover_ratio: float = 0.35,
    strings_per_inverter: int = 10,  # added to make new design solvable
    modules_per_string: int = 28,  # added to make new design solvable
    **kwargs,
):
    """
    Create a fixed-tilt single-array design
    """

    # --- legacy alias handling ---
    if rated_module_power is not None:
        module_rated_power = rated_module_power

    if rated_array_power_dc is not None:
        dc_capacity = rated_array_power_dc

    site = make_site_design(
        structure_type='tracker',
        axis_height=axis_height,
        axis_azimuth=axis_azimuth,
        axis_tilt=axis_tilt,
        max_tracking_angle=max_tracking_angle,
        night_stow_angle=night_stow_angle,
        backtracking=backtracking,
        rated_module_power=module_rated_power,
        rated_array_power_dc=dc_capacity,
        dc_ac_ratio=dc_ac_ratio,
        module_placement=module_placement,
        grid_limit=grid_limit,
        ground_cover_ratio=ground_cover_ratio,
        strings_per_inverter=strings_per_inverter,
        modules_per_string=modules_per_string,
        **kwargs,
    )
    return site
