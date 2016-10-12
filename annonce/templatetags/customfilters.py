from django import template

register = template.Library()


@register.filter('get_class_name')
def get_class_name(obj):
    return obj.__class__.__name__


@register.filter(name='add_css')
def add_css(field, args):
    css, auto_complete = args.split(',')
    updated_classes = css
    if 'class' in field.field.widget.attrs:
        updated_classes = " ".join([field.field.widget.attrs['class'], css])
    return field.as_widget(attrs={"class": updated_classes, "autocomplete": auto_complete})
