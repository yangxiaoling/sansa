from django.db.models import Q

def table_filter(request, admin_class):
    filter_conditions = {}
    for k, v in request.GET.items():
        keys = ['page', 'o', '_q']
        if k in keys:  # 为分页、排序、筛选保留的关键字
            continue
        if v:
            filter_conditions[k] = v
    return admin_class.model.objects.filter(**filter_conditions).order_by('-id'), filter_conditions


def table_sort(request, objects):
    orderby_key = request.GET.get('o')
    if orderby_key:
        res = objects.order_by(orderby_key)
        if orderby_key.startswith('-'):
            orderby_key = orderby_key.strip('-')
        else:
            orderby_key = '-' + orderby_key
    else:
        res = objects

    return res, orderby_key


def table_search(request, admin_class, objects):
    search_key = request.GET.get('_q')
    if search_key:
        q_obj = Q()
        q_obj.connector = 'or'
        for column in admin_class.search_fields:
            q_obj.children.append(('%s__contains' % column, search_key))
        res = objects.filter(q_obj)
    else:
        res = objects
    return res