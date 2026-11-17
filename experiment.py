"""Sweep field strength and compare two assumed EPM dipole states."""

import argparse
import csv
from math import degrees, isfinite, radians
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from catheter import centerline, equilibrium_angle


def run(args: argparse.Namespace) -> None:
    output = args.output_dir
    angle_rad = radians(args.field_angle_deg)
    length = args.length_mm / 1000
    states = (("ON", args.on_moment_am2, "#2356a8"),
              ("OFF", args.on_moment_am2 * args.off_ratio, "#b95124"))
    fields = [args.max_field_mt * (step / 40) for step in range(41)]
    rows = []
    fig, (response, shape) = plt.subplots(1, 2, figsize=(10, 4.1), layout="constrained")

    for state, moment, color in states:
        angles = [
            equilibrium_angle(length, args.rigidity_nm2, moment, field / 1000, angle_rad)
            for field in fields
        ]
        for field, angle in zip(fields, angles):
            x, y = centerline(length, angle, points=2)[-1]
            rows.append((state, field, degrees(angle), 1000 * x, 1000 * y))

        style = "-" if state == "ON" else "--"
        response.plot(fields, list(map(degrees, angles)), style, color=color,
                      linewidth=2.4, label=state)
        x, y = zip(*centerline(length, angles[-1]))
        shape.plot([1000 * value for value in x], [1000 * value for value in y],
                   style, color=color, linewidth=2.4, label=state)
        shape.scatter(1000 * x[-1], 1000 * y[-1], color=color, s=25, zorder=3)
        print(f"{state:>3} at {fields[-1]:g} mT: {degrees(angles[-1]):.2f} deg, "
              f"tip ({1000 * x[-1]:.2f}, {1000 * y[-1]:.2f}) mm")

    fig.suptitle(f"Static catheter steering | field direction {args.field_angle_deg:g}°",
                 fontweight="bold")
    response.set(title="Steering response", xlabel="Field strength (mT)", ylabel="Tip angle (°)")
    shape.set(title=f"Centerline at {fields[-1]:g} mT", xlabel="Axial position (mm)",
              ylabel="Lateral position (mm)", aspect="equal")
    for axis in (response, shape):
        axis.legend(frameon=False)
        axis.grid(alpha=0.25)
        axis.spines[["top", "right"]].set_visible(False)

    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / "field_sweep.png", dpi=140)
    plt.close(fig)
    with (output / "field_sweep.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("state", "field_mT", "tip_angle_deg", "tip_x_mm", "tip_y_mm"))
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length-mm", type=float, default=30)
    parser.add_argument("--rigidity-nm2", type=float, default=1e-6)
    parser.add_argument("--on-moment-am2", type=float, default=2e-3)
    parser.add_argument("--off-ratio", type=float, default=0.10,
                        help="OFF dipole moment as a fraction of ON (default: 0.10).")
    parser.add_argument("--max-field-mt", type=float, default=40)
    parser.add_argument("--field-angle-deg", type=float, default=90)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()

    if not 0 <= args.off_ratio <= 1:
        parser.error("--off-ratio must be between 0 and 1.")
    if not isfinite(args.max_field_mt) or args.max_field_mt < 0:
        parser.error("--max-field-mt must be finite and nonnegative.")
    try:
        run(args)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
