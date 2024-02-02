from datetime import date

from django import forms

from app_worktime.models import *

from django.forms.renderers import TemplatesSetting

class CustomFormRenderer(TemplatesSetting):
    field_template_name = "field_inline.html"


# ----- Параметри відбору для Журналу обліку робочого часу----
class WorkTimeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        tab_nom = kwargs.pop('tab_nom', '')
        dep_permit = kwargs.pop('dep_permit', None)
        super(WorkTimeForm, self).__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.get_list_for_choice(tab_nom, dep_permit)
        self.fields['par_work_date'].widget.attrs.update({'max': date.today().strftime('%Y-%m-%d')})

    """ період:
        якщо +, то work_date - перший день місяця та відбір даних по місяцю
        якщо - , то  work_date = робочий день в періоді та відбір по конкретній даті
    """
    period = forms.BooleanField(label="За місяць", initial=True, required=False, widget=forms.CheckboxInput())
    par_work_date = forms.DateField(label="Дата початку місяця", required=True,
                                    widget=forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off', }))
    # 'max': date.today().strftime('%Y-%m-%d')}))
    employee = forms.ModelChoiceField(label="Співробітник", queryset=Employee.get_list_for_choice(), required=True)


# ----- Параметри відбору для Звіту по обліку робочого часу----
class WorkTimeRepForm(forms.Form):
    def __init__(self, *args, **kwargs):
        tab_nom = kwargs.pop('tab_nom', '')
        dep_permit = kwargs.pop('dep_permit', None)
        super(WorkTimeRepForm, self).__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.get_list_for_choice(tab_nom, dep_permit)
        # if dep_permit:
        self.fields['dep'].queryset = Department.get_list_for_choice(dep_permit)
        self.fields['section'].queryset = Department.get_list_section_for_choice(dep_permit)

    period = forms.BooleanField(label="Період", required=False, widget=forms.CheckboxInput())
    par_work_date = forms.DateField(label="Дата початку місяця", required=True,
                                    widget=forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}))
    par_work_date_end = forms.DateField(label="Закінчення періоду", required=True,
                                        widget=forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}))
    employee = forms.ModelChoiceField(label="Співробітник", queryset=Employee.get_list_for_choice(), required=False)
    section = forms.ModelChoiceField(label="Бюро", queryset=Department.get_list_for_choice(),
                                     to_field_name='dep_code',  # Вказуємо поле для вибору
                                     required=False)
    dep = forms.ModelChoiceField(label="Підрозділ", queryset=Department.get_list_for_choice(),
                                 to_field_name='dep_code',  # Вказуємо поле для вибору
                                 required=False)
    ntc_total = forms.BooleanField(label="По НТЦ", initial=False, required=False, widget=forms.CheckboxInput())


# ================ Форми вводу даних в БД ========================
class WorkTime_rowForm(forms.ModelForm):
    """----- Коригування/додавання рядка таблиці розподілу робочого часу НТЦ ---"""

    nam_zak = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = AccountWorkTime
        fields = ['work_date', 'zakaz',
                  'work_content', 'work_detail',
                  'doc_kind', 'doc_designation', 'doc_name',
                  'doc_format', 'doc_krform', 'kol_normoper',
                  'work_time', 'work_percent',
                  'id', 'employee']
        widgets = {
            'id': forms.HiddenInput(),
            'employee': forms.HiddenInput(),
            'work_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'autocomplete': 'off',
                                                                   'max': date.today().strftime('%Y-%m-%d')}),
            'work_detail': forms.TextInput(attrs={'size': '69'}),
            'doc_designation': forms.TextInput(attrs={'size': '35', 'onfocus': 'this.select()'}),
            'doc_name': forms.TextInput(attrs={'size': '69', 'onfocus': 'this.select()'}),
            'doc_krform': forms.TextInput(
                attrs={'type': 'number', 'min': '0', 'max': '9999', 'onfocus': 'this.select()'}),
            'kol_normoper': forms.TextInput(
                attrs={'type': 'number', 'min': '0', 'max': '9999', 'onfocus': 'this.select()'}),
            'work_time': forms.TextInput(attrs={'type': 'number', 'step': '0.25', 'min': '0.25', 'max': '8',
                                                'onfocus': 'this.select()'}),
            'work_percent': forms.TextInput(
                attrs={'type': 'number', 'min': '0', 'max': '100', 'onfocus': 'this.select()'}),
        }
