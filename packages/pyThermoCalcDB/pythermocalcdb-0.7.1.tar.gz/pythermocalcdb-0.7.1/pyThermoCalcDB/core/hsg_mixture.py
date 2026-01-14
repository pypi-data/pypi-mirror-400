# import libs
import logging
from typing import Optional, List, Dict, Literal, cast, Any
from pythermodb_settings.models import Temperature, Pressure, Component, CustomProp, ComponentKey
from pythermodb_settings.utils import set_component_id
import pycuc
from pyThermoLinkDB.thermo import Source
from pyThermoLinkDB.models.component_models import ComponentEquationSource
# locals
from .hsg_properties import HSGProperties
from ..utils.component_tools import map_state_to_phase

# NOTE: set up logger
logger = logging.getLogger(__name__)


class HSGMixture:
    """
    Class to represent a mixture of components and calculate its thermodynamic properties using HSG method.

    This class provides thermodynamic property calculations for multi-component mixtures using the HSG
    (Heat capacity, entropy, and Gibbs energy) methodology. It aggregates component properties and
    enables mixture-level calculations with support for custom departure and excess contributions.

    Methods
    -------
    _components_hsg_properties()
        Private method to initialize HSGProperties instances for all mixture components.
    calc_mixture_enthalpy(temperature, phase, departure_enthalpy, excess_enthalpy)
        Calculate the mixture enthalpy (J/mol) at a given temperature and phase with optional contributions.
    """

    def __init__(
        self,
        components: List[Component],
        source: Source,
        component_key: ComponentKey,
    ):
        """
        Initialize the HSGMixture with a list of components and optional custom properties.

        Parameters
        ----------
        components : List[Component]
            A list of Component objects representing the mixture components.
        source : Source
            The Source object representing the data source for the components.
        component_key : Literal[...], optional
            The key to identify components, by default 'Name-State'.
        """
        # NOTE: set attributes
        self.components = components
        self.source = source
        self.component_key = component_key

        # SECTION: set component IDs
        self.component_ids = [
            set_component_id(
                component=component,
                component_key=cast(ComponentKey, self.component_key)
            )
            for component in self.components
        ]

        # NOTE: mole fraction components
        self.mole_fractions = [
            c.mole_fraction for c in self.components
        ]

        # NOTE: state components
        self.states = [
            c.state for c in self.components
        ]

        # SECTION: hsg properties instances
        self.hsg_properties = self._components_hsg_properties()

    def _components_hsg_properties(self) -> Dict[str, HSGProperties]:
        """
        Get the HSGProperties instances for all components in the mixture.

        Returns
        -------
        Dict[str, HSGProperties]
            A dictionary mapping component IDs to their corresponding HSGProperties instances.
        """
        try:
            # NOTE: initialize hsg properties dict
            hsg_properties = {}

            # SECTION: build hsg properties for components
            for component_id, component in zip(self.component_ids, self.components):
                if component_id not in hsg_properties:
                    hsg_properties[component_id] = HSGProperties(
                        component=component,
                        source=self.source,
                        component_key=cast(ComponentKey, self.component_key)
                    )

            # >> hsg properties
            return hsg_properties
        except Exception as e:
            logger.error(
                f"Error in getting HSG properties for components: {e}")
            return {}

    def calc_mixture_enthalpy(
            self,
            temperature: Temperature,
            reference: Literal['IG', 'None'] = 'IG',
            departure_enthalpy: Optional[CustomProp] = None,
            excess_enthalpy: Optional[CustomProp] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate the mixture enthalpy (J/mol) at a given temperature (K) and pressure for specified phase.

        The mixture enthalpy is calculated by summing the contributions from each component based on their mole fractions
        and phase-specific enthalpy values. Optional departure and excess enthalpy contributions can be included in the calculation.

        The reference state can be specified as 'IG' (ideal gas) or 'None' (no reference). The 'IG' reference state is commonly used to calculate enthalpy while the ideal-gas state at 298.15 K and 1 atm is used as the baseline. The 'None' reference state calculates absolute enthalpy values without referencing to a specific state. This means that the enthalpy values are calculated directly based on the defined enthalpy of formation and heat capacity equations for each phase.

        Parameters
        ----------
        temperature : Temperature
            The temperature of the mixture.
        reference : Literal['IG', 'None'], optional
            The reference state for enthalpy calculation, by default 'IG'.
        departure_enthalpy : Optional[CustomProp], optional
            The departure enthalpy contribution, by default None.
        excess_enthalpy : Optional[CustomProp], optional
            The excess enthalpy contribution, by default None.

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing the mixture enthalpy value and unit, or None if calculation fails.

        Notes
        -----
        - This method calculates the mixture enthalpy based on the specified phase and contributions.
        - The calculation may involve ideal and non-ideal contributions depending on the phase.
        - The result is provided in J/mol.
        - R is the universal gas constant (8.3145 J/mol.K).
        - Global reference is ideal gas state at 298.15 K and 1 atm, and all elements are in their standard states (embedded in EnFo).

        Equations
        ---------
        - The mixture enthalpy is calculated using the formula:
            H_mix = Σ(x_i * H_i) + H_departure + H_excess

        where H_departure and H_excess are optional contributions, and scalar values.

        H_i for each component is calculated based on the phase, in case of unavailability of the H_LIQ and H_SOL are requested, the following relations are used:

        - ideal gas enthalpy (H_IG) is calculated as:
            H_IG(T) = ΔH_f(T) + ∫(Cp_IG dT) from 298.15 K to T

        - liquid enthalpy (H_LIQ) is calculated as:
            H_LIQ(T) = H_IG(T) - ΔH_vap(T)

        - solid enthalpy (H_SOL) is calculated as (not implemented):
            H_SOL(T) = H_IG(T) - ΔH_vap(T) - ΔH_fusion(T)
        """
        try:
            # SECTION: calculate mixture enthalpy
            mixture_enthalpy_value = 0.0

            # NOTE: loop through components
            for component_id, mole_fraction, state in zip(
                self.component_ids,
                self.mole_fractions,
                self.states
            ):
                # ! determine phase based on component state
                phase = map_state_to_phase(
                    state=state
                )

                # Explicitly cast phase to Literal['IG', 'LIQ', 'SOL']
                phase_literal = cast(Literal['IG', 'LIQ', 'SOL'], phase)

                # ! get component hsg properties
                hsg_prop = self.hsg_properties.get(component_id)
                if hsg_prop is None:
                    logger.error(
                        f"HSG properties not found for component ID: {component_id}")
                    return None

                # NOTE: calculate phase enthalpy for component
                # ! [J/mol]
                # >> check reference
                # ! reference 'IG' uses phase enthalpy calculation
                # ! reference 'None' uses absolute enthalpy calculation
                if reference == 'IG':
                    component_enthalpy = hsg_prop.calc_reference_enthalpy(
                        temperature=temperature,
                        phase=phase_literal
                    )
                elif reference == 'None':
                    component_enthalpy = hsg_prop.calc_enthalpy(
                        temperature=temperature,
                        phase=phase_literal
                    )
                else:
                    logger.error(
                        f"Invalid reference state: {reference} for component ID: {component_id}")
                    return None

                # >> check if calculation was successful
                if component_enthalpy is None:
                    logger.error(
                        f"Failed to calculate enthalpy for component ID: {component_id}")
                    return None

                # NOTE: accumulate mixture enthalpy
                # ! [J/mol]
                mixture_enthalpy_value += mole_fraction * component_enthalpy.value

            # SECTION: add departure and excess enthalpy contributions if provided
            # NOTE: departure enthalpy
            if departure_enthalpy is not None:
                # get departure enthalpy value
                val_ = departure_enthalpy.value
                unit_ = departure_enthalpy.unit

                # ! [J/mol]
                if unit_ != 'J/mol':
                    # >> convert to J/mol
                    val_ = pycuc.convert_from_to(
                        value=val_,
                        from_unit=unit_,
                        to_unit='J/mol'
                    )

                mixture_enthalpy_value += val_

            # NOTE: excess enthalpy
            if excess_enthalpy is not None:
                # get excess enthalpy value
                val_ = excess_enthalpy.value
                unit_ = excess_enthalpy.unit

                # ! [J/mol]
                if unit_ != 'J/mol':
                    # >> convert to J/mol
                    val_ = pycuc.convert_from_to(
                        value=val_,
                        from_unit=unit_,
                        to_unit='J/mol'
                    )

                mixture_enthalpy_value += val_

            return {
                'value': mixture_enthalpy_value,
                'unit': 'J/mol'
            }
        except Exception as e:
            logger.error(
                f"Error calculating mixture enthalpy: {e}")
            return None
