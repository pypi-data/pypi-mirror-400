# import libs
import logging
from typing import Optional, List, Dict, Literal, cast, Any
from pythermodb_settings.models import Temperature, Pressure, Component, CustomProp, ComponentKey
from math import exp
from pythermodb_settings.utils import set_component_id, set_components_state
import pycuc
from pyThermoLinkDB.thermo import Source
from pyreactlab_core.models.reaction import Reaction
# locals
from .hsg_properties import HSGProperties
from ..utils.component_tools import (
    map_component_state, map_state_to_phase
)
from ..configs.constants import (
    R_J_molK,
    T_ref_K,
)

# NOTE: logger setup
logger = logging.getLogger(__name__)


class HSGReaction:
    """
    HSGReaction class to handle chemical reactions using HSG properties. It is used to calculate thermodynamic properties of reactions based on the HSG method as:
    - Standard Enthalpy of reaction
    - Phase Enthalpy of reaction
    - Standard Gibbs free energy of reaction

    Methods
    -------
    - calc_standard_rxn_enthalpy(temperature: Temperature) -> Optional[Dict[str, Any]]:
        Calculate the standard enthalpy of reaction at the specified temperature.
    - calc_phase_reaction_enthalpy(temperature: Temperature, rxn_departure_enthalpy: Optional[CustomProp] = None, rxn_excess_enthalpy: Optional[CustomProp] = None) -> Optional[Dict[str, Any]]:
        Calculate the phase (actual) enthalpy of reaction at the specified temperature, considering departure and excess enthalpies if provided.
    - calc_standard_rxn_gibbs_energy(temperature: Temperature) -> Optional[Dict
        Calculate the standard Gibbs free energy of reaction at the specified temperature.

    Notes
    -----
    Key Reaction attributes:
    - reaction : str
        The reaction equation string (e.g., "CO2(g) + 3H2(g) => CH3OH(g) + H2O(g)")
    - reactants : List[Dict]
        List of reactant dictionaries with coefficient, molecule, state, and molecule_state
    - products : List[Dict]
        List of product dictionaries with coefficient, molecule, state, and molecule_state
    - reaction_coefficients : float
        Overall stoichiometric coefficients
    - reaction_stoichiometry : Dict[str, float]
        Stoichiometric coefficients for each component (negative for reactants, positive for products)
    - state_count : Dict[str, int]
        Count of components in each state (g, l, aq, s)
    - reaction_phase : str
        Primary phase of the reaction (e.g., 'gas', 'liquid')
    - reaction_state : Dict[str, str]
        State of each component in the reaction
    - reactants_names : List[str]
        List of reactant component IDs
    - products_names : List[str]
        List of product component IDs
    """
    # SECTION: Attributes
    # NOTE: component key
    # ! used where to consider component state
    _component_key: ComponentKey = 'Formula-State'

    # ! ignore component state
    _standard_component_key: ComponentKey = 'Name-Formula'

    # NOTE: universal gas constant [J/mol.K]
    __R: float = R_J_molK
    # NOTE: reference temperature [K]
    __T_Ref_K: float = T_ref_K

    def __init__(
        self,
        reaction: Reaction,
        source: Source,
    ):
        """
        Initialize the HSGMixture with a list of components and optional custom properties.

        Parameters
        ----------
        reaction : Reaction
            The Reaction object representing the chemical reaction.
        source : Source
            The Source object representing the data source for the components.
        """
        # NOTE: set attributes
        self.reaction = reaction
        self.source = source

        # SECTION: set components
        self.components = reaction.available_components
        # checker
        if reaction.component_checker is False:
            raise ValueError(
                "Some components in the reaction are not available in the provided components list."
            )

        # NOTE: standard components
        self.standard_components = set_components_state(
            components=self.components,
            state='g'
        )

        # NOTE: map components
        self.map_components = reaction.map_components

        # SECTION: set component IDs
        self.component_ids = [
            set_component_id(
                component=component,
                component_key=self._component_key
            )
            for component in self.components
        ]

        self.standard_component_ids = [
            set_component_id(
                component=component,
                component_key='Name-Formula'
            )
            for component in self.components
        ]

        # NOTE: set component phase states
        self.component_states = [
            comp.state for comp in self.components
        ]

        # NOTE: mole fraction components
        self.mole_fractions = [
            c.mole_fraction for c in self.components
        ]

        # SECTION: hsg properties instances
        self.hsg_properties = self._components_hsg_properties()

        # SECTION: hsg properties instances for standard states
        self.standard_hsg_properties = self._components_hsg_properties(
            search_mode='standard'
        )

    def _components_hsg_properties(
            self,
            search_mode: Literal['standard', 'original'] = 'original'
    ) -> Dict[str, HSGProperties]:
        """
        Get the HSGProperties instances for all components in the mixture.

        Returns
        -------
        Dict[str, HSGProperties]
            A dictionary mapping component IDs to their corresponding HSGProperties instances.
        """
        try:
            # SECTION: select components by state
            # NOTE: initialize components source
            components_src: List[Component] = []
            component_ids_src: List[str] = []

            # NOTE: select components
            # ! components
            # ! component ids
            # ! component key

            # >> component ids source
            if search_mode == 'standard':
                components_src = self.standard_components
                component_ids_src = self.standard_component_ids
                component_key_src = self._standard_component_key
            elif search_mode == 'original':
                components_src = self.components
                component_ids_src = self.component_ids
                component_key_src = self._component_key
            else:
                raise ValueError(
                    f"Invalid mode '{search_mode}'. Supported modes are 'standard' and 'original'."
                )

            # SECTION: Retrieve components source
            # NOTE: initialize hsg properties dict
            hsg_properties = {}

            # SECTION: build hsg properties for components
            for component_id, component in zip(component_ids_src, components_src):

                # >> check if component already processed
                if component_id not in hsg_properties:
                    # get hsg properties
                    hsg_properties[component_id] = HSGProperties(
                        component=component,
                        source=self.source,
                        component_key=component_key_src
                    )

            # >> hsg properties
            return hsg_properties
        except Exception as e:
            logger.error(
                f"Error in getting HSG properties for components: {e}")
            return {}

    def calc_standard_rxn_enthalpy(
        self,
        temperature: Temperature,
    ) -> Optional[CustomProp]:
        """
        Calculate the `standard enthalpy of reaction` at the specified temperature and pressure using HSG properties.

            dH_rxn = Σ(ν_i * H_IG(T))

        The reference state is ideal gas at 298.15 K and 1 atm. The enthalpy of each component is calculated with respect to this reference state. However, no departure or excess enthalpy contributions are considered in this standard calculation. This method does not use the second approach of calculating standard enthalpy of reaction based on component states (liquid, solid).

        Parameters
        ----------
        temperature : Temperature
            The temperature at which to calculate the reaction enthalpy.
        rxn_departure_enthalpy : Optional[CustomProp], optional
            The departure enthalpy of the reaction, by default None.
        rxn_excess_enthalpy : Optional[CustomProp], optional
            The excess enthalpy of the reaction, by default None.

        Returns
        -------
        Optional[CustomProp]
            A dictionary containing the reaction enthalpy and related information, or None if calculation fails.

        Notes
        -----
        - The reaction enthalpy is calculated using the standard enthalpies of formation of the reactants and products.
        - No departure or excess enthalpy contributions are considered in this standard calculation.
        - The result is provided in J/mol.
        - R is the universal gas constant (8.3145 J/mol.K).
        - Global reference is ideal gas state at 298.15 K and 1 atm, and all elements are in their standard states (embedded in dEnFo).

        Equations
        ---------
        For a reaction:
            aA + bB => cC + dD
        - The reaction enthalpy (ΔH_rxn) is calculated as:
            dH_rxn = Σ(ν_i * H_IG(T))

        - ideal gas enthalpy (H_IG) is calculated as:
            H_IG(T) = ΔH_f(T) + ∫(Cp_IG dT) from 298.15 K to T

        When H_IG is not available, the following approximations are used:

        - liquid enthalpy (H_LIQ) is calculated:
            H_LIQ(T) = H_IG(T) - ΔH_vap(T)

        - solid enthalpy (H_SOL) is calculated as (not implemented):
            H_SOL(T) = H_IG(T) - ΔH_vap(T) - ΔH_fusion(T)
        """
        try:
            # NOTE: initialize reaction enthalpy
            reaction_enthalpy = 0.0

            # SECTION: calculate reaction enthalpy
            for component_id, coeff in self.reaction.reaction_stoichiometry.items():
                # NOTE: >> get hsg properties
                # ! gas-phase properties
                # >> reset component id
                # TODO: review this part
                component_ = self.map_components.get(
                    component_id,
                    None
                )
                # >> check component
                if component_ is None:
                    logger.error(
                        f"Component mapping not found for component ID: {component_id}"
                    )
                    return None

                # >> set component id
                component_id_ = set_component_id(
                    component=component_,
                    component_key=self._standard_component_key
                )

                # NOTE: get hsg properties
                # ! standard gas-phase properties
                hsg_prop = self.standard_hsg_properties.get(
                    component_id_,
                    None
                )
                if hsg_prop is None:
                    logger.error(
                        f"Gas-phase HSG properties not found for component ID: {component_id}"
                    )
                    return None

                # ! Cast phase to ideal-gas
                phase = map_state_to_phase(
                    state=component_.state
                )

                # >> calculate component enthalpy
                # NOTE: calculate phase enthalpy
                # ! [J/mol]
                # ! ideal-gas reference
                component_enthalpy = hsg_prop.calc_reference_enthalpy(
                    temperature=temperature,
                    phase=cast(Literal['IG', 'LIQ', 'SOL'], phase),
                )
                # >> check component enthalpy
                if component_enthalpy is None:
                    raise ValueError(
                        f"Failed to calculate enthalpy for component ID: {component_id}"
                    )

                # >> accumulate reaction enthalpy
                reaction_enthalpy += coeff * component_enthalpy.value

            # >> return reaction enthalpy
            res = {
                'value': reaction_enthalpy,  # J/mol
                'unit': 'J/mol'
            }
            res = CustomProp(**res)

            return res
        except Exception as e:
            logger.error(f"Error in calculating reaction enthalpy: {e}")
            return None

    def calc_actual_rxn_enthalpy(
        self,
        temperature: Temperature,
        rxn_departure_enthalpy: Optional[CustomProp] = None,
        rxn_excess_enthalpy: Optional[CustomProp] = None,
    ) -> Optional[CustomProp]:
        """
        Calculate the `phase (actual) enthalpy of reaction` at the specified temperature and pressure using HSG properties.

            dH_rxn = Σ(ν_i * H_IG(T)) + rxn_departure_enthalpy + rxn_excess_enthalpy

        Parameters
        ----------
        temperature : Temperature
            The temperature at which to calculate the reaction enthalpy.
        rxn_departure_enthalpy : Optional[CustomProp], optional
            The departure enthalpy of the reaction, by default None.
        rxn_excess_enthalpy : Optional[CustomProp], optional
            The excess enthalpy of the reaction, by default None.

        Returns
        -------
        Optional[CustomProp]
            A dictionary containing the reaction enthalpy and related information, or None if calculation fails.

        Notes
        -----
        - The reaction enthalpy is calculated using the standard enthalpies of formation of the reactants and products, adjusted for departure and excess enthalpies if provided.
        - departure_enthalpy is added directly to the reaction enthalpy.
        - excess_enthalpy is also added directly to the reaction enthalpy.
        - The calculation may involve ideal and non-ideal contributions depending on the phase.
        - The result is provided in J/mol.
        - R is the universal gas constant (8.3145 J/mol.K).
        - Global reference is ideal gas state at 298.15 K and 1 atm, and all elements are in their standard states (embedded in dEnFo).

        Equations
        ---------
        For a reaction:
            aA + bB => cC + dD
        - The reaction enthalpy (ΔH_rxn) is calculated as:
            dH_rxn = Σ(ν_i * H_IG(T)) + Σ(ν_i * departure_enthalpy) + Σ(ν_i * excess_enthalpy)

        - ideal gas enthalpy (H_IG) is calculated as:
            H_IG(T) = ΔH_f(T) + ∫(Cp_IG dT) from 298.15 K to T

        - liquid enthalpy (H_LIQ) is calculated as:
            H_LIQ(T) = H_IG(T) - ΔH_vap(T)

        - solid enthalpy (H_SOL) is calculated as (not implemented):
            H_SOL(T) = H_IG(T) - ΔH_vap(T) - ΔH_fusion(T)
        """
        try:
            # NOTE: initialize reaction enthalpy
            reaction_enthalpy = 0.0

            # SECTION: calculate reaction enthalpy
            for component_id, coeff in self.reaction.reaction_stoichiometry.items():
                # >> get hsg properties
                hsg_prop = self.hsg_properties.get(component_id, None)
                if hsg_prop is None:
                    logger.error(
                        f"HSG properties not found for component ID: {component_id}"
                    )
                    return None

                # NOTE: get component state
                component_state = self.reaction.reaction_state.get(
                    component_id,
                    None
                )
                if component_state is None:
                    logger.warning(
                        f"Component state not found for component ID: {component_id}. Using default state from component."
                    )
                    return None

                # ! >> map component state
                phase_str = map_component_state(
                    component=hsg_prop.component
                )
                # Cast phase to Literal['IG', 'LIQ', 'SOL']
                phase = cast(Literal['IG', 'LIQ', 'SOL'], phase_str)

                # >> calculate component enthalpy
                # NOTE: calculate phase enthalpy
                # ! [J/mol]
                component_enthalpy = hsg_prop.calc_reference_enthalpy(
                    temperature=temperature,
                    phase=phase,
                )
                # >> check component enthalpy
                if component_enthalpy is None:
                    raise ValueError(
                        f"Failed to calculate enthalpy for component ID: {component_id}"
                    )

                # >> accumulate reaction enthalpy
                reaction_enthalpy += coeff * component_enthalpy.value

            # SECTION: add departure and excess enthalpy contributions if provided
            # NOTE: departure enthalpy
            if rxn_departure_enthalpy is not None:
                # get departure enthalpy value
                val_ = rxn_departure_enthalpy.value
                unit_ = rxn_departure_enthalpy.unit

                # ! [J/mol]
                if unit_ != 'J/mol':
                    # >> convert to J/mol
                    val_ = pycuc.convert_from_to(
                        value=val_,
                        from_unit=unit_,
                        to_unit='J/mol'
                    )

                reaction_enthalpy += val_

            # NOTE: excess enthalpy
            if rxn_excess_enthalpy is not None:
                # get excess enthalpy value
                val_ = rxn_excess_enthalpy.value
                unit_ = rxn_excess_enthalpy.unit

                # ! [J/mol]
                if unit_ != 'J/mol':
                    # >> convert to J/mol
                    val_ = pycuc.convert_from_to(
                        value=val_,
                        from_unit=unit_,
                        to_unit='J/mol'
                    )

                reaction_enthalpy += val_

            # >> return reaction enthalpy
            res = {
                'value': reaction_enthalpy,  # J/mol
                'unit': 'J/mol'
            }
            res = CustomProp(**res)

            return res
        except Exception as e:
            logger.error(f"Error in calculating reaction enthalpy: {e}")
            return None

    def calc_standard_rxn_gibbs_free_energy(
        self,
        temperature: Temperature,
    ) -> Optional[CustomProp]:
        """
        Calculate the `standard Gibbs free energy of reaction` at the specified temperature and pressure using HSG properties.

            dG_rxn = Σ(ν_i * GiEnFo_IG(T))

        Parameters
        ----------
        temperature : Temperature
            The temperature at which to calculate the reaction Gibbs free energy.

        Returns
        -------
        Optional[CustomProp]
            A dictionary containing the reaction Gibbs free energy and related information, or None if calculation fails.

        Notes
        -----
        - The reaction Gibbs free energy is calculated using the standard Gibbs free energies of formation of the reactants and products.
        - The result is provided in J/mol.
        - R is the universal gas constant (8.3145 J/mol.K).
        - Global reference is ideal gas state at 298.15 K and 1 atm, and all elements are in their standard states (embedded in dGf).

        Equations
        ---------
        For a reaction:
            aA + bB => cC + dD
        - The reaction Gibbs free energy (ΔG_rxn) is calculated as:
            dG_rxn = Σ(ν_i * GiEnFo_IG(T))

        - ideal gas Gibbs free energy (GiEnFo_IG) is calculated as:
            GiEnFo_IG(T) = EnFo_f(T) + ∫(Cp_IG dT) - T * ∫(Cp_IG/T dT) from 298.15 K to T
        """
        try:
            # NOTE: initialize reaction Gibbs free energy
            reaction_gibbs_energy = 0.0

            # SECTION: calculate reaction Gibbs free energy
            for component_id, coeff in self.reaction.reaction_stoichiometry.items():
                # NOTE: >> get hsg properties
                # ! >> reset component id
                # TODO: review this part
                component_ = self.map_components.get(
                    component_id,
                    None
                )
                # >> check component
                if component_ is None:
                    logger.error(
                        f"Component mapping not found for component ID: {component_id}"
                    )
                    return None

                # >> set component id
                component_id_ = set_component_id(
                    component=component_,
                    component_key=self._standard_component_key
                )

                # NOTE: get hsg properties
                # ! standard gas-phase properties
                hsg_prop = self.standard_hsg_properties.get(
                    component_id_,
                    None
                )
                if hsg_prop is None:
                    logger.error(
                        f"HSG properties not found for component ID: {component_id}"
                    )
                    return None

                # >> calculate component Gibbs free energy
                # NOTE: calculate phase Gibbs free energy
                # ! [J/mol]
                component_gibbs_energy = hsg_prop.calc_gibbs_free_energy(
                    temperature=temperature,
                    phase='IG',
                )
                # >> check component Gibbs free energy
                if component_gibbs_energy is None:
                    logger.error(
                        f"Failed to calculate Gibbs free energy for component ID: {component_id}"
                    )
                    return None

                # >> accumulate reaction Gibbs free energy
                reaction_gibbs_energy += coeff * component_gibbs_energy.value

            # >> return reaction Gibbs free energy
            res = {
                'value': reaction_gibbs_energy,  # J/mol
                'unit': 'J/mol'
            }
            res = CustomProp(**res)

            return res
        except Exception as e:
            logger.error(
                f"Error in calculating reaction Gibbs free energy: {e}"
            )
            return None

    def calc_equilibrium_constant_STD(
        self,
        temperature: Temperature,
        **kwargs
    ) -> Optional[CustomProp]:
        '''
        Calculates the standard equilibrium constant of a reaction at a given temperature which defined as:
            Keq_std = exp(-ΔG_rxn_std / (R * T))

        Parameters
        ----------
        temperature : Temperature
            The temperature at which to calculate the equilibrium constant.
        kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Optional[CustomProp]
            A dictionary containing the equilibrium constant at the given temperature [dimensionless].
        '''
        try:
            # NOTE: >> calculate standard Gibbs free energy of reaction
            # ! [J/mol]
            dG_rxn_std = self.calc_standard_rxn_gibbs_free_energy(
                temperature=temperature,
            )
            if dG_rxn_std is None:
                raise ValueError(
                    "Failed to calculate standard Gibbs free energy of reaction."
                )

            # NOTE: temperature
            # ! [K]
            T_value = temperature.value
            T_unit = temperature.unit
            if T_unit != 'K':
                T_value = pycuc.convert_from_to(
                    value=T_value,
                    from_unit=T_unit,
                    to_unit='K'
                )

            # SECTION: equilibrium constant at standard conditions
            Ka = HSGReaction.vh(
                gibbs_energy_of_reaction_std=dG_rxn_std.value,
                temperature=T_value,
            )

            # ? save
            return Ka
        except Exception as e:
            logger.error(
                f"Error in ReactionAnalyzer.calc_equilibrium_constant_STD(): {str(e)}")
            return None

    @staticmethod
    def vh(
        gibbs_energy_of_reaction_std: float,
        temperature: float,
        **kwargs
    ) -> Optional[CustomProp]:
        '''
        Calculates change in Gibbs free energy of a reaction at different temperatures using the Van't Hoff equation as:
            Keq = exp(-ΔG_rxn_std / (R * T))

        Parameters
        ----------
        gibbs_energy_of_reaction_std : float
            Standard Gibbs free energy of reaction at reference temperature [J/mol].
        temperature : float
            The temperature [K] at which to calculate Gibbs energy.
        kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Optional[CustomProp]
            A dictionary containing the equilibrium constant at the given temperature [dimensionless].
        '''
        try:
            # SECTION: equilibrium constant at temperature T
            Ka = exp(
                -1*gibbs_energy_of_reaction_std /
                (HSGReaction.__R*temperature)
            )
            # ? save
            res = {
                'value': float(Ka),
                'unit': 'dimensionless',
            }
            res = CustomProp(**res)
            return res
        except Exception as e:
            logger.error(
                f"Error in ReactionAnalyzer.vh(): {str(e)}")
            return None

    @staticmethod
    def vh_shortcut(
        enthalpy_of_reaction_std: float,
        equilibrium_constant_std: float,
        temperature: float,
        **kwargs
    ) -> Optional[CustomProp]:
        """
        Shortcut for Van't Hoff equation to calculate equilibrium constant at different temperatures as:
            Keq = Keq_std * exp( (-ΔH_rxn_std / R) * (1/T - 1/T_ref) )

        where, Keq_std is the equilibrium constant at standard conditions (T_ref), and ΔH_rxn_std is the enthalpy of reaction at standard conditions.
        Tref is set to 298.15 K.

        Parameters
        ----------
        enthalpy_of_reaction_std : float
            Enthalpy of reaction at standard conditions [J/mol].
        equilibrium_constant_std : float
            Equilibrium constant at standard conditions [dimensionless].
        temperature : float
            The temperature [K] at which to calculate Gibbs energy.
        kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Optional[CustomProp]
            A dictionary containing the equilibrium constant at the given temperature [dimensionless].
        """
        try:
            # NOTE: calculate equilibrium constant at temperature T
            A = (-1*enthalpy_of_reaction_std/HSGReaction.__R) * \
                (1/temperature - 1/HSGReaction.__T_Ref_K)
            Ka = equilibrium_constant_std*exp(A)

            # res
            res = {
                'value': float(Ka),
                'unit': 'dimensionless',
            }
            res = CustomProp(**res)
            return res
        except Exception as e:
            logger.error(
                f"Error in ReactionAnalyzer.vh_shortcut(): {str(e)}")
            return None
