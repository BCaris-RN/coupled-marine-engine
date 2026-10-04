# coupled-marine-engine (formerly in_your_dreams_2 renamed 10/04/2026)
Update for in_your_dreams (archived): coupled thermodynamic engine; 17 state planetary
Version 2 


# Changelog: Old Version to Current Coupled Marine Engine Suite


Date written: 2026-07-02  
Current branch: `codex/seawater-kw-total-scale`  
Current code commit: `688223dca1729e29d20e5c1fbf4ccd3479cb336a`


This changelog documents the workflow used by Brandon W. Caris, Gemini Pro,
and Codex/OpenAI to move the repository from the earlier separate-model
version into the current coupled marine feedback suite. It also explains the
science where the code makes a concrete implementation choice, and it marks
the parts that remain appropriate for graduate-level or peer-review debate.


The short version is this: the project began as separate equation-based
experiments for CFC air-sea exchange and marine halogen chemistry. The new
version turns those pieces into a reproducible three-application suite, then
adds a package-backed Paper 3 engine that joins physical ocean uptake,
halogen chemistry, pH-dependent aqueous chemistry, biology-driven CHBr3
production, and salinity/stratification effects into one 17-state integration.
The latest scientific correction replaces a pure-water `Kw(T) / [H+]`
hydrolysis pathway with a salinity-aware seawater ion-product calculation on
the Total pH Scale.


## 1. Collaboration Workflow


The collaboration had three distinct roles.


### Brandon W. Caris


Brandon served as scientific author, domain decision-maker, and final owner of
the model claims. The conceptual framing, research question, governing
license/citation language, and insistence that the outputs be useful for Paper
3 and open-science review came from Brandon. The assistants were used as
computational and editorial aids, not as scientific owners.


In practice, Brandon's role was to keep the target fixed:


- The models must stay transparent and equation-based.
- The applications must be reproducible from the command line.
- Numerical outputs must be reviewable as CSV, Markdown, and plots rather than
  opaque binary artifacts.
- The repo must preserve clear authorship and citation requirements.
- Scientific shortcuts must be called out instead of hidden.


### Gemini Pro


Gemini Pro functioned as an external reasoning and critique layer. Its value
in this workflow was not that its statements were treated as authoritative,
but that it helped surface places where the model language or physics could be
tightened before the code was finalized.


For this repository, the most important collaborative pattern was:


1. Use Gemini Pro or another model to pressure-test an assumption or wording.
2. Convert any useful criticism into a concrete scientific or software
   requirement.
3. Implement only the parts that could be expressed as equations, code,
   tests, documentation, or explicit interpretation boundaries.
4. Leave broader physical interpretation open when the simplified model could
   not settle the issue.


That distinction matters. The codebase should not claim that an AI assistant
"proved" the marine feedback theory. The assistants helped inspect, format,
challenge, and implement. The scientific claims remain Brandon's claims and
the code's claims must stand on the equations, tests, and documented limits.


### Codex/OpenAI


Codex acted as the repo-grounded implementation and verification assistant.
The work done here was practical software engineering:


- Inspect the actual repository layout before editing.
- Preserve the existing package structure rather than inventing a new one.
- Translate scientific requests into named functions, command-line runners,
  tests, generated artifacts, and documentation.
- Keep CFC, Halogens, and Coupled_Engine as related but separately runnable
  applications.
- Run package-local tests from each app environment instead of relying on an
  unreliable root environment.
- Report evidence: pass counts, generated files, and current code paths.


This role also included preventing scientific ambiguity from becoming hidden
software behavior. When a calculation used a counterfactual, pH scale,
salinity range, or interpretation boundary, the workflow aimed to make that
choice visible in code or documentation.


## 2. Old Version Starting Point


The old version can be understood as a collection of related prototypes rather
than a fully unified suite.


The CFC work already had the core idea of a temperature-attribution
experiment: compare an observed-SST run with a zero-anomaly counterfactual and
measure how warming shifts CFC-11 and CFC-12 air-sea flux. This was a strong
starting point because it used a controlled paired experiment rather than a
single unpaired simulation.


The Halogens work already had the core idea of a stiff marine boundary-layer
box model for CHBr3, Br, BrO, HO2, OH, and HOBr. This was also a strong
starting point because it treated radical chemistry as a system of coupled
ordinary differential equations rather than as disconnected algebraic
diagnostics.


The earlier Coupled_Engine state had the Paper 3 vision, but it still needed
hardening in several areas:


- It needed to behave like an installable Python package.
- It needed a command-line runner comparable to the CFC and Halogens apps.
- It needed reproducible output artifacts for Paper 3 and Zenodo-style review.
- It needed explicit matched counterfactuals for CFC inversion discrepancy and
  methane-lifetime distortion.
- It needed stronger tests around the physical and chemical assumptions.
- Its pH hydrolysis pathway used a pure-water ion-product approximation that
  was less appropriate for seawater forcing.


## 3. Phase One: CFC Air-Sea Flux Model


The first major scientific foundation was the CFC air-sea flux application.
The model asks a narrow attribution question:


How much did observed 2016-2025 sea-surface temperature anomalies shift CFC-11
and CFC-12 exchange toward the atmosphere, holding other drivers fixed?


That question is intentionally narrower than a full atmospheric inversion. It
does not claim to estimate all global CFC emissions. It asks whether a warming
mixed layer changes the ocean boundary condition enough to bias a top-down
accounting framework.


### Scientific structure


The CFC model uses a three-reservoir structure:


- Tropospheric atmospheric inventory.
- Marine mixed-layer dissolved inventory.
- Deep-ocean inventory.


The model uses a solubility-form Henry coefficient:


$$
H_{cp} = \frac{C_{\mathrm{aq}}}{p}
$$


where $C_{\mathrm{aq}}$ is aqueous concentration and $p$ is partial pressure. This
convention matters because the sign of the temperature response depends on
which Henry-law convention is used. The workflow explicitly documented the
Henry convention to avoid a common modeling error.


The air-sea flux is:


$$
F_{\mathrm{air\to sea}} =
k_{\mathrm{gas}} A
\left[H_{cp}(T,S)p_{\mathrm{air}} - C_{\mathrm{mixed}}\right]
$$


Positive $F_{\mathrm{air\to sea}}$ means ocean uptake. Negative flux means
outgassing.


The paired experiment then compares:


- Observed-SST case: temperature-dependent solubility is forced by observed
  SST anomaly history.
- Zero-anomaly case: SST anomalies are removed while all other assumptions are
  held fixed.


The difference is interpreted as the temperature-driven flux shift. In the
current documented nominal result, observed warming shifts flux toward the
atmosphere by about `0.3858 Gg` for CFC-11 and `0.1810 Gg` for CFC-12 over
2016-2025. This is described as a weakening of ocean uptake, not proof that
the global ocean became a net source.


### Workflow outcome


The CFC app was moved into `CFC/`, given package metadata, console commands,
tests, and generated review artifacts:


- `cfc-fetch-data`
- `cfc-run-model`
- `CFC/results/RESULTS.md`
- `CFC/results/summary.csv`
- `CFC/results/sensitivity.csv`
- `CFC/results/parameters.csv`
- `CFC/results/annual_fluxes.csv`
- `CFC/results/monthly_box_states.csv`
- `CFC/results/cumulative_flux.png`


This phase established a pattern for the rest of the repo: every scientific
claim should be paired with a reproducible command and a reviewable artifact.


## 4. Phase Two: Marine Halogen Boundary-Layer Model


The second foundation was the Halogens application.


The scientific question shifted from physical air-sea solubility to chemical
feedback:


Under continuous marine CHBr3 forcing, how does reactive bromine partition
among Br, BrO, and HOBr, and how does that perturb OH chemistry?


### Scientific structure


The model tracks six gas-phase species:


$$
\mathrm{CHBr_3},\ \mathrm{Br},\ \mathrm{BrO},\
\mathrm{HO_2},\ \mathrm{OH},\ \mathrm{HOBr}
$$


The state is stiff because fast radical chemistry and slower reservoir changes
occur in the same system. That is why the workflow used SciPy's implicit
Radau solver rather than a simple explicit time-stepper.


The core loss and cycling reactions are represented by:


$$
\begin{aligned}
L_{\mathrm{CHBr_3}} &=
\left(J_{\mathrm{CHBr_3}}
+ k_{\mathrm{OH+CHBr_3}}[\mathrm{OH}]
+ k_{\mathrm{Cl+CHBr_3}}[\mathrm{Cl}]\right)[\mathrm{CHBr_3}], \\
R_{\mathrm{BrO}} &= k_{\mathrm{Br+O_3}}[\mathrm{Br}][\mathrm{O_3}], \\
R_{\mathrm{HOBr}} &= k_{\mathrm{BrO+HO_2}}[\mathrm{BrO}][\mathrm{HO_2}], \\
P_{\mathrm{HOBr}} &= J_{\mathrm{HOBr}}[\mathrm{HOBr}], \\
D_{\mathrm{HOBr}} &= k_{\mathrm{term}}[\mathrm{HOBr}].
\end{aligned}
$$


The important correction in this phase was adding a terminal HOBr deposition
and washout sink. Without a terminal sink, the active bromine family can keep
accumulating in a way that looks chemically active but is not a physically
closed steady state. With the sink, the active bromine budget becomes:


$$
\frac{d\left([\mathrm{Br}] + [\mathrm{BrO}] + [\mathrm{HOBr}]\right)}{dt}
= 3J_{\mathrm{CHBr_3}}[\mathrm{CHBr_3}]
- k_{\mathrm{term}}[\mathrm{HOBr}]
$$


That identity became a regression-testable scientific invariant.


### Workflow outcome


The Halogens app was packaged as `Halogens/`, given a command-line run path,
tests, and output artifacts:


- `halogens-run`
- `Halogens/outputs/summary.txt`
- `Halogens/outputs/radical_trends.png`


The current documented scenario comparison shows:


- Marine anomaly ocean source is about `583.832%` higher than the cold
  baseline source.
- Equilibrated OH is about `25.665%` higher in the marine anomaly case.
- Both cases reach the strict steady-state criterion, but on different
  timescales.


The workflow also added an important interpretation boundary: this is a
conceptual box model, not a validated atmospheric abundance forecast.


## 5. Phase Three: Coupled_Engine Becomes the Paper 3 Engine


The third phase joined the physical CFC model and halogen chemistry into the
`Coupled_Engine` package.


This is where the repository moved from "two related prototypes" to a single
Paper 3 framework.


### Unified state vector


The Coupled_Engine integrates a 17-element state vector:


- CHBr3 gas.
- Br.
- BrO.
- HO2.
- OH.
- HOBr.
- Dissolved mixed-layer CHBr3.
- CFC-11 atmosphere, mixed layer, and deep ocean.
- CFC-11 cumulative air-to-sea flux and cumulative external forcing.
- CFC-12 atmosphere, mixed layer, and deep ocean.
- CFC-12 cumulative air-to-sea flux and cumulative external forcing.


All derivatives use seconds as the time base. Gas chemistry uses
$\mathrm{molecules\ cm^{-3}}$, dissolved CHBr3 uses
$\mathrm{mol\ m^{-3}}$, and CFC inventories use $\mathrm{mol}$.


### Three dynamic Paper 3 indices


The coupled model adds three time-dependent indices.


#### pH-dependent CHBr3 hydrolysis


The hydrolysis pathway represents base-catalyzed aqueous CHBr3 loss. The core
logic is:


$$
r_{\mathrm{hydrolysis}} =
k_{\mathrm{hydrolysis}}(T)[\mathrm{OH}^{-}]
$$


The Arrhenius coefficient controls temperature sensitivity:


$$
k_{\mathrm{hydrolysis}}(T) =
A \exp\left(-\frac{E_a}{RT}\right)
$$


The old version computed $[\mathrm{OH}^{-}]$ from a pure-water-style
$K_w(T) / [\mathrm{H}^{+}]$ expression. The new version now computes
$[\mathrm{OH}^{-}]$ using a salinity-aware seawater ion product on the Total
pH Scale. That final correction is described in detail in Section 8.


#### Chlorophyll-a-scaled CHBr3 production


The biological forcing represents a chlorophyll-linked source of dissolved
CHBr3:


$$
E =
1.127 \times 10^{5}
f_{\mathrm{species}}
M_{\mathrm{coastal}}
\mathrm{Chl}\text{-}\mathrm{a}
$$


The workflow kept this as a transparent scaling law instead of burying it
inside a larger empirical model. The code converts the surface emission flux
from $\mathrm{molecules\ cm^{-2}\ s^{-1}}$ into a mixed-layer source term in
$\mathrm{mol\ m^{-3}\ s^{-1}}$.


This is scientifically useful because chlorophyll-a is a proxy for marine
biological productivity, but it is also an obvious debate point. Chlorophyll
does not uniquely determine bromoform production everywhere; species
composition, light, nutrients, region, and physical ventilation all matter.
That is why the model treats the coefficient as a controlled parameterization,
not a final global emission inventory.


#### Haline stratification and gas-transfer damping


The model applies stratification damping to the Wanninkhof gas-transfer
velocity using a Gradient Richardson Number multiplier:


$$
M_{\mathrm{strat}} =
\left(1 + \gamma Ri_g\right)^{-0.35}
$$


The multiplier is fixed at 1 for $Ri_g \le 0$ and tends toward zero under strong
positive stratification.


The physical meaning is straightforward: stronger stable stratification
suppresses turbulent exchange across the upper ocean, so the model reduces
air-sea transfer velocity. The scholarly debate is not whether stratification
can suppress exchange. The debate is whether this particular global-box
scaling, exponent, and forcing treatment are sufficient for a given
inversion-use case.


### Counterfactual design


The coupled engine produces its main diagnostics through matched
counterfactuals:


- Full dynamic run: pH, chlorophyll, and stratification all active.
- No-stratification run: pH and chlorophyll remain active, but the Gradient
  Richardson Number effect is removed.
- No-pH/no-biology run: physical stratification remains active, but pH is
  fixed at the reference value and chlorophyll source is removed.


This design prevents the model from comparing unrelated simulations. Each
matrix isolates one class of effect while holding the rest of the system as
close as possible.


The CFC inversion discrepancy matrix compares cumulative CFC uptake between
the stratified and unstratified cases. The methane-lifetime distortion matrix
compares OH in the full dynamic chemistry run with OH in the no-pH/no-biology
counterfactual. Because methane oxidation is proportional to OH in this
proxy, the OH ratio becomes a local lifetime-distortion diagnostic.


### Workflow outcome


`Coupled_Engine` was converted into a package with:


- `Coupled_Engine/src/engine/__init__.py`
- `Coupled_Engine/src/engine/runner.py`
- `coupled-run-model = "engine.runner:main"`
- `Coupled_Engine/tests/test_engine.py`
- `Coupled_Engine/tests/test_runner.py`


The runner writes a Paper 3 validation bundle:


- `cfc_inversion_discrepancy_matrix.csv`
- `methane_lifetime_distortion_matrix.csv`
- `climate_accounting_error_matrix.csv`
- `unified_state_trajectory.csv`
- `parameters.csv`
- `summary.md`


The runner also records fallback provenance. If `data/ph`, `data/chlorophyll`,
or `data/salinity` CSVs are missing, it uses deterministic 60-day validation
forcing and says so in the generated summary and parameter table. This is
important because silent fallback would make the output look data-driven when
it was actually a deterministic validation run.


## 6. Phase Four: Repository Governance and Citation Control


After the scientific applications were in place, the workflow moved to
repo-level governance.


The current repo has:


- A root `LICENSE`.
- A root `CITATION.cff`.
- A DOI reference in citation metadata.
- Python source headers across CFC, Halogens, and Coupled_Engine.


The purpose was to prevent the three applications from drifting into separate
licensing and citation conventions. The suite is meant to be cited as one
governed research framework, even though the apps can be run separately.


This was not just formatting. For an open scientific codebase, license and
citation metadata are part of reproducibility. They tell downstream users what
they may do, how they must attribute the work, and which scholarly object they
are referencing.


## 7. Phase Five: Review, Critique, and Scientific Tightening


The most recent workflow step was a review-driven scientific tightening of
the pH hydrolysis calculation.


The old Coupled_Engine implementation had two useful pieces:


- It recognized that aqueous CHBr3 hydrolysis should depend on hydroxide.
- It represented the hydrolysis coefficient with an Arrhenius temperature
  dependence.


The weak point was the hydroxide calculation.


The old implementation used a pure-water ion-product function:


```text
water_ion_product_mol2_l2(T)
hydroxide = Kw(T) / [H+]
```


That is reasonable as a first thermodynamic scaffold, but it is not the best
fit for seawater forcing. Ocean pH observations are commonly reported on
marine pH scales, and seawater ionic strength changes the apparent ion
product. If salinity is already present in the forcing and already influences
CFC solubility and gas exchange, then ignoring salinity in the pH-to-OH
conversion leaves the chemical side less marine-aware than the physical side.


The review conclusion was therefore:


The pH hydrolysis pathway should use a seawater ion product on the Total pH
Scale and include salinity explicitly.


That became the latest code change.


## 8. Latest Code Change: Salinity-Aware Seawater Hydrolysis


Commit `688223d` implements the latest scientific correction:


```text
Add salinity-aware seawater hydrolysis
```


Files changed:


- `Coupled_Engine/src/engine/__init__.py`
- `Coupled_Engine/tests/test_engine.py`


### What changed in the model


The pure-water function was removed:


```text
water_ion_product_mol2_l2(T)
hydroxide_concentration_mol_l(ph, T)
```


The new functions are:


```text
seawater_ion_product_total_scale(temperature_k, salinity_psu)
hydroxide_concentration_mol_m3(ph_total, temperature_k, salinity_psu, density)
ph_scaled_hydrolysis_rate(ph_total, temperature_k, salinity_psu, config)
```


The new `seawater_ion_product_total_scale` implements the Millero-style
seawater ion product on the Total pH Scale:


$$
\ln(K_w^*) =
148.9652
- \frac{13847.26}{T}
- 23.6521 \ln(T)
+ \left(\frac{118.67}{T} - 5.977 + 1.0495 \ln(T)\right)\sqrt{S}
- 0.01615S
$$


where:


- `T` is temperature in Kelvin.
- `S` is salinity in PSU.
- $K_w^*$ is returned in $\left(\mathrm{mol\ kg^{-1}}\right)^2$ on a
  solution-mass basis.


The calculation then converts from $\mathrm{mol\ kg^{-1}}$ on a
solution-mass basis to volumetric concentration using seawater density:


$$
\begin{aligned}
[\mathrm{H}^{+}]_{\mathrm{mol\ kg^{-1}}}
&= 10^{-\mathrm{pH}_{\mathrm{total}}}, \\
[\mathrm{OH}^{-}]_{\mathrm{mol\ kg^{-1}}}
&= \frac{K_w^*}{[\mathrm{H}^{+}]_{\mathrm{mol\ kg^{-1}}}}, \\
[\mathrm{OH}^{-}]_{\mathrm{mol\ m^{-3}}}
&= [\mathrm{OH}^{-}]_{\mathrm{mol\ kg^{-1}}}\rho_{\mathrm{sw}}.
\end{aligned}
$$


Because the Arrhenius hydrolysis coefficient is in
$\mathrm{L\ mol^{-1}\ s^{-1}}$, the code converts the volumetric hydroxide
concentration from $\mathrm{mol\ m^{-3}}$ to $\mathrm{mol\ L^{-1}}$ before
the hydrolysis multiplication. This uses the volumetric relationship
$1\ \mathrm{m^3} = 1000\ \mathrm{L}$:


$$
\begin{aligned}
[\mathrm{OH}^{-}]_{\mathrm{mol\ L^{-1}}}
&= \frac{[\mathrm{OH}^{-}]_{\mathrm{mol\ m^{-3}}}}{1000}, \\
r_{\mathrm{hydrolysis}}
&= k_{\mathrm{hydrolysis}}(T)
[\mathrm{OH}^{-}]_{\mathrm{mol\ L^{-1}}}.
\end{aligned}
$$


This keeps the old Arrhenius chemistry intact while making the hydroxide term
consistent with seawater salinity and Total-scale pH.


### Why this matters scientifically


CHBr3 hydrolysis is base-catalyzed, so $[\mathrm{OH}^{-}]$ directly controls
the first-order aqueous loss rate. In a marine model, $[\mathrm{OH}^{-}]$ is
not just a function of temperature and pH. It also depends on the seawater ion
product, which changes with salinity and with the pH scale convention.


The old pure-water calculation treated the pH forcing as if it could be
converted to hydroxide without salinity. That made the model internally less
consistent because salinity was already used elsewhere in the same state
derivative:


- Warner-Weiss CFC solubility depends on salinity.
- CFC exchange uses salinity-aware equilibrium concentrations.
- Stratification is represented through a salinity-linked physical index.
- But CHBr3 hydrolysis did not yet receive salinity.


The new version closes that gap. Salinity now enters both the physical CFC
side and the aqueous chemistry side of the coupled model.


### What stayed the same


The correction did not change the entire Paper 3 architecture. These parts
remain the same:


- The 17-state vector.
- The Radau integration approach.
- The CHBr3 gas-phase radical mechanism.
- The chlorophyll-a CHBr3 source scaling.
- The Richardson-number gas-transfer damping.
- The CFC counterfactual matrix design.
- The methane-lifetime distortion matrix design.
- The command-line runner and output bundle.


This was a targeted thermodynamic correction, not a rewrite.


### New tests added


The current tests now verify the seawater chemistry directly:


- `test_kw_millero_pure_water_baseline` checks that the equation reproduces a
  pure-water baseline near `pKw = 14.001161` at 25 C.
- `test_kw_self_consistent_marine_amplification` checks that, at pH 8.1 and
  25 C, the S=35 calculation produces about `6.0805x` the S=0 hydroxide
  concentration under the same equation and density convention.
- `test_thermodynamic_bounds_safeguards` rejects temperatures and salinities
  outside the empirical seawater equation range.
- `test_hydroxide_rejects_nonpositive_density` rejects invalid density.
- `test_ph_shift_suppresses_hydroxide_hydrolysis_by_60_2_percent` was updated
  so the pH 7.7 versus 8.1 suppression check still runs through the new
  salinity-aware pathway.


The old 60.2% suppression result remains because the relative pH shift is
still dominated by the hydrogen ion ratio. The important change is the
absolute marine hydroxide scale, not the existence of pH sensitivity.


## 9. Verification Evidence


The current local verification from the package environments is:


```text
Coupled_Engine: 14 passed
CFC:            11 passed
Halogens:        4 passed
Total:          29 passed
```


The older full-suite target was 22 tests before the salinity-aware chemistry
tests expanded the Coupled_Engine coverage. The current suite now has 29
passing tests.


The verification philosophy used throughout this workflow was:


- Run each application in its own environment.
- Do not treat the root directory as the reliable Python environment.
- Check scientific invariants, not only import success.
- Keep generated outputs reviewable.
- Preserve fallback provenance when deterministic validation forcing is used.


## 10. What Is Implemented Versus What Remains Debate


Some parts of this repository are implemented model decisions. Other parts are
appropriate for PhD-level debate, peer review, or future sensitivity studies.


### Implemented model decisions


These are not left ambiguous in the current code:


- The CFC model uses solubility-form Henry coefficients.
- Positive CFC air-to-sea flux means ocean uptake.
- The CFC temperature effect is isolated by an observed-SST versus
  zero-anomaly counterfactual.
- The Halogens model includes a terminal HOBr sink.
- The active bromine budget is regression-tested.
- The Coupled_Engine integrates a 17-state system with Radau.
- The Coupled_Engine uses matched counterfactuals to isolate CFC
  stratification discrepancy and OH-driven methane-lifetime distortion.
- The latest hydrolysis pathway uses seawater `Kw*` on the Total pH Scale.
- The seawater ion-product function has explicit empirical range guards.
- The runner records when it falls back to deterministic validation forcing.


### Legitimate scholarly debate


The following points are intentionally not "settled" by the code:


- Whether a global or representative box model is sufficient for operational
  treaty verification.
- Whether the selected Richardson-number damping law is the best global
  parameterization of haline stratification.
- Whether the chlorophyll-a scaling coefficient is portable across regions,
  seasons, plankton communities, and ventilation regimes.
- Whether the fixed seawater density is adequate for all pH, temperature, and
  salinity regimes used in future forcing.
- Whether all pH input data are on the Total scale, or whether future loaders
  need explicit conversion among Total, Free, Seawater, and NBS scales.
- Whether a complete carbonate chemistry system should replace the direct
  `Kw* / [H+]` hydroxide calculation in a future version.
- Whether OH changes from this simplified halogen mechanism can be mapped to
  methane lifetime at policy-relevant scale without a 3D chemistry-transport
  model.
- Whether the Climate Accounting Error Matrix should be interpreted as a
  quantitative correction to atmospheric inversions or as a diagnostic warning
  about missing ocean feedbacks.


These debates are real because the model crosses scales:


- Radical chemistry can evolve on very short timescales.
- Mixed-layer and deep-ocean inventories evolve on much longer timescales.
- Atmospheric inversion systems interpret flux mismatches at regional to
  global policy scales.
- Ocean pH, biology, stratification, and gas exchange vary spatially.


The code can make the assumptions explicit and testable. It cannot, by itself,
replace observational validation, uncertainty propagation, or peer review.


## 11. Rationale for the Current Scientific Position


The current version takes a defensible middle position.


It does not claim to be an operational inversion system. It also does not stop
at a conceptual essay. Instead, it builds a transparent computational
framework showing how dynamic marine feedbacks can create accounting errors
when atmospheric inversion models treat the ocean as a static boundary.


That position is scientifically useful because it gives reviewers something
concrete to inspect:


- They can see the equations.
- They can run the scripts.
- They can inspect the CSV outputs.
- They can challenge the coefficients.
- They can replace the forcing.
- They can test alternative pH scales or stratification laws.
- They can decide whether the magnitude is robust enough for a manuscript,
  dissertation chapter, or operational model comparison.


In other words, the repository is strongest when presented as a reproducible
mechanism and diagnostic framework. It should not be framed as final proof
that all top-down inversions are wrong. The stronger claim is that uncoupled
marine boundary assumptions can create systematic accounting errors, and this
suite provides a transparent way to quantify and debate those errors.


## 12. Final State of the New Version


The current version is a three-application research suite:


```text
CFC/
    Temperature-driven CFC-11 and CFC-12 air-sea flux attribution.


Halogens/
    Stiff marine boundary-layer CHBr3 and reactive-bromine chemistry.


Coupled_Engine/
    Paper 3 coupled 17-state engine combining CFC physical exchange,
    halogen chemistry, pH hydrolysis, chlorophyll production, and
    salinity/stratification effects.
```


The latest Coupled_Engine chemistry now treats marine pH more appropriately
by using salinity-aware seawater `Kw*` rather than a pure-water ion product.
That is the most important final scientific difference between the immediate
old code version and the current code version.


For publication or archival release, the next responsible step is to rerun
`coupled-run-model` after the salinity-aware hydrolysis correction and then
review whether the generated `results/` CSV and Markdown artifacts should be
updated to reflect the new chemistry. The code and tests are updated now; the
stored result bundle should be treated as a generated artifact that may need
refreshing before being quoted as final output for this exact version.



