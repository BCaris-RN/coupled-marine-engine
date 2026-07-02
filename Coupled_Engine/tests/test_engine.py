# ============================================================================
# Copyright (c) 2026 Brandon W. Caris. All rights reserved.
# Part of the Coupled Marine Engine Suite (in_your_dreams/Coupled_Engine)
# Licensed under CC BY 4.0 with Explicit Academic Citation Mandate.
# See master LICENSE file at repository root for full terms and string.
# ============================================================================
import numpy as np

from engine import (
    CoupledForcing,
    StateIndex,
    UnifiedConfig,
    chlorophyll_chbr3_emission_flux_molecule_cm2_s,
    hydroxide_concentration_mol_m3,
    initial_state,
    integrate_unified_state_vector,
    ph_scaled_hydrolysis_rate,
    seawater_ion_product_total_scale,
    stratification_multiplier,
    unified_derivatives,
)

DAY_S = 86_400.0


def make_forcing(
    *,
    days: int = 30,
    ph: float = 7.2,
    chlorophyll: float = 2.0,
    gradient_richardson_number: float = 1.0,
) -> CoupledForcing:
    time_s = np.arange(days + 1, dtype=float) * DAY_S
    size = time_s.size
    return CoupledForcing(
        time_s=time_s,
        sst_k=np.full(size, 288.15),
        air_temperature_k=np.full(size, 288.15),
        wind_speed_m_s=np.full(size, 8.0),
        salinity_psu=np.full(size, 35.0),
        gradient_richardson_number=np.full(
            size,
            gradient_richardson_number,
        ),
        ph=np.full(size, ph),
        chlorophyll_a_mg_m3=np.full(size, chlorophyll),
        cfc11_ppt=np.linspace(230.0, 228.0, size),
        cfc12_ppt=np.linspace(510.0, 507.0, size),
    )


def test_kw_millero_pure_water_baseline() -> None:
    """Verify Millero S=0 baseline at 25 C."""
    kw_pure = seawater_ion_product_total_scale(
        temperature_k=298.15,
        salinity_psu=0.0,
    )
    pkw_pure = -np.log10(kw_pure)

    assert np.isclose(pkw_pure, 14.001161, atol=5.0e-4)


def test_kw_self_consistent_marine_amplification() -> None:
    """Verify self-consistent Millero S=35/S=0 OH amplification."""
    oh_fresh = hydroxide_concentration_mol_m3(
        ph_total=8.1,
        temperature_k=298.15,
        salinity_psu=0.0,
        seawater_density_kg_m3=1025.0,
    )
    oh_marine = hydroxide_concentration_mol_m3(
        ph_total=8.1,
        temperature_k=298.15,
        salinity_psu=35.0,
        seawater_density_kg_m3=1025.0,
    )

    assert np.isclose(oh_marine / oh_fresh, 6.0805, atol=1.0e-3)


def test_thermodynamic_bounds_safeguards() -> None:
    """Reject values outside the seawater Kw empirical range."""
    with np.testing.assert_raises_regex(
        ValueError,
        "Temperature out of seawater validity range",
    ):
        seawater_ion_product_total_scale(
            temperature_k=350.0,
            salinity_psu=35.0,
        )

    with np.testing.assert_raises_regex(
        ValueError,
        "Salinity out of seawater validity range",
    ):
        seawater_ion_product_total_scale(
            temperature_k=298.15,
            salinity_psu=50.0,
        )


def test_hydroxide_rejects_nonpositive_density() -> None:
    with np.testing.assert_raises_regex(
        ValueError,
        "seawater density must be positive",
    ):
        hydroxide_concentration_mol_m3(
            ph_total=8.1,
            temperature_k=298.15,
            salinity_psu=35.0,
            seawater_density_kg_m3=0.0,
        )


def test_ph_shift_suppresses_hydroxide_hydrolysis_by_60_2_percent() -> None:
    config = UnifiedConfig()
    temperature_k = 288.15
    salinity_psu = 35.0

    acidic = ph_scaled_hydrolysis_rate(
        7.7,
        temperature_k,
        salinity_psu,
        config,
    )
    reference = ph_scaled_hydrolysis_rate(
        config.chbr3_hydrolysis_reference_ph,
        temperature_k,
        salinity_psu,
        config,
    )

    suppression_percent = (1.0 - acidic / reference) * 100.0
    assert np.isclose(suppression_percent, 60.2, atol=0.05)


def test_positive_richardson_number_damps_kw_asymptotically() -> None:
    config = UnifiedConfig()

    assert stratification_multiplier(1.0, config) < 1.0
    assert stratification_multiplier(0.0, config) == 1.0
    assert stratification_multiplier(-1.0, config) == 1.0
    assert stratification_multiplier(1.0e20, config) < 1.0e-6


def test_chlorophyll_adds_linearly_to_aqueous_chbr3_tendency() -> None:
    config = UnifiedConfig()
    low = make_forcing(chlorophyll=1.0)
    high = make_forcing(chlorophyll=3.0)
    state = initial_state(low, config)

    low_tendency = unified_derivatives(0.0, state, low, config)
    high_tendency = unified_derivatives(0.0, state, high, config)

    expected = (
        (
            chlorophyll_chbr3_emission_flux_molecule_cm2_s(3.0, config)
            - chlorophyll_chbr3_emission_flux_molecule_cm2_s(1.0, config)
        )
        * 1.0e4
        / 6.02214076e23
        / config.mixed_layer_depth_m
    )
    assert np.isclose(
        high_tendency[StateIndex.CHBR3_AQUEOUS]
        - low_tendency[StateIndex.CHBR3_AQUEOUS],
        expected,
        rtol=1.0e-12,
        atol=1.0e-20,
    )


def test_gas_phase_active_bromine_budget_is_preserved() -> None:
    config = UnifiedConfig()
    forcing = make_forcing()
    state = initial_state(forcing, config)
    state[:6] = (4.0e8, 2.0e5, 3.0e6, 1.0e7, 3.0e5, 7.0e6)

    tendency = unified_derivatives(0.0, state, forcing, config)
    active_bromine_tendency = (
        tendency[StateIndex.BR]
        + tendency[StateIndex.BRO]
        + tendency[StateIndex.HOBR]
    )
    expected = (
        3.0 * config.chbr3_photolysis_s * state[StateIndex.CHBR3_GAS]
        - config.hobr_termination_s * state[StateIndex.HOBR]
    )

    assert np.isclose(active_bromine_tendency, expected)


def test_unified_radau_run_returns_both_diagnostic_matrices() -> None:
    forcing = make_forcing(days=60)
    result = integrate_unified_state_vector(forcing)

    assert result.state.shape == (17, forcing.time_s.size)
    assert result.cfc_inversion_discrepancy_matrix.shape == (
        forcing.time_s.size,
        5,
    )
    assert result.methane_lifetime_distortion_matrix.shape == (
        forcing.time_s.size,
        6,
    )
    assert np.all(
        result.cfc_inversion_discrepancy_matrix[-1, 3:] > 0.0
    )
    assert result.methane_lifetime_distortion_matrix[-1, -1] < 0.0


def test_no_dynamic_indices_produce_zero_effect_matrices() -> None:
    config = UnifiedConfig()
    forcing = make_forcing(
        days=5,
        ph=config.chbr3_hydrolysis_reference_ph,
        chlorophyll=0.0,
        gradient_richardson_number=0.0,
    )
    result = integrate_unified_state_vector(forcing, config=config)

    np.testing.assert_allclose(
        result.cfc_inversion_discrepancy_matrix[:, 3:],
        0.0,
        rtol=0.0,
        atol=0.0,
    )
    np.testing.assert_allclose(
        result.methane_lifetime_distortion_matrix[:, -1],
        0.0,
        rtol=0.0,
        atol=0.0,
    )


def test_cfc_inventory_closes_against_external_forcing() -> None:
    forcing = make_forcing(days=20)
    start = initial_state(forcing)
    result = integrate_unified_state_vector(forcing, initial=start)

    for air, mixed, deep, external in (
        (
            StateIndex.CFC11_AIR,
            StateIndex.CFC11_MIXED,
            StateIndex.CFC11_DEEP,
            StateIndex.CFC11_CUMULATIVE_EXTERNAL,
        ),
        (
            StateIndex.CFC12_AIR,
            StateIndex.CFC12_MIXED,
            StateIndex.CFC12_DEEP,
            StateIndex.CFC12_CUMULATIVE_EXTERNAL,
        ),
    ):
        initial_inventory = start[air] + start[mixed] + start[deep]
        residual = (
            result.state[air]
            + result.state[mixed]
            + result.state[deep]
            - initial_inventory
            - result.state[external]
        )
        assert np.max(np.abs(residual)) < 0.05
