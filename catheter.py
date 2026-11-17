"""Static, planar deflection of a flexible tip with an axial magnetic dipole."""

from math import cos, isfinite, pi, sin


def equilibrium_angle(
    length_m: float,
    rigidity_nm2: float,
    moment_am2: float,
    field_t: float,
    field_angle_rad: float,
) -> float:
    """Return the signed tip angle in radians for a field in (-pi, pi)."""
    parameters = (length_m, rigidity_nm2, moment_am2, field_t, field_angle_rad)
    if not all(map(isfinite, parameters)):
        raise ValueError("All inputs must be finite.")
    if length_m <= 0 or rigidity_nm2 <= 0 or moment_am2 < 0 or field_t < 0:
        raise ValueError("Length and rigidity must be positive. Moment and field must be nonnegative.")
    if abs(field_angle_rad) >= pi:
        raise ValueError("Field angle must be strictly between -pi and pi radians.")

    actuation = moment_am2 * field_t * length_m / rigidity_nm2
    if not isfinite(actuation):
        raise ValueError("The dimensionless actuation ratio must be finite.")
    if actuation == 0 or field_angle_rad == 0:
        return 0.0

    # By symmetry, solve for a positive field angle and restore the sign.
    # The equilibrium lies between the base tangent and the field direction.
    field_angle = abs(field_angle_rad)
    lower, upper = 0.0, min(field_angle, actuation)
    for _ in range(60):
        angle = (lower + upper) / 2
        if angle < actuation * sin(field_angle - angle):
            lower = angle
        else:
            upper = angle

    angle = (lower + upper) / 2
    return angle if field_angle_rad > 0 else -angle


def centerline(
    length_m: float, tip_angle_rad: float, points: int = 100
) -> list[tuple[float, float]]:
    """Sample (x, y) in meters along a constant-curvature arc."""
    if not isfinite(length_m) or length_m <= 0 or not isfinite(tip_angle_rad):
        raise ValueError("Length must be positive and the tip angle must be finite.")
    if points < 2:
        raise ValueError("At least two sample points are required.")

    positions = []
    for index in range(points):
        distance = length_m * (index / (points - 1))
        half_angle = tip_angle_rad / 2 * (index / (points - 1))
        # Evaluate the straight limit without subtracting nearly equal cosines.
        sinc = sin(half_angle) / half_angle if half_angle else 1.0
        chord = distance * sinc
        positions.append((chord * cos(half_angle), chord * sin(half_angle)))
    return positions
