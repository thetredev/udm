# ../smoke_trace/smoke_trace.py
# Code taken and modified from: https://forums.sourcepython.com/viewtopic.php?f=20&t=2248

"""Provides a way to figure out whether or not a bullet flew through smoke before impact."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
#   Math
import math

# Source.Python
#   Entities
from entities.dictionary import EntityDictionary


# =============================================================================
# >> CONSTANTS
# =============================================================================
# Smoke radius defined within Counter-Strike: Source.
SMOKE_RADIUS = 155


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
smoke_instances = EntityDictionary()


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def is_line_blocked_by_smoke(start, end, bloat=1.0):
    """Checks if the line defined by the given 'start' and 'end' points is
    blocked by a smoke.

    Args:
        start (Vector): Starting point of the line.
        end (Vector): Ending point of the line.
        bloat (float): Used to fine-tune the radius of the smoke.

    Returns:
        bool: True if the line is blocked by a smoke, False otherwise.
    """
    smoke_radius_sq = SMOKE_RADIUS * SMOKE_RADIUS * bloat * bloat
    max_smoked_length = 0.7 * SMOKE_RADIUS
    total_smoked_length = 0.0

    line_dir = end - start
    line_length = line_dir.normalize()

    for smoke in smoke_instances.values():
        smoke_origin = smoke.origin

        to_grenade = smoke_origin - start
        along_dist = to_grenade.dot(line_dir)

        # Find the closest point to the 'smokegrenade_projectile' along the
        # line.
        if along_dist < 0:
            close = start
        elif along_dist >= line_length:
            close = end
        else:
            close = start + line_dir * along_dist

        to_close = close - smoke_origin
        length_sq = to_close.length_sqr

        # Does some part of the line go through the smoke?
        if length_sq < smoke_radius_sq:
            start_sq = to_grenade.length_sqr
            end_sq = (smoke_origin - end).length_sqr

            # Is the starting point inside the smoke?
            if start_sq < smoke_radius_sq:

                # Is the ending point inside the smoke?
                if end_sq < smoke_radius_sq:
                    # The whole line is inside the smoke.
                    total_smoked_length += (end - start).length
                else:
                    # The line starts inside the smoke, but ends up outside.
                    half_smoked_length = math.sqrt(smoke_radius_sq - length_sq)

                    if along_dist > 0:
                        # The line goes through the closest point.
                        total_smoked_length += half_smoked_length + (close - start).length
                    else:
                        # The line starts after the closest point.
                        total_smoked_length += half_smoked_length - (close - start).length

            # Is the ending point inside the smoke?
            elif end_sq < smoke_radius_sq:
                # The line starts outside the smoke, but ends up inside.
                half_smoked_length = math.sqrt(smoke_radius_sq - length_sq)

                v = end - smoke_origin
                if v.dot(line_dir) > 0:
                    # The line goes through the closest point.
                    total_smoked_length += half_smoked_length + (close - end).length

                else:
                    # The line ends before reaching the closest point.
                    total_smoked_length += half_smoked_length - (close - end).length

            else:
                # Both the starting and ending points are outside the smoke.
                smoked_length = 2.0 * math.sqrt(smoke_radius_sq - length_sq)
                total_smoked_length += smoked_length

            if total_smoked_length > max_smoked_length:
                return True, smoke

    return False, None
