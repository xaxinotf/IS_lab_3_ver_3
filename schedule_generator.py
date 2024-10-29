import csv
import random
import copy
from tabulate import tabulate


# Структури даних
class Auditorium:
    def __init__(self, auditorium_id, capacity):
        self.id = auditorium_id
        self.capacity = int(capacity)


class Group:
    def __init__(self, group_number, student_amount, subgroups):
        self.number = group_number
        self.size = int(student_amount)
        self.subgroups = subgroups.split(';') if subgroups else []  # Список підгруп


class Lecturer:
    def __init__(self, lecturer_id, name, subjects_can_teach, types_can_teach, max_hours_per_week):
        self.id = lecturer_id
        self.name = name
        self.subjects_can_teach = subjects_can_teach.split(';') if subjects_can_teach else []
        self.types_can_teach = types_can_teach.split(';') if types_can_teach else []
        self.max_hours_per_week = int(max_hours_per_week)


class Subject:
    def __init__(self, subject_id, name, group_id, num_lectures, num_practicals, requires_subgroups, week_type):
        self.id = subject_id
        self.name = name
        self.group_id = group_id
        self.num_lectures = int(num_lectures)
        self.num_practicals = int(num_practicals)
        self.requires_subgroups = True if requires_subgroups.lower() == 'yes' else False
        self.week_type = week_type  # 'EVEN', 'ODD', або 'Both'


# Функції для читання CSV-файлів
def read_auditoriums(filename):
    auditoriums = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                auditoriums.append(Auditorium(row['auditoriumID'], row['capacity']))
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено. Переконайтеся, що він знаходиться у правильній директорії.")
    except Exception as e:
        print(f"Помилка при читанні {filename}: {e}")
    return auditoriums


def read_groups(filename):
    groups = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                groups.append(Group(row['groupNumber'], row['studentAmount'], row['subgroups']))
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено. Переконайтеся, що він знаходиться у правильній директорії.")
    except Exception as e:
        print(f"Помилка при читанні {filename}: {e}")
    return groups


def read_lecturers(filename):
    lecturers = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                lecturers.append(Lecturer(
                    row['lecturerID'],
                    row['lecturerName'],
                    row['subjectsCanTeach'],
                    row['typesCanTeach'],
                    row['maxHoursPerWeek']
                ))
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено. Переконайтеся, що він знаходиться у правильній директорії.")
    except Exception as e:
        print(f"Помилка при читанні {filename}: {e}")
    return lecturers


def read_subjects(filename):
    subjects = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
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
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено. Переконайтеся, що він знаходиться у правильній директорії.")
    except Exception as e:
        print(f"Помилка при читанні {filename}: {e}")
    return subjects


# Завантаження даних
auditoriums = read_auditoriums('auditoriums.csv')
groups = read_groups('groups.csv')
lecturers = read_lecturers('lecturers.csv')
subjects = read_subjects('subjects.csv')

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
        self.assigned = False
        # Призначається під час розкладу
        self.time_slot = None
        self.auditorium = None
        self.lecturer = None


class Schedule:
    def __init__(self):
        # Ключ: time_slot (day, period), Значення: список занять у цей час
        self.timetable = {time_slot: [] for time_slot in TIME_SLOTS}
        self.fitness = None  # Буде розраховано

    def calculate_fitness(self):
        penalty = 0
        lecturer_hours = {lecturer.id: 0 for lecturer in lecturers}
        group_schedule = {}
        for group in groups:
            group_schedule[group.number] = []
            for subgroup in group.subgroups:
                group_schedule[f"{group.number} (Subgroup {subgroup})"] = []

        lecturer_schedule = {lecturer.id: [] for lecturer in lecturers}

        for time_slot, lessons in self.timetable.items():
            used_auditoriums = []
            used_lecturers = []
            used_groups = []

            for lesson in lessons:
                # Перевірка місткості аудиторії
                if lesson.group.size > lesson.auditorium.capacity:
                    penalty += 10  # Аудиторія занадто мала
                    print(f"Penalty: Auditorium {lesson.auditorium.id} too small for Group {lesson.group.number}")

                # Перевірка подвійного бронювання аудиторії
                if lesson.auditorium.id in used_auditoriums:
                    penalty += 10  # Подвійне бронювання аудиторії
                    print(f"Penalty: Auditorium {lesson.auditorium.id} double booked at {time_slot}")
                else:
                    used_auditoriums.append(lesson.auditorium.id)

                # Перевірка кваліфікації викладача
                if lesson.subject.id not in lesson.lecturer.subjects_can_teach or lesson.type not in lesson.lecturer.types_can_teach:
                    penalty += 10  # Викладач не кваліфікований
                    print(
                        f"Penalty: Lecturer {lesson.lecturer.name} not qualified for {lesson.subject.name} ({lesson.type})")

                # Перевірка доступності викладача
                if lesson.lecturer.id in used_lecturers:
                    penalty += 10  # Подвійне бронювання викладача
                    print(f"Penalty: Lecturer {lesson.lecturer.name} double booked at {time_slot}")
                else:
                    used_lecturers.append(lesson.lecturer.id)
                    lecturer_schedule[lesson.lecturer.id].append(time_slot)
                    lecturer_hours[lesson.lecturer.id] += 1  # Припускаємо 1 година на заняття

                # Перевірка доступності групи
                group_identifier = lesson.group.number
                if lesson.subgroup:
                    group_identifier += f" (Subgroup {lesson.subgroup})"
                if group_identifier in used_groups:
                    penalty += 10  # Подвійне бронювання групи
                    print(f"Penalty: Group {group_identifier} double booked at {time_slot}")
                else:
                    used_groups.append(group_identifier)
                    if group_identifier in group_schedule:
                        group_schedule[group_identifier].append(time_slot)
                    else:
                        # Якщо група не була додана, додаємо її
                        group_schedule[group_identifier] = [time_slot]
                        penalty += 10  # Можливо, сталася помилка в групах
                        print(f"Warning: Group {group_identifier} not initialized in group_schedule.")

        # Перевірка максимальної кількості годин викладачів
        for lecturer in lecturers:
            if lecturer_hours[lecturer.id] > lecturer.max_hours_per_week:
                penalty += 5 * (lecturer_hours[lecturer.id] - lecturer.max_hours_per_week)
                print(
                    f"Penalty: Lecturer {lecturer.name} exceeds max hours by {lecturer_hours[lecturer.id] - lecturer.max_hours_per_week}")

        # Мінімізація пробілів у розкладі (м'яка умова)
        for group_id, schedule_list in group_schedule.items():
            schedule_sorted = sorted(schedule_list, key=lambda x: (DAYS.index(x[0]), int(x[1])))
            for i in range(len(schedule_sorted) - 1):
                day1, period1 = schedule_sorted[i]
                day2, period2 = schedule_sorted[i + 1]
                if day1 == day2:
                    gaps = int(period2) - int(period1) - 1
                    if gaps > 0:
                        penalty += gaps
                        print(
                            f"Penalty: Gaps in group {group_id} schedule on {day1} between periods {period1} and {period2}")

        for lecturer_id, schedule_list in lecturer_schedule.items():
            schedule_sorted = sorted(schedule_list, key=lambda x: (DAYS.index(x[0]), int(x[1])))
            for i in range(len(schedule_sorted) - 1):
                day1, period1 = schedule_sorted[i]
                day2, period2 = schedule_sorted[i + 1]
                if day1 == day2:
                    gaps = int(period2) - int(period1) - 1
                    if gaps > 0:
                        penalty += gaps
                        lecturer_name = next((lec.name for lec in lecturers if lec.id == lecturer_id), "Unknown")
                        print(
                            f"Penalty: Gaps in lecturer {lecturer_name} schedule on {day1} between periods {period1} and {period2}")

        # Розрахунок фітнесу
        self.fitness = 1 / (1 + penalty)
        # print(f"Fitness calculated: {self.fitness} with penalty {penalty}\n")


POPULATION_SIZE = 50
GENERATIONS = 100


def create_initial_population():
    population = []
    for i in range(POPULATION_SIZE):
        schedule = Schedule()
        # Для кожного предмета створюємо заняття та призначаємо їх випадково
        for subject in subjects:
            group = next((g for g in groups if g.number == subject.group_id), None)
            if not group:
                print(f"Warning: Group {subject.group_id} not found for subject {subject.name}")
                continue
            # Лекції
            lectures_total = subject.num_lectures  # Загальна кількість лекцій за семестр
            for _ in range(lectures_total):
                lesson = Lesson(subject, 'Лекція', group)
                assign_randomly(lesson, schedule)
            # Практичні
            pract_total = subject.num_practicals  # Загальна кількість практичних за семестр
            if subject.requires_subgroups and group.subgroups:
                for subgroup in group.subgroups:
                    for _ in range(pract_total // len(group.subgroups)):
                        lesson = Lesson(subject, 'Практика', group, subgroup)
                        assign_randomly(lesson, schedule)
            else:
                for _ in range(pract_total):
                    lesson = Lesson(subject, 'Практика', group)
                    assign_randomly(lesson, schedule)
        population.append(schedule)
        # print(f"Created schedule {i+1}/{POPULATION_SIZE}")
    return population


def assign_randomly(lesson, schedule):
    # Випадкове призначення часового слоту, аудиторії та викладача
    time_slot = random.choice(TIME_SLOTS)
    auditorium = random.choice(auditoriums)
    possible_lecturers = [lecturer for lecturer in lecturers if
                          lesson.subject.id in lecturer.subjects_can_teach and lesson.type in lecturer.types_can_teach]

    if not possible_lecturers:
        print(
            f"Warning: No suitable lecturer found for {lesson.subject.name} ({lesson.type}) for Group {lesson.group.number}" + (
                f" (Subgroup {lesson.subgroup})" if lesson.subgroup else ""))
        return

    lecturer = random.choice(possible_lecturers)

    # Призначаємо заняття
    lesson.time_slot = time_slot
    lesson.auditorium = auditorium
    lesson.lecturer = lecturer
    schedule.timetable[time_slot].append(lesson)


def selection(population):
    # Вибір розкладів на основі фітнесу
    population.sort(key=lambda x: x.fitness, reverse=True)
    selected = population[:POPULATION_SIZE // 2]  # Вибір верхньої половини
    return selected


def crossover(parent1, parent2):
    # Одноточковий кросовер
    child = Schedule()
    crossover_point = len(TIME_SLOTS) // 2
    for idx, time_slot in enumerate(TIME_SLOTS):
        if idx < crossover_point:
            # Створюємо поверхневу копію занять з parent1
            child.timetable[time_slot] = copy.deepcopy(parent1.timetable[time_slot])
        else:
            # Створюємо поверхневу копію занять з parent2
            child.timetable[time_slot] = copy.deepcopy(parent2.timetable[time_slot])
    return child


def mutate(schedule):
    # Випадкова мутація деяких занять
    for _ in range(10):  # Мутуємо 10 занять
        time_slot = random.choice(TIME_SLOTS)
        if schedule.timetable[time_slot]:
            lesson = random.choice(schedule.timetable[time_slot])
            # Випадкове змінення часового слоту, аудиторії або викладача
            action = random.choice(['time_slot', 'auditorium', 'lecturer'])
            if action == 'time_slot':
                new_time_slot = random.choice(TIME_SLOTS)
                schedule.timetable[time_slot].remove(lesson)
                lesson.time_slot = new_time_slot
                schedule.timetable[new_time_slot].append(lesson)
            elif action == 'auditorium':
                new_auditorium = random.choice(auditoriums)
                lesson.auditorium = new_auditorium
            elif action == 'lecturer':
                possible_lecturers = [lecturer for lecturer in lecturers if
                                      lesson.subject.id in lecturer.subjects_can_teach and lesson.type in lecturer.types_can_teach]
                if possible_lecturers:
                    new_lecturer = random.choice(possible_lecturers)
                    lesson.lecturer = new_lecturer


def genetic_algorithm():
    population = create_initial_population()
    # Розрахунок фітнесу для початкової популяції
    for schedule in population:
        schedule.calculate_fitness()
    for generation in range(GENERATIONS):
        selected = selection(population)
        new_population = []
        while len(new_population) < POPULATION_SIZE:
            parent1, parent2 = random.sample(selected, 2)
            child = crossover(parent1, parent2)
            mutate(child)
            child.calculate_fitness()
            new_population.append(child)
        population = new_population
        best_fitness = max(schedule.fitness for schedule in population)
        # Вивід фітнесу лише для кожного 10-го покоління або коли фітнес = 1.0
        if (generation + 1) % 10 == 0 or best_fitness == 1.0:
            print(f'Generation {generation + 1}: Best Fitness = {best_fitness}\n')
        if best_fitness == 1.0:
            break
    # Повернення найкращого розкладу
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

    for time_slot in TIME_SLOTS:
        lessons = schedule.timetable[time_slot]
        for lesson in lessons:
            # Визначення типу тижня
            if lesson.subject.week_type.lower() == 'even':
                weeks = ['EVEN']
            elif lesson.subject.week_type.lower() == 'odd':
                weeks = ['ODD']
            else:
                weeks = ['EVEN', 'ODD']

            # Рядок часового слоту
            timeslot_str = f"day {DAYS.index(time_slot[0]) + 1}, lesson {PERIODS.index(time_slot[1]) + 1}"

            # Група з підгрупою, якщо є
            group_str = lesson.group.number
            if lesson.subgroup:
                group_str += f" (Subgroup {lesson.subgroup})"

            # Предмет
            subject_str = lesson.subject.name

            # Тип
            type_str = lesson.type

            # Викладач
            lecturer_str = lesson.lecturer.name

            # Аудиторія
            auditorium_str = lesson.auditorium.id

            # Кількість студентів
            if lesson.subgroup and lesson.group.subgroups:
                students = lesson.group.size // len(lesson.group.subgroups)
            else:
                students = lesson.group.size
            students_str = str(students)

            # Місткість аудиторії
            capacity_str = str(lesson.auditorium.capacity)

            # Додавання рядка до відповідного тижня
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

            for week in weeks:
                if week == 'EVEN':
                    even_week_table.append(row)
                elif week == 'ODD':
                    odd_week_table.append(row)

    # Відображення таблиці для Парного Тижня
    print("\nBest schedule - EVEN week:\n")
    if even_week_table:
        print(tabulate(even_week_table, headers=headers, tablefmt="grid", stralign="center"))
    else:
        print("No lessons scheduled for EVEN week.\n")

    # Відображення таблиці для Непарного Тижня
    print("\nBest schedule - ODD week:\n")
    if odd_week_table:
        print(tabulate(odd_week_table, headers=headers, tablefmt="grid", stralign="center"))
    else:
        print("No lessons scheduled for ODD week.\n")


# Запуск генетичного алгоритму та отримання найкращого розкладу
best_schedule = genetic_algorithm()

# Вивід фінального розкладу у консоль
print_schedule(best_schedule)
