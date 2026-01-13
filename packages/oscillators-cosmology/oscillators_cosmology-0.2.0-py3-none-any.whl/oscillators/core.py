"""
Базовые классы и структуры данных для космологических симуляций.

Этот модуль содержит фундаментальные типы данных:
- SpinType: типы спина частиц
- ParticleType: типы частиц
- Particle: класс частицы
- QuantumOscillator: квантовый осциллятор с учетом спина
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class SpinType(Enum):
    """
    Типы спина частиц (в единицах ħ).
    
    Определяет статистику частиц:
    - Целый спин (0, 1, 2) → бозоны (статистика Бозе-Эйнштейна)
    - Полуцелый спин (1/2) → фермионы (статистика Ферми-Дирака)
    """
    SCALAR = 0      # Бозон, спин 0 (хиггс, инфлатон)
    SPINOR = 0.5    # Фермион, спин 1/2 (электроны, кварки)
    VECTOR = 1      # Бозон, спин 1 (фотоны, глюоны, W/Z)
    TENSOR = 2      # Бозон, спин 2 (гравитоны)


class ParticleType(Enum):
    """
    Типы рождающихся частиц в ранней Вселенной.
    
    Включает как частицы Стандартной Модели,
    так и гипотетические (темная материя, инфлатон).
    """
    INFLATON = "inflaton"       # Скалярное поле инфлатона
    PHOTON = "photon"           # Электромагнитное излучение
    QUARK = "quark"             # Кварки
    LEPTON = "lepton"           # Лептоны (электроны, нейтрино)
    DARK_MATTER = "dark_matter" # Темная материя
    HIGGS = "higgs"             # Бозон Хиггса


@dataclass
class Particle:
    """
    Рожденная частица в космологической симуляции.
    
    Attributes:
        type: тип частицы (ParticleType)
        energy: энергия частицы в GeV
        momentum: 3-вектор импульса
        position: 3-вектор положения
        spin: спин частицы
        creation_time: время рождения
        antiparticle: флаг античастицы
        lifetime: время жизни частицы (None = стабильная)
    """
    type: ParticleType
    energy: float
    momentum: np.ndarray
    position: np.ndarray
    spin: float
    creation_time: float
    antiparticle: bool = False
    lifetime: Optional[float] = None
    
    def __post_init__(self):
        """Установка времени жизни частицы."""
        if self.lifetime is None:
            self.lifetime = get_particle_lifetime(self.type)
    
    def __str__(self):
        prefix = "anti-" if self.antiparticle else ""
        return f"{prefix}{self.type.value}: E={self.energy:.3e} GeV, |p|={np.linalg.norm(self.momentum):.3e}"
    
    @property
    def mass(self) -> float:
        """Вычисление массы из E² = p² + m² (c=1)"""
        p_squared = np.sum(self.momentum**2)
        m_squared = self.energy**2 - p_squared
        return np.sqrt(max(0, m_squared))
    
    @property
    def velocity(self) -> np.ndarray:
        """Вычисление скорости v = p/E"""
        if self.energy > 0:
            return self.momentum / self.energy
        return np.zeros(3)
    
    def is_decayed(self, current_time: float) -> bool:
        """
        Проверка, распалась ли частица.
        
        Args:
            current_time: текущее время симуляции
            
        Returns:
            True если частица распалась
        """
        if self.lifetime is None:
            return False
        age = current_time - self.creation_time
        # Экспоненциальный распад: P(decay) = 1 - exp(-t/τ)
        decay_prob = 1.0 - np.exp(-age / self.lifetime)
        return np.random.random() < decay_prob


@dataclass
class QuantumOscillator:
    """
    Квантовый осциллятор с учетом спина.
    
    Моделирует квантовое поле как осциллятор с определенной
    частотой, амплитудой и спиновым состоянием.
    
    Attributes:
        frequency: частота осциллятора (связана с массой)
        amplitude: комплексная амплитуда
        spin: тип спина (SpinType)
        spin_state: вектор состояния в пространстве спина
        position: пространственное положение
    """
    frequency: float
    amplitude: complex
    spin: SpinType
    spin_state: Optional[np.ndarray] = None
    position: Optional[np.ndarray] = None
    
    def __post_init__(self):
        """Инициализация спинового состояния после создания объекта."""
        if self.position is None:
            self.position = np.zeros(3)
            
        # Инициализируем пространство спина в зависимости от типа
        if self.spin_state is None:
            if self.spin == SpinType.SCALAR:
                self.spin_state = np.array([1.0], dtype=complex)
                self.spin_dim = 1
            elif self.spin == SpinType.SPINOR:
                # Спинор: два компонента (спин "вверх" по умолчанию)
                self.spin_state = np.array([1.0, 0.0], dtype=complex)
                self.spin_dim = 2
            elif self.spin == SpinType.VECTOR:
                # Вектор: три компонента (поляризации)
                self.spin_state = np.array([1.0, 0.0, 0.0], dtype=complex)
                self.spin_dim = 3
            elif self.spin == SpinType.TENSOR:
                # Тензор 2-го ранга: 5 независимых компонент для спина 2
                self.spin_state = np.array([1.0, 0.0, 0.0, 0.0, 0.0], dtype=complex)
                self.spin_dim = 5
        else:
            self.spin_dim = len(self.spin_state)
    
    @property
    def energy(self) -> float:
        """Энергия осциллятора E = |amplitude|² × frequency"""
        return np.abs(self.amplitude)**2 * self.frequency
    
    def evolve_spin(self, dt: float, magnetic_field: Optional[np.ndarray] = None):
        """
        Эволюция спинового состояния во внешнем поле.
        
        Использует уравнение Паули для спина 1/2.
        
        Args:
            dt: временной шаг
            magnetic_field: 3-вектор магнитного поля
        """
        if self.spin == SpinType.SCALAR:
            return  # Скаляры не имеют спиновой динамики
        
        # Матрицы Паули для спина 1/2
        sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
        sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
        
        if self.spin == SpinType.SPINOR and magnetic_field is not None:
            # Уравнение Паули (нерелятивистский предел Дирака)
            H = -0.5 * (magnetic_field[0] * sigma_x + 
                        magnetic_field[1] * sigma_y + 
                        magnetic_field[2] * sigma_z)
            U = np.eye(2, dtype=complex) - 1j * H * dt
            self.spin_state = U @ self.spin_state
            self.spin_state /= np.linalg.norm(self.spin_state)
    
    def evolve_amplitude(self, dt: float, damping: float = 0.0):
        """
        Эволюция амплитуды осциллятора.
        
        Args:
            dt: временной шаг
            damping: коэффициент затухания (трение Хаббла)
        """
        # Фазовая эволюция с затуханием
        phase_factor = np.exp(-1j * self.frequency * dt - damping * dt)
        self.amplitude *= phase_factor


# Физические константы (в натуральных единицах ħ = c = k_B = 1)
class PhysicalConstants:
    """
    Физические константы для космологических вычислений.
    
    Используются натуральные единицы: ħ = c = k_B = 1.
    Энергия измеряется в GeV, время в GeV⁻¹, длина в GeV⁻¹.
    
    Конверсии:
        - 1 GeV⁻¹ ≈ 6.58 × 10⁻²⁵ сек
        - 1 GeV⁻¹ ≈ 1.97 × 10⁻¹⁶ м
        - 1 К ≈ 8.62 × 10⁻¹⁴ GeV
    """
    
    # Фундаментальные константы (в натуральных единицах)
    SPEED_OF_LIGHT = 1.0        # c = 1
    PLANCK_CONSTANT = 1.0       # ħ = 1
    BOLTZMANN_CONSTANT = 1.0    # k_B = 1
    
    # Гравитационная константа G = 1/M_Planck² в натуральных единицах
    GRAVITATIONAL_CONSTANT = 1.0 / (1.22e19)**2
    
    # Конверсионные факторы
    GEV_TO_SECONDS = 6.58e-25      # 1 GeV⁻¹ в секундах
    GEV_TO_METERS = 1.97e-16       # 1 GeV⁻¹ в метрах
    KELVIN_TO_GEV = 8.617e-14      # 1 К в GeV
    
    # Массы частиц в GeV
    ELECTRON_MASS = 0.000511
    MUON_MASS = 0.1057
    TAU_MASS = 1.777
    UP_QUARK_MASS = 0.0022
    DOWN_QUARK_MASS = 0.0047
    STRANGE_QUARK_MASS = 0.095
    CHARM_QUARK_MASS = 1.27
    BOTTOM_QUARK_MASS = 4.18
    TOP_QUARK_MASS = 173.0
    HIGGS_MASS = 125.1
    W_BOSON_MASS = 80.4
    Z_BOSON_MASS = 91.2
    PROTON_MASS = 0.938
    NEUTRON_MASS = 0.940
    
    # Планковские единицы
    PLANCK_MASS = 1.22e19         # GeV
    PLANCK_TIME = 5.39e-44        # секунды
    PLANCK_LENGTH = 1.62e-35      # метры
    PLANCK_TEMPERATURE = 1.42e32  # Кельвин
    
    # Космологические параметры (Planck 2018)
    CMB_TEMPERATURE = 2.7255      # Кельвин
    CMB_TEMPERATURE_GEV = 2.7255 * 8.617e-14  # В GeV
    BARYON_TO_PHOTON_RATIO = 6.1e-10  # η = n_B / n_γ
    DARK_MATTER_FRACTION = 0.268  # Ω_DM (Planck 2018)
    DARK_ENERGY_FRACTION = 0.684  # Ω_Λ (Planck 2018)
    BARYON_FRACTION = 0.049       # Ω_b (Planck 2018)
    HUBBLE_CONSTANT = 67.4        # km/s/Mpc (Planck 2018)
    
    # Температуры фазовых переходов
    ELECTROWEAK_SCALE = 246.0     # GeV (VEV Хиггса)
    QCD_SCALE = 0.2               # GeV (Λ_QCD)
    GUT_SCALE = 1e16              # GeV (приблизительно)
    
    # Константы взаимодействия (при масштабе M_Z)
    FINE_STRUCTURE = 1.0 / 137.036      # α_EM
    WEAK_COUPLING = 1.0 / 30.0          # α_W
    STRONG_COUPLING = 0.118             # α_s(M_Z)
    
    # Степени свободы
    G_EFF_SM_HIGH_T = 106.75    # g_* для T >> 100 GeV
    G_EFF_SM_LOW_T = 3.36       # g_* после аннигиляции e+e-


def get_particle_mass(ptype: ParticleType) -> float:
    """
    Получить массу частицы по типу (в GeV).
    
    Args:
        ptype: тип частицы
        
    Returns:
        масса в GeV
    """
    masses = {
        ParticleType.INFLATON: 1e13,
        ParticleType.PHOTON: 0.0,
        ParticleType.QUARK: 0.005,  # средняя легких кварков
        ParticleType.LEPTON: PhysicalConstants.ELECTRON_MASS,
        ParticleType.DARK_MATTER: 100.0,  # WIMP кандидат
        ParticleType.HIGGS: PhysicalConstants.HIGGS_MASS
    }
    return masses.get(ptype, 0.0)


def get_particle_spin(ptype: ParticleType) -> float:
    """
    Получить спин частицы по типу.
    
    Args:
        ptype: тип частицы
        
    Returns:
        спин в единицах ħ
    """
    spins = {
        ParticleType.INFLATON: 0,    # скаляр
        ParticleType.PHOTON: 1,      # вектор
        ParticleType.QUARK: 0.5,     # фермион
        ParticleType.LEPTON: 0.5,    # фермион
        ParticleType.DARK_MATTER: 0.5,  # предположение
        ParticleType.HIGGS: 0        # скаляр
    }
    return spins.get(ptype, 0)


def get_particle_lifetime(ptype: ParticleType) -> Optional[float]:
    """
    Получить время жизни частицы (в планковских единицах времени).
    
    Инфлатоны распадаются очень быстро (~10^-37 секунд).
    Хиггс нестабилен (~10^-22 секунд).
    Остальные частицы условно стабильны на масштабах симуляции.
    
    Args:
        ptype: тип частицы
        
    Returns:
        время жизни или None (стабильная)
    """
    lifetimes = {
        ParticleType.INFLATON: 1e-5,     # Очень быстрый распад (~10^-37 с)
        ParticleType.PHOTON: None,        # Стабильный
        ParticleType.QUARK: None,         # Связанные в адронах
        ParticleType.LEPTON: None,        # Электрон стабилен
        ParticleType.DARK_MATTER: None,   # Стабильная (по определению)
        ParticleType.HIGGS: 1e-3          # ~10^-22 секунд
    }
    return lifetimes.get(ptype, None)


def fermi_dirac(energy: float, temperature: float, mu: float = 0.0) -> float:
    """
    Распределение Ферми-Дирака для фермионов.
    
    f(E) = 1 / (exp((E-μ)/T) + 1)
    
    Args:
        energy: энергия частицы (GeV)
        temperature: температура (GeV)
        mu: химический потенциал (GeV)
        
    Returns:
        вероятность занятости состояния
    """
    if temperature <= 0:
        return 0.0
    x = (energy - mu) / temperature
    if x > 50:  # Защита от переполнения
        return 0.0
    if x < -50:
        return 1.0
    return 1.0 / (np.exp(x) + 1.0)


def bose_einstein(energy: float, temperature: float, mu: float = 0.0) -> float:
    """
    Распределение Бозе-Эйнштейна для бозонов.
    
    n(E) = 1 / (exp((E-μ)/T) - 1)
    
    Args:
        energy: энергия частицы (GeV)
        temperature: температура (GeV)
        mu: химический потенциал (GeV)
        
    Returns:
        среднее число частиц в состоянии
    """
    if temperature <= 0:
        return 0.0
    x = (energy - mu) / temperature
    if x > 50:  # Защита от переполнения
        return 0.0
    if x < 0.01:  # Защита от деления на ноль
        return temperature / energy if energy > 0 else 0.0
    return 1.0 / (np.exp(x) - 1.0)


def planck_distribution(energy: float, temperature: float) -> float:
    """
    Планковское распределение для фотонов (μ=0).
    
    Args:
        energy: энергия фотона (GeV)
        temperature: температура (GeV)
        
    Returns:
        среднее число фотонов в моде
    """
    return bose_einstein(energy, temperature, mu=0.0)


def thermal_energy_density(temperature: float, g_eff: float = 106.75) -> float:
    """
    Плотность энергии релятивистского газа.
    
    ρ = (π²/30) × g_eff × T⁴
    
    Args:
        temperature: температура (GeV)
        g_eff: эффективное число степеней свободы
               (106.75 для СМ при T > 100 GeV)
        
    Returns:
        плотность энергии (GeV⁴)
    """
    return (np.pi**2 / 30) * g_eff * temperature**4

