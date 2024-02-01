from django.urls import path
from .views import *

urlpatterns = [
    path('', main_page_view, name='index'),
    path('scan/', scanner_qr, name='scanner_qr'),

    path('', main_page_view, name='index'),
    path('sign-in/', login_main_page_view, name='main_login'),
    # =================== Довідники ==================
    path('dep_list/<int:id_record>/', departments.list_edit_dov, name='dep_list'),
    path('dep_update/<int:id_record>/', departments.update_rec_dov, name='dep_update'),
    path('dep_delete/<int:id_record>/', departments.del_rec_dov, name='dep_delete'),

    path('empl_list/<int:id_record>/', employees.list_edit_dov, name='empl_list'),
    path('empl_update/<int:id_record>/', employees.update_rec_dov, name='empl_update'),
    path('empl_delete/<int:id_record>/', employees.del_rec_dov, name='empl_delete'),

    # =============== Розподіл робочого часу НТЦ ==================
    path('worktime/', work_time_ntc.list_worktime, name='list_worktime'),
    path('worktime/<options>', work_time_ntc.list_worktime, name='list_worktime'),
    path('worktime/<period>/<work_date>/<tab_nom>', work_time_ntc.list_worktime, name='list_worktime'),
    path('worktime_edit/<int:edit_mode>/<int:id_row>/<options>', work_time_ntc.list_worktime, name='edit_worktime'),
    path('worktime_save/<int:id_row>/<options>', work_time_ntc.update_worktime, name='save_worktime'),
    path('worktime_delrow/<operation>/<int:id_row>/<options>', work_time_ntc.update_worktime, name='delrow_worktime'),

    path('worktime_report/', work_time_ntc.get_report, name='report_worktime'),
    path('worktime_report/<mode>/<kind_rep>', work_time_ntc.get_report, name='report_print_worktime'),
    path('worktime_report2/<kind_rep>', work_time_ntc.get_report, name='report2_worktime'),
    path('worktime_report2/<kind_rep>/<options>', work_time_ntc.get_report, name='report2_worktime'),
    path('get_all_work_percent/', work_time_ntc.get_all_work_percent, name='get_all_work_percent'),

    path('worktime_filters/<options>', work_time_ntc.list_worktime_filters, name='list_worktime_filters'),

    # =============== Розподіл робочого часу технологів ==================
    path('worktime2/', work_time_tech.list_worktime, name='list_worktime2'),
    path('worktime2/<options>', work_time_tech.list_worktime, name='list_worktime2'),
    path('worktime2/<period>/<work_date>/<tab_nom>', work_time_tech.list_worktime, name='list_worktime2'),
    path('worktime2_edit/<int:edit_mode>/<int:id_row>/<options>', work_time_tech.list_worktime, name='edit_worktime2'),
    path('worktime2_save/<int:id_row>/<options>', work_time_tech.update_worktime, name='save_worktime2'),
    path('worktime2_delrow/<operation>/<int:id_row>/<options>', work_time_tech.update_worktime, name='delrow_worktime2'),

    path('worktime2_filters/<options>', work_time_tech.list_worktime_filters, name='list_worktime2_filters'),

    path('worktime2_report/', work_time_tech.get_report, name='report_worktime2'),
    path('worktime2_report/<mode>/<kind_rep>', work_time_tech.get_report, name='report_print_worktime2'),
    path('worktime2_report2/<kind_rep>', work_time_tech.get_report, name='report2_worktime2'),
    path('worktime2_report2/<kind_rep>/<options>', work_time_tech.get_report, name='report2_worktime2'),
]
