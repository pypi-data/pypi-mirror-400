# import libs
import logging
from typing import Optional, Dict, Any, Tuple, Literal

from pythermodb_settings.models import Temperature
import pycuc

# local imports (same folder)
from enthalpy import calc_En_IG
from entropy import calc_Ent_IG

# NOTE: logger setup
logger = logging.getLogger(__name__)


# SECTION: Gibbs free energy calculations (ideal gas)
# NOTE:
#   G_IG(T) = H_IG(T) - T * S_IG(T)
# where:
#   - H_IG is ideal-gas enthalpy [J/mol]
#   - S_IG is ideal-gas entropy  [J/mol.K]
#   - T is temperature [K]
#
# This module focuses on a *single component* Gibbs free energy.


G_IG_Method = Literal["NASA7", "NASA9", "Shomate"]


def _to_kelvin(temperature: Temperature) -> float:
    """Return temperature value in K."""
    T_value = temperature.value
    T_unit = temperature.unit.strip()
    if T_unit != "K":
        T_value = pycuc.convert_from_to(
            value=T_value, from_unit=T_unit, to_unit="K")
    return float(T_value)


def GiFrEn_IG(
    method: G_IG_Method,
    *,
    temperature: Temperature,
    temperature_range: Optional[Tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    universal_gas_constant: float = 8.31446261815324,  # J/mol.K
    message: Optional[str] = None,
    **coeffs: Any,
) -> Optional[Dict[str, Any]]:
    """Calculate ideal-gas Gibbs free energy of a component at a temperature.

    Parameters
    ----------
    method:
        One of: "NASA7", "NASA9", "Shomate".
        This must match the coefficient set provided in **coeffs.

    temperature:
        Temperature object (will be converted to K if needed).

    temperature_range:
        Optional validity range. If provided and T is outside, returns None.

    output_unit:
        If None, returns "J/mol".
        Otherwise uses pycuc.convert_from_to for conversion.

    universal_gas_constant:
        Passed through to En_IG / S_IG where applicable.

    coeffs:
        Same coefficient names expected by En_IG and S_IG:
        - NASA9: a1..a7, b1 (enthalpy), b2 (entropy)
        - NASA7: a1..a7
        - Shomate: A..G

    Returns
    -------
    Dict with keys:
        result: {value, unit, symbol}
        message

    Notes
    -----
    - Internally forces H to J/mol and S to J/mol.K before computing G.
    - Gibbs here is the *ideal-gas* reference value (useful for ΔG° and Keq workflows).
    """
    try:
        # T in K
        T_k = _to_kelvin(temperature)

        # Optional: range check (convert bounds to K)
        if temperature_range is not None:
            T_low_k = _to_kelvin(temperature_range[0])
            T_high_k = _to_kelvin(temperature_range[1])
            if not (T_low_k <= T_k <= T_high_k):
                logger.warning(
                    f"Temperature {T_k} K is out of the specified range [{T_low_k} K, {T_high_k} K]."
                )
                return None

        # H in J/mol (force for unit consistency)
        H_res = calc_En_IG(
            method=method,
            temperature=Temperature(value=T_k, unit="K"),
            temperature_range=temperature_range,
            output_unit="J/mol",
            universal_gas_constant=universal_gas_constant,
            message=None,
            **coeffs,
        )
        if H_res is None:
            return None
        H = float(H_res["result"]["value"])  # J/mol

        # S in J/mol.K (force for unit consistency)
        S_res = calc_Ent_IG(
            method=method,
            temperature=Temperature(value=T_k, unit="K"),
            temperature_range=temperature_range,
            output_unit="J/mol.K",
            universal_gas_constant=universal_gas_constant,
            message=None,
            **coeffs,
        )
        if S_res is None:
            return None
        S = float(S_res["result"]["value"])  # J/mol.K

        # Gibbs in J/mol
        G_value = H - T_k * S
        G_value = float(G_value)

        # Output unit conversion
        if output_unit is None:
            G_unit = "J/mol"
        else:
            G_unit = output_unit
            G_value = pycuc.convert_from_to(
                value=G_value, from_unit="J/mol", to_unit=G_unit)

        return {
            "result": {"value": G_value, "unit": G_unit, "symbol": "GiFrEn_IG"},
            "message": message if message is not None else "Ideal gas Gibbs free energy calculation successful",
        }

    except Exception as e:
        logger.error(f"Error in ideal gas Gibbs free energy calculation: {e}")
        return None


def dGiFrEn_IG(
    method: G_IG_Method,
    *,
    T_initial: Temperature,
    T_final: Temperature,
    temperature_range: Optional[Tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    universal_gas_constant: float = 8.31446261815324,
    message: Optional[str] = None,
    **coeffs: Any,
) -> Optional[Dict[str, Any]]:
    """Calculate ideal-gas Gibbs free energy change between two temperatures.

    dG_IG = G_IG(T_final) - G_IG(T_initial)

    Default unit: J/mol.
    """
    try:
        G_i = GiFrEn_IG(
            method,
            temperature=T_initial,
            temperature_range=temperature_range,
            output_unit=output_unit,
            universal_gas_constant=universal_gas_constant,
            message=None,
            **coeffs,
        )
        if G_i is None:
            return None

        G_f = GiFrEn_IG(
            method,
            temperature=T_final,
            temperature_range=temperature_range,
            output_unit=output_unit,
            universal_gas_constant=universal_gas_constant,
            message=None,
            **coeffs,
        )
        if G_f is None:
            return None

        dG_value = float(G_f["result"]["value"] - G_i["result"]["value"])
        dG_unit = output_unit if output_unit is not None else "J/mol"

        return {
            "result": {"value": dG_value, "unit": dG_unit, "symbol": "dGiFrEn_IG"},
            "message": message if message is not None else "Ideal gas Gibbs free energy change calculation successful",
        }

    except Exception as e:
        logger.error(
            f"Error in ideal gas Gibbs free energy change calculation: {e}")
        return None
