from django.shortcuts import render, redirect
from king_admin import king_admin
from django.core.paginator import Paginator
from king_admin import utils
from king_admin.forms import create_model_form
from django.contrib.auth.decorators import login_required
# from lady.permissions.permission import check_permission
# Create your views here.
from django import forms

@login_required
def index(request):
    return render(request, 'king_admin/table_index.html', {'table_list': king_admin.enabled_admins})


# def display_table_objs(request, app_name, model_name):  # 模板中的传的两个参数在这里接收
#     admin_class = king_admin.enabled_admins[app_name][model_name]
#     return render(request, 'king_admin/table_objs.html', {'admin_class': admin_class})

@login_required
# @check_permission
def display_table_objs(request, app_name, model_name):  # 模板中的传的两个参数在这里接收
    admin_class = king_admin.enabled_admins[app_name][model_name]
    # objects = admin_class.model.objects.all()
    if request.method == 'POST':
        print(request.POST)
        admin_action = request.POST.get('action')
        selected_ids = request.POST.get('selected_ids')
        if selected_ids:
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(','))
        else:
            raise KeyError('No object got selected!')
        if hasattr(admin_class, admin_action):
            action_func = getattr(admin_class, admin_action)
            request._admin_action = admin_action
            return action_func(admin_class, request, selected_objs)
    objects, filter_conditions = utils.table_filter(request, admin_class)
    objects = utils.table_search(request, admin_class, objects)
    objects, orderby_key = utils.table_sort(request, objects)
    paginator = Paginator(objects, king_admin.BaseAdmin.list_per_page)
    page = request.GET.get('page')
    query_sets = paginator.get_page(page)
    return render(request, 'king_admin/table_objs.html', {'admin_class': admin_class,
                                                          'query_sets': query_sets,
                                                          'filter_conditions': filter_conditions,
                                                          'orderby_key': orderby_key,
                                                          'previous_orderby': request.GET.get('o', ''),
                                                          'search_text': request.GET.get('_q', '')})


@login_required
# @check_permission
def table_obj_change(request, app_name, model_name, obj_id):
    admin_class = king_admin.enabled_admins[app_name][model_name]
    obj = admin_class.model.objects.get(id=obj_id)
    model_form_class = create_model_form(request, admin_class)
    if request.method == 'GET':
        modelform_obj = model_form_class(instance=obj)
    elif request.method == 'POST':
        modelform_obj = model_form_class(request.POST, instance=obj)
        if modelform_obj.is_valid():
            modelform_obj.save()
        else:
            print('errors', modelform_obj.errors)
    return render(request, 'king_admin/table_obj_change.html', {'modelform_obj': modelform_obj,
                                                                'admin_class': admin_class,
                                                                'app_name': app_name,
                                                                'model_name': model_name})


@login_required
def table_obj_add(request, app_name, model_name):
    admin_class = king_admin.enabled_admins[app_name][model_name]
    model_form_class = create_model_form(request, admin_class)
    if request.method == 'GET':
        modelform_obj = model_form_class()

    elif request.method == 'POST':
        modelform_obj = model_form_class(request.POST)
        if modelform_obj.is_valid():
            modelform_obj.save()
            return redirect(request.path.replace('/add', ''))
        else:
            print(modelform_obj.errors)

    return render(request, 'king_admin/table_obj_add.html', {'modelform_obj': modelform_obj,
                                                             'admin_class': admin_class,
                                                             'app_name': app_name,
                                                             'model_name': model_name})


@login_required
def table_obj_delete(request, app_name, model_name, obj_id):
    admin_class = king_admin.enabled_admins[app_name][model_name]
    obj = admin_class.model.objects.filter(id=obj_id)

    if admin_class.readonly_table:
        errors = {"readonly_table": "table is readonly ,obj [%s] cannot be deleted" % obj}
    else:
        errors = {}

    if request.method == 'POST':
        if not admin_class.readonly_table:
            obj.delete()
            return redirect('/king_admin/%s/%s' % (app_name, model_name))

    return render(request, 'king_admin/table_obj_delete.html', {'obj': obj,
                                                                'app_name': app_name,
                                                                'model_name': model_name,
                                                                'errors': errors})


@login_required
def password_reset(request, app_name, model_name, obj_id):
    admin_class = king_admin.enabled_admins[app_name][model_name]
    obj = admin_class.model.objects.get(id=obj_id)
    errors = {}

    if request.method == 'POST':
        _password1 = request.POST.get("password1")
        _password2 = request.POST.get("password2")
        if _password1 == _password2:
            if len(_password2) > 5:
                obj.set_password(_password1)
                obj.save()
                return redirect(request.path.rstrip("password/"))

            else:
                errors["password_too_short"] = "must not less than 6 letters"
        else:
            errors['invalid_password'] = "passwords are not the same"
    return render(request, 'king_admin/password_reset.html', {'obj': obj, 'errors': errors})
