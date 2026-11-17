# EPM Catheter Steering Simulator

A small Python simulation of how a uniform magnetic field bends a flexible catheter tip in a plane. The example compares two effective dipole moments representing the ON and OFF states of an electropermanent magnet (EPM).

![Steering angle versus applied field and catheter centerlines at 40 mT](field_sweep.png)

## Run the experiment

Use Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python experiment.py
python -m unittest discover -v
```

The experiment writes a plot and a CSV of tip angles and positions to `output/`. The committed [plot](field_sweep.png) and [CSV](field_sweep.csv) show the default run. Use `python experiment.py --help` to see all parameters. For example, this run reverses the field angle and sets the residual OFF moment to zero.

```bash
python experiment.py --field-angle-deg -60 --off-ratio 0 --output-dir output/reversed
```

## Model

The catheter tip is an inextensible flexible segment of length $L$ and uniform flexural rigidity $EI$. Its magnetic dipole points along the local tip tangent. The applied field has magnitude $B$ and angle $\phi$ relative to the clamped base. Under static equilibrium, the elastic and magnetic torques balance.

$$
\frac{EI}{L}\theta = mB\sin(\phi-\theta)
$$

The solver brackets the signed tip angle $\theta$ between the base tangent and the field direction for $|\phi| < 180^\circ$. The resulting centerline is a circular arc with curvature $\theta/L$.

Each EPM state is represented by a fixed effective dipole moment $m$. The switching pulse, magnetic hysteresis, field gradients, wall contact, and transient motion are outside the model. All parameter values are illustrative. The example uses a 30 mm segment, $EI=10^{-6}\,\mathrm{N\,m^2}$, an ON moment of $2\times10^{-3}\,\mathrm{A\,m^2}$, and a residual OFF moment of 10% of ON. No hardware measurements are used.

## Default result

The field points 90° from the base and increases from 0 to 40 mT.

| State at 40 mT | Tip angle | Lateral deflection |
| --- | ---: | ---: |
| ON | 62.82° | 14.86 mm |
| OFF | 13.38° | 3.49 mm |

The angle describes the tip tangent. Lateral deflection is the tip's distance from the undeformed axis in this plane.

## References

- Chautems et al., [Magnetic Continuum Device with Variable Stiffness for Minimally Invasive Surgery](https://doi.org/10.1002/aisy.201900086), Section 2.3.2. Source for the constant-curvature torque balance.
- Knaian, [Electropermanent Magnetic Connectors and Actuators](https://dspace.mit.edu/entities/publication/d65bb0a6-f490-40ba-b1dd-100bb2bfa0d8), MIT PhD thesis, 2010. Background on bistable electropermanent magnets.
