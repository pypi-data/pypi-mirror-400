# import libs
import logging
from typing import Dict, Literal, Optional, Any
from pyThermoDB.core import TableEquation
from pyThermoDB.models import EquationResult
import pycuc
from scipy import integrate
from pyThermoLinkDB.models.component_models import ComponentEquationSource
# locals
from ..configs.thermo_props import Cp_IG_INTEGRATION_UNIT

# NOTE: Logger
logger = logging.getLogger(__name__)


def Cp_integral(
    eq_src: ComponentEquationSource,
    T_ref: float,
    T: float,
    output_unit: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Integrate the heat capacity equation from T_ref to T (J/mol).
    The expression is as:

        ∫Cp dT from T_ref to T

    After integration, the unit will be energy per mole (e.g., J/mol).

    Parameters
    ----------
    eq_src : ComponentEquationSource
        The heat capacity equation to integrate.
    T_ref : float
        The reference temperature (lower limit of integration).
    T : float
        The target temperature (upper limit of integration).
    output_unit : Optional[str], optional
        The desired output unit for the integrated value, by default None. If None, the unit from the equation will be used.

    Returns
    -------
    Optional[Dict[str, Any]]
        The integrated heat capacity value, or None if an error occurs as:
        {
            'value': float,
            'unit': str
        }

    Notes
    -----
    output_unit is important because:
    - the heat capacity unit is defined, for example, as energy per mole per Kelvin (e.g., J/mol.K), so: the integrated value will be in energy per mole (e.g., J/mol), as a result.
    - If output_unit is None, the result will be in the unit defined by the heat capacity equation.
    """
    try:
        # SECTION: equation expression
        # NOTE: extract Cp equation
        # ! args
        eq_args = eq_src.args
        # ! arg symbols
        eq_arg_symbols = eq_src.arg_symbols
        # ! returns
        eq_returns = eq_src.returns
        # >> get return units
        returns_outer_key, returns_inner = next(
            iter(eq_returns.items())
        )
        eq_return_unit: str = returns_inner['unit']

        # ! return symbols
        eq_return_symbols = eq_src.return_symbols
        # ! equation
        Cp_eq = eq_src.source

        # NOTE: Cp integral
        # unit: [J/mol]
        # init unit_
        unit_ = None

        # scipy integrate method
        def integrand_1(T):
            '''
            Integral of Cp equation, unit: [J/mol]
            '''
            nonlocal unit_
            res_ = Cp_eq.cal(T=T)
            cal_ = res_.get('value', None)
            unit_ = res_.get('unit', None)  # ! get unit from equation

            # >> check
            if cal_ is None:
                logger.error(
                    f"Failed to calculate Cp for equation at T={T} K.")
                raise

            # >> check
            if (
                not isinstance(cal_, str) and
                not isinstance(cal_, float)
            ):
                logger.error(
                    f"Invalid Cp value at T={T} K: {cal_}")
                raise

            # >> check
            if unit_ is None:
                logger.error(
                    f"Equation does not have a unit for Cp at T={T} K.")
                raise

            return cal_

        # ! check integral
        function_integral = Cp_eq.body_integral

        # NOTE: calculate integral
        if function_integral:
            # calc
            # method 1 (still takes return unit from equation)
            _eq_Cp_integral = Cp_eq.cal_integral(
                T1=T_ref,
                T2=T
            )
        else:
            # calc
            # method 2 (still takes return unit from equation)
            _eq_Cp_integral, _ = integrate.quad(
                integrand_1,
                T_ref,
                T
            )

        # SECTION: check and convert unit
        # ! set when method 1 is used
        # >> check
        if unit_ is None:
            logger.warning(
                f"Equation does not have a unit for Cp integral.")
            unit_ = eq_return_unit  # ! fallback to equation return unit

        # >> check
        if _eq_Cp_integral is None:
            logger.error(
                f"Failed to calculate Cp integral from T={T_ref} K to T={T} K.")
            return None

        # TODO: FINALLY convert Cp equation to [J/mol.K] (after integration means the unit is [J/mol])
        # ! check output unit
        if output_unit is not None:
            if (
                output_unit == 'J/mol' or
                output_unit == 'j/mol'
            ):
                # >>> use `J/mol.K`` as default only for integration unit, the actual unit after integration should be `J/mol`
                _eq_Cp_integral = pycuc.to(
                    _eq_Cp_integral,
                    f"{unit_} => J/mol.K"
                )
            else:
                # >>> convert to desired unit
                _eq_Cp_integral = pycuc.to(
                    _eq_Cp_integral,
                    f"{unit_} => {output_unit}"
                )

        return {
            'value': _eq_Cp_integral,
            'unit': output_unit if output_unit is not None else unit_
        }
    except Exception as e:
        logger.error(
            f"Error integrating Cp equation from T={T_ref} K to T={T} K: {e}")
        return None


def Cp__RT_integral(
    eq_src: ComponentEquationSource,
    T_ref: float,
    T: float,
    R: float,
    R_unit: str = 'J/mol.K',
) -> Optional[Dict[str, Any]]:
    """
    Integrate the dimensionless heat capacity equation Cp/RT from T_ref to T.
    The expression is as:

        ∫(Cp/RT) dT from T_ref to T

    After integration, the unit will be dimensionless.

    Parameters
    ----------
    eq_src : ComponentEquationSource
        The heat capacity equation to integrate.
    T_ref : float
        The reference temperature (lower limit of integration).
    T : float
        The target temperature (upper limit of integration).
    R : float
        The universal gas constant.
    R_unit : str, optional
        The unit of the universal gas constant R, by default 'J/mol.K'.

    Returns
    -------
    Optional[Dict[str, Any]]
        The integrated dimensionless heat capacity value, or None if an error occurs.

    Notes
    -----
    output_unit is important because:
    - the heat capacity unit is defined, for example, as energy per mole per Kelvin (e.g., J/mol.K), so: the integrated value will be dimensionless when divided by RT.
    - as Cp and R normally have the same unit basis (energy per mole per Kelvin), the result of the integration Cp/RT is dimensionless.
    - so R_unit is needed to ensure compatibility between Cp and R units during calculation.
    - for better calculation performance, R is converted to the Cp unit before calculation.
    - the term Cp/RT is dimensionless, after integration, the result remains identical even if different units are used for Cp and R, as long as they are compatible.
    """
    try:
        # SECTION: equation expression
        # NOTE: extract Cp equation
        # ! args
        eq_args = eq_src.args
        # ! arg symbols
        eq_arg_symbols = eq_src.arg_symbols
        # ! returns
        eq_returns = eq_src.returns
        # >> get return units
        returns_outer_key, returns_inner = next(
            iter(eq_returns.items())
        )
        # ! return unit
        eq_return_unit: str = returns_inner['unit']
        # ! return symbols
        eq_return_symbols = eq_src.return_symbols
        # ! equation
        Cp_eq = eq_src.source

        # SECTION: Cp and R unit compatibility check
        # ! compatible unit check between Cp and R is done in the pycuc.to function
        # NOTE: compatibility unit
        # >> check Cp unit compatibility with R unit
        if eq_return_unit.lower() != R_unit.lower():
            # set R unit compatible with Cp unit
            R = pycuc.to(
                value=R,
                unit_conversion_block=f"{R_unit} => {eq_return_unit}"
            )

        # SECTION: integral [Cp/RT]
        # unit: [dimensionless]
        # init unit
        unit_ = None
        # scipy integrate method

        def integrand_0(T):
            '''
            Dimensionless integrand for Cp/RT calculation.
            '''
            # modify the nonlocal variable
            nonlocal unit_
            res_ = Cp_eq.cal(T=T)
            cal_ = res_.get('value', None)
            unit_ = res_.get('unit', None)

            # >> check
            if cal_ is None:
                logger.error(
                    f"Failed to calculate Cp for equation at T={T} K.")
                raise

            # >> check
            if not isinstance(cal_, str) and not isinstance(cal_, float):
                logger.error(
                    f"Invalid Cp value at T={T} K: {cal_}")
                raise

            # >> check
            if unit_ is None:
                logger.error(
                    f"Equation does not have a unit for Cp at T={T} K.")
                raise

            # NOTE: calculate Cp/RT
            res = cal_/(T*R)
            return res

        # ! check custom
        custom_integral = Cp_eq.custom_integral

        # SECTION: Calculate integral
        if custom_integral.get('Cp/RT', None) is not None:
            # calc
            # method 1 (custom)
            # >>> already takes return unit from equation and make a dimensionless unit
            _eq_Cp_integral_Cp__RT = Cp_eq.cal_custom_integral(
                'Cp/RT',
                T1=T_ref,
                T2=T
            )
        else:
            # calc
            # method 2 (scipy integrate)
            # >>> raise error if Cp unit is not compatible with R unit.
            _eq_Cp_integral_Cp__RT, _ = integrate.quad(
                integrand_0,
                T_ref,
                T
            )

        # SECTION: check and convert unit (not needed as the result is dimensionless)
        # >> check
        if _eq_Cp_integral_Cp__RT is None:
            logger.error(
                f"Failed to calculate Cp/RT integral from T={T_ref} K to T={T} K.")
            return None

        # TODO: FINALLY convert Cp equation to [J/mol.K]
        # NOTE: the unit after integration is dimensionless, so no need to convert
        # ! very important check output unit as Cp and R have different units

        return {
            'value': _eq_Cp_integral_Cp__RT,
            'unit': 'dimensionless'
        }
    except Exception as e:
        logger.error(
            f"Error integrating Cp/RT equation from T={T_ref} K to T={T} K: {e}")
        return None


def Cp__T_integral(
    eq_src: ComponentEquationSource,
    T_ref: float,
    T: float,
    output_unit: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Integrate the heat capacity equation Cp/T from T_ref to T (J/mol.K).
    The expression is as:

        ∫(Cp/T) dT from T_ref to T

    After integration, the unit will be energy per mole and temperature (e.g., J/mol.K).

    Parameters
    ----------
    eq_src : ComponentEquationSource
        The heat capacity equation to integrate.
    T_ref : float
        The reference temperature (lower limit of integration).
    T : float
        The target temperature (upper limit of integration).
    output_unit : Optional[str], optional
        The desired output unit for the integrated value, by default None. If None, the unit from the equation will be used.

    Returns
    -------
    Optional[Dict[str, Any]]
        The integrated heat capacity over temperature value, or None if an error occurs.

    Notes
    -----
    - the heat capacity unit is defined, for example, as energy per mole per Kelvin (e.g., J/mol.K), so: the integrated value will be in energy per mole (e.g., J/mol), as a result.
    """
    try:
        # SECTION: equation expression
        # NOTE: extract Cp equation
        # ! args
        eq_args = eq_src.args
        # ! arg symbols
        eq_arg_symbols = eq_src.arg_symbols
        # ! returns
        eq_returns = eq_src.returns
        # >> get return units
        returns_outer_key, returns_inner = next(
            iter(eq_returns.items()))
        eq_return_unit: str = returns_inner['unit']
        # ! return symbols
        eq_return_symbols = eq_src.return_symbols
        # ! equation
        Cp_eq = eq_src.source

        # SECTION: Cp/T integral
        # unit: [J/mol]
        # init unit_
        unit_ = None

        # scipy integrate method
        def integrand_2(T):
            '''
            Integral of Cp/T equation, unit: [J/mol.K]
            '''
            nonlocal unit_
            res_ = Cp_eq.cal(T=T)
            cal_ = res_.get('value', None)
            unit_ = res_.get('unit', None)  # ! get unit from equation

            # >> check
            if cal_ is None:
                logger.error(
                    f"Failed to calculate Cp for equation at T={T} K.")
                raise

            # >> check
            if (
                not isinstance(cal_, str) and
                not isinstance(cal_, float)
            ):
                logger.error(
                    f"Invalid Cp value at T={T} K: {cal_}")
                raise

            # >> check
            if unit_ is None:
                logger.error(
                    f"Equation does not have a unit for Cp at T={T} K.")
                raise

            return cal_/T

        # ! check custom
        custom_integral = Cp_eq.custom_integral

        # NOTE: calculate integral
        if custom_integral.get('Cp/T', None) is not None:
            # calc
            # method 1 (custom)
            # >>> already takes return unit from equation
            _eq_Cp_integral__T = Cp_eq.cal_custom_integral(
                'Cp/T',
                T1=T_ref,
                T2=T
            )
        else:
            # calc
            # method 2 (scipy integrate)
            _eq_Cp_integral__T, _ = integrate.quad(
                integrand_2,
                T_ref,
                T
            )

        # SECTION: check and convert unit
        # ! set when method 1 is used
        # check
        if unit_ is None:
            logger.warning(
                f"Equation does not have a unit for Cp/T integral.")
            unit_ = eq_return_unit  # ! fallback to equation return unit

        # >> check
        if _eq_Cp_integral__T is None:
            logger.error(
                f"Failed to calculate Cp/T integral from T={T_ref} K to T={T} K.")
            return None

        # to float
        _eq_Cp_integral__T = float(_eq_Cp_integral__T)

        # TODO: FINALLY convert integral to [J/mol.K]
        # ! check output unit
        if output_unit is not None:
            if (
                output_unit == 'J/mol.K' or
                output_unit == 'j/mol.K'
            ):
                # >>> use `J/mol.K`` as default only for integration
                _eq_Cp_integral__T = pycuc.to(
                    _eq_Cp_integral__T,
                    f"{unit_} => J/mol.K"
                )
            else:
                # >>> convert to desired unit
                _eq_Cp_integral__T = pycuc.to(
                    _eq_Cp_integral__T,
                    f"{unit_} => {output_unit}"
                )

        return {
            'value': _eq_Cp_integral__T,
            'unit': output_unit if output_unit is not None else unit_
        }
    except Exception as e:
        logger.error(
            f"Error integrating Cp/T equation from T={T_ref} K to T={T} K: {e}")
        return None


def calc_eq(
    eq_src: ComponentEquationSource,
    vars: Dict[str, Any],
    output_unit: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Calculate the value of an equation given its source and arguments.

    Parameters
    ----------
    eq_src : ComponentEquationSource
        The equation source to be calculated.
    vars : Dict[str, Any]
        A dictionary of variable names and their corresponding values to be used in the equation.
    output_unit : Optional[str], optional
        The desired output unit for the calculated value, by default None.

    Returns
    -------
    Optional[Dict[str, Any]]
        The result of the equation calculation, or None if an error occurs.
    """
    try:
        # SECTION: equation expression
        # NOTE: extract Cp equation
        # ! args
        eq_args = eq_src.args
        # ! arg symbols
        eq_arg_symbols = eq_src.arg_symbols
        # ! returns
        eq_returns = eq_src.returns
        # >> get return units
        returns_outer_key, returns_inner = next(
            iter(eq_returns.items())
        )
        eq_return_unit: str = returns_inner['unit']

        # ! return symbols
        eq_return_symbols = eq_src.return_symbols
        # ! equation
        equation = eq_src.source

        # SECTION: check all vars are provided
        for arg in eq_args:
            if arg not in vars:
                logger.error(
                    f"Missing argument '{arg}' for equation calculation.")
                raise ValueError(
                    f"Missing argument '{arg}' for equation calculation.")

        # SECTION: calculate equation
        res: EquationResult = equation.cal(**vars)

        # NOTE: value
        value = res['value']
        unit_ = res['unit']

        # >> check
        if value is None or unit_ is None:
            logger.error(
                f"Equation calculation returned None value or unit.")
            return None

        # >> check
        if not isinstance(value, (float, int)):
            logger.error(
                f"Equation calculation returned invalid value type: {type(value)}.")
            return None

        # SECTION: convert unit if needed
        if output_unit is not None:
            if (
                output_unit.lower() == unit_.lower()
            ):
                # >> same unit, no conversion needed
                pass
            else:
                # >>> convert to desired unit
                value = pycuc.to(
                    value,
                    f"{unit_} => {output_unit}"
                )
                unit_ = output_unit

        return {
            'value': value,
            'unit': unit_
        }
    except Exception as e:
        logger.error(
            f"Error calculating equation: {e}")
        return None
