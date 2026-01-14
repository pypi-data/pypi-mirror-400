# import libs
import logging
import math
from typing import Dict, Any, Literal, Optional, List
from pythermodb_settings.models import Component, Temperature, Pressure, CustomProp, ComponentKey
from pythermodb_settings.utils import set_component_id
import pycuc
from pyThermoLinkDB.thermo import Source
from pyThermoLinkDB.models.component_models import ComponentEquationSource
# local
from ..configs.thermo_props import (
    EnFo_IG_UNIT,
    EnFo_LIQ_UNIT,
    EnFo_SOL_UNIT,
    Ent_STD_UNIT,
    GiEnFo_IG_UNIT,
    GiEnFo_LIQ_UNIT,
    GiEnFo_SOL_UNIT,
    EnFo_IG_SYMBOL,
    EnFo_LIQ_SYMBOL,
    EnFo_SOL_SYMBOL,
    GiEnFo_IG_SYMBOL,
    GiEnFo_LIQ_SYMBOL,
    GiEnFo_SOL_SYMBOL,
    Ent_STD_SYMBOL,
    En_IG_SYMBOL,
    En_LIQ_SYMBOL,
    En_SOL_SYMBOL,
    Cp_IG_SYMBOL,
    Cp_LIQ_SYMBOL,
    Cp_SOL_SYMBOL,
    Cp_IG_UNIT,
    Cp_LIQ_UNIT,
    Cp_SOL_UNIT,
    EnVap_SYMBOL,
    EnVap_UNIT,
    EnSub_SYMBOL,
    EnSub_UNIT
)
from .calc import (
    Cp_integral,
    Cp__RT_integral,
    Cp__T_integral,
    calc_eq
)
from ..models import (
    ComponentEnthalpy,
    ComponentGibbsFreeEnergy,
    ComponentEnthalpyChange,
    ComponentEntropyChange,
    ComponentHeatOfVaporization,
    ComponentHeatOfSublimation
)

# NOTE: Logger
logger = logging.getLogger(__name__)


class HSGProperties:
    """
    HSG Properties class to calculate enthalpy and entropy of formation, and Gibbs free energy of formation for a given compound.

    Notes
    -----
    - HSG stands for Enthalpy (H), Entropy (S), and Gibbs free energy (G).
    - This class uses component data and equations from a specified source to perform calculations.
    - Heat capacity equations are used to calculate temperature-dependent properties and should have units in J/mol.K for accurate results.
    - All enthalpy and Gibbs energy results are provided in J/mol.
    - Reference temperature is set to 298.15 K.
    - The Gibbs free energy of formation symbol must be consistent with the defined unit in the configuration which is GiEnFo_IG.
    - Enthalpy of formation symbols must be consistent with their defined units in the configuration (EnFo_IG_UNIT, EnFo_LIQ_UNIT) for liquid and ideal gas phases respectively.

    Equations
    ---------
    - Enthalpy change is calculated by integrating the heat capacity equation from T1 to T2.
    - Enthalpy of formation at temperature T is calculated as:
        `ΔH(T) = ΔH(298.15 K) + ∫[Cp dT]` from 298.15 K to T
    - Gibbs free energy of formation at temperature T is calculated as:
        `ΔG(T) = ΔH(T) - T * ΔS(T)`
    where ΔS(T) is derived from the heat capacity equations.
    - All integrals are evaluated using the heat capacity equations provided in the source.
    - Heat capacity equation is defined as Cp = f(T) with units in J/mol.K.
    - Integration of Cp over temperature yields enthalpy changes in J/mol.
    - Integration of Cp/RT over temperature is used in Gibbs energy calculations.
    - Evaporation and sublimation enthalpies can be calculated if the respective equations are provided in the source.
    - Both evaporation and sublimation enthalpy equations are defined as functions of temperature with units in J/mol as:
        EnVap = f(T)  and  EnSub = f(T)
    """
    # NOTE: attributes
    # reference temperature in K
    T_ref = 298.15
    # universal gas constant in J/mol.K
    R = 8.3145

    def __init__(
        self,
        component: Component,
        source: Source,
        component_key: ComponentKey,
    ) -> None:
        """
        Initialize HSGProperties with a component and source.

        Parameters
        ----------
        component : Component
            The chemical component for which HSG properties are to be calculated, it consists of the following attributes:
                - name: str
                - formula: str
                - state: str
                - mole_fraction: float, optional
        source : Source
            The source containing data for calculations.
        component_key : Literal
            The key to identify the component in the source data. Defaults to 'Name-State'.
        """
        # NOTE: component
        self.component = component
        # NOTE: source
        self.source = source
        # NOTE: component key
        self.component_key = component_key

        # >> set component id
        self.component_id = set_component_id(
            component=self.component,
            component_key=self.component_key
        )

        # SECTION: extract component source
        self.component_source = self.source.get_component_data(
            component_id=self.component_id,
            components=[self.component],
        )

        # SECTION: retrieve heat capacity equation source
        # NOTE: ideal gas heat capacity equation source
        self.Cp_IG_eq_src = self._get_Cp_equation_source(
            phase='IG'
        )

        # NOTE: liquid heat capacity equation source
        self.Cp_LIQ_eq_src = self._get_Cp_equation_source(
            phase='LIQ'
        )

        # NOTE: solid heat capacity equation source
        self.Cp_SOL_eq_src = self._get_Cp_equation_source(
            phase='SOL'
        )

        # SECTION: retrieve other necessary data if needed
        # NOTE: enthalpy of vaporization equation source
        self.EnVap_eq_src = self._get_equation_source(
            prop_name=EnVap_SYMBOL
        )

        # NOTE: enthalpy of sublimation equation source
        self.EnSub_eq_src = self._get_equation_source(
            prop_name=EnSub_SYMBOL
        )

    def _get_formation_data(
            self,
            prop_name: str
    ) -> Optional[Dict[str, Any]]:
        '''
        Retrieve formation data for the specified property.

        Parameters
        ----------
        prop_name : str
            The name of the property for which formation data is to be retrieved.

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing the formation data if available, otherwise None.
        '''
        try:
            res = self.source.data_extractor(
                component_id=self.component_id,
                prop_name=prop_name,
            )

            return res
        except Exception as e:
            logger.exception(
                f"Error retrieving formation data for {prop_name}: {e}")
            return None

    def _get_Cp_equation_source(
            self,
            phase: Literal['IG', 'LIQ', 'SOL']
    ) -> Optional[ComponentEquationSource]:
        '''
        Retrieve the heat capacity equation source for the component.

        Parameters
        ----------
        phase : Literal['IG', 'LIQ', 'SOL']
            The phase of the component ('IG' for ideal gas, 'LIQ' for liquid).

        Returns
        -------
        Optional[ComponentEquationSource]
            The heat capacity equation source if available, otherwise None.
        '''
        try:
            # NOTE: select symbol based on phase
            if phase == 'IG':
                Cp_symbol = Cp_IG_SYMBOL
            elif phase == 'LIQ':
                Cp_symbol = Cp_LIQ_SYMBOL
            elif phase == 'SOL':
                Cp_symbol = Cp_SOL_SYMBOL
            else:
                raise ValueError(
                    f"Invalid phase: {phase}. Must be 'IG' or 'LIQ'.")

            # NOTE: build equation
            Cp_eq_src = self.source.eq_builder(
                components=[self.component],
                prop_name=Cp_symbol,
                component_key=self.component_key  # type: ignore
            )

            # >> check Cp equation
            if Cp_eq_src is None:
                logger.warning(
                    f"No heat capacity equation available for component {self.component_id}.")
                return None

            # >> for component
            component_Cp_eq_src: ComponentEquationSource | None = Cp_eq_src.get(
                self.component_id
            )

            if component_Cp_eq_src is None:
                logger.warning(
                    f"No heat capacity equation available for component {self.component_id}.")
                raise ValueError("No heat capacity equation source found.")

            return component_Cp_eq_src
        except Exception as e:
            logger.exception(
                f"Error retrieving heat capacity equation source: {e}")
            raise

    def _get_equation_source(
            self,
            prop_name: str
    ) -> Optional[ComponentEquationSource]:
        '''
        Retrieve the equation source for the specified property.

        Parameters
        ----------
        prop_name : str
            The name of the property for which the equation source is to be retrieved.

        Returns
        -------
        Optional[ComponentEquationSource]
            The equation source if available, otherwise None.
        '''
        try:
            # NOTE: build equation
            eq_src = self.source.eq_builder(
                components=[self.component],
                prop_name=prop_name,
                component_key=self.component_key  # type: ignore
            )

            # >> check equation
            if eq_src is None:
                logger.warning(
                    f"No equation available for property {prop_name} for component {self.component_id}.")
                return None

            # >> for component
            component_eq_src: ComponentEquationSource | None = eq_src.get(
                self.component_id
            )

            if component_eq_src is None:
                logger.warning(
                    f"No equation available for property {prop_name} for component {self.component_id}.")
                return None

            return component_eq_src
        except Exception as e:
            logger.exception(
                f"Error retrieving equation source for {prop_name}: {e}")
            raise

    def _calc_enthalpy_change(
            self,
            Cp_eq_src: ComponentEquationSource,
            T1: float,
            T2: float,
    ) -> Optional[float]:
        '''
        Calculate the enthalpy change in (J/mol) between two temperatures using the provided equation source.

        Parameters
        ----------
        Cp_eq_src : ComponentEquationSource
            The equation source for heat capacity.
        T1 : float
            The initial temperature in Kelvin (K).
        T2 : float
            The final temperature in Kelvin (K).

        Returns
        -------
        Optional[float]
            The calculated enthalpy change if successful, otherwise None.

        Notes
        -----
        - The enthalpy change is calculated by integrating the heat capacity equation from T1 to T2.
        - If output_unit is provided, the result will be converted to the specified unit.
        - If output_unit is None, the result will be in the unit defined by the heat capacity equation. This is important because:
        the heat capacity unit is defined, for example, as energy per mole per Kelvin (e.g., J/mol.K), so: the integrated value will be in energy per mole (e.g., J/mol), as a result.
        - heat capacity equation usually return values in `J/mol.K` for correct enthalpy calculation.
        - heat capacity equation integration usually yield values in `J/mol`.
        '''
        try:
            # SECTION: integrate Cp equation from T1 to T2
            # NOTE: output unit is usually `J/mol`
            delta_H = Cp_integral(
                eq_src=Cp_eq_src,
                T_ref=T1,
                T=T2,
                output_unit='J/mol'  # ! specify output unit as J/mol
            )

            # >> check
            if delta_H is None:
                logger.error(
                    f"Failed to calculate enthalpy change from {T1} K to {T2} K.")
                return None

            return float(delta_H['value'])
        except Exception as e:
            logger.exception(
                f"Error calculating enthalpy change from {T1} K to {T2} K: {e}")
            return None

    def calc_enthalpy_change(
            self,
            T1: Temperature,
            T2: Temperature,
            phase: Literal['IG', 'LIQ'] = 'IG',
    ) -> Optional[ComponentEnthalpyChange]:
        '''
        Calculate the enthalpy change in (J/mol) between two temperatures using the provided equation source.

        Parameters
        ----------
        T1 : Temperature
            The initial temperature.
        T2 : Temperature
            The final temperature.
        phase : Literal['IG', 'LIQ']
            The phase of the component ('IG' for ideal gas, 'LIQ' for liquid). Defaults to 'IG'.

        Returns
        -------
        Optional[ComponentEnthalpyChange]
            A ComponentEnthalpyChange object containing the calculated enthalpy change if successful, otherwise None.
        '''
        try:
            # SECTION: convert temperatures to K if necessary
            T1_val = T1.value
            T1_unit = T1.unit
            if T1_unit != 'K':
                T1_val = pycuc.to(
                    T1_val,
                    f"{T1_unit} => K"
                )

            T2_val = T2.value
            T2_unit = T2.unit
            if T2_unit != 'K':
                T2_val = pycuc.to(
                    T2_val,
                    f"{T2_unit} => K"
                )

            # SECTION: calculate enthalpy change
            # NOTE: check Cp equation source
            if phase == 'IG':
                if self.Cp_IG_eq_src is None:
                    logger.error(
                        f"No ideal gas heat capacity equation source available for component {self.component_id}.")
                    return None

                # set
                Cp_eq_src = self.Cp_IG_eq_src
            elif phase == 'LIQ':
                if self.Cp_LIQ_eq_src is None:
                    logger.error(
                        f"No liquid heat capacity equation source available for component {self.component_id}.")
                    return None

                # set
                Cp_eq_src = self.Cp_LIQ_eq_src
            else:
                logger.error(
                    f"Invalid phase: {phase}. Must be 'IG' or 'LIQ'.")
                return None

            # NOTE: calculate enthalpy change
            delta_H_val = self._calc_enthalpy_change(
                Cp_eq_src=Cp_eq_src,
                T1=T1_val,
                T2=T2_val,
            )

            # >> check
            if delta_H_val is None:
                logger.error(
                    f"Failed to calculate enthalpy change between temperatures: {T1_val} K and {T2_val} K.")
                return None

            # >> prepare result
            result = {
                'temperature_initial': T1,
                'temperature_final': T2,
                'phase': phase,
                'value': delta_H_val,
                'unit': 'J/mol',
                'symbol': 'dEn_IG' if phase == 'IG' else 'dEn_LIQ'
            }

            # >> set
            result = ComponentEnthalpyChange(**result)

            return result
        except Exception as e:
            logger.exception(
                f"Error calculating enthalpy change between temperatures: {e}")
            return None

    def calc_enthalpy(
            self,
            temperature: Temperature,
            phase: Literal['IG', 'LIQ', 'SOL'] = 'IG',
    ) -> Optional[ComponentEnthalpy]:
        '''
        Calculate the enthalpy (J/mol) at a given temperature (K) and phase including ideal-gas, liquid, solid.

        Each phase uses its respective enthalpy of formation and heat capacity equations. If the equations for a specific phase are not available, the method will return None for that phase.

        Enthalpy and heat capacity equations symbols must be defined as follows:
        - EnFo_IG for ideal gas phase
        - EnFo_LIQ for liquid phase
        - EnFo_SOL for solid phase
        - Cp_IG for ideal gas heat capacity
        - Cp_LIQ for liquid heat capacity
        - Cp_SOL for solid heat capacity

        Parameters
        ----------
        temperature : Temperature
            The temperature at which to calculate the enthalpy.
        phase : Literal['IG', 'LIQ', 'SOL']
            The phase of the component ('IG' for ideal gas, 'LIQ' for liquid, 'SOL' for solid). Defaults to 'IG'.

        Returns
        -------
        Optional[ComponentEnthalpy]
            A ComponentEnthalpy object containing the calculated enthalpy if successful, otherwise None.
        '''
        try:
            # SECTION: temperature value
            T_val = temperature.value
            T_unit = temperature.unit

            # >> convert temperature to K if necessary
            # ! K
            if T_unit != 'K':
                T_val = pycuc.to(
                    T_val,
                    f"{T_unit} => K"
                )

            # NOTE: get symbol based on phase
            if phase == 'IG':
                # set
                EnFo_SYMBOL = EnFo_IG_SYMBOL
                EnFo_UNIT = EnFo_IG_UNIT
                Cp_eq_src = self.Cp_IG_eq_src
            elif phase == 'LIQ':
                # set
                EnFo_SYMBOL = EnFo_LIQ_SYMBOL
                Cp_eq_src = self.Cp_LIQ_eq_src
                EnFo_UNIT = EnFo_LIQ_UNIT
            elif phase == 'SOL':
                # set
                EnFo_SYMBOL = EnFo_SOL_SYMBOL
                Cp_eq_src = self.Cp_SOL_eq_src
                EnFo_UNIT = EnFo_SOL_UNIT
            else:
                logger.error(
                    f"Invalid phase: {phase}. Must be 'IG' or 'LIQ'.")
                return None

            # >> check Cp equation source
            if Cp_eq_src is None:
                logger.error(
                    f"No heat capacity equation source available for component {self.component_id} in phase {phase}.")
                return None

            # SECTION: get formation data
            # >> enthalpy of formation (EnFo_X) unit ?
            formation_data = self._get_formation_data(EnFo_SYMBOL)

            # >> check formation data
            if formation_data is None:
                logger.warning(
                    f"No formation data available for enthalpy of formation."
                )
                return None

            # NOTE: unit conversion if necessary
            # TODO: convert to [J/mol]
            EnFo_val = formation_data['value']
            EnFo_unit = formation_data['unit']
            # ! to [J/mol]
            unit_ = f"{EnFo_unit} => {EnFo_UNIT}"
            EnFo_IG_val = pycuc.to(
                EnFo_val,
                unit_
            )

            # SECTION: heat capacity calculation
            # NOTE: integrate Cp from T_ref to T
            # ! reference temperature is 298.15 K
            # ! [J/mol]
            delta_Cp_val = self._calc_enthalpy_change(
                Cp_eq_src=Cp_eq_src,
                T1=self.T_ref,
                T2=T_val,
            )

            # >> check
            if delta_Cp_val is None:
                logger.error(
                    f"Failed to integrate Cp equation from T={self.T_ref} K to T={T_val} K.")
                return None

            # SECTION: calculate enthalpy of formation at temperature
            # ! [J/mol]
            EnFo_IG_T_val = EnFo_IG_val + delta_Cp_val

            # SECTION: prepare result
            result_ = {
                'temperature': temperature,
                'value': EnFo_IG_T_val,
                'unit': EnFo_IG_UNIT,
                'symbol': EnFo_IG_SYMBOL
            }

            # >> set
            result = ComponentEnthalpy(**result_)
            return result
        except Exception as e:
            logger.exception(
                f"Error calculating enthalpy of formation: {e}")
            return None

    def calc_enthalpy_range(
            self,
            temperatures: list[Temperature],
            phase: Literal['IG', 'LIQ', 'SOL'] = 'IG',
    ) -> List[ComponentEnthalpy]:
        '''
        Calculate the enthalpy in (J/mol) over a range of temperatures in Kelvin (K).

        Parameters
        ----------
        temperatures : list[Temperature]
            A list of temperatures at which to calculate the enthalpy.
        phase : Literal['IG', 'LIQ', 'SOL']
            The phase of the component ('IG' for ideal gas, 'LIQ' for liquid). Defaults to 'IG'.

        Returns
        -------
        list[ComponentEnthalpy]
            A list of ComponentEnthalpy objects containing the calculated enthalpy at each temperature.
        '''
        results = []
        try:
            for temp in temperatures:
                result = self.calc_enthalpy(
                    temperature=temp,
                    phase=phase
                )
                if result is not None:
                    results.append(result)
            return results
        except Exception as e:
            logger.exception(
                f"Error calculating enthalpy of formation over range: {e}")
            return results

    def calc_gibbs_free_energy(
            self,
            temperature: Temperature,
            phase: Literal['IG', 'LIQ', 'SOL'] = 'IG',
    ) -> Optional[ComponentGibbsFreeEnergy]:
        '''
        Calculate the Gibbs free energy (J/mol) at a given temperature (K).

        Parameters
        ----------
        temperature : Temperature
            The temperature at which to calculate the Gibbs free energy of formation.
        phase : Literal['IG', 'LIQ', 'SOL']
            The phase of the component ('IG' for ideal gas, 'LIQ' for liquid). Defaults to 'IG'.

        Returns
        -------
        Optional[ComponentGibbsFreeEnergy]
            A ComponentGibbsFreeEnergy object containing the calculated Gibbs free energy of formation if successful, otherwise None.

        Notes
        -----
        - The Gibbs free energy of formation is calculated using the enthalpy of formation and heat capacity equations.
        - All Gibbs energy results are provided in J/mol.
        - Reference temperature is set to 298.15 K.
        - The Gibbs free energy of formation symbol must be consistent with the defined unit in the configuration which are GiEnFo_IG, GiFrEn_LIQ, GiFrEn_SOL for ideal-gas, liquid, and solid, respectively.
        - The reference state can be 'IG' (ideal gas) or 'None' (no reference). The 'IG' reference state is commonly used to calculate standard Gibbs free energy of reaction, and then used in equilibrium calculations (Keq).
        '''
        try:
            # SECTION: temperature value
            T_val = temperature.value
            T_unit = temperature.unit

            # >> convert temperature to K if necessary
            if T_unit != 'K':
                T_val = pycuc.to(
                    T_val,
                    f"{T_unit} => K"
                )

            # SECTION: get formation data
            # >> enthalpy of formation (EnFo_X) unit ?
            # >> gibbs energy of formation (GiEnFo_X) unit ?
            if phase == 'IG':
                EnFo_SYMBOL = EnFo_IG_SYMBOL
                GiEnFo_SYMBOL = GiEnFo_IG_SYMBOL
                GiEnFo_UNIT = GiEnFo_IG_UNIT
                Cp_eq_src = self.Cp_IG_eq_src
            elif phase == 'LIQ':
                EnFo_SYMBOL = EnFo_LIQ_SYMBOL
                GiEnFo_SYMBOL = GiEnFo_LIQ_SYMBOL
                GiEnFo_UNIT = GiEnFo_LIQ_UNIT
                Cp_eq_src = self.Cp_LIQ_eq_src
            elif phase == 'SOL':
                EnFo_SYMBOL = EnFo_SOL_SYMBOL
                GiEnFo_SYMBOL = GiEnFo_SOL_SYMBOL
                GiEnFo_UNIT = GiEnFo_SOL_UNIT
                Cp_eq_src = self.Cp_SOL_eq_src
            else:
                logger.error(
                    f"Invalid phase: {phase}. Must be 'IG' or 'LIQ'.")
                return None

            # >> get formation data
            formation_data = self._get_formation_data(EnFo_SYMBOL)
            gibbs_formation_data = self._get_formation_data(GiEnFo_SYMBOL)

            # >> check formation data
            if formation_data is None:
                logger.warning(
                    f"No formation data available for enthalpy of formation.")
                return None

            if gibbs_formation_data is None:
                logger.warning(
                    f"No formation data available for Gibbs free energy of formation.")
                return None

            # NOTE: unit conversion if necessary
            # TODO: convert to [J/mol]
            EnFo_IG_val = formation_data['value']
            EnFo_IG_unit = formation_data['unit']
            # ! to [J/mol]
            unit_ = f"{EnFo_IG_unit} => {EnFo_IG_UNIT}"
            EnFo_IG_val = pycuc.to(
                EnFo_IG_val,
                unit_
            )

            GiEnFo_IG_val = gibbs_formation_data['value']
            GiEnFo_IG_unit = gibbs_formation_data['unit']
            # ! to [J/mol]
            unit_ = f"{GiEnFo_IG_unit} => {GiEnFo_IG_UNIT}"
            GiEnFo_IG_val = pycuc.to(
                GiEnFo_IG_val,
                unit_
            )

            # SECTION: heat capacity calculation
            # NOTE: check Cp equation source
            if Cp_eq_src is None:
                logger.error(
                    f"No ideal gas heat capacity equation source available for component {self.component_id}.")
                return None

            # NOTE: integrate Cp from T_ref to T
            # ! [J/mol]
            _eq_Cp_integral = self._calc_enthalpy_change(
                Cp_eq_src=Cp_eq_src,
                T1=self.T_ref,
                T2=T_val,
            )

            # >> check
            if _eq_Cp_integral is None:
                logger.error(
                    f"Failed to integrate Cp equation from T={self.T_ref} K to T={T_val} K.")
                return None

            # NOTE: integrate Cp/RT from T_ref to T
            # ! dimensionless
            _eq_Cp_integral_Cp__RT = Cp__RT_integral(
                eq_src=Cp_eq_src,
                T_ref=self.T_ref,
                T=T_val,
                R=self.R,
                R_unit='J/mol.K',
            )

            # >> check
            if _eq_Cp_integral_Cp__RT is None:
                logger.error(
                    f"Failed to integrate Cp/RT equation from T={self.T_ref} K to T={T_val} K.")
                return None

            # SECTION: calculate Gibbs free energy of formation at temperature
            # ! Gibbs free energy of formation at T
            # ! [J/mol]
            # A
            A = (GiEnFo_IG_val - EnFo_IG_val)/(self.R*self.T_ref)
            # B
            B = EnFo_IG_val/(self.R*T_val)
            # C
            C = (1/T_val)*_eq_Cp_integral/self.R
            # D
            D = _eq_Cp_integral_Cp__RT['value']
            # E (dimensionless)
            E = A + B + C - D
            # >> at T [J/mol]
            GiEn_T = float(E*self.R*T_val)

            # SECTION: prepare result
            result = {
                'temperature': temperature,
                'value': GiEn_T,
                'unit': GiEnFo_UNIT,
                'symbol': GiEnFo_SYMBOL
            }

            # >> set
            result = ComponentGibbsFreeEnergy(**result)

            return result
        except Exception as e:
            logger.exception(
                f"Error calculating Gibbs free energy of formation: {e}")
            return None

    def calc_gibbs_free_energy_range(
            self,
            temperatures: list[Temperature],
            phase: Literal['IG', 'LIQ', 'SOL'] = 'IG',
    ) -> List[ComponentGibbsFreeEnergy]:
        '''
        Calculate the Gibbs free energy of formation in (J/mol) over a range of temperatures in Kelvin (K).

        Parameters
        ----------
        temperatures : list[Temperature]
            A list of temperatures at which to calculate the Gibbs free energy.
        phase : Literal['IG', 'LIQ', 'SOL']
            The phase of the component ('IG' for ideal gas, 'LIQ' for liquid). Defaults to 'IG'.

        Returns
        -------
        list[ComponentGibbsFreeEnergy]
            A list of ComponentGibbsFreeEnergy objects containing the calculated Gibbs free energy at each temperature.
        '''
        results = []
        try:
            for temp in temperatures:
                result = self.calc_gibbs_free_energy(
                    temperature=temp,
                    phase=phase
                )

                # check
                if result is not None:
                    results.append(result)
            return results
        except Exception as e:
            logger.exception(
                f"Error calculating Gibbs free energy of formation over range: {e}")
            return results

    def calc_entropy_change(
            self,
            T1: Temperature,
            T2: Temperature,
            P1: Pressure,
            P2: Pressure,
            phase: Literal['IG', 'LIQ', 'SOL'],
    ) -> Optional[ComponentEntropyChange]:
        '''
        Calculate the entropy change (J/mol.K) between two temperatures using the provided equation source.

        Parameters
        ----------
        T1 : Temperature
            The initial temperature.
        T2 : Temperature
            The final temperature.
        P1 : Pressure
            The initial pressure.
        P2 : Pressure
            The final pressure.
        phase : Literal['IG', 'LIQ', 'SOL']
            The phase of the component ('IG' for ideal gas, 'LIQ' for liquid).

        Returns
        -------
        Optional[ComponentEntropyChange]
            The calculated entropy change if successful, otherwise None.

        Notes
        -----
        - The entropy change is calculated by integrating the heat capacity equation from T1 to T2 and accounting for pressure changes.
        - Phase-specific calculations are performed based on the provided phase.
        - The general equation is ΔS = ∫(Cp/T dT) - R ln(P2/P1) for both ideal gases and liquids.
        - For ideal gases, the pressure change contribution is included using the relation ΔS = nR ln(P2/P1).
        - For liquids, the pressure change contribution is typically negligible and may be omitted.
        - The result is provided in J/mol.K.
        - R is the universal gas constant (8.3145 J/mol.K).
        '''
        try:
            # SECTION: convert temperatures to K if necessary
            T1_val = T1.value
            T1_unit = T1.unit
            if T1_unit != 'K':
                T1_val = pycuc.to(
                    T1_val,
                    f"{T1_unit} => K"
                )

            T2_val = T2.value
            T2_unit = T2.unit
            if T2_unit != 'K':
                T2_val = pycuc.to(
                    T2_val,
                    f"{T2_unit} => K"
                )

            # SECTION: calculate entropy change
            # NOTE: check Cp equation source
            if phase == 'IG':
                if self.Cp_IG_eq_src is None:
                    logger.error(
                        f"No ideal gas heat capacity equation source available for component {self.component_id}.")
                    return None

                # set
                Cp_eq_src = self.Cp_IG_eq_src
                Ent_symbol = 'dEnt_IG'
            elif phase == 'LIQ':
                if self.Cp_LIQ_eq_src is None:
                    logger.error(
                        f"No liquid heat capacity equation source available for component {self.component_id}.")
                    return None

                # set
                Cp_eq_src = self.Cp_LIQ_eq_src
                Ent_symbol = 'dEnt_LIQ'
            elif phase == 'SOL':
                if self.Cp_SOL_eq_src is None:
                    logger.error(
                        f"No solid heat capacity equation source available for component {self.component_id}.")
                    return None

                # set
                Cp_eq_src = self.Cp_SOL_eq_src
                Ent_symbol = 'dEnt_SOL'
            else:
                logger.error(
                    f"Invalid phase: {phase}. Must be 'IG', 'LIQ' or 'SOL'.")
                return None

            # SECTION: integrate Cp/T dT from T1 to T2
            # ! [J/mol.K]
            delta_S_temp = Cp__T_integral(
                eq_src=Cp_eq_src,
                T_ref=T1_val,
                T=T2_val,
                output_unit='J/mol.K'  # ! specify output unit as J/mol.K
            )

            # >> check
            if delta_S_temp is None:
                logger.error(
                    f"Failed to calculate entropy change from {T1_val} K to {T2_val} K.")
                return None

            # SECTION: pressure change contribution
            # ! [J/mol.K]
            delta_S_pressure = 0.0
            if phase == 'IG':
                # ideal gas
                delta_S_pressure = -self.R * math.log(P2.value / P1.value)
            elif phase == 'LIQ':
                # liquid - typically negligible
                delta_S_pressure = 0.0
            elif phase == 'SOL':
                # solid - typically negligible
                delta_S_pressure = 0.0
            else:
                logger.error(
                    f"Invalid phase: {phase}. Must be 'IG', 'LIQ', 'SOL'.")
                return None

            # SECTION: total entropy change
            # ! [J/mol.K]
            delta_S_val = delta_S_temp['value'] + delta_S_pressure
            # >> prepare result
            result = {
                'temperature_initial': T1,
                'temperature_final': T2,
                'pressure_initial': P1,
                'pressure_final': P2,
                'phase': phase,
                'value': delta_S_val,
                'unit': 'J/mol.K',
                'symbol': Ent_symbol
            }

            # >> set
            result = ComponentEntropyChange(**result)

            return result
        except Exception as e:
            logger.exception(
                f"Error calculating entropy change between temperatures: {e}")
            return None

    def calc_evaporation_enthalpy(
            self,
            temperature: Temperature,
    ) -> Optional[ComponentHeatOfVaporization]:
        '''
        Calculate the enthalpy of evaporation (J/mol) at a given temperature (K).

        Parameters
        ----------
        temperature : Temperature
            The temperature at which to calculate the enthalpy of evaporation.

        Returns
        -------
        Optional[ComponentHeatOfVaporization]
            A ComponentHeatOfVaporization object containing the calculated enthalpy of evaporation if successful, otherwise None.
        '''
        try:
            # SECTION: temperature value
            T_val = temperature.value
            T_unit = temperature.unit

            # >> convert temperature to K if necessary
            if T_unit != 'K':
                T_val = pycuc.to(
                    T_val,
                    f"{T_unit} => K"
                )

            # SECTION: check EnVap equation source
            if self.EnVap_eq_src is None:
                logger.error(
                    f"No enthalpy of vaporization equation source available for component {self.component_id}.")
                return None

            # SECTION: evaluate EnVap equation at temperature
            EnVap_result = calc_eq(
                eq_src=self.EnVap_eq_src,
                vars={
                    'T': T_val
                },
                output_unit='J/mol'  # ! specify output unit as J/mol
            )

            # >> check
            if EnVap_result is None:
                logger.error(
                    f"Failed to evaluate enthalpy of vaporization equation at T={T_val} K.")
                return None

            # SECTION: prepare result
            result_ = {
                'temperature': temperature,
                'value': EnVap_result['value'],
                'unit': 'J/mol',
                'symbol': EnVap_SYMBOL
            }

            # >> set
            result = ComponentHeatOfVaporization(**result_)

            return result
        except Exception as e:
            logger.exception(
                f"Error calculating enthalpy of evaporation: {e}")
            return None

    def calc_sublimation_enthalpy(
            self,
            temperature: Temperature,
    ) -> Optional[ComponentHeatOfSublimation]:
        '''
        Calculate the enthalpy of sublimation (J/mol) at a given temperature (K).

        Parameters
        ----------
        temperature : Temperature
            The temperature at which to calculate the enthalpy of sublimation.

        Returns
        -------
        Optional[ComponentHeatOfSublimation]
            A ComponentHeatOfSublimation object containing the calculated enthalpy of sublimation if successful, otherwise None.
        '''
        try:
            # SECTION: temperature value
            T_val = temperature.value
            T_unit = temperature.unit

            # >> convert temperature to K if necessary
            if T_unit != 'K':
                T_val = pycuc.to(
                    T_val,
                    f"{T_unit} => K"
                )

            # SECTION: check EnSub equation source
            if self.EnSub_eq_src is None:
                logger.error(
                    f"No enthalpy of sublimation equation source available for component {self.component_id}.")
                return None

            # SECTION: evaluate EnSub equation at temperature
            EnSub_result = calc_eq(
                eq_src=self.EnSub_eq_src,
                vars={
                    'T': T_val
                },
                output_unit='J/mol'  # ! specify output unit as J/mol
            )

            # >> check
            if EnSub_result is None:
                logger.error(
                    f"Failed to evaluate enthalpy of sublimation equation at T={T_val} K.")
                return None

            # SECTION: prepare result
            result_ = {
                'temperature': temperature,
                'value': EnSub_result['value'],
                'unit': 'J/mol',
                'symbol': EnSub_SYMBOL
            }

            # >> set
            result = ComponentHeatOfSublimation(**result_)

            return result
        except Exception as e:
            logger.exception(
                f"Error calculating enthalpy of sublimation: {e}")
            return None

    def calc_reference_enthalpy(
            self,
            temperature: Temperature,
            phase: Literal['IG', 'LIQ', 'SOL'],
    ) -> Optional[ComponentEnthalpy]:
        """
        Calculate the enthalpy (J/mol) for a specific phase at a given temperature (K). The phases supported are ideal gas (IG), liquid (LIQ), and solid (SOL).

        The reference phase is `ideal gas` at 298.15 K and 1 atm. In the case of `the unavailability of enthalpy for liquid and solid phases`, they are calculated based on the ideal gas enthalpy and phase change enthalpies. Thus, the

        Parameters
        ----------
        temperature : Temperature
            The temperature at which to calculate the enthalpy of formation.
        phase : Literal['IG', 'LIQ', 'SOL']
            The phase of the component ('IG' for ideal gas, 'LIQ' for liquid, 'SOL' for solid).

        Returns
        -------
        Optional[ComponentEnthalpyOfFormation]
            A ComponentEnthalpyOfFormation object containing the calculated enthalpy of formation if successful, otherwise None.

        Notes
        -----
        - The enthalpy of formation for each phase is calculated based on the ideal gas enthalpy and phase change enthalpies.
        - All enthalpy results are provided in J/mol.
        - Reference temperature is set to 298.15 K.
        - The enthalpy of formation symbols must be consistent with the defined units in the configuration which are EnFo_IG, EnFo_LIQ, and EnFo_SOL.

        Equations
        ---------
        - ideal gas enthalpy (H_IG) is calculated as:
            H_IG(T) = ΔH_f(T) + ∫(Cp_IG dT) from 298.15 K to T

        - liquid enthalpy (H_LIQ) is calculated as:
            H_LIQ(T) = H_IG(T) - ΔH_vap(T)

        - solid enthalpy (H_SOL) is calculated as (not implemented):
            H_SOL(T) = H_IG(T) - ΔH_vap(T) - ΔH_fusion(T)
        """
        try:
            # SECTION: calculate ideal gas enthalpy
            # ! [J/mol]
            EnFo_IG = self.calc_enthalpy(
                temperature=temperature,
                phase='IG'
            )

            if EnFo_IG is None:
                logger.error(
                    f"Failed to calculate ideal gas enthalpy of formation for liquid phase calculation.")
                return None

            # SECTION: calculate phase-specific enthalpy of formation
            if phase == 'IG':
                return EnFo_IG
            elif phase == 'LIQ':
                # NOTE: calculate enthalpy of vaporization
                # ! [J/mol]
                EnVap = self.calc_evaporation_enthalpy(
                    temperature=temperature
                )

                if EnVap is None:
                    logger.error(
                        f"Failed to calculate enthalpy of vaporization for liquid phase calculation.")
                    return None

                # NOTE: calculate liquid enthalpy of formation
                # ! [J/mol]
                EnFo_LIQ_value = EnFo_IG.value - EnVap.value

                # prepare result
                result_ = {
                    'temperature': temperature,
                    'value': EnFo_LIQ_value,
                    'unit': 'J/mol',
                    'symbol': EnFo_LIQ_SYMBOL
                }

                # set
                result = ComponentEnthalpy(**result_)

                return result
            elif phase == 'SOL':
                # NOTE: calculate enthalpy of vaporization
                # ! [J/mol]
                EnVap = self.calc_evaporation_enthalpy(
                    temperature=temperature
                )

                if EnVap is None:
                    logger.error(
                        f"Failed to calculate enthalpy of vaporization for liquid phase calculation.")
                    return None

                # NOTE: calculate enthalpy of sublimation
                # ! [J/mol]
                EnSub = self.calc_sublimation_enthalpy(
                    temperature=temperature
                )

                if EnSub is None:
                    logger.error(
                        f"Failed to calculate enthalpy of sublimation for solid phase calculation.")
                    return None

                # NOTE: calculate solid enthalpy of formation
                # ! [J/mol]
                EnFo_SOL_value = EnFo_IG.value - EnVap.value - EnSub.value

                # prepare result
                result_ = {
                    'temperature': temperature,
                    'value': EnFo_SOL_value,
                    'unit': 'J/mol',
                    'symbol': EnFo_SOL_SYMBOL
                }

                # set
                result = ComponentEnthalpy(**result_)

                return result
            else:
                logger.error(
                    f"Invalid phase: {phase}. Must be 'IG', 'LIQ', or 'SOL'.")
                return None
        except Exception as e:
            logger.exception(
                f"Error calculating phase enthalpy of formation: {e}")
            return None
