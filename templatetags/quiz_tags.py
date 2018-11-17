from django import template

register = template.Library()


@register.inclusion_tag('wordbook/correct_answers.html', takes_context=True)
def correct_answer_for_all(context, quesiton):
    answers = quesiton.get_answers()
