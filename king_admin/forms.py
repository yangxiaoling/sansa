from django.forms import forms, ModelForm
from django.forms import ValidationError
from django.utils.translation import ugettext as _  # 国际化

# def create_model_form(model_obj):  # 这个更简单
#     class BaseModelForm(forms):
#         class Meta:
#             model = model_obj
#             fields = '__all__'
#     return BaseModelForm

def create_model_form(request, admin_class):
    '''动态生成modelform'''

    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():  # OrderedDict对象
            field_obj.widget.attrs['class'] = 'form-control'
            if 'change' in request.path and field_name in admin_class.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'

            # 添加字段级别的验证
            if hasattr(admin_class, 'clean_%s' % field_name):
                field_clean_func = getattr(admin_class, 'clean_%s' % field_name)
                setattr(cls, 'clean_%s' % field_name, field_clean_func)

        return ModelForm.__new__(cls)

    def default_clean(self):  # self为modelform对象
        '''给所有form默认添加一个clean验证'''
        errors_list = []

        if admin_class.readonly_table:
            raise ValidationError(
                _('Table %(table)s is readonly'),
                code='invalid',
                params={'table': admin_class.model._meta.model_name}
            )

        if 'change' in request.path:
            for field in admin_class.readonly_fields:
                field_val = getattr(self.instance, field)  # in db
                if hasattr(field_val, 'select_related'):  # 多对多字段特殊处理
                    set_m2m_vals = set([i.id for i in field_val.select_related()])  # 注意: 必须转为列表进而转为集合才能比较, 两个queryset对象不能比较
                    set_m2m_vals_from_frontend = set([i.id for i in self.cleaned_data.get(field)])
                    if set_m2m_vals != set_m2m_vals_from_frontend:  # 注意: 比较是否相等之前需要先转为集合, 因为列表即使元素相同但顺序不同,也是不同的
                        errors_list.append(ValidationError(
                            _('Field %(field)s is readonly'),
                            code='invalid',
                            params={'field': field}
                        ))
                    continue

                field_val_from_frontend = self.cleaned_data.get(field)
                if field_val != field_val_from_frontend:
                    errors_list.append(ValidationError(
                        _('Field %(field)s is readonly, data should be %(val)s'),
                        code='invalid',
                        params={'field': field, 'val': field_val}
                    ))

        # 调用用户自定制的验证
        res = admin_class.default_form_validation(self)  # 传入self
        # print('res', res)
        if res:
            errors_list.append(res)

        if errors_list:  # 还能这么玩, 记住吧
            raise ValidationError(errors_list)

    class Meta:
        model = admin_class.model
        fields = '__all__'
        exclude = admin_class.modelform_exclude_fields  # 排除字段

    attrs = {'Meta': Meta}
    _model_form_class = type('DynamicModelForm', (ModelForm, ), attrs)
    setattr(_model_form_class, '__new__', __new__)  # __new__在type后面添加
    setattr(_model_form_class, 'clean', default_clean)

    return _model_form_class