from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.forms import modelform_factory, TextInput
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator


class Dovidnyk:
    """
    --- Клас для роботи з простим довідником ---
    """

    def __init__(self, dov_model: type, dov_template="dovidnyk.html", dov_prefix="dep"):
        self.dov_model = dov_model
        self.dov_template: str = dov_template
        self.dov_prefix = dov_prefix
        self.dov_form = modelform_factory(model=dov_model, fields=[f.name for f in dov_model._meta.fields],
                                          widgets={'id': TextInput(attrs={'readonly': 'readonly', 'size': '5'}), })

    @staticmethod
    def has_user_perm(request):
        """ Перевірка прав на коригування довідників.
            Використовуємо стандартний дозвіл 'contenttypes.change_contenttype'  """
        # Перевіряємо дозволи поточного користувача
        user = request.user
        can_change = 1 if 'contenttypes.change_contenttype' in user.get_all_permissions() else 0
        can_view = 1 if 'contenttypes.view_contenttype' in user.get_all_permissions() else 0
        #  user = admin
        if user.is_staff or user.is_superuser:
            dep_permit = ["all"]
        else:
            groups_user = Group.objects.filter(user=user)
            dep_permit = []
            for group in groups_user:
                dep_permit.append(group.name.split()[0] if group else "*****")

        return can_view, can_change, dep_permit

    @method_decorator(login_required)
    def list_edit_dov(self, request, id_record=0, edit_mode=1):
        """ Сеанс перегляду довідника та коригування, додавання, видалення запису довідника """
        # -- дозволи
        permit = self.has_user_perm(request)
        # перевірка дозволу на доступ
        if not permit[0]: return HttpResponseRedirect("/")
        # перевірка дозволу на редагування
        if edit_mode: edit_mode = permit[1]

        # -- початкова ініціація змінних
        rec = None
        # ---------------
        # -- коригування існуючого запису
        if id_record:
            r = self.dov_model.objects.filter(pk=id_record)
            if r.count():
                rec = r[0]

        dov_form = self.dov_form(instance=rec)
        # поля таблиці
        dov_fields = [f.name for f in self.dov_model._meta.fields]

        # існуючи рядки
        rows_list_value = []
        i = 0
        for row in self.dov_model.get_list_all(permit[2]):
            rows_list_value.append({})
            for f in dov_fields:
                rows_list_value[i][f] = str(getattr(row, f))
            i += 1

        data = {"Title": self.dov_model._meta.verbose_name_plural, "permit": request.user.get_all_permissions(),
                "edit_mode": edit_mode, "dov_form": dov_form,
                "url_dov_list": f"{self.dov_prefix}_list", "url_dov_update": f"{self.dov_prefix}_update",
                "url_dov_delete": f"{self.dov_prefix}_delete",
                "id_record": id_record, "rows_list_value": rows_list_value, "dov_fields": dov_fields}
        return render(request, self.dov_template, context=data)

    @method_decorator(login_required)
    def update_rec_dov(self, request, id_record=0):
        """ Збереження змін в записі довідника """
        # перевірка дозволу на редагування
        if self.has_user_perm(request)[1]:
            if request.method == "POST":
                if id_record:  # існуючий запис
                    rec = self.dov_model.objects.get(pk=id_record)
                else:
                    rec = None  # новий запис
                    print('новий запис')

                dov_form = self.dov_form(request.POST, instance=rec)
                if dov_form.is_valid():
                    new_rec = dov_form.save()
                    print("id запису: ", new_rec.id)
                else:
                    print("!!!  Помилка валідації форми !!!!!")

        return HttpResponseRedirect(f"/{self.dov_prefix}_list/0/")

    @method_decorator(login_required)
    def del_rec_dov(self, request, id_record=0):
        """ Видалення запису """
        # перевірка дозволу на редагування
        if self.has_user_perm(request)[1]:
            if id_record:
                rec = self.dov_model.objects.get(pk=id_record)
                if rec:
                    rec.delete()
        return HttpResponseRedirect(f"/{self.dov_prefix}_list/0/")
# ----- >>
