"""Compare static catheter steering across a range of flexural rigidities."""

import argparse
import csv
from math import degrees, isfinite, log10, radians
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from catheter import equilibrium_angle


def run(args: argparse.Namespace) -> None:
    length = args.length_mm / 1000
    field = args.field_mt / 1000
    field_angle = radians(args.field_angle_deg)
    off_moment = args.on_moment_am2 * args.off_ratio
    log_min, log_max = log10(args.min_ei), log10(args.max_ei)
    rigidities = [args.min_ei]
    rigidities.extend(
        10 ** (log_min + (log_max - log_min) * i / (args.samples - 1))
        for i in range(1, args.samples - 1)
    )
    rigidities.append(args.max_ei)

    rows = []
    for ei in rigidities:
        on_angle = degrees(equilibrium_angle(length, ei, args.on_moment_am2, field, field_angle))
        off_angle = degrees(equilibrium_angle(length, ei, off_moment, field, field_angle))
        rows.append((ei, on_angle, off_angle, abs(on_angle - off_angle)))

    peak_ei, peak_on, peak_off, peak_gap = max(rows, key=lambda row: row[3])
    if peak_gap > 0:
        print(f"Largest sampled gap: {peak_gap:.2f} deg at EI = {peak_ei:.3g} N m^2")
        print(f"Tip angles at that sample: ON {peak_on:.2f} deg, OFF {peak_off:.2f} deg")
    else:
        print("ON and OFF angles coincide at every sampled rigidity.")

    _, on_angles, off_angles, gaps = zip(*rows)
    fig, (angles, difference) = plt.subplots(
        2, 1, sharex=True, figsize=(8.2, 5.8), layout="constrained"
    )
    fig.suptitle(
        f"Stiffness sweep | {args.field_mt:g} mT at {args.field_angle_deg:g}°"
        f" | OFF moment {args.off_ratio:.1%} of ON",
        fontweight="bold",
    )
    angles.semilogx(rigidities, on_angles, color="#2356a8", linewidth=2.4, label="ON")
    angles.semilogx(rigidities, off_angles, "--", color="#b95124", linewidth=2.4, label="OFF")
    angles.set_ylabel("Tip angle (°)")
    angles.legend(frameon=False)
    difference.semilogx(rigidities, gaps, color="#14766f", linewidth=2.4)
    difference.set(xlabel="Flexural rigidity EI (N m²)", ylabel="Absolute ON–OFF gap (°)")
    if peak_gap > 0:
        difference.scatter(peak_ei, peak_gap, color="#14766f", zorder=3,
                           label=f"Largest sampled gap: {peak_gap:.2f}°")
        difference.legend(frameon=False, loc="upper right")
    for axis in (angles, difference):
        axis.grid(alpha=0.25)
        axis.spines[["top", "right"]].set_visible(False)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output_dir / "stiffness_sweep.png", dpi=140)
    plt.close(fig)
    with (args.output_dir / "stiffness_sweep.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("ei_N_m2", "on_angle_deg", "off_angle_deg", "abs_angle_gap_deg"))
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-ei", type=float, default=1e-8, help="Minimum EI in N m².")
    parser.add_argument("--max-ei", type=float, default=1e-4, help="Maximum EI in N m².")
    parser.add_argument("--samples", type=int, default=401, help="Number of log-spaced samples.")
    parser.add_argument("--length-mm", type=float, default=30)
    parser.add_argument("--on-moment-am2", type=float, default=2e-3)
    parser.add_argument("--off-ratio", type=float, default=0.10)
    parser.add_argument("--field-mt", type=float, default=40)
    parser.add_argument("--field-angle-deg", type=float, default=90)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()

    if not 0 < args.min_ei < args.max_ei or not isfinite(args.max_ei):
        parser.error("EI bounds must be finite, positive, and increasing.")
    if args.samples < 2:
        parser.error("--samples must be at least 2.")
    if not 0 <= args.off_ratio <= 1:
        parser.error("--off-ratio must be between 0 and 1.")
    try:
        run(args)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
