from django.contrib import admin
from lady import models
from django.shortcuts import render, redirect, HttpResponse
from django.forms import ValidationError
# Register your models here.

enabled_admins = {}

class BaseAdmin:
    list_display = []
    list_filters = []
    list_per_page = 4
    search_fields = []
    filter_horizontal = ()
    actions = ['delete_selected_objs',]
    readonly_fields = []
    readonly_table = False
    modelform_exclude_fields = ()

    def delete_selected_objs(self, request, querysets):
        print(self, request, querysets)
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        if self.readonly_table:
            errors = {"readonly_table": "table is readonly ,obj [%s] cannot be deleted" % querysets}
        else:
            errors = {}

        if request.POST.get('delete_confirm') == 'yes':
            if not self.readonly_table:
                querysets.delete()
                return redirect('/king_admin/%s/%s' % (app_name, model_name))

        selected_ids = ','.join([str(i.id) for i in querysets])
        return render(request, 'king_admin/table_obj_delete.html', {'obj': querysets,
                                                                    'app_name': app_name,
                                                                    'model_name': model_name,
                                                                    'selected_ids': selected_ids,
                                                                    'action': request._admin_action,
                                                                    'errors': errors,
                                                                    })
    delete_selected_objs.display_name = '批量删除'

    def default_form_validation(self):
        '''用户可以在此进行自定义的表单验证，相当于django form的clean方法'''
        pass


class HostAdmin(BaseAdmin):
    list_display = ['id', 'hostname', 'ip_addr', 'port', 'idc', 'enabled']
    list_filters = ['idc', 'enabled']  # 区分choice和ForeignKey
    search_fields = ('hostname', 'ip_addr')
    # filter_horizontal = ()
    list_per_page = 4
    readonly_fields = ['hostname', 'ip_addr']
    # actions = ['func1',]
    # readonly_table = True  # 整张表只读

    def func1(self, request, querysets):
        print(self, request, querysets)


class IDCAdmin(BaseAdmin):
    list_display = ['id', 'name']


class HostGroupAdmin(BaseAdmin):
    list_display = ['id', 'name', 'bind_hosts']


class HostUserAdmin(BaseAdmin):
    list_display = ['id', 'auth_type', 'username']


class BindHostAdmin(BaseAdmin):
    list_display = ['id', 'host', 'host_user']


class UserProfileAdmin(BaseAdmin):
    # list_display = ['id', 'name', 'roles']
    list_display = ['id', 'email', 'name']
    # readonly_fields = ['password', 'last_login']
    readonly_fields = ['password',]  # 排除last_login字段
    filter_horizontal = ('user_permissions', 'groups', 'bind_hosts', 'host_groups')
    modelform_exclude_fields = ('last_login',)


def register(model_class, admin_class=None):
    model_list = enabled_admins.setdefault(model_class._meta.app_label, {})
    admin_class.model = model_class
    model_list[model_class._meta.model_name] = admin_class


register(models.Host, HostAdmin)
register(models.IDC, IDCAdmin)
register(models.UserProfile, UserProfileAdmin)
register(models.HostGroup, HostGroupAdmin)
register(models.HostUser, HostUserAdmin)
register(models.BindHost, BindHostAdmin)