from datetime import datetime

from django.db import models, connections
from django.db.models import Q

from worktime.settings import BASE_DIR
import os
import json
import codecs


# =========== Функцхї ===============
def get_list_field_title(self, fnames, name_field_id=""):
    """   отримання списку  назв полів укр  """
    listf = []
    for f in fnames:
        for field in self._meta.get_fields():
            if field.name == f:
                if name_field_id and field.name == 'id':
                    listf.append(name_field_id)
                else:
                    listf.append(field.verbose_name)
    return listf


# =========== Довідники ===============
directions = (('0', '–'), ('1', 'НТЦ'), ('2', 'Технологи'))
month_ua = ('', 'січень', 'лютий', 'березень', 'квітень', 'травень', 'червень', 'липень', 'серпень', 'вересень',
            'жовтень', 'листопад', 'грудень')


def get_list_zak(lst=0):
    """ ----- Отримання даних з Таблиці Замовлень. Дані отримуються з бази ms-sql ИТП прямим запитом -----
        в демо-варіанті  -  завантажуємо з файлу
    """
    file_json = str(BASE_DIR / "data" / "zakaz.json")
    rows = []
    if os.path.isfile(file_json):
        with codecs.open(file_json, 'r', 'utf-8') as file_data:
            rows = json.load(file_data)

    all_list_zak = [('ПР0001', 'Перед-контрактні роботи', 'PП'),
                    ('ПР0002', 'Інші&nbsp;роботи для служби продажу', 'PП'),
                    ('ПР0003', 'Перспективні розробки без замовлення', 'PП'),
                    ('ПР0004', 'Науково-дослідні роботи', 'PП'),
                    ('ПР0005', 'Інші роботи загального характеру (без замовлення)', 'PП'),
                    ('ВЗ0001', 'Інше виробниче замовлення', 'PП'),
                    ('РЗ0001', 'Разові замовлення', 'PП'),
                    ]
    all_list_zak.extend(rows)

    if lst == 1:
        list_zak = [(row[0].strip(),
                     f"{row[1].replace('&nbsp;', ' ')} *** {row[0].strip()}"
                     if row[2].strip() == 'ОП' else
                     f"{row[0].strip()} - {row[1].replace('&nbsp;', ' ')}")
                    for row in all_list_zak]
        return list_zak
    elif lst == 9:
        list_zak = [(row[0].strip(), row[1].strip()) for row in all_list_zak]
        return list_zak
    else:
        dict_zak = {zak.zakaz: zak.name_zak for zak in ZakazHistory.objects.all()}
        return dict_zak


class ZakazHistory(models.Model):
    """ --- Історія Виробничіх Замовлень ---
    Замовлення з часом будуть закриті і їх назви будуть недоступні, бо список активних замовлень вибирається динамічно.
    Для вирішення проблеми  додана таблиця та процедури для зберігання замовлень, які були використані в роботах.
    Параметр Тип замовлення = 'ОП' для насосів 'ЗЧ' - для запчастин
    """
    zakaz = models.CharField("Виробниче Замовлення", max_length=20, primary_key=True)
    name_zak = models.CharField("Виробниче Замовлення", max_length=100, default='')
    type_zak = models.CharField("Тип замовлення", max_length=5, default='ОП')

    def __str__(self):
        return f"{self.zakaz} - {self.name_zak}"

    class Meta:
        verbose_name = 'Історія Виробничіх Замовлень'
        verbose_name_plural = 'Історія Виробничіх Замовлень'
        ordering = ['type_zak', 'zakaz']


class DocType(models.Model):
    """ --- Класифікатор типів документів ---- """
    id = models.AutoField("id", primary_key=True)
    name = models.CharField("Тип документу", max_length=50)

    def __str__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        verbose_name = 'Тип документів'
        verbose_name_plural = 'Типи документів'
        ordering = ["id"]


class DocKind(models.Model):
    """ --- Класифікатор видів документів ---- """
    id = models.PositiveIntegerField("id", primary_key=True)
    npp = models.PositiveIntegerField("№ пп", null=False, default=0)
    doctype = models.ForeignKey(DocType, on_delete=models.PROTECT, verbose_name="Тип документу")
    name = models.CharField("Вид документу", max_length=60)

    def __str__(self):
        return self.name  # f"{str(self.npp)[:-1]} - {self.name}"

    class Meta:
        verbose_name = 'Вид документів'
        verbose_name_plural = 'Види документів'
        ordering = ["npp"]


class WorkContent(models.Model):
    """ --- Класифікатор змісту робіт, що виконуються --- """
    id = models.PositiveIntegerField("id", primary_key=True)
    npp = models.PositiveIntegerField("№ пп", null=False, default=0)
    content = models.CharField("Назва робіт", max_length=100)
    doc_kinds = models.ManyToManyField(DocKind, verbose_name="Види документів")
    direction = models.CharField("Дирекція", max_length=2, default='–', choices=directions)

    def __str__(self):
        return self.content

    @staticmethod
    def get_doc_kinds():
        pass

    class Meta:
        verbose_name = 'Класифікатор змісту робіт, що виконуються'
        verbose_name_plural = 'Класифікатор змісту робіт, що виконуються'
        ordering = ["direction", "npp"]


format_A = (('0', '–'), ('.5', 'А5'), ('1', 'А4'), ('2', 'А3'), ('4', 'А2'), ('8', 'А1'), ('16', 'А0'))


class Department(models.Model):
    """   -----  Підрозділи -----  """
    id = models.AutoField("id", primary_key=True)
    dep_code = models.CharField("Код підрозділу", max_length=10)
    dep_name = models.CharField("Назва підрозділу", max_length=15)
    dep_fullname = models.CharField("Повна назва підрозділу", max_length=70)
    dep_shef_name = models.CharField("Керівник підрозділу", max_length=50, default='?')
    dep_shef_position = models.CharField("Посада керівника підрозділу", max_length=50, default='?')
    dep_director_name = models.CharField("Директор з напрямку", max_length=50, default='?')
    dep_director_position = models.CharField("Посада Директора з напрямку", max_length=50, default='?')
    dep_direction = models.CharField("Дирекція", max_length=2, default='–', choices=directions)

    def __str__(self):
        return self.dep_name if self.dep_code.endswith("000") else f"{self.dep_code[:2]}000 - {self.dep_name}"

    @staticmethod
    def get_list_for_choice(deps=["all"]):
        """  список  (код, назва) для поля вибору в формі """
        queryset = Department.objects.filter(dep_code__contains="000")
        queryset = queryset.exclude(dep_name__startswith="?")
        if deps and deps[0] != "all":
            queryset = queryset.filter(dep_code__in=deps)
        return queryset

    @staticmethod
    def get_list_section_for_choice(deps=["all"]):
        """  Відбір БЮРО """
        queryset = Department.objects.exclude(dep_code__contains="000")
        if deps and deps[0] != "all":
            # формуємо список бюро для доступу
            #  якщо в deps - відділ, то беремо всі бюро для відділу
            #  якщо в deps - бюро то в умови додаємо саме бюро
            sections = []
            for dep in deps:
                if dep.endswith('000'):  # відділ
                    sections.append(dep[:2])
                else:  # бюро
                    sections.append(dep)
            query = Q()  # Початковий Q-об'єкт (пустий)
            # Додавання умов до Q-об'єкта
            for condition in sections:
                query |= Q(dep_code__startswith=condition)
            # Відбір даних за умовами
            queryset = queryset.filter(query)
        return queryset

    @staticmethod
    def get_list_all(deps):
        """ Вібір підрозділів з урахуванням доступу """
        if deps[0] == "all":
            queryset = Department.objects.all()
        else:
            #  доступ по переліку доступних підрозділів
            queryset = Department.objects.filter(dep_code__in=deps)
        return queryset

    # Metadata
    class Meta:
        verbose_name = 'Підрозділ'
        verbose_name_plural = 'Підрозділи'
        ordering = ["dep_code"]


class Employee(models.Model):
    """  -----  Співробітники -----  """
    id = models.AutoField("id", primary_key=True)
    uses = models.BooleanField("Активний", default=True)
    tab_nom = models.CharField("Табельний номер", max_length=10)
    full_name = models.CharField("П.І.Б.", max_length=60)
    position = models.CharField("Посада", max_length=50)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name="Підрозділ",
                                   related_name="department")
    section = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name="Бюро",
                                related_name="section")

    def __str__(self):
        return f"{self.full_name} ({self.tab_nom})"

    @staticmethod
    def get_list_all(deps):
        """ Вібір підрозділів з урахуванням доступу """
        if deps[0] == "all":
            queryset = Employee.objects.all()
        else:
            #  доступ по переліку доступних підрозділів
            queryset = Employee.objects.filter(department__dep_code__in=deps)
        return queryset

    @staticmethod
    def get_list_for_choice(tab_nom="", deps=None):
        """  список  (код, назва) для поля вибору в формі """
        # -------- по співробітниках
        if tab_nom:
            # -- дозволені всі
            if tab_nom == "all":
                queryset = Employee.objects.all()
            # -- конкретний співробітник
            else:
                queryset = Employee.objects.filter(tab_nom=tab_nom)
        # ---------- по бюро та нових підрозділах
        else:
            if deps:
                # формуємо список бюро для доступу
                #  якщо в deps - відділ, то беремо всі бюро для відділу
                #  якщо в deps - бюро то в умови додаємо саме бюро
                sections = []
                departmens = []
                for dep in deps:
                    if dep.endswith('000'):  # відділ
                        departmens.append(dep)
                    else:  # бюро
                        sections.append(dep)
                query = Q()  # Початковий Q-об'єкт (пустий)
                # Додавання умов до Q-об'єкта
                for condition in departmens:  # відділи
                    query |= Q(department__dep_code=condition)
                for condition in sections:  # бюро
                    query |= Q(section__dep_code=condition)
                # Відбір даних за умовами
                queryset = Employee.objects.filter(query)
                # queryset = Employee.objects.filter(department__dep_code__in=deps)

            # -- не передано параметрів
            else:
                queryset = Employee.objects.filter(pk=0)

        return queryset.filter(uses=True)

    # Metadata
    class Meta:
        verbose_name = 'Співробітник'
        verbose_name_plural = 'Співробітники'
        ordering = ["full_name"]


class AccountWorkTime(models.Model):
    """ ----- Розподіл робочого часу по заказах ----"""
    id = models.AutoField("id", primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Співробітник")
    work_date = models.DateField("Дата роботи", null=False, blank=False)
    zakaz = models.CharField("Виробниче Замовлення", max_length=20, choices=get_list_zak(1))
    work_content = models.ForeignKey(WorkContent, on_delete=models.PROTECT, verbose_name="Зміст роботи")
    work_detail = models.CharField("Деталізація робіт", max_length=150)
    doc_kind = models.ForeignKey(DocKind, on_delete=models.PROTECT, verbose_name="Створено документ")
    doc_designation = models.CharField("Позначення документа", max_length=80, default='–')
    doc_name = models.CharField("Назва документа", max_length=60, default='–')
    doc_format = models.CharField("Формат документа", max_length=2, default='–', choices=format_A)
    doc_krform = models.PositiveIntegerField("Кількість аркушів документу", default=0)
    doc_kolA4 = models.DecimalField("К-ть документів, приведених до формату А4, од", default=0, decimal_places=2, max_digits=5)
    work_time = models.DecimalField("Витрачено годин", default=0, decimal_places=2, max_digits=5)
    work_percent = models.PositiveIntegerField("Об'єм виконання роботи по документу за вказану кількість годин, % ", default=100)
    kol_normoper = models.PositiveIntegerField("Кількість нормооперацій", default=0)

    def __str__(self):
        return f"{self.employee}  {self.work_date}"

    class Meta:
        verbose_name = 'Розподіл робочого часу по заказах'
        verbose_name_plural = 'Розподіл робочого часу по заказах'
        ordering = ["employee", "-work_date", "-id"]


class ReportWorkTimeTempl(models.Model):
    """ ------ Шаблон Підсумкового звіту по виконаним роботам ---- """
    id = models.AutoField("id", primary_key=True)
    rep_code = models.CharField("Код звіту", max_length=5, null=False, blank=False)
    npp = models.CharField("№\nп/п", max_length=10, null=False, blank=False)
    work_content = models.ForeignKey(WorkContent, on_delete=models.PROTECT, verbose_name="Зміст роботи")
    doc_type = models.ForeignKey(DocType, on_delete=models.PROTECT, verbose_name="Тип документу", default=8)
    doc_kind = models.ForeignKey(DocKind, on_delete=models.PROTECT, verbose_name="Вид документу", null=True, blank=True)

    def __str__(self):
        return f"{self.npp} {self.work_content}"

    class Meta:
        verbose_name = 'Шаблони Підсумкових звітів по виконаним роботам'
        verbose_name_plural = 'Шаблон Підсумкового звіту по виконаним роботам'
        ordering = ["rep_code", "npp"]


class WorkTimeFact(models.Model):
    """ ----- Фактично відпрацьваний час працівниками по табелю по місяцях ----"""
    id = models.AutoField("id", primary_key=True)
    tab_nom = models.CharField("Табельний номер", max_length=10, default='000')
    work_date = models.DateField("Перше число місяця", null=False, blank=False)
    fact_time = models.DecimalField("Фактично відпрацьовано годин", default=0, decimal_places=2, max_digits=5)

    def __str__(self):
        return f"{self.work_date} {self.tab_nom} {self.fact_time}"

    class Meta:
        verbose_name = 'Фактично відпрацьваний час по табелю'
        verbose_name_plural = 'Фактично відпрацьваний час по табелю'
        ordering = ["tab_nom", "work_date"]


"""
    SELECT distinct
        CASE WHEN z.KTZAJ = 'ЗЧ' AND LEFT(z.KZAJ, 4) <> '0005' THEN SUBSTRING(z.KZAJ, PATINDEX('%-%', z.KZAJ) 
           + 1, 10) ELSE z.KZAJ END as KZAJ
       , CASE WHEN CHARINDEX(CHAR(13), z.COMM) > 1 THEN LEFT(z.COMM, CHARINDEX(CHAR(13), z.COMM) - 1) ELSE 
           z.COMM END AS NAME_ZAK
       , z.KTZAJ
       , z.DZAJ
        FROM ZAE z
        inner join (
               select distinct CASE WHEN PATINDEX('%S', kzajnpp) > 1 THEN 
                      LEFT(kzajnpp, PATINDEX('%S', kzajnpp) - 1) ELSE kzajnpp END as KZAJNPP
               from PLA
               where kplt in ('510', '511', '513')
                     and DIZG_F is null 
                     and PR_IZG_F <> '+'
                     and KSTATUS not in ('X', 'Z')
               ) as pl on z.kzaj = pl.KZAJNPP
        WHERE  z.DATE_Z is null 
               and ((z.DIZG_PL is null
               and z.KTZAJ in ('ОП'))
               or (z.KTZAJ in ('ЗЧ', 'ГР', 'РН', 'ПП')))
        UNION ALL
        select distinct CASE WHEN LEFT(k.NAIMKM_S, 12) = 'График з-ч №' THEN LEFT(SUBSTRING(k.NAIMKM_S, 13, 254), 
                  patindex('%_PZ%', SUBSTRING(k.NAIMKM_S, 13, 254)) - 1) ELSE SUBSTRING(k.NAIMKM_S, 
                  patindex('%PZ_%', k.NAIMKM_S) + 3, 254) END AS KZAJ
               ,CASE WHEN LEFT(k.NAIMKM_S, 12) = 'График з-ч №' THEN 'ЗапЧасти' ELSE k.NMAT_MAT1 END AS NAME_ZAK
               ,CASE WHEN LEFT(k.NAIMKM_S, 12) = 'График з-ч №' THEN 'ЗЧ' ELSE 'ОП' END AS KTZAJ
               ,s.DATE_D as DZAJ
        from TKIS s
        left join KSM k ON k.KMAT = s.KMATGP
        left join ZAE z ON z.KZAJ = CASE WHEN LEFT(k.NAIMKM_S, 12) = 'График з-ч №' THEN LEFT(SUBSTRING(k.NAIMKM_S, 13, 254), 
                  patindex('%_PZ%', SUBSTRING(k.NAIMKM_S, 13, 254)) - 1) ELSE SUBSTRING(k.NAIMKM_S, 
                  patindex('%PZ_%', k.NAIMKM_S) + 3, 254) END
        inner join (
               select distinct CASE WHEN PATINDEX('%S', kzajnpp) > 1 THEN 
                      LEFT(kzajnpp, PATINDEX('%S', kzajnpp) - 1) ELSE kzajnpp END as KZAJNPP
               from PLA
               where kplt in ('510', '511', '513')
                     and DIZG_F is null 
                     and PR_IZG_F <> '+'
                     and KSTATUS not in ('X', 'Z')
               ) as pl on z.kzaj = pl.KZAJNPP
        where s.TIPSOST = '901'
               and s.NU = 0
               and s.FIO_D = 'ArchSozdPZ'
               and z.KZAJ is null
    order by 3 desc, 2, 1
"""
