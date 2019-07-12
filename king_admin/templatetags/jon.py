from django import template
from django.utils.safestring import mark_safe
from datetime import datetime, timedelta
from django.core.exceptions import FieldDoesNotExist

register = template.Library()

@register.simple_tag
def return_model_name(admin_class):  # _meta(以下划线开头的)不能在模板中使用
    return admin_class.model._meta.verbose_name_plural

# 做了分页就得从后端返回数据了
# @register.simple_tag
# def get_query_sets(admin_class):
#     return admin_class.model.objects.all()


@register.simple_tag
def build_table_row(request, row, admin_class):
    row_html = ''
    for column in admin_class.list_display:
        try:
            field_obj = row._meta.get_field(column)
            if field_obj.choices:  # 判断choices类型
                column_data = getattr(row, 'get_%s_display' % column)()
            else:
                column_data = getattr(row, column)

            if type(column_data).__name__ == 'datetime':  # 判断时间类型
                column_data = column_data.strftime("%Y-%m-%d %H:%M:%S")

            if column == 'id':
                row_html += '<td><a href="%s%s/change">%s</a></td>' % (request.path, row.id, column_data)
            else:
                row_html += '<td>%s</td>' % column_data
        # 显示不在数据库中的字段
        except FieldDoesNotExist as e:
            if hasattr(admin_class, column):
                column_func = getattr(admin_class, column)
                column_data = column_func(row)
                row_html += '<td>%s</td>' % column_data
    return mark_safe(row_html)


# @register.simple_tag
# def render_page_ele(loop_counter, query_sets, filter_conditions):
#     filters = ''
#     for k, v in filter_conditions.items():
#         filters += '&%s=%s' % (k, v)
#     if abs(loop_counter - query_sets.number) <= 1:  # 只显示当前页、前后各一页
#         ele_class = ''
#         if loop_counter == query_sets.number:  # 当前页
#             ele_class = 'active'
#         ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (ele_class, loop_counter, filters, loop_counter)
#         return mark_safe(ele)
#     return ''  # py默认返回None, 会在页面显示


@register.simple_tag
def build_paginators(query_sets, filter_conditions, previous_orderby, search_text):
    filters = ''
    pager = ''
    for k, v in filter_conditions.items():
        filters += '&%s=%s' % (k, v)
    filters += '&o=%s' % previous_orderby
    filters += '&%s=%s' % ('_q', search_text)

    # 在当前页的两边各加一个'...'
    added_pot = False
    for page_num in query_sets.paginator.page_range:
        if page_num < 3 or page_num > query_sets.paginator.num_pages - 2:
            ele_class = ''
            if page_num == query_sets.number:  # 当前页
                ele_class = 'active'
            pager += '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (ele_class, page_num, filters, page_num)
        elif abs(page_num - query_sets.number) <= 1:  # 只显示当前页、前后各一页
            ele_class = ''
            if page_num == query_sets.number:  # 当前页
                added_pot = False  # 当前页后边也要加一个'...'
                ele_class = 'active'
            pager += '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (ele_class, page_num, filters, page_num)
        else:
            if not added_pot:
                pager += '<li><a>...</a></li>'
                added_pot = True

    return mark_safe(pager)

@register.simple_tag
def render_filter_ele(filter_field, admin_class, filter_conditions):
    # select_ele = '''<select name="%s"><option value="">-----</option>''' % (filter_field, )
    select_ele = '''<select class="form-control"  name={filter_field}><option value="">-----</option>'''
    field_obj = admin_class.model._meta.get_field(filter_field)
    selected = ''
    selected_item = None
    if field_obj.name in filter_conditions:
        selected_item = filter_conditions[field_obj.name]
    elif '%s__gte' % field_obj.name in filter_conditions:  # 对于日期格式, 在前端就改为了__gte格式, 省去了在后端判断, 但前端显示过滤条件又成了问题,
        selected_item = filter_conditions['%s__gte' % field_obj.name]

    if field_obj.choices:
        for choice_item in field_obj.choices:
            if str(choice_item[0]) == selected_item:
                selected = 'selected'
            select_ele += '''<option value="%s" %s>%s</option>''' % (choice_item[0], selected, choice_item[1])
            selected = ''

    if type(field_obj).__name__ == 'ForeignKey':
        for choice_item in field_obj.get_choices()[1:]:
            if str(choice_item[0]) == selected_item:  # 之所以多次把choice_item为字符串而不是一次把字符串转为整型, 是因为select_item可以是任何类型, 比如下面的日期, '2017-6-30'
                selected = 'selected'
            select_ele += '''<option value="%s" %s>%s</option>''' % (choice_item[0], selected, choice_item[1])
            selected = ''

    if type(field_obj).__name__ in ['DateTimeField', 'DateField']:
        date_els = []
        today_ele = datetime.now().date()
        date_els.append(['今天', today_ele])
        date_els.append(["昨天", today_ele - timedelta(days=1)])
        date_els.append(["近7天", today_ele - timedelta(days=7)])
        date_els.append(["本月", today_ele.replace(day=1)])
        date_els.append(["近30天", today_ele - timedelta(days=30)])
        date_els.append(["近90天", today_ele - timedelta(days=90)])
        date_els.append(["近180天", today_ele - timedelta(days=180)])
        date_els.append(["本年", today_ele.replace(month=1, day=1)])
        date_els.append(["近一年", today_ele - timedelta(days=365)])

        selected = ''
        for item in date_els:
            if str(item[1]) == selected_item:
                selected = 'selected'
            select_ele += '''<option value="%s" %s>%s</option>''' % (item[1], selected, item[0])
            selected = ''

        filter_field_name = '%s__gte' % filter_field  # 特殊处理

    else:
        filter_field_name = filter_field

    select_ele += '</select>'
    select_ele = select_ele.format(filter_field=filter_field_name)

    return mark_safe(select_ele)

@register.simple_tag
def build_table_header_column(column, orderby_key, filter_conditions, admin_class):
    filters = ''
    for k, v in filter_conditions.items():
        filters += '&%s=%s' % (k, v)

    ele = '''<th><a href="?o={orderby_key}%s">{column}</a>
    {sort_icon}
    </th>''' % filters
    sort_icon = ''

    if orderby_key:
        if orderby_key.startswith('-'):
            sort_icon = '<span class="glyphicon glyphicon-chevron-up"></span>'
        else:
            sort_icon = '<span class="glyphicon glyphicon-chevron-down"></span>'

        if column == orderby_key.strip('-'):
            orderby_key = orderby_key
        else:
            orderby_key = column
            sort_icon = ''  # 非排序字段不显示排序图标
    else:
        orderby_key = column

    # 字段名显示verbose_name
    try:
        column_verbose = admin_class.model._meta.get_field(column).verbose_name
    except FieldDoesNotExist as e:
        column_verbose = getattr(admin_class, column).display_name
        orderby_key = ''

    ele = ele.format(orderby_key=orderby_key, column=column_verbose, sort_icon=sort_icon)
    return mark_safe(ele)


@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.verbose_name_plural


@register.simple_tag
def get_m2m_obj_list(admin_class, field, modelform_obj):
    '''返回m2m所有待选数据'''
    # 表结构对象的某个字段
    field_obj = getattr(admin_class.model, field.name)
    # all_obj_list = field_obj.rel.to.objects.all()
    all_obj_list = field_obj.rel.model.objects.all()  # django2.0

    # 单条数据的对象中的某个字段
    if modelform_obj.instance.id:  # 普通字段显示为'', 外键、多对多字段报错, 必须事先判断有没有这个实例
        obj_instance_field = getattr(modelform_obj.instance, field.name)
        selected_obj_list = obj_instance_field.all()
    else:
        return all_obj_list

    standby_obj_list = []
    for obj in all_obj_list:
        if obj not in selected_obj_list:
            standby_obj_list.append(obj)

    return standby_obj_list


@register.simple_tag
def get_m2m_selected_obj_list(modelform_obj, field):
    '''返回已选择的m2m数据'''
    if modelform_obj.instance.id:
        field_obj = getattr(modelform_obj.instance, field.name)
        return field_obj.all()


def recursive_related_objs_lookup(objs):
    ul_ele = '<ul>'
    for obj in objs:
        # 展示当前对象
        li_ele = '''<li>%s: %s</li>''' % (obj._meta.verbose_name, obj.__str__().strip('<>'))
        ul_ele += li_ele

        # 展示正向多对多
        for m2m_field in obj._meta.many_to_many:
            m2m_field_obj = getattr(obj, m2m_field.name)
            sub_ul_ele = '<ul>'
            for o in m2m_field_obj.select_related():
                li_ele = '''<li>%s: %s</li>''' % (m2m_field.name, o.__str__().strip('<>'))
                sub_ul_ele += li_ele
            sub_ul_ele += '</ul>'
            ul_ele += sub_ul_ele

        # 展示多对一、反向多对多
        for related_obj in obj._meta.related_objects:
            if 'ManyToManyRel' in related_obj.__repr__():
                if hasattr(obj, related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())
                    # 上面accessor_obj 相当于 customer.enrollment_set
                    if hasattr(accessor_obj, 'select_related'):
                        target_objs = accessor_obj.select_related()
                        # target_objs 相当于 customer.enrollment_set.all()

                        sub_ul_ele = '<ul style="color:red">'
                        for o in target_objs:
                            li_ele = '''<li>%s: %s</li>''' % (o._meta.verbose_name, o.__str__().strip('<>'))
                            sub_ul_ele += li_ele
                        sub_ul_ele += '</ul>'
                        ul_ele += sub_ul_ele

            elif hasattr(obj, related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                accessor_obj = getattr(obj, related_obj.get_accessor_name())
                # 上面accessor_obj 相当于 customer.enrollment_set
                if hasattr(accessor_obj, 'select_related'):
                    target_objs = accessor_obj.select_related()
                    # target_objs 相当于 customer.enrollment_set.all()
                else:
                    print("one to one i guess:", accessor_obj)
                    target_objs = accessor_obj

                if len(target_objs) > 0:
                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes

    ul_ele += '</ul>'
    return ul_ele


@register.simple_tag
def display_obj_related(objs):
    if objs:
        return mark_safe(recursive_related_objs_lookup(objs))


@register.simple_tag
def get_display_name(admin_class, action):
    action_func = getattr(admin_class, action)
    return action_func.display_name if hasattr(action_func, 'display_name') else action


@register.simple_tag
def is_change_func(request, field, admin_class):
    return 'change' in request.path and field.name in admin_class.readonly_fields