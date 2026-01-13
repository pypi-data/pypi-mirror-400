#!/usr/bin/env python3
"""
Примеры запуска симуляций библиотеки oscillators.

Запуск всех примеров:
    python -m oscillators.examples

Запуск конкретного примера:
    python -m oscillators.examples --example matter_genesis
    python -m oscillators.examples --example spin_dynamics
    python -m oscillators.examples --example detailed_genesis
    python -m oscillators.examples --example parametric_resonance
    python -m oscillators.examples --example leptogenesis
    python -m oscillators.examples --example quantum_creation
"""

import argparse
import numpy as np
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, fcluster


def example_matter_genesis():
    """
    Пример 1: Симуляция рождения материи из инфлатона.
    
    Моделирует полный процесс от распада инфлатона до
    формирования частиц с барионной асимметрией.
    """
    from .simulation import MatterGenesisSimulation
    
    print("="*70)
    print("ПРИМЕР 1: Симуляция рождения материи")
    print("="*70)
    
    print("\nИнициализация симуляции...")
    print("Параметры:")
    print("  - Начальная энергия инфлатона: 1e16 GeV")
    print("  - Параметр Хаббла: 1e-5")
    print("  - Время симуляции: 1000 единиц")
    print("  - Начальная температура: 1e15 GeV\n")
    
    # Создание симуляции
    sim = MatterGenesisSimulation(
        volume_size=10.0,
        initial_inflaton_energy=1e16,
        hubble_parameter=1e-5
    )
    
    # Запуск эволюции
    history = sim.evolve_universe(total_time=1000.0, dt=0.1)
    
    # Визуализация
    sim.visualize_genesis(history)
    
    # Дополнительный анализ кластеризации
    if len(sim.particles) > 10:
        print("\nАнализ кластеризации частиц:")
        positions = np.array([p.position for p in sim.particles[:100]])
        
        if len(positions) > 1:
            distances = pdist(positions)
            print(f"  Среднее расстояние: {np.mean(distances):.3f}")
            print(f"  Минимальное: {np.min(distances):.3f}")
            print(f"  Максимальное: {np.max(distances):.3f}")
            
            if len(positions) > 3:
                Z = linkage(positions, method='ward')
                clusters = fcluster(Z, t=2, criterion='distance')
                n_clusters = len(set(clusters))
                print(f"  Обнаружено кластеров: {n_clusters}")
                
                if n_clusters > 1:
                    print("  → Наблюдается кластеризация (зародыш структуры!)")
    
    return sim, history


def example_spin_dynamics():
    """
    Пример 2: Эволюция спинов в расширяющейся вселенной.
    
    Демонстрирует спонтанное нарушение симметрии
    при остывании системы осцилляторов.
    """
    from .simulation import PrimordialOscillatorUniverse
    from .core import SpinType
    
    print("="*70)
    print("ПРИМЕР 2: Динамика спинов")
    print("="*70)
    
    print("\nСоздание вселенной осцилляторов...")
    universe = PrimordialOscillatorUniverse(total_energy=50.0)
    
    print("Запуск симуляции нарушения симметрии...")
    history = universe.simulate_symmetry_breaking(steps=500)
    
    # Визуализация
    universe.visualize_evolution(history)
    
    # Вычисление спиновой энтропии
    def calculate_entropy(osc_list):
        total = len(osc_list)
        probs = []
        for spin_type in SpinType:
            count = sum(1 for osc in osc_list if osc.spin == spin_type)
            if count > 0:
                probs.append(count / total)
        return -sum(p * np.log(p) for p in probs if p > 0)
    
    initial_universe = PrimordialOscillatorUniverse(total_energy=50.0)
    initial_entropy = calculate_entropy(initial_universe.oscillators)
    final_entropy = calculate_entropy(universe.oscillators)
    
    print(f"\nСпиновая энтропия:")
    print(f"  Начальная: {initial_entropy:.4f}")
    print(f"  Финальная: {final_entropy:.4f}")
    print(f"  Изменение: {final_entropy - initial_entropy:+.4f}")
    
    if final_entropy < initial_entropy:
        print("  → Возникла спиновая упорядоченность!")
    else:
        print("  → Спиновый беспорядок возрос")
    
    return universe, history


def example_detailed_genesis():
    """
    Пример 3: Полная детальная модель рождения материи.
    
    Объединяет все механизмы:
    - Инфляцию
    - Параметрический резонанс
    - Лептогенез
    - Нуклеосинтез
    """
    from .simulation import DetailedMatterGenesis
    
    print("="*70)
    print("ПРИМЕР 3: Детальная модель рождения материи")
    print("="*70)
    
    print("\nЭто может занять несколько минут...\n")
    
    model = DetailedMatterGenesis()
    results = model.simulate_full_genesis()
    
    return model, results


def example_parametric_resonance():
    """
    Пример 4: Параметрический резонанс (отдельный анализ).
    
    Демонстрирует механизм разогрева через
    неустойчивость уравнения Матье.
    """
    from .models import ParametricResonance
    
    print("="*70)
    print("ПРИМЕР 4: Параметрический резонанс")
    print("="*70)
    
    print("\nАнализ параметрического резонанса при разогреве...")
    
    resonance = ParametricResonance(inflaton_mass=1e13, coupling=1e-7)
    results = resonance.simulate_resonance_bands()
    
    # Тест разных параметров
    print("\nТестирование разных параметров:")
    test_params = [
        (1e13, 1e-7),
        (1e12, 1e-6),
        (1e14, 1e-8)
    ]
    
    for mass, coupling in test_params:
        resonance.m = mass
        resonance.g = coupling
        
        k_sample = 1.0
        phi_sample = 1e16
        rate = resonance.particle_production_rate(phi_sample, k_sample)
        
        print(f"  M={mass:.1e} GeV, g={coupling:.1e}: dn/dt = {rate:.2e}")
    
    return resonance, results


def example_leptogenesis():
    """
    Пример 5: Лептогенез (отдельный анализ).
    
    Демонстрирует генерацию барионной асимметрии
    через распад тяжелых нейтрино.
    """
    from .models import LeptogenesisModel
    
    print("="*70)
    print("ПРИМЕР 5: Лептогенез")
    print("="*70)
    
    print("\nМоделирование лептогенеза...")
    print("Параметры:")
    print("  - Масса тяжелого нейтрино: 1e10 GeV")
    print("  - Константа Юкавы: 1e-6")
    print("  - CP-нарушение: 1e-6\n")
    
    model = LeptogenesisModel(M=1e10, Yukawa=1e-6, CP_violation=1e-6)
    asymmetry = model.solve_leptogenesis()
    
    return model, asymmetry


def example_quantum_creation():
    """
    Пример 6: Квантовое рождение в расширяющейся Вселенной.
    
    Демонстрирует рождение частиц из вакуума
    при изменении масштабного фактора.
    """
    from .models import QuantumCreationInExpandingUniverse
    
    print("="*70)
    print("ПРИМЕР 6: Квантовое рождение частиц")
    print("="*70)
    
    print("\nМоделирование квантового рождения...")
    print("Параметры:")
    print("  - Масса поля: 0.1")
    print("  - Параметр Хаббла: 0.01\n")
    
    model = QuantumCreationInExpandingUniverse(mass=0.1, expansion_rate=0.01)
    results = model.analyze_particle_creation()
    
    return model, results


def run_all_examples():
    """Запуск всех примеров последовательно."""
    print("\n" + "="*70)
    print("ЗАПУСК ВСЕХ ПРИМЕРОВ БИБЛИОТЕКИ COSMOLOGY")
    print("="*70 + "\n")
    
    examples = [
        ("Параметрический резонанс", example_parametric_resonance),
        ("Лептогенез", example_leptogenesis),
        ("Квантовое рождение", example_quantum_creation),
        ("Рождение материи", example_matter_genesis),
        ("Динамика спинов", example_spin_dynamics),
        ("Детальная модель", example_detailed_genesis),
    ]
    
    results = {}
    
    for name, func in examples:
        print(f"\n{'='*70}")
        print(f"Запуск: {name}")
        print("="*70)
        
        try:
            results[name] = func()
            print(f"\n✓ {name} - выполнено успешно")
        except Exception as e:
            print(f"\n✗ {name} - ошибка: {e}")
            results[name] = None
    
    print("\n" + "="*70)
    print("ВСЕ ПРИМЕРЫ ЗАВЕРШЕНЫ")
    print("="*70)
    
    return results


def main():
    """Главная функция запуска примеров."""
    parser = argparse.ArgumentParser(
        description="Примеры использования библиотеки oscillators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Доступные примеры:
  matter_genesis      - Симуляция рождения материи из инфлатона
  spin_dynamics       - Эволюция спинов в расширяющейся вселенной
  detailed_genesis    - Полная детальная модель рождения материи
  parametric_resonance - Параметрический резонанс при разогреве
  leptogenesis        - Генерация барионной асимметрии
  quantum_creation    - Квантовое рождение из вакуума
  all                 - Запуск всех примеров

Примеры использования:
  python -m oscillators.examples --example matter_genesis
  python -m oscillators.examples --example all
  python -m oscillators.examples --list
        """
    )
    
    parser.add_argument(
        "--example", "-e",
        type=str,
        default="all",
        help="Название примера для запуска (по умолчанию: all)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Показать список доступных примеров"
    )
    
    args = parser.parse_args()
    
    examples_map = {
        "matter_genesis": example_matter_genesis,
        "spin_dynamics": example_spin_dynamics,
        "detailed_genesis": example_detailed_genesis,
        "parametric_resonance": example_parametric_resonance,
        "leptogenesis": example_leptogenesis,
        "quantum_creation": example_quantum_creation,
        "all": run_all_examples,
    }
    
    if args.list:
        print("\nДоступные примеры:")
        print("-" * 50)
        for name, func in examples_map.items():
            if name != "all":
                doc = func.__doc__.split('\n')[1].strip() if func.__doc__ else ""
                print(f"  {name:25s} - {doc}")
        print(f"  {'all':25s} - Запуск всех примеров")
        return
    
    if args.example not in examples_map:
        print(f"Ошибка: неизвестный пример '{args.example}'")
        print(f"Доступные примеры: {', '.join(examples_map.keys())}")
        return
    
    # Запуск выбранного примера
    examples_map[args.example]()


if __name__ == "__main__":
    main()

