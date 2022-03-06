from django import template

register = template.Library()


# Custom Filter to replace " " by "+" in the query which in turn generates a search result on the same page
@register.filter
def replace_space(query):
    query = str(query)
    return query.replace(" ", "+")
