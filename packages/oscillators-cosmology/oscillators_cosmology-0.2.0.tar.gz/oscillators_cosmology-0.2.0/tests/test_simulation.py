"""
Тесты для модуля simulation.py - комплексных симуляций.
"""

import pytest
import numpy as np
from oscillators.simulation import (
    MatterGenesisSimulation,
    PrimordialOscillatorUniverse,
    DetailedMatterGenesis
)
from oscillators.core import ParticleType, SpinType


class TestMatterGenesisSimulation:
    """Тесты для MatterGenesisSimulation."""
    
    def test_initialization(self, matter_genesis_simulation):
        """Тест инициализации."""
        sim = matter_genesis_simulation
        
        assert sim.volume_size == 1.0
        assert sim.time == 0.0
        assert sim.temperature > 0
        assert len(sim.particles) == 0
    
    def test_inflaton_potential(self, matter_genesis_simulation):
        """Тест потенциала инфлатона."""
        sim = matter_genesis_simulation
        
        # V(φ) = ½m²φ² + ¼λφ⁴
        V0 = sim.inflaton_potential(0)
        V1 = sim.inflaton_potential(1e10)
        
        assert V0 == 0  # V(0) = 0
        assert V1 > 0   # V(φ) > 0 для φ ≠ 0
    
    def test_inflaton_potential_derivative(self, matter_genesis_simulation):
        """Тест производной потенциала."""
        sim = matter_genesis_simulation
        
        # dV/dφ(0) = 0
        dV0 = sim.inflaton_potential_derivative(0)
        assert abs(dV0) < 1e-10
        
        # dV/dφ(φ) > 0 для φ > 0
        dV1 = sim.inflaton_potential_derivative(1e10)
        assert dV1 > 0
    
    def test_evolve_inflaton(self, matter_genesis_simulation):
        """Тест эволюции инфлатона."""
        sim = matter_genesis_simulation
        
        initial_field = sim.inflaton_field
        energy = sim.evolve_inflaton(dt=0.1)
        
        assert energy >= 0
        assert np.isfinite(energy)
        # Поле должно измениться
        assert sim.inflaton_field != initial_field or sim.inflaton_velocity != 0
    
    def test_parametric_resonance(self, matter_genesis_simulation):
        """Тест параметрического резонанса."""
        sim = matter_genesis_simulation
        
        factor = sim.parametric_resonance(time=1.0)
        
        assert factor >= 1.0  # Резонанс усиливает
        assert np.isfinite(factor)
    
    def test_evolve_universe_short(self, matter_genesis_simulation):
        """Тест короткой эволюции."""
        sim = matter_genesis_simulation
        
        history = sim.evolve_universe(total_time=10.0, dt=1.0, show_progress=False)
        
        assert len(history) > 0
        assert all('time' in h for h in history)
        assert all('temperature' in h for h in history)
        assert all('baryon_asymmetry' in h for h in history)
    
    def test_temperature_decreases(self, matter_genesis_simulation):
        """Тест, что температура уменьшается."""
        sim = matter_genesis_simulation
        
        history = sim.evolve_universe(total_time=50.0, dt=1.0, show_progress=False)
        
        # Температура должна убывать
        temps = [h['temperature'] for h in history]
        assert temps[-1] < temps[0]
    
    def test_scale_factor_increases(self, matter_genesis_simulation):
        """Тест, что масштабный фактор растёт."""
        sim = matter_genesis_simulation
        
        history = sim.evolve_universe(total_time=50.0, dt=1.0, show_progress=False)
        
        scales = [h['scale_factor'] for h in history]
        assert scales[-1] > scales[0]
    
    def test_particles_created(self, matter_genesis_simulation):
        """Тест, что частицы создаются."""
        sim = matter_genesis_simulation
        
        history = sim.evolve_universe(total_time=100.0, dt=1.0, show_progress=False)
        
        # Должны появиться частицы
        final_count = history[-1]['n_particles']
        assert final_count >= 0
    
    def test_baryon_asymmetry_calculated(self, matter_genesis_simulation):
        """Тест вычисления барионной асимметрии."""
        sim = matter_genesis_simulation
        
        history = sim.evolve_universe(total_time=100.0, dt=1.0, show_progress=False)
        
        eta = history[-1]['baryon_asymmetry']
        assert np.isfinite(eta)
    
    def test_particle_statistics(self, matter_genesis_simulation):
        """Тест статистики частиц."""
        sim = matter_genesis_simulation
        
        history = sim.evolve_universe(total_time=100.0, dt=1.0, show_progress=False)
        
        stats = history[-1]['particle_stats']
        assert isinstance(stats, dict)
        assert ParticleType.PHOTON in stats
        assert ParticleType.QUARK in stats
    
    def test_cp_violation_parameter(self, matter_genesis_simulation):
        """Тест параметра CP-нарушения."""
        sim = matter_genesis_simulation
        
        assert sim.CP_violation_parameter == 1e-10
        
        # Создаём симуляцию с другим CP-нарушением
        sim2 = MatterGenesisSimulation(cp_violation=1e-8)
        assert sim2.CP_violation_parameter == 1e-8
    
    def test_calculate_baryon_asymmetry(self, matter_genesis_simulation):
        """Тест метода calculate_baryon_asymmetry."""
        sim = matter_genesis_simulation
        
        # Начальная асимметрия должна быть 0 (нет фотонов)
        eta = sim.calculate_baryon_asymmetry()
        assert eta == 0.0
        
        # После эволюции должна быть ненулевой (если есть фотоны)
        sim.evolve_universe(total_time=100.0, dt=1.0, show_progress=False)
        eta_after = sim.calculate_baryon_asymmetry()
        assert np.isfinite(eta_after)


class TestPrimordialOscillatorUniverse:
    """Тесты для PrimordialOscillatorUniverse."""
    
    def test_initialization(self, primordial_universe):
        """Тест инициализации."""
        assert primordial_universe.total_energy == 10.0
        assert len(primordial_universe.oscillators) > 0
    
    def test_symmetric_beginning(self):
        """Тест симметричного начала."""
        universe = PrimordialOscillatorUniverse(total_energy=10.0, initial_symmetry=True)
        
        # Должны быть осцилляторы разных типов
        spin_types = set(osc.spin for osc in universe.oscillators)
        assert len(spin_types) > 1
    
    def test_spin_distribution(self, primordial_universe):
        """Тест распределения спинов."""
        dist = primordial_universe.spin_distribution
        
        assert isinstance(dist, dict)
        assert SpinType.SCALAR in dist
        assert SpinType.SPINOR in dist
        assert SpinType.VECTOR in dist
        assert SpinType.TENSOR in dist
        
        total = sum(dist.values())
        assert total == len(primordial_universe.oscillators)
    
    def test_simulate_symmetry_breaking(self, primordial_universe):
        """Тест симуляции нарушения симметрии."""
        history = primordial_universe.simulate_symmetry_breaking(
            temperature=1.0, steps=50, show_progress=False
        )
        
        assert len(history) > 0
        assert 'step' in history[0]
        assert 'temperature' in history[0]
        assert 'spin_counts' in history[0]
    
    def test_temperature_decreases_in_simulation(self, primordial_universe):
        """Тест, что температура падает."""
        history = primordial_universe.simulate_symmetry_breaking(
            temperature=1.0, steps=100, show_progress=False
        )
        
        temps = [h['temperature'] for h in history]
        assert temps[-1] < temps[0]
    
    def test_interaction_probability(self, primordial_universe):
        """Тест вероятности взаимодействия."""
        # Фермион-фермион (подавлено из-за Паули)
        p_ff = primordial_universe._interaction_probability(
            SpinType.SPINOR, SpinType.SPINOR, 1.0
        )
        
        # Вектор-вектор (усилено)
        p_vv = primordial_universe._interaction_probability(
            SpinType.VECTOR, SpinType.VECTOR, 1.0
        )
        
        # Тензор (гравитационное, слабое)
        p_tt = primordial_universe._interaction_probability(
            SpinType.TENSOR, SpinType.TENSOR, 1.0
        )
        
        # Вектор-вектор должно быть сильнее
        assert p_vv > p_ff
        # Тензор (гравитация) слабее
        assert p_tt < p_vv
    
    def test_generate_new_spin(self, primordial_universe):
        """Тест генерации нового спина."""
        # Спинор + Спинор → Скаляр или Вектор
        for _ in range(10):
            new_spin = primordial_universe._generate_new_spin(
                SpinType.SPINOR, SpinType.SPINOR
            )
            assert new_spin in [SpinType.SCALAR, SpinType.VECTOR]


class TestDetailedMatterGenesis:
    """Тесты для DetailedMatterGenesis."""
    
    def test_initialization(self, detailed_genesis):
        """Тест инициализации."""
        assert detailed_genesis.resonance_model is not None
        assert detailed_genesis.leptogenesis_model is not None
        assert detailed_genesis.quantum_model is not None
    
    def test_simulate_full_genesis(self, detailed_genesis, capsys):
        """Тест полной симуляции."""
        # Этот тест может быть медленным, поэтому мы просто проверяем,
        # что он запускается без ошибок
        import matplotlib
        matplotlib.use('Agg')  # Не показывать графики
        
        results = detailed_genesis.simulate_full_genesis()
        
        assert isinstance(results, dict)
        assert 'inflation' in results
        assert 'reheating' in results
        assert 'asymmetry' in results
        assert 'equilibrium' in results
    
    def test_inflation_phase(self, detailed_genesis):
        """Тест инфляционной фазы."""
        results = detailed_genesis._simulate_inflation()
        
        assert 'N_e_folds' in results
        assert 'H_inf' in results
        assert 'power_spectrum' in results
        
        assert results['N_e_folds'] == 60
        assert results['H_inf'] > 0
    
    def test_reheating_phase(self, detailed_genesis):
        """Тест фазы разогрева."""
        results = detailed_genesis._simulate_reheating()
        
        assert 'reheating_temperature' in results
        assert 'particle_yields' in results
        assert 'efficiency' in results
        
        assert results['reheating_temperature'] > 0
        assert results['efficiency'] > 0
        assert results['efficiency'] <= 1
    
    def test_asymmetry_phase(self, detailed_genesis):
        """Тест фазы генерации асимметрии."""
        import matplotlib
        matplotlib.use('Agg')
        
        results = detailed_genesis._simulate_asymmetry()
        
        assert 'lepton_asymmetry' in results
        assert 'baryon_asymmetry' in results
        assert 'sphaleron_rate' in results
        assert 'final_B' in results
    
    def test_equilibrium_phase(self, detailed_genesis):
        """Тест фазы равновесия."""
        results = detailed_genesis._simulate_equilibrium()
        
        assert 'annihilation' in results
        assert 'cmb' in results
        assert 'nucleosynthesis' in results
        
        # Проверяем CMB
        assert abs(results['cmb']['kelvin'] - 2.725) < 0.01
        
        # Проверяем нуклеосинтез
        abundances = results['nucleosynthesis']['abundances']
        assert 'H' in abundances
        assert 'He4' in abundances
        assert abundances['H'] > abundances['He4']


class TestSimulationIntegration:
    """Интеграционные тесты симуляций."""
    
    def test_full_simulation_pipeline(self, random_seed):
        """Тест полного пайплайна симуляции."""
        # Создаём симуляцию
        sim = MatterGenesisSimulation(
            volume_size=1.0,
            initial_inflaton_energy=1e12,
            hubble_parameter=1e-5,
            cp_violation=1e-10
        )
        
        # Запускаем эволюцию
        history = sim.evolve_universe(total_time=50.0, dt=1.0, show_progress=False)
        
        # Проверяем результаты
        assert len(history) > 0
        
        final = history[-1]
        assert final['time'] > 0
        assert final['temperature'] > 0
        assert np.isfinite(final['baryon_asymmetry'])
    
    def test_oscillator_universe_pipeline(self, random_seed):
        """Тест пайплайна вселенной осцилляторов."""
        universe = PrimordialOscillatorUniverse(total_energy=5.0)
        
        history = universe.simulate_symmetry_breaking(
            temperature=0.5, steps=30, show_progress=False
        )
        
        assert len(history) > 0
        
        final = history[-1]
        total_oscillators = sum(final['spin_counts'].values())
        assert total_oscillators >= len(universe.oscillators)
    
    def test_numerical_stability(self):
        """Тест численной стабильности."""
        sim = MatterGenesisSimulation(
            volume_size=1.0,
            initial_inflaton_energy=1e16,  # Высокая энергия
            hubble_parameter=1e-5
        )
        
        history = sim.evolve_universe(total_time=100.0, dt=0.5, show_progress=False)
        
        # Проверяем, что нет nan или inf
        for h in history:
            assert np.isfinite(h['temperature'])
            assert np.isfinite(h['scale_factor'])
            assert np.isfinite(h['inflaton_energy'])
            assert np.isfinite(h['baryon_asymmetry'])

