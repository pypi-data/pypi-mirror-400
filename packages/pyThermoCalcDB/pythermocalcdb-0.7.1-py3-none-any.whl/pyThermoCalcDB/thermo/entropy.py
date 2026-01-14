# import libs
import logging
import numpy as np
from typing import Optional, Dict, Any, Tuple, Literal
from pythermodb_settings.models import Temperature
import pycuc
# locals

# NOTE: logger setup
logger = logging.getLogger(__name__)


# SECTION: entropy calculations using NASA 9-coefficient polynomial
# NOTE: calculate ideal gas entropy using NASA 9-coefficient polynomial

def S_IG_NASA9_polynomial(
    a1: float,
    a2: float,
    a3: float,
    a4: float,
    a5: float,
    a6: float,
    a7: float,
    b2: float,
    temperature: Temperature,
    temperature_range: Optional[tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    universal_gas_constant: float = 8.31446261815324,  # J/mol.K
    message: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Calculate the ideal gas entropy (S_IG) using NASA 9-coefficient polynomial coefficients. The NASA polynomial equation is defined as:

    S_IG(T) = R * ( -a1/(2*T^2) - a2/T + a3 ln T + a4 T + a5 T^2/2 + a6 T^3/3 + a7 T^4/4 + b2 )

    where S is the entropy at temperature T.

    Parameters
    ----------
    a1 : float
        NASA polynomial coefficient a1
    a2 : float
        NASA polynomial coefficient a2
    a3 : float
        NASA polynomial coefficient a3
    a4 : float
        NASA polynomial coefficient a4
    a5 : float
        NASA polynomial coefficient a5
    a6 : float
        NASA polynomial coefficient a6
    a7 : float
        NASA polynomial coefficient a7
    b2 : float
        NASA polynomial coefficient b2
    temperature : Temperature
        Temperature at which to calculate entropy defined in pythermodb_settings.models.Temperature, should be in Kelvin
    output_unit : Optional[str], optional
        Desired output unit for entropy (default is None, which returns J/mol.K)
    universal_gas_constant : float, optional
        Universal gas constant in J/mol.K (default is 8.31446261815324 J/mol.K)
    message : Optional[str], optional
        Optional message regarding the calculation

    Returns
    -------
    Optional[Dict[str, Any]]
        Result dictionary containing the calculated ideal gas entropy and related information, or None if an error occurs.
    """
    try:
        # SECTION: Input Validation
        # NOTE: extract temperature value in [K]
        T_value = temperature.value  # assuming temperature is in Kelvin
        T_unit = temperature.unit

        # >> check temperature unit
        if T_unit != "K":
            T_value = pycuc.convert_from_to(
                value=T_value, from_unit=T_unit, to_unit="K"
            )

        # NOTE: check temperature range validity
        if temperature_range is not None:
            T_low = temperature_range[0].value
            T_high = temperature_range[1].value
            T_low_unit = temperature_range[0].unit.strip()
            T_high_unit = temperature_range[1].unit.strip()

            # >> convert to K if necessary
            if T_low_unit != "K":
                T_low = pycuc.convert_from_to(
                    value=T_low, from_unit=T_low_unit, to_unit="K"
                )
            if T_high_unit != "K":
                T_high = pycuc.convert_from_to(
                    value=T_high, from_unit=T_high_unit, to_unit="K"
                )

            # >> check validity
            if not (T_low <= T_value <= T_high):
                logger.warning(
                    f"Temperature {T_value} K is out of the specified range [{T_low} K, {T_high} K]."
                )
                return None

        # NOTE: check coefficients
        coeffs = [a1, a2, a3, a4, a5, a6, a7, b2]
        for i, coeff in enumerate(coeffs):
            if not isinstance(coeff, (int, float)):
                logger.error(
                    f"Coefficient a{i+1} is not a valid number: {coeff}")
                return None

        # SECTION: calculate S using NASA 9-coefficient polynomial equation, temperature in K, and R in J/mol.K
        # S in J/mol.K
        S_value = universal_gas_constant * (
            -a1 / (2.0 * T_value**2)
            - a2 / T_value
            + a3 * np.log(T_value)
            + a4 * T_value
            + (a5 / 2.0) * T_value**2
            + (a6 / 3.0) * T_value**3
            + (a7 / 4.0) * T_value**4
            + b2
        )
        S_value = float(S_value)

        # set unit
        if output_unit is None:
            S_unit = "J/mol.K"
        else:
            # new unit
            S_unit = output_unit
            # convert
            S_value = pycuc.convert_from_to(
                value=S_value,
                from_unit="J/mol.K",
                to_unit=S_unit
            )

        # return result model
        res = {
            "result": {
                "value": S_value,
                "unit": S_unit,
                "symbol": "Ent_IG"
            },
            "message": message if message is not None else "Ideal gas entropy calculation using NASA-9 successful"
        }

        return res
    except Exception as e:
        logger.error(f"Error in ideal gas entropy calculation: {e}")
        return None


# NOTE: calculate entropy using NASA 9-coefficient integral polynomial at a given temperature range

def S_IG_NASA9_polynomial_range(
    a1: float,
    a2: float,
    a3: float,
    a4: float,
    a5: float,
    a6: float,
    a7: float,
    b2: float,
    T_low: Temperature,
    T_high: Temperature,
    T_points: int = 10,
    temperature_range: Optional[tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    universal_gas_constant: float = 8.31446261815324,  #
    message: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Calculate the integral ideal gas entropy (S_IG) over a temperature range using NASA 9-coefficient polynomial coefficients.

    Parameters
    ----------
    a1 : float
        NASA polynomial coefficient a1
    a2 : float
        NASA polynomial coefficient a2
    a3 : float
        NASA polynomial coefficient a3
    a4 : float
        NASA polynomial coefficient a4
    a5 : float
        NASA polynomial coefficient a5
    a6 : float
        NASA polynomial coefficient a6
    a7 : float
        NASA polynomial coefficient a7
    b2 : float
        NASA polynomial coefficient b2
    T_low : Temperature
        Lower temperature bound defined in pythermodb_settings.models.Temperature, should be in Kelvin
    T_high : Temperature
        Upper temperature bound defined in pythermodb_settings.models.Temperature, should be in Kelvin
    T_points : int, optional
        Number of temperature points to calculate within the range (default is 10)
    output_unit : Optional[str], optional
        Desired output unit for entropy (default is None, which returns J/mol.K)
    universal_gas_constant : float, optional
        Universal gas constant in J/mol.K (default is 8.31446261815324 J/mol.K)
    message : Optional[str], optional
        Optional message regarding the calculation

    Returns
    -------
    Optional[Dict[str, Any]]
        A dictionary containing the calculated ideal gas entropy values over the temperature range, or None if an error occurs.
    """
    try:
        # SECTION: generate temperature points between T_low and T_high
        T_low_value = T_low.value
        T_high_value = T_high.value
        T_low_unit = T_low.unit.strip()
        T_high_unit = T_high.unit.strip()

        # >> convert to K if necessary
        if T_low_unit != "K":
            T_low_value = pycuc.convert_from_to(
                value=T_low_value, from_unit=T_low_unit, to_unit="K"
            )
        if T_high_unit != "K":
            T_high_value = pycuc.convert_from_to(
                value=T_high_value, from_unit=T_high_unit, to_unit="K"
            )

        temperatures = np.linspace(T_low_value, T_high_value, T_points)

        # SECTION: calculate S at each temperature point
        entropy_results = []

        # loop over temperatures
        for T in temperatures:
            temp_obj = Temperature(value=T, unit="K")
            res = S_IG_NASA9_polynomial(
                a1, a2, a3, a4, a5, a6, a7, b2,
                temperature=temp_obj,
                temperature_range=temperature_range,
                output_unit=output_unit,
                universal_gas_constant=universal_gas_constant,
                message=None
            )

            # check result
            if res is None:
                entropy_results.append(0.0)  # append zero if error
                continue

            # set
            entropy_results.append(res["result"]['value'])

        # return result model
        res = {
            "result": {
                "values": {
                    "x": temperatures.tolist(),
                    "y": entropy_results,
                },
                "unit": output_unit if output_unit is not None else "J/mol.K",
                "symbol": "Ent_IG"
            },
            "message": message if message is not None else "Integral ideal gas entropy calculation over range using NASA-9 successful"
        }
        return res
    except Exception as e:
        logger.error(
            f"Error in integral ideal gas entropy range calculation: {e}")
        return None


# NOTE: delta S using NASA 9-coefficient polynomial between two temperatures

def dS_IG_NASA9_polynomial(
    a1: float,
    a2: float,
    a3: float,
    a4: float,
    a5: float,
    a6: float,
    a7: float,
    b2: float,
    T_initial: Temperature,
    T_final: Temperature,
    temperature_range: Optional[tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    universal_gas_constant: float = 8.31446261815324,  #
    message: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Calculate entropy change (dS_IG) between two temperatures using NASA 9-coefficient polynomial coefficients.
    """
    try:
        # SECTION: calculate S at initial temperature
        res_initial = S_IG_NASA9_polynomial(
            a1, a2, a3, a4, a5, a6, a7, b2,
            temperature=T_initial,
            temperature_range=temperature_range,
            output_unit=output_unit,
            universal_gas_constant=universal_gas_constant,
            message=None
        )
        if res_initial is None:
            return None

        S_initial = res_initial["result"]["value"]

        # SECTION: calculate S at final temperature
        res_final = S_IG_NASA9_polynomial(
            a1, a2, a3, a4, a5, a6, a7, b2,
            temperature=T_final,
            temperature_range=temperature_range,
            output_unit=output_unit,
            universal_gas_constant=universal_gas_constant,
            message=None
        )
        if res_final is None:
            return None

        S_final = res_final["result"]["value"]

        # SECTION: calculate entropy change
        delta_S = S_final - S_initial
        delta_S = float(delta_S)

        # set unit
        if output_unit is None:
            delta_S_unit = "J/mol.K"
        else:
            delta_S_unit = output_unit

        # return result model
        res = {
            "result": {
                "value": delta_S,
                "unit": delta_S_unit,
                "symbol": "dEnt_IG"
            },
            "message": message if message is not None else "Entropy change calculation using NASA-9 successful"
        }
        return res

    except Exception as e:
        logger.error(f"Error in entropy change calculation: {e}")
        return None


# SECTION: entropy calculations using Shomate equation

def S_IG_shomate(
    A: float,
    B: float,
    C: float,
    D: float,
    E: float,
    F: float,
    G: float,
    temperature: Temperature,
    temperature_range: Optional[tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    message: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Calculate the ideal gas entropy (S_IG) using Shomate equation coefficients. The Shomate equation is defined as:

    S_IG(T) = A*ln(t) + B*t + C*t^2/2 + D*t^3/3 - E/(2*t^2) + G, where t = T/1000

    where S is the entropy [J/mol.K] at temperature T [K].
    """
    try:
        # SECTION: Input Validation
        # NOTE: extract temperature value in [K]
        T_value = temperature.value  # assuming temperature is in Kelvin
        T_unit = temperature.unit

        # >> check temperature unit
        if T_unit != "K":
            T_value = pycuc.convert_from_to(
                value=T_value, from_unit=T_unit, to_unit="K"
            )
            T_unit = "K"

        # NOTE: check temperature range validity
        if temperature_range is not None:
            T_low = temperature_range[0].value
            T_high = temperature_range[1].value
            T_low_unit = temperature_range[0].unit.strip()
            T_high_unit = temperature_range[1].unit.strip()

            # >> convert to K if necessary
            if T_low_unit != "K":
                T_low = pycuc.convert_from_to(
                    value=T_low, from_unit=T_low_unit, to_unit="K"
                )
            if T_high_unit != "K":
                T_high = pycuc.convert_from_to(
                    value=T_high, from_unit=T_high_unit, to_unit="K"
                )

            # >> check validity
            if not (T_low <= T_value <= T_high):
                logger.warning(
                    f"Temperature {T_value} K is out of the specified range [{T_low} K, {T_high} K]."
                )
                return None

        # NOTE: check coefficients
        coeffs = [A, B, C, D, E, F, G]
        for i, coeff in enumerate(coeffs):
            if not isinstance(coeff, (int, float)):
                logger.error(
                    f"Coefficient {['A','B','C','D','E','F','G'][i]} is not a valid number: {coeff}")
                return None

        # SECTION: calculate S using Shomate equation, temperature in K
        # S in J/mol.K
        t = T_value / 1000.0

        S_value = (
            A * np.log(t) +
            B * t +
            C * t**2 / 2 +
            D * t**3 / 3 -
            E / (2.0 * t**2) +
            G
        )
        S_value = float(S_value)

        # set unit
        if output_unit is None:
            S_unit = "J/mol.K"
        else:
            # set new unit
            S_unit = output_unit
            # convert
            S_value = pycuc.convert_from_to(
                value=S_value,
                from_unit="J/mol.K",
                to_unit=S_unit
            )

        # return result model
        res = {
            "result": {
                "value": S_value,
                "unit": S_unit,
                "symbol": "Ent_IG"
            },
            "message": message if message is not None else "Ideal gas entropy calculation using Shomate equation successful"
        }

        return res
    except Exception as e:
        logger.error(f"Error in ideal gas entropy calculation: {e}")
        return None


# NOTE: calculate entropy using Shomate equation at a given temperature range

def S_IG_shomate_range(
    A: float,
    B: float,
    C: float,
    D: float,
    E: float,
    F: float,
    G: float,
    T_low: Temperature,
    T_high: Temperature,
    T_points: int = 10,
    temperature_range: Optional[tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    message: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Calculate the integral ideal gas entropy (S_IG) over a temperature range using Shomate equation coefficients.
    """
    try:
        # SECTION: generate temperature points between T_low and T_high
        T_low_value = T_low.value
        T_high_value = T_high.value
        T_low_unit = T_low.unit.strip()
        T_high_unit = T_high.unit.strip()

        # >> convert to K if necessary
        if T_low_unit != "K":
            T_low_value = pycuc.convert_from_to(
                value=T_low_value, from_unit=T_low_unit, to_unit="K"
            )

        if T_high_unit != "K":
            T_high_value = pycuc.convert_from_to(
                value=T_high_value, from_unit=T_high_unit, to_unit="K"
            )

        temperatures = np.linspace(T_low_value, T_high_value, T_points)

        # SECTION: calculate S at each temperature point
        entropy_results = []

        # loop over temperatures
        for T in temperatures:
            temp_obj = Temperature(value=T, unit="K")
            res = S_IG_shomate(
                A, B, C, D, E, F, G,
                temperature=temp_obj,
                temperature_range=temperature_range,
                output_unit=output_unit,
                message=None
            )

            # check result
            if res is None:
                entropy_results.append(0.0)  # append zero if error
                continue

            # set
            entropy_results.append(res["result"]['value'])

        # return result model
        res = {
            "result": {
                "values": {
                    "x": temperatures.tolist(),
                    "y": entropy_results,
                },
                "unit": output_unit if output_unit is not None else "J/mol.K",
                "symbol": "Ent_IG"
            },
            "message": message if message is not None else "Integral ideal gas entropy calculation over range using Shomate equation successful"
        }

        return res
    except Exception as e:
        logger.error(
            f"Error in integral ideal gas entropy range calculation: {e}")
        return None


# SECTION: entropy calculations using NASA 7-coefficient polynomial (NASA7)

def S_IG_NASA7_polynomial(
    a1: float,
    a2: float,
    a3: float,
    a4: float,
    a5: float,
    a6: float,
    a7: float,
    temperature: Temperature,
    temperature_range: Optional[tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    universal_gas_constant: float = 8.31446261815324,  # J/mol.K
    message: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Calculate ideal-gas entropy using NASA 7-coefficient polynomial.

    NASA7 relations (T in K):
        S/R = a1 ln T + a2*T + a3*T^2/2 + a4*T^3/3 + a5*T^4/4 + a7

    Notes
    -----
    - a6 is for enthalpy (a6/T), so it is not used for entropy.
    """
    try:
        # SECTION: Input Validation
        T_value = temperature.value
        T_unit = temperature.unit

        # >> convert to K if necessary
        if T_unit != "K":
            T_value = pycuc.convert_from_to(
                value=T_value, from_unit=T_unit, to_unit="K")

        # NOTE: check temperature range validity
        if temperature_range is not None:
            T_low = temperature_range[0].value
            T_high = temperature_range[1].value
            T_low_unit = temperature_range[0].unit.strip()
            T_high_unit = temperature_range[1].unit.strip()

            if T_low_unit != "K":
                T_low = pycuc.convert_from_to(
                    value=T_low, from_unit=T_low_unit, to_unit="K")
            if T_high_unit != "K":
                T_high = pycuc.convert_from_to(
                    value=T_high, from_unit=T_high_unit, to_unit="K")

            if not (T_low <= T_value <= T_high):
                logger.warning(
                    f"Temperature {T_value} K is out of the specified range [{T_low} K, {T_high} K]."
                )
                return None

        # NOTE: check coefficients (a6 kept for signature consistency)
        coeffs = [a1, a2, a3, a4, a5, a6, a7]
        for i, coeff in enumerate(coeffs):
            if not isinstance(coeff, (int, float)):
                logger.error(
                    f"Coefficient a{i+1} is not a valid number: {coeff}")
                return None

        # SECTION: calculate S using NASA7 entropy form
        S_value = universal_gas_constant * (
            a1 * np.log(T_value)
            + a2 * T_value
            + a3 * T_value**2 / 2.0
            + a4 * T_value**3 / 3.0
            + a5 * T_value**4 / 4.0
            + a7
        )
        S_value = float(S_value)

        # set unit
        if output_unit is None:
            S_unit = "J/mol.K"
        else:
            S_unit = output_unit
            S_value = pycuc.convert_from_to(
                value=S_value, from_unit="J/mol.K", to_unit=S_unit)

        return {
            "result": {"value": S_value, "unit": S_unit, "symbol": "Ent_IG"},
            "message": message if message is not None else "Ideal gas entropy calculation using NASA-7 successful",
        }

    except Exception as e:
        logger.error(f"Error in ideal gas entropy calculation (NASA7): {e}")
        return None


def S_IG_NASA7_polynomial_range(
    a1: float,
    a2: float,
    a3: float,
    a4: float,
    a5: float,
    a6: float,
    a7: float,
    T_low: Temperature,
    T_high: Temperature,
    T_points: int = 10,
    temperature_range: Optional[tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    universal_gas_constant: float = 8.31446261815324,
    message: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    try:
        # SECTION: generate temperature points
        T_low_value = T_low.value
        T_high_value = T_high.value
        T_low_unit = T_low.unit.strip()
        T_high_unit = T_high.unit.strip()

        if T_low_unit != "K":
            T_low_value = pycuc.convert_from_to(
                value=T_low_value, from_unit=T_low_unit, to_unit="K")
        if T_high_unit != "K":
            T_high_value = pycuc.convert_from_to(
                value=T_high_value, from_unit=T_high_unit, to_unit="K")

        temperatures = np.linspace(T_low_value, T_high_value, T_points)

        entropy_results = []
        for T in temperatures:
            temp_obj = Temperature(value=float(T), unit="K")
            res = S_IG_NASA7_polynomial(
                a1, a2, a3, a4, a5, a6, a7,
                temperature=temp_obj,
                temperature_range=temperature_range,
                output_unit=output_unit,
                universal_gas_constant=universal_gas_constant,
                message=None,
            )
            entropy_results.append(
                0.0 if res is None else res["result"]["value"])

        return {
            "result": {
                "values": {"x": temperatures.tolist(), "y": entropy_results},
                "unit": output_unit if output_unit is not None else "J/mol.K",
                "symbol": "Ent_IG",
            },
            "message": message if message is not None else "Integral ideal gas entropy over range using NASA-7 successful",
        }

    except Exception as e:
        logger.error(f"Error in NASA7 entropy range calculation: {e}")
        return None


def dS_IG_NASA7_polynomial(
    a1: float,
    a2: float,
    a3: float,
    a4: float,
    a5: float,
    a6: float,
    a7: float,
    T_initial: Temperature,
    T_final: Temperature,
    temperature_range: Optional[tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    universal_gas_constant: float = 8.31446261815324,
    message: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    try:
        res_initial = S_IG_NASA7_polynomial(
            a1, a2, a3, a4, a5, a6, a7,
            temperature=T_initial,
            temperature_range=temperature_range,
            output_unit=output_unit,
            universal_gas_constant=universal_gas_constant,
            message=None,
        )
        if res_initial is None:
            return None
        S_initial = res_initial["result"]["value"]

        res_final = S_IG_NASA7_polynomial(
            a1, a2, a3, a4, a5, a6, a7,
            temperature=T_final,
            temperature_range=temperature_range,
            output_unit=output_unit,
            universal_gas_constant=universal_gas_constant,
            message=None,
        )
        if res_final is None:
            return None
        S_final = res_final["result"]["value"]

        delta_S = float(S_final - S_initial)

        return {
            "result": {
                "value": delta_S,
                "unit": output_unit if output_unit is not None else "J/mol.K",
                "symbol": "dEnt_IG"
            },
            "message": message if message is not None else "Entropy change calculation using NASA-7 successful",
        }

    except Exception as e:
        logger.error(f"Error in entropy change calculation (NASA7): {e}")
        return None


# SECTION: General dispatcher for S_IG methods
S_IG_Method = Literal["NASA7", "NASA9", "Shomate"]


def _require_coeffs(coeffs: Dict[str, Any], required: Tuple[str, ...]) -> Optional[Dict[str, Any]]:
    missing = [k for k in required if k not in coeffs]
    if missing:
        logger.error(
            f"Missing coefficients for Ent_IG: {missing}. Required: {list(required)}")
        return None
    return {k: coeffs[k] for k in required}


def calc_Ent_IG(
    method: S_IG_Method,
    *,
    temperature: Temperature,
    temperature_range: Optional[Tuple[Temperature, Temperature]] = None,
    output_unit: Optional[str] = None,
    universal_gas_constant: float = 8.31446261815324,  # J/mol.K
    message: Optional[str] = None,
    **coeffs: Any,
) -> Optional[Dict[str, Any]]:
    """
    Dispatcher for ideal-gas entropy.
    Routes to:
    - S_IG_NASA7_polynomial(a1..a7, temperature=..., ...)
    - S_IG_NASA9_polynomial(a1..a7, b2, temperature=..., ...)
    - S_IG_shomate(A..G, temperature=..., ...)
    """
    try:
        if method == "NASA7":
            req = ("a1", "a2", "a3", "a4", "a5", "a6", "a7")
            pack = _require_coeffs(coeffs, req)
            if pack is None:
                return None
            return S_IG_NASA7_polynomial(
                pack["a1"], pack["a2"], pack["a3"], pack["a4"], pack["a5"], pack["a6"], pack["a7"],
                temperature=temperature,
                temperature_range=temperature_range,
                output_unit=output_unit,
                universal_gas_constant=universal_gas_constant,
                message=message,
            )

        if method == "NASA9":
            req = ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "b2")
            pack = _require_coeffs(coeffs, req)
            if pack is None:
                return None
            return S_IG_NASA9_polynomial(
                pack["a1"], pack["a2"], pack["a3"], pack["a4"], pack["a5"], pack["a6"], pack["a7"], pack["b2"],
                temperature=temperature,
                temperature_range=temperature_range,
                output_unit=output_unit,
                universal_gas_constant=universal_gas_constant,
                message=message,
            )

        if method == "Shomate":
            req = ("A", "B", "C", "D", "E", "F", "G")
            pack = _require_coeffs(coeffs, req)
            if pack is None:
                return None
            return S_IG_shomate(
                pack["A"], pack["B"], pack["C"], pack["D"], pack["E"], pack["F"], pack["G"],
                temperature=temperature,
                temperature_range=temperature_range,
                output_unit=output_unit,
                message=message,
            )

        # Should never hit due to method checks
        logger.error(f"Unsupported S_IG method: {method!r}")
        return None

    except Exception as e:
        logger.error(f"Error in S_IG dispatcher: {e}")
        return None
