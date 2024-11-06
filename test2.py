import csv
import random
import copy
from tabulate import tabulate
import datetime

# Структури даних
class Auditorium:
    def __init__(self, auditorium_id, capacity):
        self.id = auditorium_id
        self.capacity = int(capacity)

class Group:
    def __init__(self, group_number, student_amount, subgroups):
        self.number = group_number
        self.size = int(student_amount)
        self.subgroups = subgroups.strip('"').split(';') if subgroups else []

class Lecturer:
    def __init__(self, lecturer_id, name, subjects_can_teach, types_can_teach, max_hours_per_week):
        self.id = lecturer_id
        self.name = name
        self.subjects_can_teach = [s.strip() for s in subjects_can_teach.split(';')] if subjects_can_teach else []
        self.types_can_teach = [t.strip() for t in types_can_teach.split(';')] if types_can_teach else []
        self.max_hours_per_week = int(max_hours_per_week)
        self.assigned_hours_even = 0  # Навантаження на парний тиждень
        self.assigned_hours_odd = 0   # Навантаження на непарний тиждень

class Subject:
    def __init__(self, subject_id, name, group_id, num_lectures, num_practicals, requires_subgroups, week_type):
        self.id = subject_id
        self.name = name
        self.group_id = group_id
        self.num_lectures = int(num_lectures)
        self.num_practicals = int(num_practicals)
        self.requires_subgroups = True if requires_subgroups.lower() == 'yes' else False
        self.week_type = week_type.lower()  # 'both', 'even', 'odd'

# Функції для читання CSV-файлів
def read_auditoriums(filename):
    auditoriums = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            auditoriums.append(Auditorium(row['auditoriumID'], row['capacity']))
    return auditoriums

def read_groups(filename):
    groups = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            groups.append(Group(row['groupNumber'], row['studentAmount'], row['subgroups']))
    return groups

def read_lecturers(filename):
    lecturers = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            lecturers.append(Lecturer(
                row['lecturerID'],
                row['lecturerName'],
                row['subjectsCanTeach'],
                row['typesCanTeach'],
                row['maxHoursPerWeek']
            ))
    return lecturers

def read_subjects(filename):
    subjects = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            subjects.append(Subject(
                row['id'],
                row['name'],
                row['groupID'],
                row['numLectures'],
                row['numPracticals'],
                row['requiresSubgroups'],
                row['weekType']
            ))
    return subjects

# Завантаження даних
auditoriums = read_auditoriums('auditoriums.csv')
groups = read_groups('groups.csv')
lecturers = read_lecturers('lecturers.csv')
subjects = read_subjects('subjects.csv')

# Перевірка відповідності groupID у subjects.csv з groups.csv
valid_group_ids = set(group.number for group in groups)
filtered_subjects = []
for subject in subjects:
    if subject.group_id in valid_group_ids:
        filtered_subjects.append(subject)
    else:
        print(f"Warning: Group {subject.group_id} not found for subject {subject.name}")
subjects = filtered_subjects

# Перевірка, що кожен subject має принаймні одного викладача
subject_ids = set(subject.id for subject in subjects)
lecturer_subjects = set()
for lecturer in lecturers:
    lecturer_subjects.update(lecturer.subjects_can_teach)

missing_subjects = subject_ids - lecturer_subjects
if missing_subjects:
    print(f"Warning: Для наступних предметів немає викладачів: {', '.join(missing_subjects)}")

# Визначення часів: 5 днів, 4 періоди на день
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
PERIODS = ['1', '2', '3', '4']  # Періоди у день
TIME_SLOTS = [(day, period) for day in DAYS for period in PERIODS]

class Lesson:
    def __init__(self, subject, lesson_type, group, subgroup=None):
        self.subject = subject
        self.type = lesson_type  # 'Лекція' або 'Практика'
        self.group = group
        self.subgroup = subgroup  # Для практичних, якщо потрібні підгрупи
        self.time_slot = None
        self.auditorium = None
        self.lecturer = None

class Schedule:
    def __init__(self):
        # Ключ: time_slot (day, period), Значення: список занять у цей час
        self.even_timetable = {time_slot: [] for time_slot in TIME_SLOTS}
        self.odd_timetable = {time_slot: [] for time_slot in TIME_SLOTS}
        self.fitness = None  # Буде розраховано

    def calculate_fitness(self):
        penalty = 0
        # Фітнес для парного тижня
        penalty += self._calculate_fitness_for_week(self.even_timetable)
        # Фітнес для непарного тижня
        penalty += self._calculate_fitness_for_week(self.odd_timetable)
        # Врахування м'яких обмежень по предметах
        penalty += self._calculate_soft_constraints()
        # Захист від ділення на нуль або негативного значення
        if penalty < 0:
            penalty = 0
        self.fitness = 1 / (1 + penalty)

    def _calculate_fitness_for_week(self, timetable):
        penalty = 0
        # Мінімізація прогалин у розкладі для груп (м'яке обмеження)
        for group in groups:
            schedule_list = []
            for time_slot, lessons in timetable.items():
                for lesson in lessons:
                    if lesson.group.number == group.number:
                        schedule_list.append(time_slot)
            schedule_sorted = sorted(schedule_list, key=lambda x: (DAYS.index(x[0]), int(x[1])))
            for i in range(len(schedule_sorted) - 1):
                day1, period1 = schedule_sorted[i]
                day2, period2 = schedule_sorted[i + 1]
                if day1 == day2:
                    gaps = int(period2) - int(period1) - 1
                    if gaps > 0:
                        penalty += gaps
        # Мінімізація прогалин у розкладі для викладачів (м'яке обмеження)
        for lecturer in lecturers:
            schedule_list = []
            for time_slot, lessons in timetable.items():
                for lesson in lessons:
                    if lesson.lecturer and lesson.lecturer.id == lecturer.id:
                        schedule_list.append(time_slot)
            schedule_sorted = sorted(schedule_list, key=lambda x: (DAYS.index(x[0]), int(x[1])))
            for i in range(len(schedule_sorted) - 1):
                day1, period1 = schedule_sorted[i]
                day2, period2 = schedule_sorted[i + 1]
                if day1 == day2:
                    gaps = int(period2) - int(period1) - 1
                    if gaps > 0:
                        penalty += gaps
            # Балансування навантаження на викладачів (м'яке обмеження)
            hours_assigned = len(schedule_list)
            max_hours = lecturer.max_hours_per_week
            if hours_assigned > max_hours:
                penalty += (hours_assigned - max_hours) * 2  # Штраф за перевищення
        return penalty

    def _calculate_soft_constraints(self):
        penalty = 0
        # Додавання штрафів за недотримання або перевищення кількості годин по предметах (м'яке обмеження)
        for subject in subjects:
            scheduled_lectures = 0
            scheduled_practicals = 0
            for timetable in [self.even_timetable, self.odd_timetable]:
                for time_slot, lessons in timetable.items():
                    for lesson in lessons:
                        if lesson.subject.id == subject.id:
                            if lesson.type == 'Лекція':
                                scheduled_lectures += 1
                            elif lesson.type == 'Практика':
                                scheduled_practicals += 1
            # Обчислення різниці між запланованими та необхідними годинами
            diff_lectures = scheduled_lectures - subject.num_lectures
            diff_practicals = scheduled_practicals - subject.num_practicals
            # Додавання штрафу за кожну недодану або перевищену годину (пропорційно різниці)
            penalty += abs(diff_lectures) * 2  # Штраф помножений на 2 для більшої ваги
            penalty += abs(diff_practicals) * 2
        return penalty

def is_conflict(lesson, time_slot, timetable):
    for existing_lesson in timetable[time_slot]:
        # Перевірка викладача (жорстке обмеження)
        if lesson.lecturer and existing_lesson.lecturer and existing_lesson.lecturer.id == lesson.lecturer.id:
            return True
        # Перевірка групи (жорстке обмеження)
        if existing_lesson.group.number == lesson.group.number:
            # Якщо підгрупи, перевіряємо підгрупу
            if lesson.subgroup and existing_lesson.subgroup:
                if existing_lesson.subgroup == lesson.subgroup:
                    return True
            else:
                return True
        # Перевірка аудиторії (жорстке обмеження)
        if lesson.auditorium and existing_lesson.auditorium and existing_lesson.auditorium.id == lesson.auditorium.id:
            # Виняток для лекцій з одним викладачем
            if not (
                lesson.type == 'Лекція' and
                existing_lesson.type == 'Лекція' and
                lesson.lecturer and existing_lesson.lecturer and
                lesson.lecturer.id == existing_lesson.lecturer.id
            ):
                return True
    return False

def get_possible_lecturers(lesson):
    # Співставляємо викладачів за subject.id та типом заняття (жорстке обмеження)
    possible = [lecturer for lecturer in lecturers if
                lesson.subject.id in lecturer.subjects_can_teach and
                lesson.type in lecturer.types_can_teach]
    if not possible:
        print(f"No lecturer available for {lesson.subject.name} ({lesson.type}) with subject ID {lesson.subject.id}.")
    return possible

# Генетичний алгоритм налаштування
POPULATION_SIZE = 50
GENERATIONS = 100

def assign_randomly(lesson, schedule):
    timetables = [schedule.even_timetable, schedule.odd_timetable]
    assigned = False
    for timetable in timetables:
        available_time_slots = TIME_SLOTS.copy()
        random.shuffle(available_time_slots)
        for time_slot in available_time_slots:
            if not is_conflict(lesson, time_slot, timetable):
                lesson.time_slot = time_slot
                timetable[time_slot].append(copy.deepcopy(lesson))
                assigned = True
                break
        if not assigned:
            return False
    return True

def create_initial_population():
    population = []
    for _ in range(POPULATION_SIZE):
        schedule = Schedule()
        # Для кожного предмета створюємо заняття та призначаємо їх
        for subject in subjects:
            group = next((g for g in groups if g.number == subject.group_id), None)
            if not group:
                print(f"Warning: Group {subject.group_id} not found for subject {subject.name}")
                continue
            # Лекції
            lectures_total = subject.num_lectures
            for _ in range(lectures_total):
                lesson = Lesson(subject, 'Лекція', group)
                possible_lecturers = get_possible_lecturers(lesson)
                if not possible_lecturers:
                    continue
                lecturer = random.choice(possible_lecturers)
                lesson.lecturer = lecturer
                # Фільтрація аудиторій за місткістю
                suitable_auditoriums = [aud for aud in auditoriums if aud.capacity >= group.size]
                if not suitable_auditoriums:
                    print(f"No auditorium available for {lesson.subject.name} for group {group.number}")
                    continue
                auditorium = random.choice(suitable_auditoriums)
                lesson.auditorium = auditorium
                # Призначення рандомного часового слоту без порушення жорстких обмежень
                assigned = assign_randomly(lesson, schedule)
                if not assigned:
                    print(f"Failed to assign lecture for {lesson.subject.name} to group {group.number}.")
            # Практичні
            pract_total = subject.num_practicals
            if subject.requires_subgroups and group.subgroups:
                for subgroup in group.subgroups:
                    # Розрахунок кількості практичних на підгрупу
                    num_practicals_per_subgroup = pract_total // len(group.subgroups)
                    for _ in range(num_practicals_per_subgroup):
                        lesson = Lesson(subject, 'Практика', group, subgroup)
                        possible_lecturers = get_possible_lecturers(lesson)
                        if not possible_lecturers:
                            continue
                        lecturer = random.choice(possible_lecturers)
                        lesson.lecturer = lecturer
                        # Розрахунок кількості студентів у підгрупі
                        subgroup_size = group.size // len(group.subgroups)
                        suitable_auditoriums = [aud for aud in auditoriums if aud.capacity >= subgroup_size]
                        if not suitable_auditoriums:
                            print(f"No auditorium available for {lesson.subject.name} for subgroup {subgroup} of group {group.number}")
                            continue
                        auditorium = random.choice(suitable_auditoriums)
                        lesson.auditorium = auditorium
                        # Призначення рандомного часового слоту без порушення жорстких обмежень
                        assigned = assign_randomly(lesson, schedule)
                        if not assigned:
                            print(f"Failed to assign practical for {lesson.subject.name} to subgroup {subgroup} of group {group.number}.")
            else:
                for _ in range(pract_total):
                    lesson = Lesson(subject, 'Практика', group)
                    possible_lecturers = get_possible_lecturers(lesson)
                    if not possible_lecturers:
                        continue
                    lecturer = random.choice(possible_lecturers)
                    lesson.lecturer = lecturer
                    suitable_auditoriums = [aud for aud in auditoriums if aud.capacity >= group.size]
                    if not suitable_auditoriums:
                        print(f"No auditorium available for {lesson.subject.name} for group {group.number}")
                        continue
                    auditorium = random.choice(suitable_auditoriums)
                    lesson.auditorium = auditorium
                    assigned = assign_randomly(lesson, schedule)
                    if not assigned:
                        print(f"Failed to assign practical for {lesson.subject.name} to group {group.number}.")
        # Обчислення фітнесу
        schedule.calculate_fitness()
        population.append(schedule)
    return population

def selection(population):
    # Вибираємо найкращі розклади на основі фітнесу (елітізм)
    population.sort(key=lambda x: x.fitness, reverse=True)
    selected = population[:int(0.2 * len(population))]  # Вибір топ 20%
    return selected

def crossover(parent1, parent2):
    child = Schedule()
    for time_slot in TIME_SLOTS:
        # Вибираємо, чи копіювати заняття з parent1 або parent2
        if random.random() < 0.5:
            source_lessons_even = parent1.even_timetable[time_slot]
            source_lessons_odd = parent1.odd_timetable[time_slot]
        else:
            source_lessons_even = parent2.even_timetable[time_slot]
            source_lessons_odd = parent2.odd_timetable[time_slot]
        # Копіюємо заняття для парного тижня
        for lesson in source_lessons_even:
            if not is_conflict(lesson, time_slot, child.even_timetable):
                child.even_timetable[time_slot].append(copy.deepcopy(lesson))
        # Копіюємо заняття для непарного тижня
        for lesson in source_lessons_odd:
            if not is_conflict(lesson, time_slot, child.odd_timetable):
                child.odd_timetable[time_slot].append(copy.deepcopy(lesson))
    # Розрахунок фітнесу після кросоверу
    child.calculate_fitness()
    return child

def mutate(schedule):
    # Випадкова зміна декількох занять у розкладі
    mutation_rate = 0.1  # Ймовірність мутації 10%
    for timetable in [schedule.even_timetable, schedule.odd_timetable]:
        for time_slot in TIME_SLOTS:
            if timetable[time_slot]:
                for lesson in timetable[time_slot][:]:
                    if random.random() < mutation_rate:
                        original_time_slot = lesson.time_slot
                        new_time_slot = random.choice(TIME_SLOTS)
                        if new_time_slot == original_time_slot:
                            continue
                        if not is_conflict(lesson, new_time_slot, timetable):
                            timetable[original_time_slot].remove(lesson)
                            lesson.time_slot = new_time_slot
                            timetable[new_time_slot].append(lesson)
    # Розрахунок фітнесу після мутації
    schedule.calculate_fitness()

def genetic_algorithm():
    population = create_initial_population()
    for generation in range(GENERATIONS):
        selected = selection(population)
        new_population = []
        # Елітізм: зберігаємо топ 10% найкращих індивідів без змін
        elite_size = int(0.1 * POPULATION_SIZE)
        elites = selected[:elite_size]
        new_population.extend(copy.deepcopy(elites))
        # Випадковий кросовер та мутація для решти
        while len(new_population) < POPULATION_SIZE:
            parent1, parent2 = random.sample(selected, 2)
            child = crossover(parent1, parent2)
            mutate(child)
            new_population.append(child)
        population = new_population
        best_fitness = max(schedule.fitness for schedule in population)
        if (generation + 1) % 10 == 0 or best_fitness == 1.0:
            print(f'Generation {generation + 1}: Best Fitness = {best_fitness}\n')
        if best_fitness == 1.0:
            print(f'Optimal schedule found at generation {generation + 1}.')
            break
    best_schedule = max(population, key=lambda x: x.fitness)
    return best_schedule

def print_schedule(schedule):
    even_week_table = []
    odd_week_table = []
    headers = [
        'Timeslot',
        'Group(s)',
        'Subject',
        'Type',
        'Lecturer',
        'Auditorium',
        'Students',
        'Capacity'
    ]

    def create_row(time_slot, lesson):
        timeslot_str = f"{time_slot[0]}, period {time_slot[1]}"
        group_str = lesson.group.number
        if lesson.subgroup:
            group_str += f" (Subgroup {lesson.subgroup})"
        subject_str = lesson.subject.name
        type_str = lesson.type
        lecturer_str = lesson.lecturer.name if lesson.lecturer else "N/A"
        auditorium_str = lesson.auditorium.id if lesson.auditorium else "N/A"
        if lesson.subgroup and lesson.group.subgroups:
            students = lesson.group.size // len(lesson.group.subgroups)
        else:
            students = lesson.group.size
        students_str = str(students)
        capacity_str = str(lesson.auditorium.capacity) if lesson.auditorium else "N/A"
        row = [
            timeslot_str,
            group_str,
            subject_str,
            type_str,
            lecturer_str,
            auditorium_str,
            students_str,
            capacity_str
        ]
        return row

    for time_slot in TIME_SLOTS:
        lessons_even = schedule.even_timetable[time_slot]
        for lesson in lessons_even:
            row = create_row(time_slot, lesson)
            even_week_table.append(row)
        lessons_odd = schedule.odd_timetable[time_slot]
        for lesson in lessons_odd:
            row = create_row(time_slot, lesson)
            odd_week_table.append(row)

    print("\nBest schedule - EVEN week:\n")
    if even_week_table:
        print(tabulate(even_week_table, headers=headers, tablefmt="grid", stralign="center"))
    else:
        print("No lessons scheduled for EVEN week.\n")

    print("\nBest schedule - ODD week:\n")
    if odd_week_table:
        print(tabulate(odd_week_table, headers=headers, tablefmt="grid", stralign="center"))
    else:
        print("No lessons scheduled for ODD week.\n")

if __name__ == "__main__":
    # Запуск генетичного алгоритму та отримання найкращого розкладу
    best_schedule = genetic_algorithm()
    # Вивід фінального розкладу у консоль
    print_schedule(best_schedule)
