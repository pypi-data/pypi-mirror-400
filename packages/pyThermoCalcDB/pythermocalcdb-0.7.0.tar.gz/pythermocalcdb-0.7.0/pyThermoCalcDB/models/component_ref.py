# import libs
from typing import Any, Dict, Callable
from pydantic import BaseModel, Field, ConfigDict
from pyThermoDB.core import TableEquation
from pythermodb_settings.models import Temperature, Pressure


# NOTE: enthalpy change result model
class ComponentEnthalpyChange(BaseModel):
    '''
    Component Enthalpy Change Result Model

    Attributes
    ----------
    temperature_initial : Temperature
        The initial temperature for the enthalpy change calculation.
    temperature_final : Temperature
        The final temperature for the enthalpy change calculation.
    value : float
        The enthalpy change value.
    unit : str
        The enthalpy change unit.
    symbol : str
        The enthalpy change symbol.
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)

    temperature_initial: Temperature = Field(
        ...,
        description="The initial temperature for the enthalpy change calculation."
    )

    temperature_final: Temperature = Field(
        ...,
        description="The final temperature for the enthalpy change calculation."
    )

    value: float = Field(
        ...,
        description="The enthalpy change value."
    )
    unit: str = Field(
        ...,
        description="The enthalpy change unit."
    )
    symbol: str = Field(
        ...,
        description="The enthalpy change symbol."
    )

# NOTE: enthalpy of formation result model


class ComponentEnthalpy(BaseModel):
    '''
    Component Enthalpy of Formation Result Model

    Attributes
    ----------
    temperature : Temperature
        The temperature at which the enthalpy of formation is calculated.
    value : float
        The enthalpy of formation value.
    unit : str
        The enthalpy of formation unit.
    symbol : str
        The enthalpy of formation symbol.
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)

    temperature: Temperature = Field(
        ...,
        description="The temperature at which the enthalpy of formation is calculated."
    )

    value: float = Field(
        ...,
        description="The enthalpy of formation value."
    )
    unit: str = Field(
        ...,
        description="The enthalpy of formation unit."
    )
    symbol: str = Field(
        ...,
        description="The enthalpy of formation symbol."
    )


# NOTE: gibbs free energy of formation result model


class ComponentGibbsFreeEnergy(BaseModel):
    '''
    Component Gibbs Energy of Formation Result Model

    Attributes
    ----------
    temperature : Temperature
        The temperature at which the Gibbs energy of formation is calculated.
    value : float
        The Gibbs energy of formation value.
    unit : str
        The Gibbs energy of formation unit.
    symbol : str
        The Gibbs energy of formation symbol.
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)

    temperature: Temperature = Field(
        ...,
        description="The temperature at which the Gibbs energy of formation is calculated."
    )

    value: float = Field(
        ...,
        description="The Gibbs energy of formation value."
    )
    unit: str = Field(
        ...,
        description="The Gibbs energy of formation unit."
    )
    symbol: str = Field(
        ...,
        description="The Gibbs energy of formation symbol."
    )

# NOTE: entropy change result model


class ComponentEntropyChange(BaseModel):
    '''
    Component Entropy Change Result Model

    Attributes
    ----------
    temperature_initial : Temperature
        The initial temperature for the entropy change calculation.
    temperature_final : Temperature
        The final temperature for the entropy change calculation.
    pressure_initial : Pressure
        The initial pressure for the entropy change calculation.
    pressure_final : Pressure
        The final pressure for the entropy change calculation.
    phase : str
        The phase of the component ('IG' for ideal gas, 'LIQ' for liquid
    value : float
        The entropy change value.
    unit : str
        The entropy change unit.
    symbol : str
        The entropy change symbol.
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)

    temperature_initial: Temperature = Field(
        ...,
        description="The initial temperature for the entropy change calculation."
    )

    temperature_final: Temperature = Field(
        ...,
        description="The final temperature for the entropy change calculation."
    )

    pressure_initial: Pressure = Field(
        ...,
        description="The initial pressure for the entropy change calculation."
    )

    pressure_final: Pressure = Field(
        ...,
        description="The final pressure for the entropy change calculation."
    )

    phase: str = Field(
        ...,
        description="The phase of the component ('IG' for ideal gas, 'LIQ' for liquid)."
    )

    value: float = Field(
        ...,
        description="The entropy change value."
    )
    unit: str = Field(
        ...,
        description="The entropy change unit."
    )
    symbol: str = Field(
        ...,
        description="The entropy change symbol."
    )

# NOTE: component heat of vaporization result model


class ComponentHeatOfVaporization(BaseModel):
    '''
    Component Heat of Vaporization Result Model

    Attributes
    ----------
    temperature : Temperature
        The temperature at which the heat of vaporization is calculated.
    value : float
        The heat of vaporization value.
    unit : str
        The heat of vaporization unit.
    symbol : str
        The heat of vaporization symbol.
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)

    temperature: Temperature = Field(
        ...,
        description="The temperature at which the heat of vaporization is calculated."
    )

    value: float = Field(
        ...,
        description="The heat of vaporization value."
    )
    unit: str = Field(
        ...,
        description="The heat of vaporization unit."
    )
    symbol: str = Field(
        ...,
        description="The heat of vaporization symbol."
    )

# NOTE: component heat of sublimation result model


class ComponentHeatOfSublimation(BaseModel):
    '''
    Component Heat of Sublimation Result Model

    Attributes
    ----------
    temperature : Temperature
        The temperature at which the heat of sublimation is calculated.
    value : float
        The heat of sublimation value.
    unit : str
        The heat of sublimation unit.
    symbol : str
        The heat of sublimation symbol.
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)

    temperature: Temperature = Field(
        ...,
        description="The temperature at which the heat of sublimation is calculated."
    )

    value: float = Field(
        ...,
        description="The heat of sublimation value."
    )
    unit: str = Field(
        ...,
        description="The heat of sublimation unit."
    )
    symbol: str = Field(
        ...,
        description="The heat of sublimation symbol."
    )

# NOTE: mixture enthalpy result model


class MixtureEnthalpyResult(BaseModel):
    '''
    Mixture Enthalpy Result Model

    Attributes
    ----------
    temperature : Temperature
        The temperature at which the mixture enthalpy is calculated.
    pressure : Pressure
        The pressure at which the mixture enthalpy is calculated.
    phase : str
        The phase of the mixture ('IG' for ideal gas, 'LIQ' for liquid).
    value : float
        The mixture enthalpy value.
    unit : str
        The mixture enthalpy unit.
    symbol : str
        The mixture enthalpy symbol.
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)

    temperature: Temperature = Field(
        ...,
        description="The temperature at which the mixture enthalpy is calculated."
    )
    pressure: Pressure = Field(
        ...,
        description="The pressure at which the mixture enthalpy is calculated."
    )
    reference: str = Field(
        ...,
        description="The reference of the mixture ('IG' for ideal gas, 'LIQ' for liquid)."
    )
    value: float = Field(
        ...,
        description="The mixture enthalpy value."
    )
    unit: str = Field(
        ...,
        description="The mixture enthalpy unit."
    )
    symbol: str = Field(
        ...,
        description="The mixture enthalpy symbol."
    )
