# import libs
import logging
from typing import List, Optional, Dict, Literal, cast
from pythermodb_settings.models import Component

# NOTE: logger setup
logger = logging.getLogger(__name__)


def map_component_state(
    component: Component,
    options: Dict[str, str] = {
        "g": "IG",
        "l": "LIQ",
        "s": "SOL",
    },
    **kwargs
) -> str:
    """
    Map the phase state for a single component.

    Parameters
    ----------
    component : Component
        A Component object.
    options : Dict[str, str], optional
        A dictionary mapping component states to phase states, by default { "g": "IG", "l": "LIQ", "s": "SOL" }.
    kwargs : additional keyword arguments
        Additional keyword arguments (not used).
        - phase_state_options : Dict[str, str], optional
            A dictionary to override the default options.

    Returns
    -------
    str
        The phase state of the component.
    """
    try:
        # SECTION: set default options
        options = {
            **options, **kwargs['phase_state_options']
        } if 'phase_state_options' in kwargs else options

        # SECTION: map component state
        # NOTE: get phase state from options
        phase_state = options.get(component.state.lower(), None)

        # NOTE: phase state found
        if phase_state is None:
            raise ValueError(
                f"Phase state not found for component state: {component.state}"
            )

        return phase_state
    except Exception as e:
        logger.error(f"Error setting component state: {e}")
        raise


def alter_component_formula_state(
        component_id: str,
        separator: str,
        state: str
) -> str:
    """
    Alter the state part of a component ID.

    Parameters
    ----------
    component_id : str
        The original component ID.
    separator : str, optional
        The separator used in the component ID.
    state : str
        The new state to set in the component ID.

    Returns
    -------
    str
        The modified component ID with the new state.
    """
    try:
        # SECTION: split component ID
        parts = component_id.strip().split(separator)

        # SECTION: alter state part
        if len(parts) > 1:
            parts[-1] = state
        else:
            parts.append(state)

        # SECTION: join parts back into component ID
        new_component_id = separator.join(parts)
        return new_component_id
    except Exception as e:
        logger.error(f"Error altering component state in ID: {e}")
        raise


def map_state_to_phase(
    state: str,
    options: Dict[str, str] = {
        "g": "IG",
        "l": "LIQ",
        "s": "SOL",
        "aq": "AQU",
    }
) -> str:
    """
    Map a component state to its corresponding phase.

    Parameters
    ----------
    state : str
        The state of the component (e.g., 'g', 'l', 's', 'aq').
    options : Dict[str, str], optional
        A dictionary mapping component states to phase states, by default { "g": "IG", "l": "LIQ", "s": "SOL", "aq": "AQU" }.

    Returns
    -------
    str
        The corresponding phase of the component.
    """
    try:
        # SECTION: map state to phase
        phase = options.get(state.lower(), None)

        # >> check phase
        if phase is None:
            raise ValueError(
                f"Phase not found for component state: {state}"
            )

        return phase
    except Exception as e:
        logger.error(f"Error mapping state to phase: {e}")
        raise
