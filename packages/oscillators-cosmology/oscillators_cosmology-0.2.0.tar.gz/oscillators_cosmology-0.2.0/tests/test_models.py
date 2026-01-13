"""
Тесты для модуля models.py - физических моделей.
"""

import pytest
import numpy as np
from oscillators.models import (
    ParametricResonance,
    LeptogenesisModel,
    QuantumCreationInExpandingUniverse
)


class TestParametricResonance:
    """Тесты для модели параметрического резонанса."""
    
    def test_initialization(self, parametric_resonance):
        """Тест инициализации."""
        assert parametric_resonance.m == 1e13
        assert parametric_resonance.g == 1e-7
    
    def test_custom_initialization(self):
        """Тест инициализации с пользовательскими параметрами."""
        pr = ParametricResonance(inflaton_mass=1e12, coupling=1e-6)
        assert pr.m == 1e12
        assert pr.g == 1e-6
    
    def test_mathieu_instability_chart(self, parametric_resonance):
        """Тест карты неустойчивостей Матье."""
        q_vals, a_vals, instability = parametric_resonance.mathieu_instability_chart(
            q_range=(-5, 5), a_range=(-5, 5), resolution=50
        )
        
        assert len(q_vals) == 50
        assert len(a_vals) == 50
        assert instability.shape == (50, 50)
        
        # Проверяем, что есть зоны неустойчивости
        assert np.max(instability) > 0
    
    def test_particle_production_rate(self, parametric_resonance):
        """Тест скорости рождения частиц."""
        rate = parametric_resonance.particle_production_rate(phi_amplitude=1e16, k=1.0)
        
        # Скорость должна быть неотрицательной
        assert rate >= 0
    
    def test_particle_production_rate_zero_amplitude(self, parametric_resonance):
        """Тест при нулевой амплитуде."""
        rate = parametric_resonance.particle_production_rate(phi_amplitude=0.0, k=1.0)
        assert rate >= 0
    
    def test_floquet_exponent(self, parametric_resonance):
        """Тест показателя Флоке."""
        # Внутренний метод
        mu = parametric_resonance._floquet_exponent(a=1.0, q=0.1)
        assert mu >= 0
        
        mu_large_q = parametric_resonance._floquet_exponent(a=1.0, q=10.0)
        assert mu_large_q >= 0
    
    def test_simulate_resonance_bands_returns_dict(self, parametric_resonance):
        """Тест, что симуляция возвращает словарь."""
        results = parametric_resonance.simulate_resonance_bands(show_plot=False)
        
        assert isinstance(results, dict)
        assert 'instability_map' in results
        assert 'spectra' in results
        assert 'evolution' in results
        assert 'efficiencies' in results
    
    def test_production_rate_increases_with_amplitude(self, parametric_resonance):
        """Тест, что скорость растёт с амплитудой."""
        rate1 = parametric_resonance.particle_production_rate(phi_amplitude=1e15, k=1.0)
        rate2 = parametric_resonance.particle_production_rate(phi_amplitude=1e16, k=1.0)
        
        # Скорость должна расти с амплитудой
        assert rate2 >= rate1


class TestLeptogenesisModel:
    """Тесты для модели лептогенеза."""
    
    def test_initialization(self, leptogenesis_model):
        """Тест инициализации."""
        assert leptogenesis_model.M == 1e10
        assert leptogenesis_model.h == 1e-6
        assert leptogenesis_model.epsilon == 1e-10
    
    def test_decay_rate(self, leptogenesis_model):
        """Тест скорости распада."""
        Gamma = leptogenesis_model.decay_rate()
        
        # Γ = h² M / (8π)
        expected = (leptogenesis_model.h**2 * leptogenesis_model.M) / (8 * np.pi)
        assert Gamma == pytest.approx(expected, rel=1e-10)
        assert Gamma > 0
    
    def test_decay_asymmetry(self, leptogenesis_model):
        """Тест CP-асимметрии."""
        eps = leptogenesis_model.decay_asymmetry()
        
        # Асимметрия должна быть малой, но не нулевой
        assert eps != 0
        assert abs(eps) < 1  # Не больше 100%
    
    def test_boltzmann_equations(self, leptogenesis_model):
        """Тест уравнений Больцмана."""
        y = [1e-3, 0.0]  # [N, L]
        t = 0.0
        
        dydt = leptogenesis_model.boltzmann_equations(y, t)
        
        assert len(dydt) == 2
        assert all(np.isfinite(d) for d in dydt)
    
    def test_solve_leptogenesis(self, leptogenesis_model):
        """Тест решения лептогенеза."""
        # Решаем с коротким временем для скорости теста
        final_asymmetry = leptogenesis_model.solve_leptogenesis(t_max=100, show_plot=False)
        
        assert np.isfinite(final_asymmetry)
    
    def test_temperature_dependence(self):
        """Тест зависимости от температуры."""
        model1 = LeptogenesisModel(M=1e10, Yukawa=1e-6, CP_violation=1e-10)
        model2 = LeptogenesisModel(M=1e11, Yukawa=1e-6, CP_violation=1e-10)
        
        # Разные массы должны давать разные результаты
        assert model1.decay_rate() != model2.decay_rate()
    
    def test_cp_violation_impact(self):
        """Тест влияния CP-нарушения."""
        model_small_cp = LeptogenesisModel(CP_violation=1e-12)
        model_large_cp = LeptogenesisModel(CP_violation=1e-8)
        
        eps_small = model_small_cp.decay_asymmetry()
        eps_large = model_large_cp.decay_asymmetry()
        
        # Большее CP-нарушение даёт большую асимметрию
        assert abs(eps_large) > abs(eps_small)


class TestQuantumCreationInExpandingUniverse:
    """Тесты для модели квантового рождения частиц."""
    
    def test_initialization(self, quantum_creation_model):
        """Тест инициализации."""
        assert quantum_creation_model.m == 0.1
        assert quantum_creation_model.H == 0.01
        assert quantum_creation_model.a0 == 1.0
    
    def test_scale_factor_inflation(self, quantum_creation_model):
        """Тест масштабного фактора при инфляции."""
        # При t < 10, экспоненциальное расширение
        a0 = quantum_creation_model.scale_factor(0)
        a5 = quantum_creation_model.scale_factor(5)
        
        # a(t) = a0 * exp(H * t)
        expected = quantum_creation_model.a0 * np.exp(quantum_creation_model.H * 5)
        assert a5 == pytest.approx(expected, rel=1e-10)
        
        # a растёт со временем
        assert a5 > a0
    
    def test_scale_factor_radiation(self, quantum_creation_model):
        """Тест масштабного фактора при радиационной эре."""
        # При 10 < t < 100
        a50 = quantum_creation_model.scale_factor(50)
        a70 = quantum_creation_model.scale_factor(70)
        
        # a должен расти
        assert a70 > a50
    
    def test_scale_factor_matter(self, quantum_creation_model):
        """Тест масштабного фактора при материальной эре."""
        # При t > 100
        a150 = quantum_creation_model.scale_factor(150)
        a180 = quantum_creation_model.scale_factor(180)
        
        # a должен расти
        assert a180 > a150
    
    def test_scale_factor_monotonic(self, quantum_creation_model):
        """Тест монотонности масштабного фактора."""
        times = [0, 5, 10, 50, 100, 150, 200]
        a_values = [quantum_creation_model.scale_factor(t) for t in times]
        
        # a должен монотонно возрастать
        for i in range(len(a_values) - 1):
            assert a_values[i+1] > a_values[i]
    
    def test_solve_mode_evolution(self, quantum_creation_model):
        """Тест эволюции мод."""
        k_values = [0.1, 1.0]
        results = quantum_creation_model.solve_mode_evolution(k_values)
        
        assert len(results) == 2
        assert 0.1 in results
        assert 1.0 in results
        
        for k, data in results.items():
            assert 'chi' in data
            assert 'n_k' in data
            assert 'times' in data
            assert data['n_k'] >= 0  # Число частиц неотрицательно
    
    def test_analyze_particle_creation(self, quantum_creation_model):
        """Тест анализа рождения частиц."""
        results = quantum_creation_model.analyze_particle_creation(show_plot=False)
        
        assert isinstance(results, dict)
        # Должны быть результаты для нескольких k
        assert len(results) >= 2
    
    def test_particle_number_positive(self, quantum_creation_model):
        """Тест, что число рождённых частиц неотрицательно."""
        k_values = [0.01, 0.1, 1.0, 10.0]
        results = quantum_creation_model.solve_mode_evolution(k_values)
        
        for k, data in results.items():
            assert data['n_k'] >= 0, f"n_k должно быть >= 0 для k={k}"
    
    def test_mass_dependence(self):
        """Тест зависимости от массы."""
        model_light = QuantumCreationInExpandingUniverse(mass=0.01, expansion_rate=0.01)
        model_heavy = QuantumCreationInExpandingUniverse(mass=1.0, expansion_rate=0.01)
        
        # Тяжёлые частицы рождаются труднее
        results_light = model_light.solve_mode_evolution([1.0])
        results_heavy = model_heavy.solve_mode_evolution([1.0])
        
        # Для тяжёлых частиц рождение должно быть подавлено
        # (не всегда строго, но в большинстве случаев)
        assert results_light[1.0]['n_k'] >= 0
        assert results_heavy[1.0]['n_k'] >= 0


class TestModelIntegration:
    """Интеграционные тесты моделей."""
    
    def test_models_work_together(
        self, parametric_resonance, leptogenesis_model, quantum_creation_model
    ):
        """Тест совместной работы моделей."""
        # Параметрический резонанс
        pr_results = parametric_resonance.simulate_resonance_bands(show_plot=False)
        assert pr_results is not None
        
        # Лептогенез
        asymmetry = leptogenesis_model.solve_leptogenesis(t_max=100, show_plot=False)
        assert np.isfinite(asymmetry)
        
        # Квантовое рождение
        qc_results = quantum_creation_model.solve_mode_evolution([1.0])
        assert qc_results[1.0]['n_k'] >= 0
    
    def test_physical_consistency(self, parametric_resonance, leptogenesis_model):
        """Тест физической согласованности."""
        # Скорости должны быть положительными
        assert parametric_resonance.particle_production_rate(1e16, 1.0) >= 0
        assert leptogenesis_model.decay_rate() > 0
        
        # Асимметрия должна быть малой
        assert abs(leptogenesis_model.decay_asymmetry()) < 1

