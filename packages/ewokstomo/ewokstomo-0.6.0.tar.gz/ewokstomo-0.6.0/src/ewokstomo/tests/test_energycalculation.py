import xraylib
import numpy as np
import pytest

from ewokstomo.tasks import energycalculation as ec

try:
    from ewokscore.missing_data import MissingData  # type: ignore[assignment]
except Exception:  # pragma: no cover - optional dependency in tests
    MissingData = None  # type: ignore[assignment]


def _bm_inputs(**overrides):
    base = {
        "TYPE_CALC": 0,
        "VER_DIV": 0,
        "MACHINE_NAME": "ESRF bending magnet",
        "RB_CHOICE": 0,
        "MACHINE_R_M": 25.0,
        "BFIELD_T": 0.8,
        "BEAM_ENERGY_GEV": 6.0,
        "CURRENT_A": 0.2,
        "HOR_DIV_MRAD": 1.0,
        "PHOT_ENERGY_MIN": 100.0,
        "PHOT_ENERGY_MAX": 200000.0,
        "NPOINTS": 2,
        "LOG_CHOICE": 1,
        "PSI_MRAD_PLOT": 1.0,
        "PSI_MIN": -1.0,
        "PSI_MAX": 1.0,
        "PSI_NPOINTS": 2,
        "FILE_DUMP": False,
    }
    base.update(overrides)
    return base


def _wiggler_inputs(**overrides):
    base = {
        "PHOT_ENERGY_MIN": 100.0,
        "PHOT_ENERGY_MAX": 400000.0,
        "NPOINTS": 3,
        "ENERGY": 6.0,
        "CURRENT": 200.0,
        "FIELD": 1,
        "NPERIODS": 1,
        "ULAMBDA": 0.15,
        "K": 22.591,
        "NTRAJPOINTS": 101,
        "FILE": "",
        "SLIT_FLAG": 1,
        "SLIT_D": 56.5,
        "SLIT_NY": 101,
        "SLIT_WIDTH_H_MM": 10.0,
        "SLIT_HEIGHT_V_MM": 5.0,
        "SLIT_CENTER_H_MM": 0.0,
        "SLIT_CENTER_V_MM": 0.0,
        "SHIFT_X_FLAG": 1,
        "SHIFT_X_VALUE": -0.002385,
        "SHIFT_BETAX_FLAG": 5,
        "SHIFT_BETAX_VALUE": 0.005,
        "TRAJ_RESAMPLING_FACTOR": 10000.0,
        "SLIT_POINTS_FACTOR": 3.0,
        "LOG_CHOICE": 1,
    }
    base.update(overrides)
    return base


def test_resolve_mu_density_element_auto_density():
    energies = np.array([10.0, 20.0], dtype=float)

    mu_over_rho, rho = ec._resolve_mu_density("Al", "?", energies)

    Z = xraylib.SymbolToAtomicNumber("Al")
    expected_mu = np.array([xraylib.CS_Total(Z, energy) for energy in energies])
    expected_rho = xraylib.ElementDensity(Z)

    assert rho == pytest.approx(expected_rho)
    np.testing.assert_allclose(mu_over_rho, expected_mu)


def test_resolve_mu_density_compound_uses_alias():
    energies = np.array([1.0, 2.0, 4.0], dtype=float)

    mu_over_rho, rho = ec._resolve_mu_density(" kapton ", None, energies)

    cname = ec._canonical_compound_name("kapton") or "Kapton Polyimide Film"
    data = xraylib.GetCompoundDataNISTByName(cname)
    Zs = data["Elements"]
    weights = data["massFractions"]
    expected = np.zeros_like(energies, dtype=float)
    for Z, wf in zip(Zs, weights):
        expected += wf * np.array([xraylib.CS_Total(int(Z), e) for e in energies])

    assert rho == pytest.approx(data["density"])
    np.testing.assert_allclose(mu_over_rho, expected)


def test_apply_attenuators_respects_order_duplicates():
    energy = np.array([5000.0, 12000.0])
    spectral_power = np.array([10.0, 20.0])
    flux = np.array([5.0, 5.0])
    rho_al = xraylib.ElementDensity(xraylib.SymbolToAtomicNumber("Al"))

    task = ec.ApplyAttenuators(
        inputs={
            "energy_eV": energy,
            "spectral_power": spectral_power,
            "flux": flux,
            "attenuators": {
                "first": {
                    "material": "Al",
                    "thickness_mm": 1.0,
                    "density_g_cm3": rho_al,
                },
            },
            "order": ["first", "first"],
        }
    )
    task.execute()

    single = ec._transmission("Al", 1.0, rho_al, energy)
    combined = single * single
    np.testing.assert_allclose(task.outputs.transmission, combined)
    np.testing.assert_allclose(
        task.outputs.attenuated_spectral_power,
        spectral_power * combined,
    )
    np.testing.assert_allclose(
        task.outputs.attenuated_flux,
        flux * combined,
    )


def test_apply_attenuators_without_flux():
    energy = np.array([8000.0, 30000.0])
    spectral_power = np.array([1.0, 2.0])
    rho_be = xraylib.ElementDensity(xraylib.SymbolToAtomicNumber("Be"))

    task = ec.ApplyAttenuators(
        inputs={
            "energy_eV": energy,
            "spectral_power": spectral_power,
            "attenuators": {
                "only": {
                    "material": "Be",
                    "thickness_mm": 2.0,
                    "density_g_cm3": rho_be,
                }
            },
        }
    )
    task.execute()

    transmission = ec._transmission("Be", 2.0, rho_be, energy)

    np.testing.assert_allclose(
        task.outputs.attenuated_spectral_power,
        spectral_power * transmission,
    )
    assert task.outputs.attenuated_flux is None


def test_apply_attenuators_missing_flux_sentinel():
    if MissingData is None:
        pytest.skip("MissingData sentinel not available")

    energy = np.array([6000.0, 10000.0])
    spectral_power = np.array([3.0, 4.0])
    rho_c = xraylib.ElementDensity(xraylib.SymbolToAtomicNumber("C"))

    task = ec.ApplyAttenuators(
        inputs={
            "energy_eV": energy,
            "spectral_power": spectral_power,
            "flux": MissingData(),
            "attenuators": {
                "only": {
                    "material": "C",
                    "thickness_mm": 1.5,
                    "density_g_cm3": rho_c,
                }
            },
        }
    )

    task.execute()

    transmission = ec._transmission("C", 1.5, rho_c, energy)
    np.testing.assert_allclose(
        task.outputs.attenuated_spectral_power,
        spectral_power * transmission,
    )
    assert task.outputs.attenuated_flux is None


def test_spectrum_stats_mean_and_peak():
    energy = np.array([100.0, 200.0, 300.0])
    flux = np.array([10.0, 0.0, 30.0])

    task = ec.SpectrumStats(inputs={"energy_eV": energy, "attenuated_flux": flux})
    task.execute()

    assert task.outputs.mean_energy_eV == pytest.approx(200.0)
    assert task.outputs.mean_idx == 1
    assert task.outputs.pic_idx == 0
    assert task.outputs.pic_energy_eV == pytest.approx(100.0)


def test_spectrum_stats_no_valid_entries():
    energy = np.array([0.0, np.nan])
    flux = np.array([1.0, 2.0])

    task = ec.SpectrumStats(inputs={"energy_eV": energy, "attenuated_flux": flux})
    task.execute()

    assert np.isnan(task.outputs.mean_energy_eV)
    assert task.outputs.mean_idx == -1
    assert np.isnan(task.outputs.pic_energy_eV)
    assert task.outputs.pic_idx == -1


def test_spectrum_stats_requires_matching_shapes():
    task = ec.SpectrumStats(
        inputs={
            "energy_eV": np.array([1.0]),
            "attenuated_flux": np.array([1.0, 2.0]),
        }
    )
    with pytest.raises(ValueError):
        task.run()


def test_canonical_compound_name_strips_and_lowercases():
    assert (
        ec._canonical_compound_name("  AIR ")
        == ec._canonical_compound_name("air")
        == "Air, Dry (near sea level)"
    )
    assert ec._canonical_compound_name("") is None


def test_is_missing_data_detects_runtime_free_sentinel():
    fake_missing = type("MissingData", (), {})()
    assert ec._is_missing_data(fake_missing) is True
    assert ec._is_missing_data(None) is False


def test_transmission_handles_zero_thickness():
    energy = np.array([1.0, 2.0, 3.0])
    np.testing.assert_allclose(
        ec._transmission("Al", 0.0, 2.7, energy), np.ones_like(energy)
    )


def test_resolve_mu_density_compound_parser_defaults_to_unit_density():
    energies = np.array([8.0, 12.0], dtype=float)

    mu_over_rho, rho = ec._resolve_mu_density("SiO2", "?", energies)

    parsed = xraylib.CompoundParser("SiO2")
    expected = np.zeros_like(energies)
    for Z, wf in zip(parsed["Elements"], parsed["massFractions"]):
        expected += wf * np.array([xraylib.CS_Total(int(Z), e) for e in energies])

    assert rho == pytest.approx(1.0)
    np.testing.assert_allclose(mu_over_rho, expected)


def test_resolve_mu_density_unknown_material_raises():
    with pytest.raises(ValueError):
        ec._resolve_mu_density("not-a-material", None, np.array([1.0]))


def test_compute_bm_spectrum_sorts_outputs(monkeypatch):
    def fake_bm(**kwargs):
        energy = np.array([200.0, 100.0])
        a6 = np.zeros((2, 8))
        a6[:, 5] = [20.0, 10.0]
        a6[:, 6] = [200.0, 100.0]
        a6[:, 7] = [2000.0, 1000.0]
        return a6, None, None, energy

    monkeypatch.setattr(ec, "xoppy_calc_bm", fake_bm)

    task = ec.ComputeBMSpectrum(
        inputs=_bm_inputs(PHOT_ENERGY_MIN=50.0, PHOT_ENERGY_MAX=250.0)
    )
    task.execute()

    np.testing.assert_allclose(task.outputs.energy_eV, [100.0, 200.0])
    np.testing.assert_allclose(task.outputs.flux, [10.0, 20.0])
    np.testing.assert_allclose(task.outputs.spectral_power, [100.0, 200.0])
    np.testing.assert_allclose(task.outputs.cumulated_power, [1000.0, 2000.0])


def test_compute_bm_spectrum_validates_inputs(monkeypatch):
    def fake_bm(**kwargs):
        energy = np.array([1.0])
        a6 = np.zeros((1, 8))
        return a6, None, None, energy

    monkeypatch.setattr(ec, "xoppy_calc_bm", fake_bm)

    task = ec.ComputeBMSpectrum(inputs=_bm_inputs(TYPE_CALC=1, VER_DIV=0))
    with pytest.raises(ValueError):
        task.run()

    task = ec.ComputeBMSpectrum(inputs=_bm_inputs(TYPE_CALC=0, VER_DIV=3))
    with pytest.raises(ValueError):
        task.run()


def test_compute_wiggler_spectrum_sorts_and_uses_defaults(monkeypatch):
    captured_kwargs = {}

    def fake_wiggler_on_aperture(**kwargs):
        captured_kwargs.update(kwargs)
        return (
            [30.0, 10.0, 20.0],
            [3.0, 1.0, 2.0],
            [300.0, 100.0, 200.0],
            [3000.0, 1000.0, 2000.0],
            None,
        )

    monkeypatch.setattr(ec, "xoppy_calc_wiggler_on_aperture", fake_wiggler_on_aperture)

    task = ec.ComputeWigglerSpectrum(
        inputs=_wiggler_inputs(
            PHOT_ENERGY_MIN=50.0,
            PHOT_ENERGY_MAX=150.0,
            LOG_CHOICE=0,
        )
    )
    task.execute()

    np.testing.assert_allclose(task.outputs.energy_eV, [10.0, 20.0, 30.0])
    np.testing.assert_allclose(task.outputs.flux, [1.0, 2.0, 3.0])
    np.testing.assert_allclose(task.outputs.spectral_power, [100.0, 200.0, 300.0])
    np.testing.assert_allclose(task.outputs.cumulated_power, [1000.0, 2000.0, 3000.0])

    assert captured_kwargs["PHOT_ENERGY_MIN"] == 50.0
    assert captured_kwargs["PHOT_ENERGY_MAX"] == 150.0
    assert captured_kwargs["SHIFT_X_VALUE"] == -0.002385
    assert captured_kwargs["NPOINTS"] == 3
