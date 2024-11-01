## Звіт по Вимогам для Програми Генерації Розкладу `schedule_generator.py`

### **1. Список Груп та Підгруп**
**Вимога:** 
- Список груп \( G \), у кожної з яких є \( N \) студентів. 
- Поділ на підгрупи приблизно навпіл, який не змінюється протягом навчання.

**Реалізація:**
- **CSV-Файл `groups.csv`:** Містить інформацію про групи, кількість студентів та підгрупи.
- **Клас `Group`:** Відповідає за зберігання даних про групи та їхні підгрупи.
- **Генерація Підгруп:** Якщо предмет вимагає поділу на підгрупи (`requires_subgroups = 'Yes'`), група ділиться на підгрупи рівною кількістю студентів.

### **2. Перелік Предметів для Кожної Групи**
**Вимога:** 
- Для кожної групи перелік предметів \( P_i \) з визначеною кількістю годин \( T \) для семестру, включаючи лекції та практичні/лабораторні.

**Реалізація:**
- **CSV-Файл `subjects.csv`:** Містить інформацію про предмети, групи, кількість лекцій та практичних, вимогу поділу на підгрупи та тип тижня (`weekType`).
- **Клас `Subject`:** Зберігає деталі кожного предмету.
- **Генерація Занять:** Для кожного предмету створюються відповідні заняття (лекції та практичні) з урахуванням кількості годин.

### **3. Список Лекторів з Обмеженнями**
**Вимога:** 
- Список лекторів \( L \) з інформацією про предмети та типи занять, які вони можуть проводити.

**Реалізація:**
- **CSV-Файл `lecturers.csv`:** Містить інформацію про лекторів, предмети, які вони можуть викладати (`subjectsCanTeach`), типи занять (`typesCanTeach`) та максимальну кількість годин на тиждень.
- **Клас `Lecturer`:** Зберігає дані про лекторів та їхні обмеження.
- **Призначення Викладачів:** При створенні заняття випадковим чином обирається викладач з відповідними дозволеними предметами та типами занять.

### **4. Список Аудиторій з Ємністю**
**Вимога:** 
- Список аудиторій \( A \) з інформацією про їхню місткість \( m \).

**Реалізація:**
- **CSV-Файл `auditoriums.csv`:** Містить інформацію про аудиторії та їхню місткість.
- **Клас `Auditorium`:** Зберігає дані про аудиторії.
- **Призначення Аудиторій:** Для кожного заняття випадковим чином обирається аудиторія, яка відповідає вимогам щодо місткості.

### **5. Обмеження на Кількість Пар**
**Вимога:** 
- Максимум 20 пар на тиждень (4 пари на день).

**Реалізація:**
- **Часові Слоти:** Визначені як 5 днів на тиждень по 4 періоди (пари) на день.
- **Обмеження:** Генетичний алгоритм враховує лише доступні часові слоти, забезпечуючи, що не більше 4 пар призначено на день для кожної групи та викладача.

### **6. Випадкова Генерація Даних**
**Вимога:** 
- Дані повинні бути легко змінювані через файли, без потреби змінювати код.

**Реалізація:**
- **CSV-Файли:** Всі основні дані (групи, предмети, лектори, аудиторії) зберігаються у CSV-файлах, що дозволяє легко змінювати параметри без редагування коду.
- **Генерація Розкладу:** Алгоритм використовує дані з CSV-файлів для створення розкладу, що забезпечує гнучкість та масштабованість.

### **7. Читабельний Вивід Розкладу**
**Вимога:** 
- Читабельний вивід розкладу в консолі.

**Реалізація:**
- **Бібліотека `tabulate`:** Використовується для форматованого виводу розкладу у вигляді таблиць.
- **Функція `print_schedule`:** Відображає розклад окремо для парного та непарного тижня з детальною інформацією про кожне заняття.

### **8. Умови Викладачів та Аудиторій**
**Вимога:** 
- Один лектор може проводити лише одне заняття одночасно.
- Одна аудиторія може використовуватися одночасно лише під одне заняття, з винятком лекцій, де в аудиторії може бути декілька груп.

**Реалізація:**
- **Перевірка Подвійних Бронювань:** У фітнес-функції перевіряється, щоб лектори та аудиторії не бронювались одночасно для декількох занять.
- **Лекції:** Дозволяється декілька груп одночасно в аудиторії лише для лекцій, що враховано в логіці призначення аудиторій.

### **9. Стабільність Підгруп**
**Вимога:** 
- Підгрупи не змінюють склад протягом навчання.

**Реалізація:**
- **Ініціалізація Підгруп:** Підгрупи створюються при завантаженні даних і залишаються сталими протягом усього процесу генерації розкладу.
- **Клас `Group`:** Зберігає інформацію про підгрупи, яка не змінюється після ініціалізації.

### **10. Стабільність Розміру Популяції**
**Вимога:** 
- Генетичний алгоритм забезпечує стабільний розмір популяції.

**Реалізація:**
- **Параметри Алгоритму:** Розмір популяції встановлено на 100, а кількість поколінь на 200.
- **Створення та Оновлення Популяції:** Після кожного покоління створюється нова популяція точно такого ж розміру, забезпечуючи стабільність.

---

