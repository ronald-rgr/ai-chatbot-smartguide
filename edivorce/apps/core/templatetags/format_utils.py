# pylint: disable=invalid-name
""" Template formatting helpers """

from datetime import datetime
import locale
import re

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince

locale.setlocale(locale.LC_ALL, '')

register = template.Library()


@register.filter
def linebreaksli(value):
    """ Converts strings with newlines into <li></li>s """
    value = re.sub(r'\r\n|\r|\n', '\n', value.strip())  # normalize newlines
    lines = re.split('\n', value)
    lines = ['<li>%s</li>' % line for line in lines if line and not line.isspace()]
    return mark_safe('\n'.join(lines))


@register.filter
def date_formatter(value):
    """ Changes date format from dd/mm/yyyy to dd mmm yyyy """

    if value is None or value == '':
        return ''

    try:
        date = datetime.strptime(value, '%d/%m/%Y')
    except ValueError:
        date = None

    if date is None:
        date = datetime.strptime(value, '%b %d, %Y')

    return date.strftime('%d %b %Y')


@register.simple_tag()
def response(field, size=None, trail='', as_date=False):
    """ Return the required field value or the not-entered span """

    if field.strip():
        return '%s%s' % (date_formatter(field) if as_date else field, trail)
    style = ('min-width: %spx' % size) if size is not None else ''
    return format_html('<span class="form-entry not-complete" style="{}"></span>', style)


@register.simple_tag()
def required(field, size=None, trail=''):
    """ Return the required field value or the not-entered span """
    return response(field, size, trail)


@register.simple_tag(takes_context=True)
def checkbox(context, *args, **kwargs):
    """
    Return a checkbox icon, checked if all args true.

    Standalone arguments are evaluated as booleans according to normal python
    rules for truthy values.  A boolean is itself; an empty string is False
    while a non-empty string is True; etc.

    Keyword arguments are treated as the key being a question key in the
    responses dict, and the value as a matching value with the response.  If the
    response is a list, the value matches if its in the list.

    The weakness of this tag is that it can't handle negation (e.g., a response
    doesn't equal a particular value).  I don't have a clever way to handle that
    here that doesn't involve adding syntax or unconventional usage (e.g.,
    '^value' means not value).

    NOTE: using the tag with no arguments will result in a checked box since
    all() evaluates empty lists to True.  To simply print an empty checkbox,
    pass a False value as an argument.
    """
    args_pass = all(args)
    kwargs_pass = all([value in context['responses'].get(question, '')
                       for question, value in kwargs.items()])

    return mark_safe('<i class="fa fa%s-square-o" aria-hidden="true"></i>' %
                     ('-check' if args_pass and kwargs_pass else ''))


@register.filter
def claimantize(value):
    """ Summarize 'lives with' as Claimant 1, 2, or both """
    if 'you' in value:
        return 'Claimant 1'
    elif 'spouse' in value:
        return 'Claimant 2'
    elif 'both' in value:
        return 'Claimant 1 & Claimant 2'
    return value


@register.filter
def age(date):
    """
    Return the difference between now and date in the largest unit.

    This uses Django's timesince filter but takes only the first term,
    printing '46 years' instead of print '46 years, 7 months'.
    """
    try:
        birth = datetime.strptime(date, '%b %d, %Y')
    except ValueError:
        try:
            birth = datetime.strptime(date, '%b %d, %Y')
        except ValueError:
            birth = None
    if birth is not None:
        return timesince(birth).split(',')[0]
    return ''


@register.filter
def money(amount, symbol=True):
    """ Return a properly formatted currency string including symbol """

    try:
        return locale.currency(float(amount), symbol, grouping=True)
    except ValueError:
        pass

    return ''


@register.simple_tag(takes_context=True)
def payorize(context):
    payor = 'the payor'
    child_support_payor = context.get('child_support_payor', None)
    if child_support_payor == 'Myself (Claimant 1)':
        payor = context.get('name_you', child_support_payor)
    elif child_support_payor == 'My Spouse (Claimant 2)':
        payor = context.get('name_spouse', child_support_payor)
    elif child_support_payor == 'Both myself and my spouse':
        payor = '{} and {}'.format(context.get('name_you', 'myself'),
                                   context.get('name_spouse', 'my spouse'))
    return payor


@register.filter
def child_or_children(value):
    """ Return num followed by 'child' or 'children' as appropriate """

    try:
        value = int(value)
    except ValueError:
        return ''

    if value == 1:
        return '1 child'

    return '%d children'


@register.filter
def integer(value):
    """ Return value as an int or nothing """

    try:
        return int(float(value))
    except ValueError:
        return ''


@register.simple_tag()
def lookup(obj, property):
    """ Return the value of a dynamic property within an object"""
    return obj.get(property, '')


@register.simple_tag(takes_context=True)
def agreed_child_support_amount(context, claimant_id, line_breaks=True):
    """Return the agree amount for the specific claimant fact sheet table."""
    if not line_breaks:
        return context.get('amount_income_over_high_income_limit_{}'.format(claimant_id), '')
    else:
        return linebreaksli(context.get('amount_income_over_high_income_limit_{}'.format(claimant_id), ''))
