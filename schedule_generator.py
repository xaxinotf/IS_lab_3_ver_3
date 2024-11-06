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
        self.subgroups = subgroups.split(';') if subgroups else []

class Lecturer:
    def __init__(self, lecturer_id, name, subjects_can_teach, types_can_teach, max_hours_per_week):
        self.id = lecturer_id
        self.name = name
        self.subjects_can_teach = [s.strip() for s in subjects_can_teach.split(';')] if subjects_can_teach else []
        self.types_can_teach = [t.strip() for t in types_can_teach.split(';')] if types_can_teach else []
        self.max_hours_per_week = int(max_hours_per_week)
        self.assigned_hours = 0  # Для відстеження навантаження

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
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            print(f"Headers for {filename}: {reader.fieldnames}")  # Доданий рядок
            for row in reader:
                try:
                    auditoriums.append(Auditorium(row['auditoriumID'], row['capacity']))
                except ValueError as ve:
                    print(f"Помилка в рядку {reader.line_num} файлу {filename}: {ve}")
                except KeyError as ke:
                    print(f"Помилка в рядку {reader.line_num} файлу {filename}: Відсутнє поле {ke}")
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено. Переконайтеся, що він знаходиться у правильній директорії.")
    except Exception as e:
        print(f"Помилка при читанні {filename}: {e}")
    return auditoriums

def read_groups(filename):
    groups = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            print(f"Headers for {filename}: {reader.fieldnames}")  # Доданий рядок
            for row in reader:
                try:
                    groups.append(Group(row['groupNumber'], row['studentAmount'], row['subgroups']))
                except ValueError as ve:
                    print(f"Помилка в рядку {reader.line_num} файлу {filename}: {ve}")
                except KeyError as ke:
                    print(f"Помилка в рядку {reader.line_num} файлу {filename}: Відсутнє поле {ke}")
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено. Переконайтеся, що він знаходиться у правильній директорії.")
    except Exception as e:
        print(f"Помилка при читанні {filename}: {e}")
    return groups

def read_lecturers(filename):
    lecturers = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            print(f"Headers for {filename}: {reader.fieldnames}")  # Доданий рядок
            for row in reader:
                try:
                    lecturers.append(Lecturer(
                        row['lecturerID'],
                        row['lecturerName'],
                        row['subjectsCanTeach'],
                        row['typesCanTeach'],
                        row['maxHoursPerWeek']
                    ))
                except ValueError as ve:
                    print(f"Помилка в рядку {reader.line_num} файлу {filename}: {ve}")
                    print(f"Зміст рядка: {row}")
                except KeyError as ke:
                    print(f"Помилка в рядку {reader.line_num} файлу {filename}: Відсутнє поле {ke}")
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено. Переконайтеся, що він знаходиться у правильній директорії.")
    except Exception as e:
        print(f"Помилка при читанні {filename}: {e}")
    return lecturers

def read_subjects(filename):
    subjects = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            print(f"Headers for {filename}: {reader.fieldnames}")  # Доданий рядок
            for row in reader:
                try:
                    subjects.append(Subject(
                        row['id'],
                        row['name'],
                        row['groupID'],
                        row['numLectures'],
                        row['numPracticals'],
                        row['requiresSubgroups'],
                        row['weekType']
                    ))
                except ValueError as ve:
                    print(f"Помилка в рядку {reader.line_num} файлу {filename}: {ve}")
                except KeyError as ke:
                    print(f"Помилка в рядку {reader.line_num} файлу {filename}: Відсутнє поле {ke}")
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено. Переконайтеся, що він знаходиться у правильній директорії.")
    except Exception as e:
        print(f"Помилка при читанні {filename}: {e}")
    return subjects

# Завантаження даних
auditoriums = read_auditoriums('auditoriums.csv')
groups = read_groups('groups.csv')
lecturers = read_lecturers('lecturers.csv')  # Змінено ім'я файлу на 'lecturers.csv'
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
        self.timetable = {time_slot: [] for time_slot in TIME_SLOTS}
        self.fitness = None  # Буде розраховано

    def calculate_fitness(self):
        penalty = 0
        # Мінімізація прогалин у розкладі для груп (м'яке обмеження)
        for group in groups:
            schedule_list = []
            for time_slot, lessons in self.timetable.items():
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
            for time_slot, lessons in self.timetable.items():
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
        for lecturer in lecturers:
            hours_assigned = 0
            for time_slot, lessons in self.timetable.items():
                for lesson in lessons:
                    if lesson.lecturer and lesson.lecturer.id == lecturer.id:
                        hours_assigned += 1
            if hours_assigned > lecturer.max_hours_per_week:
                penalty += (hours_assigned - lecturer.max_hours_per_week) * 2  # Штраф за перевищення

        # Додавання штрафів за недотримання або перевищення кількості годин по предметах (м'яке обмеження)
        for subject in subjects:
            scheduled_lectures = 0
            scheduled_practicals = 0
            for time_slot, lessons in self.timetable.items():
                for lesson in lessons:
                    if lesson.subject.id == subject.id:
                        if lesson.type == 'Лекція':
                            scheduled_lectures += 1
                        elif lesson.type == 'Практика':
                            scheduled_practicals += 1
            # Обчислення різниці між запланованими та необхідними годинами
            diff_lectures = abs(scheduled_lectures - subject.num_lectures)
            diff_practicals = abs(scheduled_practicals - subject.num_practicals)
            # Додавання штрафу за кожну недодану або перевищену годину
            penalty += (diff_lectures + diff_practicals)

        # Захист від ділення на нуль або негативного значення
        if penalty < 0:
            penalty = 0

        self.fitness = 1 / (1 + penalty)

def get_possible_lecturers(lesson):
    # Співставляємо викладачів за subject.id та типом заняття (жорстке обмеження)
    possible = [lecturer for lecturer in lecturers if
               lesson.subject.id in lecturer.subjects_can_teach and
               lesson.type in lecturer.types_can_teach and
               lecturer.assigned_hours < lecturer.max_hours_per_week]
    if not possible:
        print(f"No lecturer available for {lesson.subject.name} ({lesson.type}) with subject ID {lesson.subject.id}")
    return possible

def is_conflict(lesson, time_slot, schedule):
    for existing_lesson in schedule.timetable[time_slot]:
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

# Генетичний алгоритм налаштування
POPULATION_SIZE = 50
GENERATIONS = 100

def create_initial_population():
    population = []
    for i in range(POPULATION_SIZE):
        schedule = Schedule()
        # Для кожного предмета створюємо заняття та призначаємо їх
        for subject in subjects:
            group = next((g for g in groups if g.number == subject.group_id), None)
            if not group:
                print(f"Warning: Group {subject.group_id} not found for subject {subject.name}")
                continue
            # Лекції
            lectures_total = subject.num_lectures  # Загальна кількість лекцій за семестр
            for _ in range(lectures_total):
                lesson = Lesson(subject, 'Лекція', group)
                possible_lecturers = get_possible_lecturers(lesson)
                if not possible_lecturers:
                    print(f"Cannot assign lecture for {subject.name} to group {group.number}: No available lecturers.")
                    continue  # Не може бути призначено
                lecturer = random.choice(possible_lecturers)
                lesson.lecturer = lecturer
                lecturer.assigned_hours += 1  # Збільшуємо навантаження
                # Фільтрація аудиторій за місткістю
                suitable_auditoriums = [aud for aud in auditoriums if aud.capacity >= group.size]
                if not suitable_auditoriums:
                    print(f"No auditorium available for {lesson.subject.name} for group {group.number}")
                    # Відновлення assigned_hours, оскільки аудиторію не призначено
                    lecturer.assigned_hours -= 1
                    continue
                auditorium = random.choice(suitable_auditoriums)
                lesson.auditorium = auditorium
                # Призначення рандомного часового слоту без порушення жорстких обмежень
                assigned = assign_randomly(lesson, schedule)
                if not assigned:
                    # Відновлення assigned_hours, оскільки часового слота не призначено
                    lecturer.assigned_hours -= 1
                    print(f"Failed to assign lecture for {lesson.subject.name} to group {group.number}")
            # Практичні
            pract_total = subject.num_practicals  # Загальна кількість практичних за семестр
            if subject.requires_subgroups and group.subgroups:
                for subgroup in group.subgroups:
                    # Розраховуємо кількість практичних на підгрупу
                    num_practicals_per_subgroup = pract_total // len(group.subgroups)
                    for _ in range(num_practicals_per_subgroup):
                        lesson = Lesson(subject, 'Практика', group, subgroup)
                        possible_lecturers = get_possible_lecturers(lesson)
                        if not possible_lecturers:
                            print(f"Cannot assign practical for {subject.name} to subgroup {subgroup} of group {group.number}: No available lecturers.")
                            continue  # Не може бути призначено
                        lecturer = random.choice(possible_lecturers)
                        lesson.lecturer = lecturer
                        lecturer.assigned_hours += 1  # Збільшуємо навантаження
                        # Розрахунок кількості студентів у підгрупі
                        subgroup_size = group.size // len(group.subgroups)
                        suitable_auditoriums = [aud for aud in auditoriums if aud.capacity >= subgroup_size]
                        if not suitable_auditoriums:
                            print(f"No auditorium available for {lesson.subject.name} for subgroup {subgroup} of group {group.number}")
                            # Відновлення assigned_hours, оскільки аудиторію не призначено
                            lecturer.assigned_hours -= 1
                            continue
                        auditorium = random.choice(suitable_auditoriums)
                        lesson.auditorium = auditorium
                        # Призначення рандомного часового слоту без порушення жорстких обмежень
                        assigned = assign_randomly(lesson, schedule)
                        if not assigned:
                            # Відновлення assigned_hours, оскільки часового слота не призначено
                            lecturer.assigned_hours -= 1
                            print(f"Failed to assign practical for {lesson.subject.name} to subgroup {subgroup} of group {group.number}")
            else:
                for _ in range(pract_total):
                    lesson = Lesson(subject, 'Практика', group)
                    possible_lecturers = get_possible_lecturers(lesson)
                    if not possible_lecturers:
                        print(f"Cannot assign practical for {subject.name} to group {group.number}: No available lecturers.")
                        continue  # Не може бути призначено
                    lecturer = random.choice(possible_lecturers)
                    lesson.lecturer = lecturer
                    lecturer.assigned_hours += 1  # Збільшуємо навантаження
                    # Фільтрація аудиторій за місткістю
                    suitable_auditoriums = [aud for aud in auditoriums if aud.capacity >= group.size]
                    if not suitable_auditoriums:
                        print(f"No auditorium available for {lesson.subject.name} for group {group.number}")
                        # Відновлення assigned_hours, оскільки аудиторію не призначено
                        lecturer.assigned_hours -= 1
                        continue
                    auditorium = random.choice(suitable_auditoriums)
                    lesson.auditorium = auditorium
                    # Призначення рандомного часового слоту без порушення жорстких обмежень
                    assigned = assign_randomly(lesson, schedule)
                    if not assigned:
                        # Відновлення assigned_hours, оскільки часового слота не призначено
                        lecturer.assigned_hours -= 1
                        print(f"Failed to assign practical for {lesson.subject.name} to group {group.number}")
        # Обчислення фітнесу
        schedule.calculate_fitness()
        population.append(schedule)
    return population

def assign_randomly(lesson, schedule):
    available_time_slots = TIME_SLOTS.copy()
    random.shuffle(available_time_slots)
    for time_slot in available_time_slots:
        # Перевірка відповідності тижня
        week_type = lesson.subject.week_type
        if week_type == 'even' and not is_even_week(time_slot):
            continue
        if week_type == 'odd' and not is_odd_week(time_slot):
            continue
        # Якщо week_type 'both', немає обмежень
        # Перевірка наявності конфліктів
        if not is_conflict(lesson, time_slot, schedule):
            lesson.time_slot = time_slot
            schedule.timetable[time_slot].append(lesson)
            return True
    # Якщо не вдалося призначити
    print(f"Unable to assign {lesson.type} for {lesson.subject.name} to group {lesson.group.number}" +
          (f" (Subgroup {lesson.subgroup})" if lesson.subgroup else ""))
    return False

def is_even_week(time_slot):
    # Використовуємо номер тижня року для визначення парності
    # В реальній ситуації потрібно враховувати, коли семестр починається
    # Тут для простоти використовуємо поточний тиждень
    current_date = datetime.datetime.now()
    week_number = current_date.isocalendar()[1]
    return week_number % 2 == 0

def is_odd_week(time_slot):
    week_number = datetime.datetime.now().isocalendar()[1]
    return week_number % 2 != 0

def selection(population):
    # Вибираємо найкращі розклади на основі фітнесу
    population.sort(key=lambda x: x.fitness, reverse=True)
    selected = population[:POPULATION_SIZE // 2]
    return selected

def crossover(parent1, parent2):
    child = Schedule()
    for time_slot in TIME_SLOTS:
        # Вибираємо, чи копіювати заняття з parent1 або parent2
        if random.random() < 0.5:
            for lesson in parent1.timetable[time_slot]:
                if not is_conflict(lesson, time_slot, child):
                    # Глибоке копіювання заняття
                    copied_lesson = copy.deepcopy(lesson)
                    child.timetable[time_slot].append(copied_lesson)
        else:
            for lesson in parent2.timetable[time_slot]:
                if not is_conflict(lesson, time_slot, child):
                    copied_lesson = copy.deepcopy(lesson)
                    child.timetable[time_slot].append(copied_lesson)
    # Розрахунок фітнесу після кросоверу
    child.calculate_fitness()
    return child

def mutate(schedule):
    # Випадкова зміна декількох занять у розкладі
    for _ in range(5):  # Кількість мутацій
        time_slot = random.choice(TIME_SLOTS)
        if schedule.timetable[time_slot]:
            lesson = random.choice(schedule.timetable[time_slot])
            original_time_slot = lesson.time_slot
            new_time_slot = random.choice(TIME_SLOTS)
            if new_time_slot == original_time_slot:
                continue
            # Перевірка відповідності тижня
            week_type = lesson.subject.week_type
            if week_type == 'even' and not is_even_week(new_time_slot):
                continue
            if week_type == 'odd' and not is_odd_week(new_time_slot):
                continue
            # Перевірка, чи можна призначити новий часовий слот без конфліктів
            if not is_conflict(lesson, new_time_slot, schedule):
                # Переміщуємо заняття до нового часового слота
                schedule.timetable[original_time_slot].remove(lesson)
                lesson.time_slot = new_time_slot
                schedule.timetable[new_time_slot].append(lesson)
    # Розрахунок фітнесу після мутації
    schedule.calculate_fitness()

def genetic_algorithm():
    population = create_initial_population()
    for generation in range(GENERATIONS):
        selected = selection(population)
        new_population = []
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

    for time_slot in TIME_SLOTS:
        lessons = schedule.timetable[time_slot]
        for lesson in lessons:
            # Визначення типу тижня
            if lesson.subject.week_type == 'even':
                weeks = ['EVEN']
            elif lesson.subject.week_type == 'odd':
                weeks = ['ODD']
            else:
                weeks = ['EVEN', 'ODD']

            # Рядок часового слоту
            timeslot_str = f"{time_slot[0]}, period {time_slot[1]}"

            # Група з підгрупою, якщо є
            group_str = lesson.group.number
            if lesson.subgroup:
                group_str += f" (Subgroup {lesson.subgroup})"

            # Предмет
            subject_str = lesson.subject.name

            # Тип
            type_str = lesson.type

            # Викладач
            lecturer_str = lesson.lecturer.name if lesson.lecturer else "N/A"

            # Аудиторія
            auditorium_str = lesson.auditorium.id if lesson.auditorium else "N/A"

            # Кількість студентів
            if lesson.subgroup and lesson.group.subgroups:
                students = lesson.group.size // len(lesson.group.subgroups)
            else:
                students = lesson.group.size
            students_str = str(students)

            # Місткість аудиторії
            capacity_str = str(lesson.auditorium.capacity) if lesson.auditorium else "N/A"

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
