"""
Oscillators - библиотека для моделирования рождения материи во Вселенной.

Эта библиотека реализует различные космологические модели:
- Параметрический резонанс и разогрев после инфляции
- Лептогенез и барионная асимметрия
- Квантовое рождение частиц в расширяющейся Вселенной
- Симуляция полного процесса genesis материи

Основные классы:
-----------------
Базовые типы (core):
    - SpinType: типы спина частиц (скаляр, спинор, вектор, тензор)
    - ParticleType: типы частиц (кварки, лептоны, фотоны и др.)
    - Particle: класс частицы с энергией, импульсом и положением
    - QuantumOscillator: квантовый осциллятор с учетом спина

Физические модели (models):
    - ParametricResonance: параметрический резонанс при разогреве
    - LeptogenesisModel: генерация барионной асимметрии
    - QuantumCreationInExpandingUniverse: рождение из вакуума

Симуляции (simulation):
    - MatterGenesisSimulation: рождение материи из инфлатона
    - PrimordialOscillatorUniverse: модель осцилляторов
    - DetailedMatterGenesis: полная интегрированная модель

Быстрый старт:
--------------
>>> from oscillators import MatterGenesisSimulation
>>> sim = MatterGenesisSimulation(volume_size=10.0)
>>> history = sim.evolve_universe(total_time=1000.0)
>>> sim.visualize_genesis(history)

Версия: 1.0.0
Автор: Timur Isanov <xtimon@yahoo.com>
"""

__version__ = "0.1.0"
__author__ = "Timur Isanov <xtimon@yahoo.com>"

# Базовые типы данных
from .core import (
    SpinType,
    ParticleType,
    Particle,
    QuantumOscillator,
    PhysicalConstants,
    get_particle_mass,
    get_particle_spin,
    get_particle_lifetime,
    fermi_dirac,
    bose_einstein,
    planck_distribution,
    thermal_energy_density,
)

# Физические модели
from .models import (
    ParametricResonance,
    LeptogenesisModel,
    QuantumCreationInExpandingUniverse,
)

# Симуляции
from .simulation import (
    MatterGenesisSimulation,
    PrimordialOscillatorUniverse,
    DetailedMatterGenesis,
)

# Визуализация и отчёты
from .visualization import (
    FinalVisualization,
    CosmologyReportVisualizer,
    create_final_report,
)

# Калибровка под данные Planck
from .calibration import (
    PlanckData,
    CosmologyCalibrator,
    create_calibration_report,
    get_calibrated_params,
    load_calibrated_params,
    CALIBRATED_PARAMS,
)

# Логирование
from .logging_config import (
    get_logger,
    setup_logging,
    set_level,
    enable_debug,
    enable_quiet,
)

# Публичный API
__all__ = [
    # Версия
    "__version__",
    "__author__",
    
    # Базовые типы
    "SpinType",
    "ParticleType", 
    "Particle",
    "QuantumOscillator",
    "PhysicalConstants",
    "get_particle_mass",
    "get_particle_spin",
    "get_particle_lifetime",
    
    # Термодинамические распределения
    "fermi_dirac",
    "bose_einstein",
    "planck_distribution",
    "thermal_energy_density",
    
    # Модели
    "ParametricResonance",
    "LeptogenesisModel",
    "QuantumCreationInExpandingUniverse",
    
    # Симуляции
    "MatterGenesisSimulation",
    "PrimordialOscillatorUniverse",
    "DetailedMatterGenesis",
    
    # Визуализация
    "FinalVisualization",
    "CosmologyReportVisualizer",
    "create_final_report",
    
    # Калибровка
    "PlanckData",
    "CosmologyCalibrator",
    "create_calibration_report",
    "get_calibrated_params",
    "load_calibrated_params",
    "CALIBRATED_PARAMS",
    
    # Логирование
    "get_logger",
    "setup_logging",
    "set_level",
    "enable_debug",
    "enable_quiet",
    
    # Фабричная функция
    "create_calibrated_simulation",
]


def create_calibrated_simulation(
    volume_size: float = 10.0,
    initial_inflaton_energy: float = 1e12,
    hubble_parameter: float = 1e-5,
    use_file: str = None
):
    """
    Создание симуляции с откалиброванными параметрами Planck 2018.
    
    Args:
        volume_size: размер объёма симуляции
        initial_inflaton_energy: энергия инфлатона (GeV)
        hubble_parameter: параметр Хаббла
        use_file: путь к файлу с параметрами (опционально)
        
    Returns:
        MatterGenesisSimulation с откалиброванными параметрами
        
    Example:
        >>> sim = create_calibrated_simulation()
        >>> history = sim.evolve_universe(total_time=500.0)
    """
    if use_file:
        params = load_calibrated_params(use_file)
    else:
        params = get_calibrated_params()
    
    return MatterGenesisSimulation(
        volume_size=volume_size,
        initial_inflaton_energy=initial_inflaton_energy,
        hubble_parameter=hubble_parameter,
        reheating_temperature=params.get('reheating_temp', 1e9),
        cp_violation=params.get('CP_violation', 4.97e-11)
    )


def info():
    """Выводит информацию о библиотеке."""
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                   OSCILLATORS LIBRARY v{__version__}                     ║
╠══════════════════════════════════════════════════════════════════╣
║  Библиотека для моделирования рождения материи во Вселенной      ║
╠══════════════════════════════════════════════════════════════════╣
║  Доступные модули:                                               ║
║    • core          - базовые типы данных и частицы               ║
║    • models        - физические модели (резонанс, лептогенез)    ║
║    • simulation    - комплексные симуляции                       ║
║    • visualization - визуализация и отчёты                       ║
╠══════════════════════════════════════════════════════════════════╣
║  Примеры: python run_examples.py --example matter_genesis        ║
║  Отчёт:   python run_examples.py --report                        ║
╚══════════════════════════════════════════════════════════════════╝
""")
