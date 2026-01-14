# import libs
import logging
from typing import Literal, Optional, List, Dict, Any
from pyreactlab_core.models.reaction import Reaction
from pyThermoLinkDB.models import ModelSource
from pythermodb_settings.models import Temperature, CustomProp, ComponentKey
from pythermodb_settings.utils import measure_time
from pyThermoLinkDB.thermo import Source
import pycuc
# locals
from ..core.hsg_reaction import HSGReaction

# NOTE: logger
logger = logging.getLogger(__name__)


@measure_time
def dEn_rxn_STD(
    reaction: Reaction,
    temperature: Temperature,
    model_source: ModelSource,
    **kwargs
) -> Optional[CustomProp]:
    """
    Calculate the standard enthalpy of reaction using HSG properties.

    Parameters
    ----------
    reaction : Reaction
        The Reaction object representing the chemical reaction.
    temperature : Temperature
        The Temperature object representing the temperature at which to calculate the enthalpy of reaction.
    model_source : ModelSource
        The ModelSource object representing the data source for the components.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[CustomProp]
        The standard enthalpy of reaction in J/mol, or None if calculation fails.
    """
    try:
        # SECTION: Prepare source
        Source_ = Source(model_source=model_source)

        # NOTE: initialize HSGReaction
        hsg_reaction = HSGReaction(
            reaction=reaction,
            source=Source_,
        )

        # >> calculate standard enthalpy of reaction
        dH_rxn_std = hsg_reaction.calc_standard_rxn_enthalpy(
            temperature=temperature,
        )

        return dH_rxn_std
    except Exception as e:
        logger.error(f"Error calculating standard enthalpy of reaction: {e}")
        return None


@measure_time
def dGiFrEn_rxn_STD(
    reaction: Reaction,
    temperature: Temperature,
    model_source: ModelSource,
    **kwargs
) -> Optional[CustomProp]:
    """
    Calculate the standard Gibbs free energy of reaction using HSG properties.

    Parameters
    ----------
    reaction : Reaction
        The Reaction object representing the chemical reaction.
    temperature : Temperature
        The Temperature object representing the temperature at which to calculate the Gibbs free energy of reaction.
    model_source : ModelSource
        The ModelSource object representing the data source for the components.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[CustomProp]
        The standard Gibbs free energy of reaction in J/mol, or None if calculation fails.
    """
    try:
        # SECTION: Prepare source
        Source_ = Source(model_source=model_source)

        # NOTE: initialize HSGReaction
        hsg_reaction = HSGReaction(
            reaction=reaction,
            source=Source_,
        )

        # >> calculate standard Gibbs free energy of reaction
        dG_rxn_std = hsg_reaction.calc_standard_rxn_gibbs_free_energy(
            temperature=temperature,
        )

        return dG_rxn_std
    except Exception as e:
        logger.error(
            f"Error calculating standard Gibbs free energy of reaction: {e}")
        return None


@measure_time
def Keq_STD(
    reaction: Reaction,
    temperature: Temperature,
    model_source: ModelSource,
    component_key: ComponentKey = 'Name-Formula',
    **kwargs
) -> Optional[CustomProp]:
    """
    Calculate the standard equilibrium constant of reaction using HSG properties using Van't Hoff equation as:
        Keq_std = exp(-ΔG_rxn_std / (R * T))

    Parameters
    ----------
    reaction : Reaction
        The Reaction object representing the chemical reaction.
    temperature : Temperature
        The Temperature object representing the temperature at which to calculate the equilibrium constant of reaction.
    model_source : ModelSource
        The ModelSource object representing the data source for the components.
    component_key : ComponentKey, optional
        The ComponentKey to identify components, by default 'Name-Formula'.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[CustomProp]
        The standard equilibrium constant of reaction, or None if calculation fails.
    """
    try:
        # SECTION: Prepare source
        Source_ = Source(
            model_source=model_source,
            component_key=component_key
        )

        # NOTE: initialize HSGReaction
        hsg_reaction = HSGReaction(
            reaction=reaction,
            source=Source_,
        )

        # >> calculate standard equilibrium constant of reaction
        Keq_std = hsg_reaction.calc_equilibrium_constant_STD(
            temperature=temperature,
        )

        return Keq_std
    except Exception as e:
        logger.error(
            f"Error calculating standard equilibrium constant of reaction: {e}")
        return None


@measure_time
def Keq_VH(
    dGiFrEn_std: CustomProp,
    temperature: Temperature,
    **kwargs
) -> Optional[CustomProp]:
    """
    Calculate the equilibrium constant of reaction at a given temperature using Van't Hoff equation as:
        Keq = exp(-ΔG_rxn_std / (R * T))

    Parameters
    ----------
    dGiFrEn_std : CustomProp
        The standard Gibbs free energy of reaction.
    temperature : Temperature
        The Temperature object representing the temperature at which to calculate the equilibrium constant of reaction.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[CustomProp]
        The equilibrium constant of reaction at the given temperature, or None if calculation fails.
    """
    try:
        # SECTION: input validation
        # NOTE: dGiFrEn_std
        # ! [J/mol]
        if dGiFrEn_std.unit != 'J/mol':
            dGiFrEn_std_value = pycuc.convert_from_to(
                value=dGiFrEn_std.value,
                from_unit=dGiFrEn_std.unit,
                to_unit='J/mol'
            )
        else:
            dGiFrEn_std_value = dGiFrEn_std.value

        # NOTE: temperature
        # ! [K]
        if temperature.unit != 'K':
            temperature_value = pycuc.convert_from_to(
                value=temperature.value,
                from_unit=temperature.unit,
                to_unit='K'
            )
        else:
            temperature_value = temperature.value

        # SECTION: vh equation
        vh = HSGReaction.vh

        # >> calculate equilibrium constant of reaction using Van't Hoff equation
        Keq_vh = vh(
            gibbs_energy_of_reaction_std=dGiFrEn_std_value,
            temperature=temperature_value,
        )

        return Keq_vh
    except Exception as e:
        logger.error(
            f"Error calculating equilibrium constant of reaction using Van't Hoff equation: {e}")
        return None


@measure_time
def Keq_VH_Shortcut(
    Keq_std: CustomProp,
    dEn_rxn_std: CustomProp,
    temperature: Temperature,
    **kwargs
) -> Optional[CustomProp]:
    """
    Shortcut for Van't Hoff equation to calculate equilibrium constant at different temperatures as:
        Keq = Keq_std * exp( (-ΔH_rxn_std / R) * (1/T - 1/T_ref) )

    where, Keq_std is the equilibrium constant at standard conditions (T_ref), and ΔH_rxn_std is the enthalpy of reaction at standard conditions.
    Tref is set to 298.15 K.

    Parameters
    ----------
    Keq_std : CustomProp
        The standard equilibrium constant of reaction.
    dEn_rxn_std : CustomProp
        The standard enthalpy of reaction.
    temperature : Temperature
        The Temperature object representing the temperature at which to calculate the equilibrium constant of reaction.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    Optional[CustomProp]
        The equilibrium constant of reaction at the given temperature, or None if calculation fails.
    """
    try:
        # SECTION: input validation
        # NOTE: Keq_std
        # ! [dimensionless]
        if Keq_std.unit != 'dimensionless':
            logger.error(
                f"Error: Keq_std must be dimensionless, got {Keq_std.unit} instead.")
            return None
        else:
            Keq_std_value = Keq_std.value

        # NOTE: dEn_rxn_std
        # ! [J/mol]
        if dEn_rxn_std.unit != 'J/mol':
            dEn_rxn_std_value = pycuc.convert_from_to(
                value=dEn_rxn_std.value,
                from_unit=dEn_rxn_std.unit,
                to_unit='J/mol'
            )
        else:
            dEn_rxn_std_value = dEn_rxn_std.value

        # NOTE: temperature
        # ! [K]
        if temperature.unit != 'K':
            temperature_value = pycuc.convert_from_to(
                value=temperature.value,
                from_unit=temperature.unit,
                to_unit='K'
            )
        else:
            temperature_value = temperature.value

        # SECTION: vh shortcut equation
        vh_shortcut = HSGReaction.vh_shortcut

        # >> calculate equilibrium constant of reaction using Van't Hoff shortcut equation
        Keq_vh_shortcut = vh_shortcut(
            enthalpy_of_reaction_std=dEn_rxn_std_value,
            equilibrium_constant_std=Keq_std_value,
            temperature=temperature_value,
        )

        return Keq_vh_shortcut
    except Exception as e:
        logger.error(
            f"Error calculating equilibrium constant of reaction using Van't Hoff shortcut equation: {e}")
        return None
