# Oscillators Library

Библиотека для моделирования рождения материи во Вселенной.

## Описание

Эта библиотека реализует различные космологические модели для симуляции процессов, происходивших в ранней Вселенной:

- **Параметрический резонанс** — механизм разогрева после инфляции
- **Лептогенез** — генерация барионной асимметрии через CP-нарушение
- **Квантовое рождение** — частицы из вакуумных флуктуаций
- **Полная симуляция** — от инфляции до современного состава Вселенной

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/xtimon/oscillator.git
cd oscillator

# Установка зависимостей
pip install -r requirements.txt
```

## Быстрый старт

### Быстрая демонстрация

```bash
python run_examples.py --quick
```

### Полная симуляция рождения материи

```python
from oscillators import MatterGenesisSimulation

# Создание симуляции
sim = MatterGenesisSimulation(
    volume_size=10.0,
    initial_inflaton_energy=1e16,
    hubble_parameter=1e-5
)

# Запуск эволюции Вселенной
history = sim.evolve_universe(total_time=1000.0, dt=0.1)

# Визуализация результатов
sim.visualize_genesis(history)
```

### Параметрический резонанс

```python
from oscillators import ParametricResonance

# Создание модели
resonance = ParametricResonance(inflaton_mass=1e13, coupling=1e-7)

# Анализ резонансных полос
results = resonance.simulate_resonance_bands()

# Скорость рождения частиц
rate = resonance.particle_production_rate(phi_amplitude=1e16, k=1.0)
print(f"dn/dt = {rate:.2e}")
```

### Лептогенез

```python
from oscillators import LeptogenesisModel

# Создание модели
model = LeptogenesisModel(M=1e10, Yukawa=1e-6, CP_violation=1e-6)

# Решение уравнений Больцмана
asymmetry = model.solve_leptogenesis()
print(f"Барионная асимметрия: {asymmetry:.2e}")
```

### Квантовое рождение в расширяющейся Вселенной

```python
from oscillators import QuantumCreationInExpandingUniverse

# Создание модели
model = QuantumCreationInExpandingUniverse(mass=0.1, expansion_rate=0.01)

# Анализ рождения частиц
results = model.analyze_particle_creation()
```

### Модель осцилляторов со спином

```python
from oscillators import PrimordialOscillatorUniverse

# Создание вселенной осцилляторов
universe = PrimordialOscillatorUniverse(total_energy=50.0)

# Симуляция нарушения симметрии
history = universe.simulate_symmetry_breaking(steps=500)

# Визуализация
universe.visualize_evolution(history)
```

### Полная детальная модель

```python
from oscillators import DetailedMatterGenesis

# Создание полной модели
model = DetailedMatterGenesis()

# Запуск симуляции всех фаз
results = model.simulate_full_genesis()
```

## Запуск примеров

```bash
# Список всех примеров
python run_examples.py --list

# Запуск конкретного примера
python run_examples.py --example matter_genesis
python run_examples.py --example spin_dynamics
python run_examples.py --example detailed_genesis
python run_examples.py --example parametric_resonance
python run_examples.py --example leptogenesis
python run_examples.py --example quantum_creation

# Запуск всех примеров
python run_examples.py --all

# Информация о библиотеке
python run_examples.py --info
```

## Структура проекта

```
oscillator/
├── oscillators/                # Основная библиотека
│   ├── __init__.py            # Экспорт классов
│   ├── core.py                # Базовые типы данных
│   ├── models.py              # Физические модели
│   ├── simulation.py          # Комплексные симуляции
│   └── examples.py            # Примеры использования
├── run_examples.py            # Главный скрипт запуска
├── requirements.txt           # Зависимости
├── README.md                  # Документация
└── main.py                    # Оригинальный файл (устаревший)
```

## Модули

### core.py — Базовые типы

- `SpinType` — типы спина (скаляр, спинор, вектор, тензор)
- `ParticleType` — типы частиц (кварки, лептоны, фотоны и др.)
- `Particle` — класс частицы с физическими свойствами
- `QuantumOscillator` — квантовый осциллятор с учетом спина
- `PhysicalConstants` — физические константы

### models.py — Физические модели

- `ParametricResonance` — параметрический резонанс (уравнение Матье)
- `LeptogenesisModel` — лептогенез через распад тяжелых нейтрино
- `QuantumCreationInExpandingUniverse` — квантовое рождение (формализм Боголюбова)

### simulation.py — Симуляции

- `MatterGenesisSimulation` — полная симуляция рождения материи
- `PrimordialOscillatorUniverse` — модель вселенной как осцилляторов
- `DetailedMatterGenesis` — интегрированная модель всех процессов

## Физические основы

### Параметрический резонанс

После инфляции поле инфлатона осциллирует около минимума потенциала. Это создает параметрическую неустойчивость, описываемую уравнением Матье:

```
ẍ + (a - 2q cos(2t))x = 0
```

В зонах неустойчивости число частиц растет экспоненциально.

### Лептогенез

Тяжелые нейтрино распадаются с нарушением CP-симметрии:

```
N → l + H   vs   N → l̄ + H̄
```

Эта асимметрия конвертируется в барионную через сфалеронные переходы.

### Квантовое рождение

В расширяющейся Вселенной вакуум не стационарен. Коэффициенты Боголюбова связывают вакуумы в разные моменты времени:

```
n_k = |β_k|²
```

где n_k — число рожденных частиц с импульсом k.

## Результаты симуляций

Библиотека позволяет получить:

- Спектр рожденных частиц по импульсам
- Эволюцию состава Вселенной во времени
- Барионную асимметрию η ≈ 6×10⁻¹⁰
- Современный состав (68% ΛE, 27% DM, 5% барионы)

## Лицензия

MIT License

## Автор

Timur Isanov — xtimon@yahoo.com
