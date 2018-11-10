from django import template

register = template.Library()


@register.simple_tag
def url_replace(request, value):
    dict_ = request.GET.copy()
    dict_["page"] = str(value)  # Django2.1対策。それ以外はvalueだけでOK
    return dict_.urlencode()

