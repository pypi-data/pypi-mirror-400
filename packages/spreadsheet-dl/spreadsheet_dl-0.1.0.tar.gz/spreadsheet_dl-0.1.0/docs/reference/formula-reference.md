# Consolidated Formula Reference

SpreadsheetDL provides domain-specific formulas across 11 scientific and engineering domains. This reference provides a comprehensive overview of all available formulas organized by domain.

## Quick Navigation

- [Physics](#physics)
- [Chemistry](#chemistry)
- [Biology](#biology)
- [Data Science](#data-science)
- [Finance](#finance)
- [Electrical Engineering](#electrical-engineering)
- [Mechanical Engineering](#mechanical-engineering)
- [Civil Engineering](#civil-engineering)
- [Environmental](#environmental)
- [Manufacturing](#manufacturing)
- [Education](#education)

---

## Physics

The Physics domain provides formulas for classical mechanics, electromagnetism, optics, and quantum mechanics.

### Mechanics (7 formulas)

| Formula             | Description                             | Arguments                           |
| ------------------- | --------------------------------------- | ----------------------------------- |
| `NEWTON_SECOND_LAW` | Calculate force (F = ma)                | mass, acceleration                  |
| `KINETIC_ENERGY`    | Calculate kinetic energy (KE = 0.5mv^2) | mass, velocity                      |
| `POTENTIAL_ENERGY`  | Calculate gravitational PE (PE = mgh)   | mass, height, [gravity]             |
| `WORK_ENERGY`       | Calculate work (W = Fd cos theta)       | force, distance, angle              |
| `MOMENTUM`          | Calculate momentum (p = mv)             | mass, velocity                      |
| `ANGULAR_MOMENTUM`  | Calculate angular momentum (L = Iw)     | moment_of_inertia, angular_velocity |
| `CENTRIPETAL_FORCE` | Calculate centripetal force             | mass, velocity, radius              |

### Electromagnetism (6 formulas)

| Formula           | Description                           | Arguments                        |
| ----------------- | ------------------------------------- | -------------------------------- |
| `COULOMB_LAW`     | Calculate electrostatic force         | charge1, charge2, distance, [k]  |
| `ELECTRIC_FIELD`  | Calculate electric field strength     | voltage, distance                |
| `MAGNETIC_FORCE`  | Calculate force on moving charge      | charge, velocity, B_field, angle |
| `FARADAY_LAW`     | Calculate induced EMF                 | turns, flux_change, time         |
| `LORENTZ_FORCE`   | Calculate total electromagnetic force | charge, E_field, v, B_field      |
| `POYNTING_VECTOR` | Calculate electromagnetic energy flux | E_field, H_field                 |

### Optics (6 formulas)

| Formula                  | Description                       | Arguments                      |
| ------------------------ | --------------------------------- | ------------------------------ |
| `SNELLS_LAW`             | Calculate refracted angle         | n1, theta1, n2                 |
| `LENS_MAKER_EQUATION`    | Calculate focal length            | n, R1, R2                      |
| `MAGNIFICATION_LENS`     | Calculate lens magnification      | image_dist, object_dist        |
| `BRAGG_LAW`              | Calculate X-ray diffraction       | order, wavelength, angle       |
| `THIN_FILM_INTERFERENCE` | Calculate optical path difference | n, thickness, [angle], [order] |
| `DIFFRACTION_GRATING`    | Calculate grating wavelength      | line_spacing, angle, [order]   |

### Quantum Mechanics (6 formulas)

| Formula                  | Description                       | Arguments                     |
| ------------------------ | --------------------------------- | ----------------------------- |
| `PLANCK_ENERGY`          | Calculate photon energy (E = hf)  | frequency, [h]                |
| `DE_BROGLIE_WAVELENGTH`  | Calculate matter wavelength       | momentum, [h]                 |
| `HEISENBERG_UNCERTAINTY` | Calculate minimum uncertainty     | delta_x, [hbar]               |
| `PHOTOELECTRIC_EFFECT`   | Calculate photoelectron KE        | frequency, work_function, [h] |
| `BOHR_RADIUS`            | Calculate electron orbital radius | n, [a0]                       |
| `RYDBERG_FORMULA`        | Calculate spectral wavelength     | n1, n2, [R]                   |

---

## Chemistry

The Chemistry domain provides formulas for thermodynamics, kinetics, and solutions.

### Thermodynamics (7 formulas)

| Formula              | Description                         | Arguments                      |
| -------------------- | ----------------------------------- | ------------------------------ |
| `GIBBS_FREE_ENERGY`  | Calculate Gibbs free energy         | enthalpy, temperature, entropy |
| `ENTHALPY_CHANGE`    | Calculate reaction enthalpy         | products_H, reactants_H        |
| `ENTROPY_CHANGE`     | Calculate entropy change            | final_S, initial_S             |
| `HEAT_CAPACITY`      | Calculate heat transfer             | mass, specific_heat, delta_T   |
| `HESS_LAW`           | Sum enthalpies for reaction path    | enthalpies_range               |
| `VAN_T_HOFF`         | Temperature dependence of K         | K1, delta_H, T1, T2            |
| `CLAUSIUS_CLAPEYRON` | Vapor pressure-temperature relation | P1, delta_H_vap, T1, T2        |

### Kinetics (7 formulas)

| Formula                  | Description                       | Arguments                     |
| ------------------------ | --------------------------------- | ----------------------------- |
| `RATE_LAW`               | Calculate reaction rate           | k, concentration, order       |
| `ARRHENIUS_EQUATION`     | Temperature dependence of rate    | A, Ea, T                      |
| `HALF_LIFE`              | Calculate reaction half-life      | k, [order]                    |
| `INTEGRATED_RATE_FIRST`  | First-order concentration         | C0, k, t                      |
| `INTEGRATED_RATE_SECOND` | Second-order concentration        | C0, k, t                      |
| `EQUILIBRIUM_CONSTANT`   | Calculate Keq from concentrations | products_conc, reactants_conc |
| `REACTION_QUOTIENT`      | Calculate Q for comparison to K   | products_conc, reactants_conc |

### Solutions (6 formulas)

| Formula            | Description                    | Arguments                 |
| ------------------ | ------------------------------ | ------------------------- |
| `MOLARITY`         | Calculate molar concentration  | moles, volume_L           |
| `DILUTION`         | Calculate dilution (M1V1=M2V2) | M1, V1, V2                |
| `PH_CALCULATION`   | Calculate pH from H+           | H_concentration           |
| `POH_CALCULATION`  | Calculate pOH from OH-         | OH_concentration          |
| `BUFFER_CAPACITY`  | Henderson-Hasselbalch          | pKa, acid_conc, base_conc |
| `OSMOTIC_PRESSURE` | Calculate osmotic pressure     | M, R, T, [i]              |

---

## Biology

The Biology domain provides formulas for molecular biology, ecology, biochemistry, and pharmacokinetics.

### Molecular Biology (5 formulas)

| Formula            | Description                        | Arguments                   |
| ------------------ | ---------------------------------- | --------------------------- |
| `DNA_MELTING_TEMP` | Calculate Tm for DNA               | length, GC_content          |
| `PROTEIN_MW`       | Calculate protein molecular weight | aa_sequence                 |
| `ENZYME_KINETICS`  | Michaelis-Menten kinetics          | Vmax, Km, substrate         |
| `COPY_NUMBER`      | PCR amplification                  | initial, cycles, efficiency |
| `GC_CONTENT`       | Calculate GC percentage            | G_count, C_count, total     |

### Ecology (5 formulas)

| Formula              | Description               | Arguments                    |
| -------------------- | ------------------------- | ---------------------------- |
| `POPULATION_GROWTH`  | Exponential growth        | N0, r, t                     |
| `CARRYING_CAPACITY`  | Logistic growth           | N0, r, K, t                  |
| `SPECIES_DIVERSITY`  | Shannon diversity index   | abundances_range             |
| `POPULATION_DENSITY` | Calculate density         | count, area                  |
| `MARK_RECAPTURE`     | Lincoln-Petersen estimate | marked, captured, recaptured |

### Pharmacokinetics (4 formulas)

| Formula           | Description               | Arguments                      |
| ----------------- | ------------------------- | ------------------------------ |
| `DRUG_CLEARANCE`  | Calculate clearance rate  | dose, AUC                      |
| `HALF_LIFE_ELIM`  | Elimination half-life     | Vd, clearance                  |
| `BIOAVAILABILITY` | Calculate bioavailability | AUC_oral, AUC_iv, [dose_ratio] |
| `STEADY_STATE`    | Time to steady state      | half_life, [fraction]          |

### Biochemistry (3 formulas)

| Formula           | Description                 | Arguments                        |
| ----------------- | --------------------------- | -------------------------------- |
| `PROTEIN_CONC`    | Beer-Lambert for proteins   | absorbance, extinction, path     |
| `ENZYME_ACTIVITY` | Calculate enzyme activity   | delta_product, time, enzyme_conc |
| `IC50`            | Calculate inhibitor potency | concentration, response, [Hill]  |

---

## Data Science

The Data Science domain provides formulas for statistics, regression, machine learning metrics, and clustering.

### Statistical (6 formulas)

| Formula              | Description               | Arguments              |
| -------------------- | ------------------------- | ---------------------- |
| `MEAN`               | Calculate arithmetic mean | values_range           |
| `MEDIAN`             | Calculate median          | values_range           |
| `VARIANCE`           | Calculate variance        | values_range, [sample] |
| `STANDARD_DEVIATION` | Calculate std dev         | values_range, [sample] |
| `CORRELATION`        | Pearson correlation       | x_range, y_range       |
| `COVARIANCE`         | Calculate covariance      | x_range, y_range       |

### Regression (5 formulas)

| Formula             | Description                  | Arguments                     |
| ------------------- | ---------------------------- | ----------------------------- |
| `LINEAR_REGRESSION` | Slope and intercept          | x_range, y_range              |
| `R_SQUARED`         | Coefficient of determination | predicted, actual             |
| `RESIDUAL`          | Calculate residual           | actual, predicted             |
| `MSE`               | Mean squared error           | actual_range, predicted_range |
| `RMSE`              | Root mean squared error      | actual_range, predicted_range |

### ML Metrics (5 formulas)

| Formula     | Description              | Arguments            |
| ----------- | ------------------------ | -------------------- |
| `ACCURACY`  | Classification accuracy  | TP, TN, FP, FN       |
| `PRECISION` | Classification precision | TP, FP               |
| `RECALL`    | Classification recall    | TP, FN               |
| `F1_SCORE`  | F1 score                 | precision, recall    |
| `AUC_ROC`   | Area under ROC curve     | TPR_range, FPR_range |

### Time Series (4 formulas)

| Formula          | Description               | Arguments            |
| ---------------- | ------------------------- | -------------------- |
| `MOVING_AVERAGE` | Calculate SMA             | values_range, window |
| `EXP_SMOOTHING`  | Exponential smoothing     | values_range, alpha  |
| `TREND`          | Calculate trend component | values_range         |
| `SEASONALITY`    | Calculate seasonal index  | values_range, period |

---

## Finance

The Finance domain provides formulas for time value of money, investments, and risk analysis.

### Time Value of Money (5 formulas)

| Formula         | Description             | Arguments                    |
| --------------- | ----------------------- | ---------------------------- |
| `PRESENT_VALUE` | Calculate PV            | future_value, rate, periods  |
| `FUTURE_VALUE`  | Calculate FV            | present_value, rate, periods |
| `NPV`           | Net present value       | rate, cashflows_range        |
| `IRR`           | Internal rate of return | cashflows_range              |
| `PMT`           | Calculate payment       | principal, rate, periods     |

### Investments (5 formulas)

| Formula        | Description                 | Arguments                              |
| -------------- | --------------------------- | -------------------------------------- |
| `ROI`          | Return on investment        | gain, cost                             |
| `CAGR`         | Compound annual growth rate | start_value, end_value, years          |
| `SHARPE_RATIO` | Risk-adjusted return        | return, risk_free, std_dev             |
| `BETA`         | Calculate portfolio beta    | asset_returns, market_returns          |
| `ALPHA`        | Jensen's alpha              | return, beta, market_return, risk_free |

### Depreciation (3 formulas)

| Formula | Description                | Arguments                   |
| ------- | -------------------------- | --------------------------- |
| `SLN`   | Straight-line depreciation | cost, salvage, life         |
| `DDB`   | Double declining balance   | cost, salvage, life, period |
| `SYD`   | Sum-of-years digits        | cost, salvage, life, period |

### Risk (2 formulas)

| Formula         | Description                   | Arguments                    |
| --------------- | ----------------------------- | ---------------------------- |
| `VAR`           | Value at Risk                 | returns_range, confidence    |
| `SORTINO_RATIO` | Downside risk-adjusted return | return, target, downside_dev |

---

## Electrical Engineering

The Electrical Engineering domain provides formulas for circuits, signal processing, and digital electronics.

### Power & Circuits (5 formulas)

| Formula          | Description       | Arguments                    |
| ---------------- | ----------------- | ---------------------------- |
| `OHMS_LAW`       | V = IR            | voltage, current, resistance |
| `POWER`          | P = VI            | voltage, current             |
| `IMPEDANCE`      | Complex impedance | R, XL, XC                    |
| `RESONANT_FREQ`  | LC resonance      | L, C                         |
| `QUALITY_FACTOR` | Q factor          | f0, bandwidth                |

### Signal Processing (5 formulas)

| Formula         | Description           | Arguments                 |
| --------------- | --------------------- | ------------------------- |
| `DECIBEL`       | Calculate dB          | P1, P2                    |
| `SNR`           | Signal-to-noise ratio | signal_power, noise_power |
| `BANDWIDTH`     | 3dB bandwidth         | f_upper, f_lower          |
| `SAMPLING_RATE` | Nyquist rate          | max_frequency             |
| `FILTER_CUTOFF` | RC filter cutoff      | R, C                      |

### Digital Electronics (5 formulas)

| Formula             | Description           | Arguments          |
| ------------------- | --------------------- | ------------------ |
| `BINARY_TO_DECIMAL` | Binary conversion     | binary_string      |
| `CLOCK_PERIOD`      | Period from frequency | frequency          |
| `PROPAGATION_DELAY` | Gate delay            | distance, velocity |
| `FANOUT`            | Logic fanout          | IOH, IIH           |
| `POWER_DISSIPATION` | CMOS power            | C, V, f            |

---

## Mechanical Engineering

The Mechanical Engineering domain provides formulas for stress analysis, dynamics, and fluid mechanics.

### Stress & Strain (6 formulas)

| Formula          | Description          | Arguments                    |
| ---------------- | -------------------- | ---------------------------- |
| `STRESS`         | Calculate stress     | force, area                  |
| `STRAIN`         | Calculate strain     | delta_L, L0                  |
| `YOUNGS_MODULUS` | E = stress/strain    | stress, strain               |
| `POISSON_RATIO`  | Lateral/axial strain | lateral_strain, axial_strain |
| `SHEAR_STRESS`   | Shear stress         | force, area                  |
| `TORSION`        | Torsional stress     | torque, radius, J            |

### Dynamics (5 formulas)

| Formula             | Description         | Arguments            |
| ------------------- | ------------------- | -------------------- |
| `ANGULAR_VELOCITY`  | Calculate omega     | theta, time          |
| `TORQUE`            | Calculate torque    | force, radius, angle |
| `MOMENT_OF_INERTIA` | I for rotation      | mass, radius         |
| `ROTATIONAL_KE`     | KE = 0.5 I omega^2  | I, omega             |
| `NATURAL_FREQUENCY` | Vibration frequency | k, m                 |

### Fluid Mechanics (5 formulas)

| Formula           | Description         | Arguments                            |
| ----------------- | ------------------- | ------------------------------------ |
| `REYNOLDS_NUMBER` | Flow regime         | density, velocity, length, viscosity |
| `BERNOULLI`       | Energy conservation | P, density, v, h                     |
| `FLOW_RATE`       | Q = A \* v          | area, velocity                       |
| `HEAD_LOSS`       | Darcy-Weisbach      | f, L, D, v                           |
| `PUMP_POWER`      | Hydraulic power     | Q, head, density                     |

---

## Civil Engineering

The Civil Engineering domain provides formulas for structural analysis, concrete design, and soil mechanics.

### Structural (4 formulas)

| Formula           | Description          | Arguments                |
| ----------------- | -------------------- | ------------------------ |
| `BEAM_DEFLECTION` | Calculate deflection | load, length, E, I       |
| `MOMENT_AREA`     | Calculate moment     | force, distance          |
| `SECTION_MODULUS` | S = I/c              | I, c                     |
| `SHEAR_FORCE`     | Calculate shear      | distributed_load, length |

### Concrete (4 formulas)

| Formula                | Description       | Arguments              |
| ---------------------- | ----------------- | ---------------------- |
| `COMPRESSIVE_STRENGTH` | fc from test      | load, area             |
| `REINFORCEMENT_RATIO`  | Steel ratio       | As, b, d               |
| `DEVELOPMENT_LENGTH`   | Bar development   | fy, fc, db             |
| `CRACK_WIDTH`          | Crack calculation | stress, cover, spacing |

### Soil Mechanics (4 formulas)

| Formula            | Description              | Arguments                      |
| ------------------ | ------------------------ | ------------------------------ |
| `BEARING_CAPACITY` | Ultimate bearing         | c, Nc, q, Nq, gamma, B, Ngamma |
| `SETTLEMENT`       | Consolidation settlement | Cc, H, e0, delta_sigma, sigma0 |
| `EFFECTIVE_STRESS` | Effective stress         | total_stress, pore_pressure    |
| `PERMEABILITY`     | Darcy's law              | Q, L, A, delta_h               |

---

## Environmental

The Environmental domain provides formulas for air quality, water quality, and ecological assessment.

### Air Quality (4 formulas)

| Formula           | Description         | Arguments                         |
| ----------------- | ------------------- | --------------------------------- |
| `AQI_CALCULATION` | Air Quality Index   | concentration, [pollutant]        |
| `EMISSION_RATE`   | Calculate emission  | flow, concentration, [efficiency] |
| `POLLUTION_INDEX` | Combined pollution  | pollutant1, [pollutant2], ...     |
| `DISPERSION`      | Gaussian dispersion | Q, u, sigma_y, sigma_z            |

### Water Quality (4 formulas)

| Formula               | Description               | Arguments                                      |
| --------------------- | ------------------------- | ---------------------------------------------- |
| `WATER_QUALITY_INDEX` | WQI calculation           | DO, BOD, pH, [turbidity]                       |
| `BOD_CALCULATION`     | Biochemical oxygen demand | initial_DO, final_DO, sample_vol, [bottle_vol] |
| `DISSOLVED_OXYGEN`    | DO saturation             | temperature, salinity                          |
| `COLIFORM_COUNT`      | MPN calculation           | positive_tubes                                 |

### Ecology (4 formulas)

| Formula             | Description         | Arguments        |
| ------------------- | ------------------- | ---------------- |
| `SHANNON_DIVERSITY` | Shannon index H'    | abundances_range |
| `SIMPSON_INDEX`     | Simpson's diversity | abundances_range |
| `SPECIES_RICHNESS`  | Count species       | abundances_range |
| `EVENNESS`          | Pielou's evenness   | H, S             |

### Sustainability (3 formulas)

| Formula                | Description         | Arguments                             |
| ---------------------- | ------------------- | ------------------------------------- |
| `CARBON_EQUIVALENT`    | CO2 equivalent      | mass, gas_type                        |
| `ECOLOGICAL_FOOTPRINT` | Calculate footprint | carbon_kg, [food], [housing]          |
| `SUSTAINABILITY_SCORE` | ESG score           | environmental, [social], [governance] |

---

## Manufacturing

The Manufacturing domain provides formulas for quality control, inventory, and lean manufacturing.

### Quality Control (4 formulas)

| Formula               | Description         | Arguments                     |
| --------------------- | ------------------- | ----------------------------- |
| `PROCESS_CAPABILITY`  | Cp and Cpk          | USL, LSL, mean, std_dev       |
| `CONTROL_LIMITS`      | UCL/LCL calculation | mean, std_dev, [n]            |
| `DEFECTS_PER_MILLION` | DPMO calculation    | defects, opportunities, units |
| `SIGMA_LEVEL`         | Process sigma       | DPMO                          |

### Inventory (4 formulas)

| Formula              | Description             | Arguments                             |
| -------------------- | ----------------------- | ------------------------------------- |
| `EOQ`                | Economic order quantity | demand, order_cost, holding_cost      |
| `REORDER_POINT`      | When to reorder         | daily_demand, lead_time, safety_stock |
| `SAFETY_STOCK`       | Safety inventory        | demand_std, lead_time, service_level  |
| `INVENTORY_TURNOVER` | Turnover ratio          | COGS, avg_inventory                   |

### Lean Manufacturing (4 formulas)

| Formula      | Description                     | Arguments                          |
| ------------ | ------------------------------- | ---------------------------------- |
| `TAKT_TIME`  | Customer demand rate            | available_time, demand             |
| `CYCLE_TIME` | Process cycle time              | total_time, units                  |
| `OEE`        | Overall equipment effectiveness | availability, performance, quality |
| `THROUGHPUT` | Production rate                 | units, time                        |

---

## Education

The Education domain provides formulas for grading, assessment, and learning analytics.

### Grading (9 formulas)

| Formula                 | Description         | Arguments                                     |
| ----------------------- | ------------------- | --------------------------------------------- |
| `GRADE_AVERAGE`         | Simple average      | grades_range, [exclude_zeros]                 |
| `WEIGHTED_GRADE`        | Weighted average    | grades_range, weights_range                   |
| `GRADE_CURVE`           | Apply curve         | grade, all_grades, method, [adjustment]       |
| `CURVE_GRADES`          | Distribution curve  | grade, all_grades, [target_mean], [target_sd] |
| `STANDARD_SCORE`        | Z-score             | grade, mean, std_dev                          |
| `PERCENTILE_RANK_GRADE` | Percentile position | grade, all_grades                             |
| `WEIGHTED_GPA`          | Credit-weighted GPA | grade_points, credits                         |
| `RUBRIC_SCORE`          | Rubric calculation  | scores, weights, [scale]                      |
| `PASS_FAIL_THRESHOLD`   | Binary pass/fail    | score, threshold                              |

### Assessment Theory (5 formulas)

| Formula                      | Description         | Arguments                   |
| ---------------------------- | ------------------- | --------------------------- |
| `KR20`                       | Kuder-Richardson 20 | n_items, sum_pq, variance   |
| `KR21`                       | Kuder-Richardson 21 | n_items, mean, variance     |
| `SPEARMAN_BROWN`             | Prophecy formula    | reliability, factor         |
| `STANDARD_ERROR_MEASUREMENT` | SEM                 | std_dev, reliability        |
| `TRUE_SCORE`                 | Estimate true score | observed, mean, reliability |

### Learning Analytics (8 formulas)

| Formula             | Description           | Arguments                    |
| ------------------- | --------------------- | ---------------------------- |
| `LEARNING_GAIN`     | Normalized gain       | pre_score, post_score        |
| `MASTERY_LEVEL`     | Mastery assessment    | score, threshold             |
| `ATTENDANCE_RATE`   | Attendance percentage | present, total               |
| `COMPLETION_RATE`   | Task completion       | completed, total             |
| `LEARNING_CURVE`    | Power law learning    | initial_time, trials, [rate] |
| `FORGETTING_CURVE`  | Ebbinghaus curve      | days, [strength]             |
| `SPACED_REPETITION` | Next review interval  | interval, ease, quality      |
| `MASTERY_LEARNING`  | Bloom 2-sigma         | baseline, [sigma], [sd]      |

### Content Analysis (5 formulas)

| Formula                | Description          | Arguments                          |
| ---------------------- | -------------------- | ---------------------------------- |
| `BLOOM_TAXONOMY_LEVEL` | Cognitive level      | score                              |
| `READABILITY_SCORE`    | Flesch-Kincaid       | words, sentences, syllables        |
| `CORRELATION`          | Variable correlation | x_range, y_range                   |
| `STANDARD_DEVIATION`   | Variability measure  | values_range                       |
| `TIME_ON_TASK`         | Carroll model        | time_spent, time_needed, [quality] |

---

## Usage Example

```python
from spreadsheet_dl.domains.physics import PhysicsDomainPlugin

# Initialize plugin
plugin = PhysicsDomainPlugin()
plugin.initialize()

# Get formula
KineticEnergyFormula = plugin.get_formula("KINETIC_ENERGY")

# Build formula
formula = KineticEnergyFormula()
result = formula.build("A1", "B1")  # mass in A1, velocity in B1
# Returns: "of:=0.5*A1*B1^2"
```

## See Also

- [Domain Plugin API](../api/domain-plugins.md)
- [Builder API](../api/builder.md)
- [MCP Tools Reference](mcp-tools-reference.md)
