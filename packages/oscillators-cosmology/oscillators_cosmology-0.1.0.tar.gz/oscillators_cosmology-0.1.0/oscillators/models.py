"""
Физические модели космологических процессов.

Модуль содержит реализации:
- ParametricResonance: параметрический резонанс при разогреве
- LeptogenesisModel: генерация лептонной/барионной асимметрии
- QuantumCreationInExpandingUniverse: рождение частиц из вакуума
"""

import numpy as np
from scipy.integrate import odeint
from scipy.special import zeta
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import Dict, List, Tuple, Optional


class ParametricResonance:
    """
    Модель параметрического резонанса при разогреве Вселенной.
    
    После инфляции поле инфлатона осциллирует около минимума
    потенциала, создавая параметрическую неустойчивость,
    которая приводит к экспоненциальному рождению частиц.
    
    Уравнение Матье: x'' + (a - 2q cos(2t))x = 0
    
    Attributes:
        m: масса инфлатона (GeV)
        g: константа связи инфлатон-материя
    
    Example:
        >>> resonance = ParametricResonance(inflaton_mass=1e13, coupling=1e-7)
        >>> resonance.simulate_resonance_bands()
    """
    
    def __init__(self, inflaton_mass: float = 1e13, coupling: float = 1e-7):
        """
        Инициализация модели параметрического резонанса.
        
        Args:
            inflaton_mass: масса инфлатона в GeV
            coupling: константа связи g
        """
        self.m = inflaton_mass
        self.g = coupling
        
    def mathieu_instability_chart(
        self, 
        q_range: Tuple[float, float] = (-20, 20), 
        a_range: Tuple[float, float] = (-20, 20),
        resolution: int = 400
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Построение карты неустойчивостей уравнения Матье.
        
        Зоны неустойчивости соответствуют экспоненциальному
        росту числа частиц (параметрический резонанс).
        
        Args:
            q_range: диапазон параметра q
            a_range: диапазон параметра a
            resolution: разрешение сетки
            
        Returns:
            (q_vals, a_vals, instability_map)
        """
        q_vals = np.linspace(*q_range, resolution)
        a_vals = np.linspace(*a_range, resolution)
        
        instability = np.zeros((len(a_vals), len(q_vals)))
        
        for i, a in enumerate(a_vals):
            for j, q in enumerate(q_vals):
                # Характеристичный показатель (приближение)
                mu = np.sqrt(np.abs(a + q*q/2))
                if a < q*q/4:  # Область неустойчивости
                    instability[i, j] = mu
                else:
                    instability[i, j] = 0
        
        return q_vals, a_vals, instability
    
    def particle_production_rate(self, phi_amplitude: float, k: float) -> float:
        """
        Скорость рождения частиц с импульсом k.
        
        Args:
            phi_amplitude: амплитуда осцилляций инфлатона
            k: импульс рождающихся частиц
            
        Returns:
            скорость рождения dn/dt
        """
        # Частота частицы
        omega_k = np.sqrt(k*k + self.m*self.m)
        
        # Параметры уравнения Матье
        a = (2*omega_k/self.m)**2
        q = 2*self.g*phi_amplitude*omega_k/(self.m*self.m)
        
        # Характеристичный показатель (инкремент неустойчивости)
        mu = self._floquet_exponent(a, q)
        
        # Скорость рождения частиц
        nk_dot = mu * omega_k / (2*np.pi)
        
        return nk_dot
    
    def _floquet_exponent(self, a: float, q: float) -> float:
        """
        Вычисление показателя Флоке для уравнения Матье.
        
        Args:
            a, q: параметры уравнения Матье
            
        Returns:
            показатель нестабильности μ
        """
        if q < 0.5:
            return 0.5 * np.sqrt(np.abs(q*q - (a-1)**2))
        else:
            return np.sqrt(np.maximum(0, q*q/4 - (a-1)**2))
    
    def simulate_resonance_bands(self, show_plot: bool = True) -> Dict:
        """
        Полное моделирование резонансных полос.
        
        Создает 4 графика:
        1. Карта неустойчивостей Матье
        2. Спектр рождающихся частиц
        3. Эволюция плотности частиц во времени
        4. Эффективность резонанса от амплитуды
        
        Args:
            show_plot: показывать ли графики
            
        Returns:
            словарь с результатами расчетов
        """
        results = {}
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Карта неустойчивостей
        q_vals, a_vals, instability = self.mathieu_instability_chart()
        results['instability_map'] = instability
        
        im = axes[0, 0].imshow(
            instability, 
            extent=[q_vals[0], q_vals[-1], a_vals[0], a_vals[-1]],
            origin='lower', cmap='hot', aspect='auto'
        )
        axes[0, 0].set_xlabel('Параметр q')
        axes[0, 0].set_ylabel('Параметр a')
        axes[0, 0].set_title('Карта неустойчивостей Матье')
        plt.colorbar(im, ax=axes[0, 0], label='Инкремент μ')
        
        # 2. Спектр рождения по импульсам
        k_vals = np.logspace(-3, 3, 200)
        phi_amps = [0.1, 1.0, 10.0]
        
        spectra = {}
        for phi_amp in phi_amps:
            rates = [self.particle_production_rate(phi_amp, k) for k in k_vals]
            spectra[phi_amp] = rates
            axes[0, 1].loglog(k_vals, rates, label=f'φ = {phi_amp}')
        
        results['spectra'] = spectra
        
        axes[0, 1].set_xlabel('Импульс k')
        axes[0, 1].set_ylabel('dn/dt (скорость рождения)')
        axes[0, 1].set_title('Спектр рождающихся частиц')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Эволюция во времени (3D)
        axes[1, 0].remove()
        ax3d = fig.add_subplot(2, 2, 3, projection='3d')
        
        times = np.linspace(0, 50, 500)
        k_samples = [0.1, 1.0, 10.0]
        
        evolution = {}
        for k in k_samples:
            particle_density = []
            phi_amp = 1.0
            
            for t in times:
                phi = phi_amp * np.cos(self.m * t)
                rate = self.particle_production_rate(abs(phi), k)
                
                if len(particle_density) > 0:
                    new_density = particle_density[-1] + rate * (times[1] - times[0])
                else:
                    new_density = rate * (times[1] - times[0])
                particle_density.append(new_density)
            
            evolution[k] = particle_density
            ax3d.plot(times, [k]*len(times), particle_density, 
                     label=f'k = {k}', linewidth=2)
        
        results['evolution'] = evolution
        
        ax3d.set_xlabel('Время')
        ax3d.set_ylabel('Импульс k')
        ax3d.set_zlabel('Плотность n(k)')
        ax3d.set_title('Накопление частиц')
        ax3d.legend()
        
        # 4. Эффективность резонанса
        axes[1, 1].remove()
        ax_eff = fig.add_subplot(2, 2, 4)
        
        phi_range = np.logspace(-2, 2, 100)
        efficiencies = []
        
        for phi in phi_range:
            total_rate = sum(
                self.particle_production_rate(phi, k) 
                for k in np.logspace(-2, 2, 50)
            )
            efficiencies.append(total_rate)
        
        results['efficiencies'] = (phi_range, efficiencies)
        
        ax_eff.loglog(phi_range, efficiencies, 'g-', linewidth=2)
        ax_eff.set_xlabel('Амплитуда инфлатона φ')
        ax_eff.set_ylabel('Полная скорость рождения')
        ax_eff.set_title('Эффективность резонанса')
        ax_eff.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return results


class LeptogenesisModel:
    """
    Модель лептогенеза - механизма генерации барионной асимметрии.
    
    Тяжелые нейтрино распадаются с нарушением CP-симметрии,
    создавая избыток лептонов над антилептонами.
    Сфалеронные переходы конвертируют это в барионную асимметрию.
    
    Реалистичные параметры:
    - CP-нарушение: ~10^-10 (микроскопическое)
    - Масса тяжелого нейтрино: ~10^9-10^12 GeV
    - Температура разогрева: ~10^9 GeV
    
    Attributes:
        M: масса тяжелого нейтрино (GeV)
        h: константа Юкавы
        epsilon: параметр CP-нарушения
        T: температура (GeV)
        H: параметр Хаббла
    
    Example:
        >>> model = LeptogenesisModel(M=1e10, Yukawa=1e-6, CP_violation=1e-10)
        >>> asymmetry = model.solve_leptogenesis()
    """
    
    def __init__(
        self, 
        M: float = 1e10, 
        Yukawa: float = 1e-6, 
        CP_violation: float = 1e-10  # Реалистичное микроскопическое значение
    ):
        """
        Инициализация модели лептогенеза.
        
        Args:
            M: масса тяжелого нейтрино (GeV)
            Yukawa: константа связи Юкавы
            CP_violation: параметр CP-нарушения ε (~1e-10 реалистично)
        """
        self.M = M
        self.h = Yukawa
        self.epsilon = CP_violation
        
        # Реалистичная температура разогрева
        self.T = 1e9  # GeV (вместо 1e12)
        self.H = 1.66 * np.sqrt(106.75) * self.T**2 / 1e19  # Параметр Хаббла
        
    def decay_rate(self) -> float:
        """
        Скорость распада тяжелого нейтрино.
        
        Returns:
            Γ = h² M / (8π)
        """
        return (self.h**2 * self.M) / (8 * np.pi)
    
    def decay_asymmetry(self) -> float:
        """
        CP-асимметрия в распадах.
        
        В реальности ε ~ (h² / 8π) × Im(λ) × f(M₁/M₂)
        где f - функция масс нейтрино.
        
        Для резонансного лептогенеза асимметрия может быть
        значительно усилена (до ~0.1).
        
        Returns:
            ε - эффективная CP-асимметрия
        """
        # Базовая асимметрия
        base_asymmetry = self.epsilon
        
        # Резонансное усиление (когда массы нейтрино близки)
        # Может увеличить асимметрию на несколько порядков
        resonant_enhancement = 100.0
        
        return base_asymmetry * resonant_enhancement
    
    def boltzmann_equations(self, y: List[float], t: float) -> List[float]:
        """
        Уравнения Больцмана для эволюции плотностей.
        
        Args:
            y: [N, L] - плотности тяжелых нейтрино и лептонного числа
            t: время
            
        Returns:
            [dN/dt, dL/dt]
        """
        N, L = y
        
        Gamma = self.decay_rate()
        eps = self.decay_asymmetry()
        
        # Температура падает экспоненциально
        T = self.T * np.exp(-self.H * t)
        
        # Равновесная плотность
        N_eq = (3 * float(zeta(3)) / (2 * np.pi**2)) * T**3 if T > 0 else 0
        
        # Скорости изменения
        dN_dt = -Gamma * (N - N_eq) - self.H * N
        dL_dt = eps * Gamma * (N - N_eq) - (Gamma/2) * L - self.H * L
        
        return [dN_dt, dL_dt]
    
    def solve_leptogenesis(
        self, 
        t_max: float = 1000, 
        show_plot: bool = True
    ) -> float:
        """
        Решение уравнений лептогенеза.
        
        Args:
            t_max: максимальное время интегрирования
            show_plot: показывать ли графики
            
        Returns:
            конечная барионная асимметрия
        """
        t_span = np.linspace(0, t_max, 1000)
        y0 = [1e-3, 0.0]  # Начальные условия: [N₀, L₀]
        
        solution = odeint(self.boltzmann_equations, y0, t_span)
        
        N = solution[:, 0]
        L = solution[:, 1]
        
        if show_plot:
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # 1. Эволюция плотности тяжелых нейтрино
            axes[0, 0].semilogy(t_span, np.abs(N) + 1e-20, 'b-', linewidth=2)
            axes[0, 0].set_xlabel('Время')
            axes[0, 0].set_ylabel('Плотность N')
            axes[0, 0].set_title('Эволюция тяжелых нейтрино')
            axes[0, 0].grid(True, alpha=0.3)
            
            # 2. Генерация лептонного числа
            axes[0, 1].plot(t_span, L, 'r-', linewidth=2)
            axes[0, 1].set_xlabel('Время')
            axes[0, 1].set_ylabel('Лептонное число L')
            axes[0, 1].set_title('Генерация лептонного числа')
            axes[0, 1].grid(True, alpha=0.3)
            
            # 3. Эффективность от массы
            M_range = np.logspace(8, 13, 50)
            efficiencies = []
            
            original_M = self.M
            for M_test in M_range:
                self.M = M_test
                Gamma = self.decay_rate()
                efficiency = Gamma / (self.H * self.M)
                efficiencies.append(efficiency)
            self.M = original_M
            
            axes[1, 0].loglog(M_range, efficiencies, 'g-', linewidth=2)
            axes[1, 0].axhline(y=1, color='r', linestyle='--', alpha=0.5)
            axes[1, 0].set_xlabel('Масса M (GeV)')
            axes[1, 0].set_ylabel('Эффективность')
            axes[1, 0].set_title('Зависимость от массы нейтрино')
            axes[1, 0].grid(True, alpha=0.3)
            
            # 4. Барионная асимметрия от константы связи
            h_range = np.logspace(-8, -4, 50)
            final_B = []
            
            original_h = self.h
            for h_test in h_range:
                self.h = h_test
                eps = self.decay_asymmetry()
                B_L = eps * 0.1 * np.exp(-self.M/self.T)
                final_B.append(B_L)
            self.h = original_h
            
            axes[1, 1].loglog(h_range, np.abs(final_B) + 1e-20, 'm-', linewidth=2)
            axes[1, 1].axhline(y=6e-10, color='k', linestyle=':', 
                              label='Наблюдаемое (6×10⁻¹⁰)')
            axes[1, 1].set_xlabel('Константа Юкавы h')
            axes[1, 1].set_ylabel('Барионная асимметрия η')
            axes[1, 1].set_title('Зависимость от связи')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
        
        # Конверсия в барионы через сфалероны
        final_asymmetry = L[-1] * 0.1
        
        print(f"\nЛептогенез - результаты:")
        print(f"  Начальная плотность N: {y0[0]:.2e}")
        print(f"  Конечная асимметрия L: {L[-1]:.2e}")
        print(f"  Предсказанная η (барионная): {final_asymmetry:.2e}")
        print(f"  Наблюдаемая η: 6×10⁻¹⁰")
        
        return final_asymmetry


class QuantumCreationInExpandingUniverse:
    """
    Рождение частиц из квантовых флуктуаций в расширяющейся Вселенной.
    
    Использует формализм коэффициентов Боголюбова для вычисления
    числа рожденных частиц при эволюции масштабного фактора.
    
    Attributes:
        m: масса поля
        H: параметр Хаббла
        a0: начальный масштабный фактор
    
    Example:
        >>> model = QuantumCreationInExpandingUniverse(mass=0.1, expansion_rate=0.01)
        >>> results = model.analyze_particle_creation()
    """
    
    def __init__(self, mass: float = 0.1, expansion_rate: float = 0.01):
        """
        Args:
            mass: масса поля
            expansion_rate: постоянная Хаббла H
        """
        self.m = mass
        self.H = expansion_rate
        self.a0 = 1.0
        
    def scale_factor(self, t: float) -> float:
        """
        Масштабный фактор для различных космологических эпох.
        
        Args:
            t: космологическое время
            
        Returns:
            a(t) - масштабный фактор
        """
        if t < 10:
            # Инфляция (экспоненциальное расширение)
            return self.a0 * np.exp(self.H * t)
        elif t < 100:
            # Радиационная эра (a ∝ √t)
            return self.a0 * np.exp(self.H * 10) * np.sqrt(1 + 0.1 * (t - 10))
        else:
            # Материальная эра (a ∝ t^(2/3))
            return self.a0 * np.exp(self.H * 10) * (1 + 0.01 * (t - 100))**(2/3)
    
    def solve_mode_evolution(self, k_values: List[float]) -> Dict:
        """
        Решение эволюции мод для разных импульсов k.
        
        Интегрирует уравнение Клейна-Гордона в расширяющейся
        Вселенной и вычисляет число рожденных частиц.
        
        Args:
            k_values: список импульсов
            
        Returns:
            словарь с результатами для каждого k
        """
        t_span = np.linspace(0, 200, 2000)
        results = {}
        
        for k in k_values:
            # Начальные условия (вакуум Банча-Дэвиса)
            chi0 = 1.0 / np.sqrt(2 * np.sqrt(k**2 + self.m**2))
            chi_dot0 = -1j * np.sqrt(k**2 + self.m**2) * chi0
            
            def equation(y, t):
                chi, chi_dot = y
                a = self.scale_factor(t)
                a_dot = self.H * a
                chi_ddot = -((k/a)**2 + self.m**2 - 2*(a_dot/a)**2) * chi
                return [chi_dot, chi_ddot]
            
            sol = odeint(equation, [chi0.real, chi_dot0.real], t_span)
            chi = sol[:, 0] + 1j * sol[:, 1]
            
            # Число рожденных частиц (коэффициент Боголюбова β)
            a_final = self.scale_factor(t_span[-1])
            omega_final = np.sqrt((k/a_final)**2 + self.m**2)
            
            beta_k = 0.5 * (np.sqrt(omega_final) * chi[-1] + 
                           1j/np.sqrt(omega_final) * sol[-1, 1])
            
            n_k = np.abs(beta_k)**2
            
            results[k] = {
                'chi': chi,
                'n_k': n_k,
                'times': t_span
            }
        
        return results
    
    def analyze_particle_creation(self, show_plot: bool = True) -> Dict:
        """
        Полный анализ рождения частиц.
        
        Args:
            show_plot: показывать ли графики
            
        Returns:
            результаты анализа
        """
        k_values = [0.01, 0.1, 1.0, 10.0]
        results = self.solve_mode_evolution(k_values)
        
        if show_plot:
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # 1. Масштабный фактор
            t_span = np.linspace(0, 200, 1000)
            a_vals = [self.scale_factor(t) for t in t_span]
            
            axes[0, 0].plot(t_span, a_vals, 'b-', linewidth=2)
            axes[0, 0].set_xlabel('Время')
            axes[0, 0].set_ylabel('a(t)')
            axes[0, 0].set_title('Расширение Вселенной')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Отметки эпох
            axes[0, 0].axvline(x=10, color='r', linestyle='--', alpha=0.5)
            axes[0, 0].axvline(x=100, color='r', linestyle='--', alpha=0.5)
            axes[0, 0].text(5, max(a_vals)*0.3, 'Инфляция', rotation=90, alpha=0.7)
            axes[0, 0].text(50, max(a_vals)*0.3, 'Радиация', rotation=90, alpha=0.7)
            axes[0, 0].text(150, max(a_vals)*0.3, 'Материя', rotation=90, alpha=0.7)
            
            # 2. Эволюция мод
            colors = plt.cm.viridis(np.linspace(0, 1, len(k_values)))
            
            for i, k in enumerate(k_values):
                result = results[k]
                axes[0, 1].plot(
                    result['times'], np.abs(result['chi']), 
                    color=colors[i], label=f'k = {k}', linewidth=2
                )
            
            axes[0, 1].set_xlabel('Время')
            axes[0, 1].set_ylabel('|χₖ(t)|')
            axes[0, 1].set_title('Эволюция мод поля')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
            
            # 3. Спектр рожденных частиц
            k_range = np.logspace(-3, 2, 50)
            n_k_values = []
            
            for k_test in k_range:
                result = self.solve_mode_evolution([k_test])
                n_k_values.append(result[k_test]['n_k'])
            
            axes[1, 0].loglog(k_range, n_k_values, 'g-', linewidth=2)
            axes[1, 0].set_xlabel('Импульс k')
            axes[1, 0].set_ylabel('Число частиц n(k)')
            axes[1, 0].set_title('Спектр рожденных частиц')
            axes[1, 0].grid(True, alpha=0.3)
            
            # 4. 3D зависимость от параметров
            axes[1, 1].remove()
            ax_3d = fig.add_subplot(2, 2, 4, projection='3d')
            
            mass_range = np.logspace(-2, 1, 10)
            H_range = np.logspace(-2, 0, 10)
            
            M, H = np.meshgrid(mass_range, H_range)
            density = np.zeros_like(M)
            
            for i in range(len(mass_range)):
                for j in range(len(H_range)):
                    self.m = mass_range[i]
                    self.H = H_range[j]
                    result = self.solve_mode_evolution([1.0])
                    density[j, i] = np.log10(result[1.0]['n_k'] + 1e-10)
            
            surf = ax_3d.plot_surface(
                np.log10(M), np.log10(H), density,
                cmap='viridis', alpha=0.8
            )
            
            ax_3d.set_xlabel('log₁₀(m)')
            ax_3d.set_ylabel('log₁₀(H)')
            ax_3d.set_zlabel('log₁₀(n)')
            ax_3d.set_title('Зависимость от параметров')
            
            plt.tight_layout()
            plt.show()
        
        print(f"\nКвантовое рождение частиц:")
        print(f"  Масса поля: {self.m}")
        print(f"  Параметр Хаббла: {self.H}")
        print(f"  Число частиц (k=0.1): {results[0.1]['n_k']:.2e}")
        
        return results

