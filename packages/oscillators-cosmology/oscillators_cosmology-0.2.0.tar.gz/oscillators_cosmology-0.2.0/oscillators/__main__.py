#!/usr/bin/env python3
"""
CLI интерфейс для библиотеки oscillators-cosmology.

Использование:
    python -m oscillators --help
    python -m oscillators simulate --time 1000
    python -m oscillators info
    python -m oscillators calibrate
"""

import sys
import os

# Проверяем, установлен ли click
try:
    import click
except ImportError:
    print("Для CLI требуется пакет 'click'. Установите его командой:")
    print("  pip install click")
    print("\nИли используйте библиотеку напрямую через Python API.")
    sys.exit(1)

import numpy as np


@click.group()
@click.version_option(version="0.1.0", prog_name="oscillators")
def cli():
    """
    Oscillators Cosmology - библиотека для моделирования рождения материи во Вселенной.
    
    Примеры:
    
        # Информация о библиотеке
        python -m oscillators info
        
        # Быстрая симуляция
        python -m oscillators simulate --quick
        
        # Полная симуляция
        python -m oscillators simulate --time 1000 --output ./report
        
        # Запуск калибровки
        python -m oscillators calibrate
    """
    pass


@cli.command()
def info():
    """Показать информацию о библиотеке."""
    from oscillators import info as show_info
    show_info()


@cli.command()
@click.option('--time', '-t', default=500.0, help='Время симуляции (по умолчанию 500)')
@click.option('--dt', default=0.5, help='Временной шаг (по умолчанию 0.5)')
@click.option('--volume', '-v', default=10.0, help='Размер объёма (по умолчанию 10)')
@click.option('--energy', '-e', default=1e12, help='Энергия инфлатона в GeV (по умолчанию 1e12)')
@click.option('--hubble', '-H', default=1e-5, help='Параметр Хаббла (по умолчанию 1e-5)')
@click.option('--cp-violation', default=1e-10, help='Параметр CP-нарушения (по умолчанию 1e-10)')
@click.option('--output', '-o', default='./report', help='Директория для отчёта')
@click.option('--quick', is_flag=True, help='Быстрая демонстрация (короткое время)')
@click.option('--no-plot', is_flag=True, help='Не показывать графики')
@click.option('--save-report', is_flag=True, help='Сохранить отчёт в файл')
def simulate(time, dt, volume, energy, hubble, cp_violation, output, quick, no_plot, save_report):
    """
    Запустить симуляцию рождения материи.
    
    Примеры:
    
        # Быстрая демонстрация
        python -m oscillators simulate --quick
        
        # Полная симуляция с сохранением отчёта
        python -m oscillators simulate --time 1000 --save-report --output ./my_report
        
        # Симуляция без графиков
        python -m oscillators simulate --no-plot
    """
    import matplotlib
    if no_plot:
        matplotlib.use('Agg')
    
    from oscillators import MatterGenesisSimulation, create_final_report
    
    if quick:
        time = 100.0
        dt = 1.0
        click.echo("🚀 Запуск быстрой демонстрации...")
    else:
        click.echo(f"🌌 Запуск симуляции рождения материи...")
    
    click.echo(f"   Параметры:")
    click.echo(f"   - Время: {time}")
    click.echo(f"   - Шаг: {dt}")
    click.echo(f"   - Объём: {volume}")
    click.echo(f"   - Энергия инфлатона: {energy:.1e} GeV")
    click.echo(f"   - CP-нарушение: {cp_violation:.1e}")
    click.echo()
    
    # Создаём симуляцию
    sim = MatterGenesisSimulation(
        volume_size=volume,
        initial_inflaton_energy=energy,
        hubble_parameter=hubble,
        cp_violation=cp_violation
    )
    
    # Запускаем эволюцию
    history = sim.evolve_universe(total_time=time, dt=dt, show_progress=True)
    
    # Результаты
    final = history[-1]
    click.echo()
    click.echo("=" * 60)
    click.echo("📊 РЕЗУЛЬТАТЫ СИМУЛЯЦИИ")
    click.echo("=" * 60)
    click.echo(f"   Частиц создано: {final['n_particles']}")
    click.echo(f"   Барионная асимметрия η: {final['baryon_asymmetry']:.2e}")
    click.echo(f"   (наблюдаемое значение: 6.1×10⁻¹⁰)")
    click.echo(f"   Температура: {final['temperature']:.2e} GeV")
    click.echo()
    
    # Визуализация
    if not no_plot:
        click.echo("📈 Создание визуализации...")
        sim.visualize_genesis(history)
    
    # Сохранение отчёта
    if save_report:
        click.echo(f"💾 Сохранение отчёта в {output}...")
        os.makedirs(output, exist_ok=True)
        create_final_report(sim, history, save_path=output)
        click.echo(f"✅ Отчёт сохранён в {os.path.abspath(output)}")
    
    click.echo()
    click.echo("✨ Симуляция завершена!")


@cli.command()
@click.option('--output', '-o', default='./report', help='Директория для отчёта')
def detailed(output):
    """
    Запустить детальную симуляцию всех фаз.
    
    Включает:
    - Инфляцию и квантовые флуктуации
    - Параметрический резонанс (разогрев)
    - Лептогенез и барионную асимметрию
    - Установление равновесия и нуклеосинтез
    """
    from oscillators import DetailedMatterGenesis
    
    click.echo("🌌 Запуск детальной симуляции рождения материи...")
    click.echo("   Это может занять несколько минут...")
    click.echo()
    
    model = DetailedMatterGenesis()
    results = model.simulate_full_genesis()
    
    click.echo()
    click.echo("✨ Детальная симуляция завершена!")


@cli.command()
@click.option('--output', '-o', default='./report', help='Директория для отчёта')
def calibrate(output):
    """
    Запустить калибровку параметров под данные Planck.
    
    Создаёт отчёт с откалиброванными параметрами для достижения
    наблюдаемой барионной асимметрии η ≈ 6.1×10⁻¹⁰.
    """
    from oscillators import create_calibration_report
    
    click.echo("🔧 Запуск калибровки под данные Planck 2018...")
    click.echo()
    
    params = create_calibration_report(save_path=output)
    
    click.echo()
    click.echo("📊 Откалиброванные параметры:")
    for key, value in params.items():
        click.echo(f"   {key}: {value}")
    
    click.echo()
    click.echo(f"✅ Отчёт о калибровке сохранён в {os.path.abspath(output)}")


@cli.command()
@click.option('--example', '-e', type=click.Choice([
    'matter_genesis', 'spin_dynamics', 'detailed_genesis',
    'parametric_resonance', 'leptogenesis', 'quantum_creation'
]), help='Название примера для запуска')
@click.option('--list', 'list_examples', is_flag=True, help='Показать список примеров')
def examples(example, list_examples):
    """
    Запуск примеров использования библиотеки.
    
    Примеры:
    
        # Список всех примеров
        python -m oscillators examples --list
        
        # Запуск конкретного примера
        python -m oscillators examples -e matter_genesis
    """
    available_examples = {
        'matter_genesis': 'Симуляция рождения материи из инфлатона',
        'spin_dynamics': 'Эволюция спинов в первичной Вселенной',
        'detailed_genesis': 'Детальная модель всех фаз рождения материи',
        'parametric_resonance': 'Параметрический резонанс при разогреве',
        'leptogenesis': 'Лептогенез и барионная асимметрия',
        'quantum_creation': 'Квантовое рождение в расширяющейся Вселенной'
    }
    
    if list_examples:
        click.echo("📚 Доступные примеры:")
        click.echo()
        for name, desc in available_examples.items():
            click.echo(f"   {name:25s} - {desc}")
        click.echo()
        click.echo("Запуск: python -m oscillators examples -e <название>")
        return
    
    if example is None:
        click.echo("❌ Укажите пример через --example или используйте --list")
        return
    
    click.echo(f"🚀 Запуск примера: {example}")
    click.echo(f"   {available_examples[example]}")
    click.echo()
    
    # Импортируем и запускаем соответствующий пример
    from oscillators.examples import (
        run_matter_genesis_example,
        run_spin_dynamics_example,
        run_detailed_genesis_example,
        run_parametric_resonance_example,
        run_leptogenesis_example,
        run_quantum_creation_example
    )
    
    example_funcs = {
        'matter_genesis': run_matter_genesis_example,
        'spin_dynamics': run_spin_dynamics_example,
        'detailed_genesis': run_detailed_genesis_example,
        'parametric_resonance': run_parametric_resonance_example,
        'leptogenesis': run_leptogenesis_example,
        'quantum_creation': run_quantum_creation_example
    }
    
    example_funcs[example]()


@cli.command()
def benchmark():
    """
    Запуск бенчмарка производительности.
    
    Измеряет время выполнения различных компонентов симуляции.
    """
    import time
    from oscillators import (
        MatterGenesisSimulation, ParametricResonance,
        LeptogenesisModel, QuantumCreationInExpandingUniverse
    )
    
    click.echo("⏱️  Запуск бенчмарка производительности...")
    click.echo()
    
    results = {}
    
    # Тест ParametricResonance
    click.echo("   [1/4] ParametricResonance...")
    start = time.time()
    pr = ParametricResonance()
    pr.simulate_resonance_bands(show_plot=False)
    results['parametric_resonance'] = time.time() - start
    
    # Тест LeptogenesisModel
    click.echo("   [2/4] LeptogenesisModel...")
    start = time.time()
    lm = LeptogenesisModel()
    lm.solve_leptogenesis(t_max=100, show_plot=False)
    results['leptogenesis'] = time.time() - start
    
    # Тест QuantumCreation
    click.echo("   [3/4] QuantumCreation...")
    start = time.time()
    qc = QuantumCreationInExpandingUniverse()
    qc.solve_mode_evolution([0.1, 1.0, 10.0])
    results['quantum_creation'] = time.time() - start
    
    # Тест MatterGenesis
    click.echo("   [4/4] MatterGenesisSimulation...")
    start = time.time()
    sim = MatterGenesisSimulation(volume_size=1.0)
    sim.evolve_universe(total_time=100, dt=1.0, show_progress=False)
    results['matter_genesis'] = time.time() - start
    
    click.echo()
    click.echo("=" * 50)
    click.echo("📊 РЕЗУЛЬТАТЫ БЕНЧМАРКА")
    click.echo("=" * 50)
    for name, duration in results.items():
        click.echo(f"   {name:25s}: {duration:6.2f} сек")
    click.echo("-" * 50)
    click.echo(f"   {'Всего':25s}: {sum(results.values()):6.2f} сек")
    click.echo("=" * 50)


def main():
    """Точка входа для CLI."""
    cli()


if __name__ == '__main__':
    main()

