from django import template

register = template.Library()


@register.filter(name="get_compl")
def get_compl(indexable, i):
    return indexable[i]


@register.filter(name="get_item")
def get_item(complaintlist):
    return complaintlist.your_item_key
