"""Vary the OFF dipole moment with the applied field and tip rigidity held fixed."""

import argparse
import csv
from math import degrees, radians
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from catheter import centerline, equilibrium_angle


def run(args: argparse.Namespace) -> None:
    length = args.length_mm / 1000
    field = args.field_mt / 1000
    direction = radians(args.field_angle_deg)
    on_angle = equilibrium_angle(length, args.rigidity_nm2, args.on_moment_am2, field, direction)
    on_angle_deg = degrees(on_angle)
    on_y_mm = 1000 * centerline(length, on_angle, points=2)[-1][1]

    rows = []
    for percent in range(101):
        off_moment = args.on_moment_am2 * (percent / 100)
        off_angle = equilibrium_angle(length, args.rigidity_nm2, off_moment, field, direction)
        off_angle_deg = degrees(off_angle)
        off_y_mm = 1000 * centerline(length, off_angle, points=2)[-1][1]
        rows.append((
            percent, on_angle_deg, off_angle_deg, abs(on_angle_deg - off_angle_deg),
            on_y_mm, off_y_mm, abs(on_y_mm - off_y_mm),
        ))

    percentages, _, off_angles, _, _, off_positions, _ = zip(*rows)
    fig, (angle_axis, position_axis) = plt.subplots(
        2, 1, sharex=True, figsize=(8.2, 5.8), layout="constrained"
    )
    fig.suptitle(
        f"Residual OFF moment | {args.field_mt:g} mT at {args.field_angle_deg:g}°"
        f" | EI = {args.rigidity_nm2:.3g} N m²",
        fontweight="bold",
    )
    for axis, on_value, off_values, ylabel in (
        (angle_axis, on_angle_deg, off_angles, "Tip angle (°)"),
        (position_axis, on_y_mm, off_positions, "Lateral tip position (mm)"),
    ):
        axis.axhline(on_value, color="#2356a8", linewidth=2.4, label="ON")
        axis.plot(percentages, off_values, "--", color="#b95124", linewidth=2.4, label="OFF")
        axis.fill_between(percentages, on_value, off_values, color="#2356a8", alpha=0.10)
        axis.scatter(10, off_values[10], color="#b95124", zorder=3)
        axis.axvline(10, color="#666666", linestyle=":", linewidth=1)
        axis.set(ylabel=ylabel, xlim=(0, 100))
        axis.grid(alpha=0.25)
        axis.spines[["top", "right"]].set_visible(False)
    angle_axis.legend(frameon=False)
    position_axis.set_xlabel("Residual OFF moment (% of ON moment)")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output_dir / "residual_sweep.png", dpi=140)
    plt.close(fig)
    with (args.output_dir / "residual_sweep.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow((
            "off_moment_pct_of_on", "on_angle_deg", "off_angle_deg", "abs_angle_gap_deg",
            "on_tip_y_mm", "off_tip_y_mm", "abs_tip_y_gap_mm",
        ))
        writer.writerows(rows)

    _, _, off_at_ten, angle_gap, _, off_y_at_ten, _ = rows[10]
    print(f"ON tip angle: {on_angle_deg:.2f} deg")
    print(f"At 10% residual moment: OFF {off_at_ten:.2f} deg and {off_y_at_ten:.2f} mm laterally")
    print(f"Absolute ON–OFF angle gap at 10%: {angle_gap:.2f} deg")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length-mm", type=float, default=30)
    parser.add_argument("--rigidity-nm2", type=float, default=1e-6)
    parser.add_argument("--on-moment-am2", type=float, default=2e-3)
    parser.add_argument("--field-mt", type=float, default=40)
    parser.add_argument("--field-angle-deg", type=float, default=90)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()

    try:
        run(args)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
