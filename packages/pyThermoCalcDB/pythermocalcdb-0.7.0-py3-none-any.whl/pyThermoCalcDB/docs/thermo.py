# import libs
import logging
from typing import Literal, Optional, List
from pyThermoLinkDB.models import ModelSource
from pythermodb_settings.models import (
    Component,
    Temperature,
    Pressure,
    CustomProp,
    ComponentKey
)
from pyThermoLinkDB.thermo import Source
import pycuc
# local
from ..utils.tools import measure_time
from ..core.hsg_properties import HSGProperties
from ..core.hsg_mixture import HSGMixture
from ..models.component_ref import (
    ComponentGibbsFreeEnergy,
    ComponentEnthalpy,
    ComponentEnthalpyChange,
    ComponentEntropyChange,
    MixtureEnthalpyResult
)

# NOTE: Logger
logger = logging.getLogger(__name__)


@measure_time
def calc_dEn(
        component: Component,
        model_source: ModelSource,
        temperature_initial: Temperature,
        temperature_final: Temperature,
        component_key: ComponentKey = 'Name-Formula',
        **kwargs
) -> Optional[ComponentEnthalpyChange]:
    """
    Calculate the enthalpy change (J/mol) between two temperatures (K) for a component.

    Parameters
    ----------
    component : Component
        The chemical component for which to calculate the enthalpy change.
    model_source : ModelSource
        The source model containing necessary data.
    temperature_initial : Temperature
        The initial temperature.
    temperature_final : Temperature
        The final temperature.
    component_key : Literal[..., optional]
        The key to identify the component, by default 'Name-State'.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[ComponentEnthalpyChange]
        The enthalpy change value, or None if calculation fails.

    Notes
    -----
    - The function initializes the HSGProperties class and uses it to compute the enthalpy change.
    - The enthalpy change is calculated by integrating the heat capacity equation between the two specified temperatures.
    - The result is provided in J/mol.
    - Reference temperature is set to 298.15 K.
    """
    try:
        # SECTION: Input validation
        if not isinstance(component, Component):
            logger.error("Invalid component provided.")
            return None

        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(temperature_initial, Temperature):
            logger.error("Invalid initial temperature provided.")
            return None

        if not isinstance(temperature_final, Temperature):
            logger.error("Invalid final temperature provided.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            component_key=component_key
        )

        # SECTION: Initialize HSGProperties
        hsg_props = HSGProperties(
            component=component,
            source=Source_,
            component_key=component_key
        )

        # NOTE: calculate enthalpy change
        delta_H = hsg_props.calc_enthalpy_change(
            T1=temperature_initial,
            T2=temperature_final
        )

        return delta_H
    except Exception as e:
        logger.error(
            f"Error calculating enthalpy change for component '{component.name}': {e}")
        return None


@measure_time
def calc_En(
    component: Component,
    model_source: ModelSource,
    temperature: Temperature,
    component_key: ComponentKey = 'Name-Formula',
    **kwargs
) -> Optional[ComponentEnthalpy]:
    """
    Calculate the enthalpy (J/mol) at a given temperature (K) for a component.

    Parameters
    ----------
    component : Component
        The chemical component for which to calculate the enthalpy of formation.
    model_source : ModelSource
        The source model containing necessary data.
    temperature : Temperature
        The temperature at which to calculate the enthalpy of formation.
    component_key : Literal[..., optional]
        The key to identify the component, by default 'Name-State'.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[ComponentEnthalpy]
        A ComponentEnthalpy object containing the enthalpy of formation value, unit, and symbol, or None if calculation fails.

    Notes
    -----
    - The function initializes the HSGProperties class and uses it to compute the enthalpy of formation.
    - The enthalpy of formation symbol must be consistent with the defined unit in the configuration which is EnFo_IG.
    - Reference temperature is set to 298.15 K.
    - All enthalpy results are provided in J/mol.
    """
    try:
        # SECTION: Input validation
        if not isinstance(component, Component):
            logger.error("Invalid component provided.")
            return None

        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(temperature, Temperature):
            logger.error("Invalid temperature provided.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            component_key=component_key
        )

        # SECTION: Initialize HSGProperties
        hsg_props = HSGProperties(
            component=component,
            source=Source_,
            component_key=component_key
        )

        # NOTE: calculate
        EnFo_result = hsg_props.calc_enthalpy(
            temperature=temperature
        )

        return EnFo_result
    except Exception as e:
        logger.error(
            f"Error calculating enthalpy of formation for component '{component.name}': {e}")
        return None


@measure_time
def calc_GiFrEn(
        component: Component,
        model_source: ModelSource,
        temperature: Temperature,
        phase: Literal['IG', 'LIQ', 'SOL'] = 'IG',
        component_key: ComponentKey = 'Name-Formula',
        **kwargs
) -> Optional[ComponentGibbsFreeEnergy]:
    """
    Calculate the Gibbs free energy (J/mol) at a given temperature (K) for a component.

    Parameters
    ----------
    component : Component
        The chemical component for which to calculate the Gibbs free energy of formation.
    model_source : ModelSource
        The source model containing necessary data.
    temperature : Temperature
        The temperature at which to calculate the Gibbs free energy of formation.
    phase : Literal['IG', 'LIQ', 'SOL'], optional
        The phase of the component ('IG' for ideal gas, 'LIQ' for liquid, 'SOL' for solid). Default is 'IG'.
    component_key : Literal[..., optional]
        The key to identify the component, by default 'Name-State'.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[ComponentGibbsFreeEnergy]
        A ComponentGibbsFreeEnergy object containing the Gibbs free energy of formation value, unit, and symbol, or None if calculation fails.

    Notes
    -----
    - The function initializes the HSGProperties class and uses it to compute the Gibbs free energy of formation.
    - The Gibbs free energy of formation symbol must be consistent with the defined unit in the configuration which is GiEnFo_IG.
    - Reference temperature is set to 298.15 K.
    - All Gibbs energy results are provided in J/mol.
    """
    try:
        # SECTION: Input validation
        if not isinstance(component, Component):
            logger.error("Invalid component provided.")
            return None

        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(temperature, Temperature):
            logger.error("Invalid temperature provided.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            component_key=component_key
        )

        # SECTION: Initialize HSGProperties
        hsg_props = HSGProperties(
            component=component,
            source=Source_,
            component_key=component_key
        )

        # NOTE: calculate
        GiEnFo_result = hsg_props.calc_gibbs_free_energy(
            temperature=temperature,
            phase=phase
        )

        return GiEnFo_result
    except Exception as e:
        logger.error(
            f"Error calculating Gibbs free energy of formation for component '{component.name}': {e}")
        return None


@measure_time
def calc_En_range(
        component: Component,
        model_source: ModelSource,
        temperatures: list[Temperature],
        component_key: ComponentKey = 'Name-Formula',
        **kwargs
) -> Optional[list[ComponentEnthalpy]]:
    """
    Calculate the enthalpy of formation (J/mol) over a range of temperatures (K) for a component.

    Parameters
    ----------
    component : Component
        The chemical component for which to calculate the enthalpy of formation.
    model_source : ModelSource
        The source model containing necessary data.
    temperatures : list[Temperature]
        The list of temperatures at which to calculate the enthalpy of formation.
    component_key : Literal[..., optional]
        The key to identify the component, by default 'Name-State'.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[list[ComponentEnthalpy]]
        A list of ComponentEnthalpy objects containing the enthalpy of formation values, units, and symbols, or None if calculation fails.

    Notes
    -----
    - The function initializes the HSGProperties class and uses it to compute the enthalpy of formation.
    - The enthalpy of formation symbol must be consistent with the defined unit in the configuration which is EnFo_IG.
    - Reference temperature is set to 298.15 K.
    - All enthalpy results are provided in J/mol.
    """
    try:
        # SECTION: Input validation
        if not isinstance(component, Component):
            logger.error("Invalid component provided.")
            return None

        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not all(isinstance(temp, Temperature) for temp in temperatures):
            logger.error("Invalid temperatures provided.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            component_key=component_key
        )

        # SECTION: Initialize HSGProperties
        hsg_props = HSGProperties(
            component=component,
            source=Source_,
            component_key=component_key
        )

        # NOTE: calculate
        EnFo_results = hsg_props.calc_enthalpy_range(
            temperatures=temperatures
        )

        return EnFo_results
    except Exception as e:
        logger.error(
            f"Error calculating enthalpy of formation range for component '{component.name}': {e}")
        return None


@measure_time
def calc_GiFrEn_range(
        component: Component,
        model_source: ModelSource,
        temperatures: list[Temperature],
        component_key: ComponentKey = 'Name-Formula',
        **kwargs
) -> Optional[list[ComponentGibbsFreeEnergy]]:
    """
    Calculate the Gibbs free energy (J/mol) over a range of temperatures (K) for a component.

    Parameters
    ----------
    component : Component
        The chemical component for which to calculate the Gibbs free energy of formation.
    model_source : ModelSource
        The source model containing necessary data.
    temperatures : list[Temperature]
        The list of temperatures at which to calculate the Gibbs free energy of formation.
    component_key : Literal[..., optional]
        The key to identify the component, by default 'Name-Formula'.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[list[ComponentGibbsFreeEnergy]]
        A list of ComponentGibbsFreeEnergy objects containing the Gibbs free energy of formation values, units, and symbols, or None if calculation fails.

    Notes
    -----
    - The function initializes the HSGProperties class and uses it to compute the Gibbs free energy of formation.
    - The Gibbs free energy of formation symbol must be consistent with the defined unit in the configuration which is GiEnFo_IG.
    - Reference temperature is set to 298.15 K.
    - All Gibbs energy results are provided in J/mol.
    """
    try:
        # SECTION: Input validation
        if not isinstance(component, Component):
            logger.error("Invalid component provided.")
            return None

        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not all(isinstance(temp, Temperature) for temp in temperatures):
            logger.error("Invalid temperatures provided.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            component_key=component_key
        )

        # SECTION: Initialize HSGProperties
        hsg_props = HSGProperties(
            component=component,
            source=Source_,
            component_key=component_key
        )

        # NOTE: calculate
        GiEnFo_results = hsg_props.calc_gibbs_free_energy_range(
            temperatures=temperatures
        )

        return GiEnFo_results
    except Exception as e:
        logger.error(
            f"Error calculating Gibbs free energy of formation range for component '{component.name}': {e}")
        return None


@measure_time
def calc_dEnt(
        component: Component,
        model_source: ModelSource,
        temperature_initial: Temperature,
        temperature_final: Temperature,
        pressure_initial: Pressure,
        pressure_final: Pressure,
        phase: Literal['IG', 'LIQ', 'SOL'],
        component_key: ComponentKey = 'Name-Formula',
        **kwargs
) -> Optional[ComponentEntropyChange]:
    """
    Calculate the entropy change (J/mol.K) between two temperatures (K) and pressures in any unit for a component.

    The entropy change is calculated by integrating the heat capacity equation between the two specified temperatures and accounting for pressure changes based on the phase of the component. The result is provided in J/mol.K.

    The calculation considers the following:
    - For ideal gases, the pressure change contribution is included using the relation ΔS = nR ln(P2/P1).
    - For liquids, the pressure change contribution is typically negligible and may be omitted.
    - For solids, the pressure change contribution is typically negligible and may be omitted.

    The expression for entropy change is given by:
        ΔS = ∫(Cp/T) dT + ln(P2/P1) * R  (for ideal gases)
        ΔS = ∫(Cp/T) dT                    (for liquids)
        ΔS = ∫(Cp/T) dT                    (for solids)

    Parameters
    ----------
    component : Component
        The chemical component for which to calculate the entropy change.
    model_source : ModelSource
        The source model containing necessary data.
    temperature_initial : Temperature
        The initial temperature.
    temperature_final : Temperature
        The final temperature.
    pressure_initial : Pressure
        The initial pressure.
    pressure_final : Pressure
        The final pressure.
    phase : Literal['IG', 'LIQ', 'SOL'], optional
        The phase of the component ('IG' for ideal gas, 'LIQ' for liquid, 'SOL' for solid).
    component_key : Literal[..., optional]
        The key to identify the component, by default 'Name-State'.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[ComponentEntropyChange]
        The entropy change value, or None if calculation fails.

    Notes
    -----
    - The function initializes the HSGProperties class and uses it to compute the entropy change.
    - The entropy change is calculated by integrating the heat capacity equation between the two specified temperatures and accounting for pressure changes.
    - The result is provided in J/mol.K.
    - R is the universal gas constant (8.3145 J/mol.K).
    - Pressures can be provided in any unit as they will be converted internally.
    """
    try:
        # SECTION: Input validation
        if not isinstance(component, Component):
            logger.error("Invalid component provided.")
            return None

        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(temperature_initial, Temperature):
            logger.error("Invalid initial temperature provided.")
            return None

        if not isinstance(temperature_final, Temperature):
            logger.error("Invalid final temperature provided.")
            return None

        if not isinstance(pressure_initial, Pressure):
            logger.error("Invalid initial pressure provided.")
            return None

        if not isinstance(pressure_final, Pressure):
            logger.error("Invalid final pressure provided.")
            return None

        if phase not in ['IG', 'LIQ', 'SOL']:
            logger.error(
                "Invalid phase provided. Must be 'IG', 'LIQ', or 'SOL'.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            component_key=component_key
        )

        # SECTION: Initialize HSGProperties
        hsg_props = HSGProperties(
            component=component,
            source=Source_,
            component_key=component_key
        )

        # NOTE: calculate entropy change
        delta_S = hsg_props.calc_entropy_change(
            T1=temperature_initial,
            T2=temperature_final,
            P1=pressure_initial,
            P2=pressure_final,
            phase=phase
        )

        return delta_S
    except Exception as e:
        logger.error(
            f"Error calculating entropy change for component '{component.name}': {e}")
        return None


@measure_time
def calc_En_mix(
        components: List[Component],
        model_source: ModelSource,
        temperature: Temperature,
        pressure: Pressure,
        reference: Literal['IG', 'None'] = 'IG',
        departure_enthalpy: Optional[CustomProp] = None,
        excess_enthalpy: Optional[CustomProp] = None,
        component_key: ComponentKey = 'Name-Formula',
        output_unit: Optional[str] = None,
        **kwargs
) -> Optional[MixtureEnthalpyResult]:
    """
    Calculate the mixture enthalpy at a given temperature (K) and return the result is provided in J/mol.

    The mixture enthalpy is calculated based on the individual component enthalpies and their mole fractions. The function initializes the HSGMixture class and uses it to compute the mixture enthalpy.

    Parameters
    ----------
    components : List[Component]
        The list of chemical components in the mixture.
    model_source : ModelSource
        The source model containing necessary data.
    temperature : Temperature
        The temperature of the mixture.
    pressure : Pressure
        The pressure of the mixture.
    reference : Literal['IG', 'None']
        The reference state for enthalpy calculation.
    departure_enthalpy : Optional[CustomProp], optional
        Custom departure enthalpy property, by default None.
    excess_enthalpy : Optional[CustomProp], optional
        Custom excess enthalpy property, by default None.
    component_key : Literal[..., optional]
        The key to identify the components, by default 'Name-Formula'.
    output_unit : Optional[str], optional
        The desired output unit for mixture enthalpy, by default None (J/mol).
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[MixtureEnthalpyResult]
        A MixtureEnthalpyResult object containing the mixture enthalpy value, unit, and symbol, or None if calculation fails.

    Notes
    -----
    - The function initializes the HSGMixture class and uses it to compute the mixture enthalpy.
    - The mixture enthalpy is calculated based on the individual component enthalpies and their mole fractions.
    - The result is provided in J/mol.
    - The calculation may involve ideal and non-ideal contributions depending on the phase.
    - Only 'IG' and 'LIQ' phases are currently supported.
    - Flash calculations are not performed; the phase must be specified.
    """
    try:
        # SECTION: Input validation
        if not all(isinstance(comp, Component) for comp in components):
            logger.error("Invalid components provided.")
            return None

        if not isinstance(model_source, ModelSource):
            logger.error("Invalid model_source provided.")
            return None

        if not isinstance(temperature, Temperature):
            logger.error("Invalid temperature provided.")
            return None

        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            component_key=component_key
        )

        # SECTION: Initialize HSGMixture
        hsg_mixture = HSGMixture(
            components=components,
            source=Source_,
            component_key=component_key
        )

        # NOTE: calculate mixture enthalpy
        mixture_enthalpy = hsg_mixture.calc_mixture_enthalpy(
            temperature=temperature,
            reference=reference,
            departure_enthalpy=departure_enthalpy,
            excess_enthalpy=excess_enthalpy,
        )

        # >> check
        if mixture_enthalpy is None:
            logger.error("Mixture enthalpy calculation failed.")
            return None

        # set
        mixture_enthalpy_value = mixture_enthalpy['value']
        mixture_enthalpy_unit = mixture_enthalpy['unit']

        # SECTION: convert unit if needed
        if (
            output_unit is not None and
            mixture_enthalpy_unit != output_unit
        ):
            # >> convert
            converted_value = pycuc.convert_from_to(
                value=mixture_enthalpy_value,
                from_unit=mixture_enthalpy_unit,
                to_unit=output_unit
            )
            # >> update
            mixture_enthalpy_value = converted_value
            mixture_enthalpy_unit = output_unit

        # NOTE: prepare result
        res = {
            'temperature': temperature,
            'pressure': pressure,
            'reference': str(reference),
            'value': mixture_enthalpy_value,
            'unit': mixture_enthalpy_unit,
            'symbol': 'En_mix'
        }

        # set
        res = MixtureEnthalpyResult(**res)
        return res
    except Exception as e:
        logger.error(
            f"Error calculating mixture enthalpy: {e}")
        return None
