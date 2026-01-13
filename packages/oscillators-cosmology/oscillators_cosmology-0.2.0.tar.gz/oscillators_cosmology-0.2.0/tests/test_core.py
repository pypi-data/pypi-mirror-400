"""
Тесты для модуля core.py - базовых типов и структур данных.
"""

import pytest
import numpy as np
from oscillators.core import (
    SpinType, ParticleType, Particle, QuantumOscillator,
    PhysicalConstants, get_particle_mass, get_particle_spin,
    get_particle_lifetime, fermi_dirac, bose_einstein,
    planck_distribution, thermal_energy_density
)


class TestSpinType:
    """Тесты для SpinType enum."""
    
    def test_spin_values(self):
        """Проверка значений спинов."""
        assert SpinType.SCALAR.value == 0
        assert SpinType.SPINOR.value == 0.5
        assert SpinType.VECTOR.value == 1
        assert SpinType.TENSOR.value == 2
    
    def test_spin_is_boson(self):
        """Проверка, что целые спины — бозоны."""
        bosons = [SpinType.SCALAR, SpinType.VECTOR, SpinType.TENSOR]
        for spin in bosons:
            assert spin.value == int(spin.value), f"{spin} должен быть бозоном"
    
    def test_spin_is_fermion(self):
        """Проверка, что полуцелые спины — фермионы."""
        assert SpinType.SPINOR.value == 0.5
        assert SpinType.SPINOR.value != int(SpinType.SPINOR.value)


class TestParticleType:
    """Тесты для ParticleType enum."""
    
    def test_particle_types_exist(self):
        """Проверка существования всех типов частиц."""
        expected_types = ['inflaton', 'photon', 'quark', 'lepton', 'dark_matter', 'higgs']
        for ptype in ParticleType:
            assert ptype.value in expected_types
    
    def test_particle_type_values(self):
        """Проверка значений типов частиц."""
        assert ParticleType.PHOTON.value == 'photon'
        assert ParticleType.QUARK.value == 'quark'
        assert ParticleType.DARK_MATTER.value == 'dark_matter'


class TestParticle:
    """Тесты для класса Particle."""
    
    def test_particle_creation(self, sample_particle):
        """Тест создания частицы."""
        assert sample_particle.type == ParticleType.QUARK
        assert sample_particle.energy == 1.0
        assert sample_particle.spin == 0.5
        assert sample_particle.antiparticle is False
    
    def test_antiparticle_creation(self, sample_antiparticle):
        """Тест создания античастицы."""
        assert sample_antiparticle.antiparticle is True
        assert sample_antiparticle.type == ParticleType.QUARK
    
    def test_photon_creation(self, sample_photon):
        """Тест создания фотона."""
        assert sample_photon.type == ParticleType.PHOTON
        assert sample_photon.spin == 1.0
        assert sample_photon.antiparticle is False
    
    def test_particle_mass_property(self, sample_particle):
        """Тест вычисления массы из E² = p² + m²."""
        E = sample_particle.energy
        p = np.linalg.norm(sample_particle.momentum)
        expected_mass = np.sqrt(max(0, E**2 - p**2))
        assert abs(sample_particle.mass - expected_mass) < 1e-10
    
    def test_particle_velocity_property(self, sample_particle):
        """Тест вычисления скорости v = p/E."""
        expected_velocity = sample_particle.momentum / sample_particle.energy
        np.testing.assert_array_almost_equal(sample_particle.velocity, expected_velocity)
    
    def test_photon_is_massless(self, sample_photon):
        """Тест, что фотон безмассовый (в пределах точности)."""
        # Для фотона E = |p|, масса должна быть ~0
        assert sample_photon.mass < 0.01
    
    def test_particle_str(self, sample_particle):
        """Тест строкового представления."""
        s = str(sample_particle)
        assert 'quark' in s
        assert 'E=' in s
    
    def test_antiparticle_str(self, sample_antiparticle):
        """Тест строкового представления античастицы."""
        s = str(sample_antiparticle)
        assert 'anti-' in s
    
    def test_is_decayed_stable_particle(self, sample_photon):
        """Тест, что стабильная частица не распадается."""
        # Фотоны стабильны
        assert sample_photon.is_decayed(1e10) is False
    
    def test_particle_with_custom_lifetime(self):
        """Тест частицы с заданным временем жизни."""
        particle = Particle(
            type=ParticleType.HIGGS,
            energy=125.0,
            momentum=np.array([0.0, 0.0, 0.0]),
            position=np.array([0.0, 0.0, 0.0]),
            spin=0,
            creation_time=0.0,
            lifetime=1e-3
        )
        assert particle.lifetime == 1e-3


class TestQuantumOscillator:
    """Тесты для класса QuantumOscillator."""
    
    def test_scalar_oscillator(self, scalar_oscillator):
        """Тест скалярного осциллятора."""
        assert scalar_oscillator.spin == SpinType.SCALAR
        assert scalar_oscillator.spin_dim == 1
        assert len(scalar_oscillator.spin_state) == 1
    
    def test_spinor_oscillator(self, spinor_oscillator):
        """Тест спинорного осциллятора."""
        assert spinor_oscillator.spin == SpinType.SPINOR
        assert spinor_oscillator.spin_dim == 2
        assert len(spinor_oscillator.spin_state) == 2
    
    def test_vector_oscillator(self, vector_oscillator):
        """Тест векторного осциллятора."""
        assert vector_oscillator.spin == SpinType.VECTOR
        assert vector_oscillator.spin_dim == 3
        assert len(vector_oscillator.spin_state) == 3
    
    def test_tensor_oscillator(self):
        """Тест тензорного осциллятора."""
        osc = QuantumOscillator(
            frequency=1.0,
            amplitude=1.0 + 0j,
            spin=SpinType.TENSOR,
            position=np.array([0.0, 0.0, 0.0])
        )
        assert osc.spin_dim == 5
        assert len(osc.spin_state) == 5
    
    def test_oscillator_energy(self, scalar_oscillator):
        """Тест вычисления энергии осциллятора."""
        expected_energy = np.abs(scalar_oscillator.amplitude)**2 * scalar_oscillator.frequency
        assert abs(scalar_oscillator.energy - expected_energy) < 1e-10
    
    def test_evolve_amplitude(self, scalar_oscillator):
        """Тест эволюции амплитуды."""
        initial_amplitude = scalar_oscillator.amplitude
        scalar_oscillator.evolve_amplitude(dt=0.1, damping=0.0)
        
        # Амплитуда должна изменить фазу
        assert np.abs(scalar_oscillator.amplitude) == pytest.approx(np.abs(initial_amplitude), rel=1e-5)
    
    def test_evolve_amplitude_with_damping(self, scalar_oscillator):
        """Тест эволюции с затуханием."""
        initial_energy = scalar_oscillator.energy
        scalar_oscillator.evolve_amplitude(dt=1.0, damping=0.1)
        
        # Энергия должна уменьшиться
        assert scalar_oscillator.energy < initial_energy
    
    def test_spinor_evolve_spin(self, spinor_oscillator):
        """Тест эволюции спина."""
        initial_state = spinor_oscillator.spin_state.copy()
        spinor_oscillator.evolve_spin(dt=0.1, magnetic_field=np.array([0.0, 0.0, 1.0]))
        
        # Состояние должно измениться
        # (но нормировка сохраняется)
        norm = np.linalg.norm(spinor_oscillator.spin_state)
        assert abs(norm - 1.0) < 1e-10
    
    def test_scalar_evolve_spin_no_change(self, scalar_oscillator):
        """Тест, что скаляр не меняется при эволюции спина."""
        initial_state = scalar_oscillator.spin_state.copy()
        scalar_oscillator.evolve_spin(dt=0.1, magnetic_field=np.array([1.0, 0.0, 0.0]))
        
        np.testing.assert_array_equal(scalar_oscillator.spin_state, initial_state)


class TestPhysicalConstants:
    """Тесты для физических констант."""
    
    def test_constants_positive(self):
        """Проверка, что все константы положительные."""
        assert PhysicalConstants.ELECTRON_MASS > 0
        assert PhysicalConstants.PLANCK_MASS > 0
        assert PhysicalConstants.CMB_TEMPERATURE > 0
    
    def test_planck_mass(self):
        """Проверка массы Планка."""
        # M_Planck ≈ 1.22 × 10^19 GeV
        assert 1e19 < PhysicalConstants.PLANCK_MASS < 2e19
    
    def test_cmb_temperature(self):
        """Проверка температуры CMB."""
        # T_CMB ≈ 2.725 K
        assert abs(PhysicalConstants.CMB_TEMPERATURE - 2.725) < 0.01
    
    def test_baryon_to_photon_ratio(self):
        """Проверка отношения барионов к фотонам."""
        # η ≈ 6.1 × 10^-10
        assert 5e-10 < PhysicalConstants.BARYON_TO_PHOTON_RATIO < 7e-10
    
    def test_cosmological_fractions(self):
        """Проверка космологических долей."""
        total = (PhysicalConstants.DARK_ENERGY_FRACTION + 
                 PhysicalConstants.DARK_MATTER_FRACTION + 
                 PhysicalConstants.BARYON_FRACTION)
        assert abs(total - 1.0) < 0.01


class TestParticleFunctions:
    """Тесты для функций работы с частицами."""
    
    def test_get_particle_mass(self):
        """Тест получения массы частицы."""
        assert get_particle_mass(ParticleType.PHOTON) == 0.0
        assert get_particle_mass(ParticleType.HIGGS) == pytest.approx(125.0, rel=0.1)
        assert get_particle_mass(ParticleType.INFLATON) > 1e10
    
    def test_get_particle_spin(self):
        """Тест получения спина частицы."""
        assert get_particle_spin(ParticleType.PHOTON) == 1
        assert get_particle_spin(ParticleType.HIGGS) == 0
        assert get_particle_spin(ParticleType.QUARK) == 0.5
        assert get_particle_spin(ParticleType.LEPTON) == 0.5
    
    def test_get_particle_lifetime(self):
        """Тест получения времени жизни."""
        assert get_particle_lifetime(ParticleType.PHOTON) is None  # стабильный
        assert get_particle_lifetime(ParticleType.INFLATON) is not None  # нестабильный
        assert get_particle_lifetime(ParticleType.HIGGS) is not None  # нестабильный


class TestStatisticalDistributions:
    """Тесты для статистических распределений."""
    
    def test_fermi_dirac_limits(self):
        """Тест граничных условий Ферми-Дирака."""
        # При E >> T, f → 0
        assert fermi_dirac(100.0, 1.0) < 1e-10
        
        # При E << T, f → 1/2 (для μ=0)
        assert abs(fermi_dirac(0.0, 1.0) - 0.5) < 0.01
        
        # При T=0, защита от деления
        assert fermi_dirac(1.0, 0.0) == 0.0
    
    def test_fermi_dirac_range(self):
        """Проверка, что значения в диапазоне [0, 1]."""
        for E in [0.1, 1.0, 10.0]:
            for T in [0.1, 1.0, 10.0]:
                f = fermi_dirac(E, T)
                assert 0 <= f <= 1
    
    def test_bose_einstein_limits(self):
        """Тест граничных условий Бозе-Эйнштейна."""
        # При E >> T, n → 0
        assert bose_einstein(100.0, 1.0) < 1e-10
        
        # При T=0, защита
        assert bose_einstein(1.0, 0.0) == 0.0
    
    def test_bose_einstein_positive(self):
        """Проверка, что значения положительные."""
        for E in [0.5, 1.0, 5.0]:
            for T in [0.1, 1.0, 10.0]:
                n = bose_einstein(E, T)
                assert n >= 0
    
    def test_planck_distribution(self):
        """Тест планковского распределения."""
        # Планк = Бозе-Эйнштейн с μ=0
        E, T = 1.0, 1.0
        assert planck_distribution(E, T) == bose_einstein(E, T, mu=0.0)
    
    def test_thermal_energy_density(self):
        """Тест плотности тепловой энергии."""
        # ρ = (π²/30) × g_eff × T⁴
        T = 1.0
        g_eff = 106.75
        
        expected = (np.pi**2 / 30) * g_eff * T**4
        assert thermal_energy_density(T, g_eff) == pytest.approx(expected, rel=1e-10)
    
    def test_thermal_energy_scaling(self):
        """Проверка масштабирования ρ ∝ T⁴."""
        rho1 = thermal_energy_density(1.0)
        rho2 = thermal_energy_density(2.0)
        
        # rho2 / rho1 должно быть 2⁴ = 16
        assert rho2 / rho1 == pytest.approx(16.0, rel=1e-10)

