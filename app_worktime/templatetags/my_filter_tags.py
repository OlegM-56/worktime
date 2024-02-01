from django import template

register = template.Library()


# ---- Отримання табельного номеру зі строки про користувача ---
@register.filter(name='get_tab_nom')
def get_tab_nom(str_user):
    tab_nom = str_user.split('№ ')[1]
    tab_nom = tab_nom.split(')')[0]
    if not tab_nom:
        tab_nom = '000'

    return tab_nom
