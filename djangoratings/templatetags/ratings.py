"""
Template tags for Django
"""
# TODO: add in Jinja tags if Coffin is available

from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist

from djangoratings.models import Vote

register = template.Library()

class RatingByRequestNode(template.Node):
    def __init__(self, request, obj, context_var):
        self.request = request
        self.obj, self.field_name = obj.split('.')
        self.context_var = context_var
    
    def render(self, context):
        try:
            request = template.resolve_variable(self.request, context)
            obj = template.resolve_variable(self.obj, context)
            field = getattr(obj, self.field_name)
        except (template.VariableDoesNotExist, AttributeError):
            return ''
        try:
            vote = field.get_rating_for_user(request.user, request.META['REMOTE_ADDR'])
            context[self.context_var] = vote
        except ObjectDoesNotExist:
            context[self.context_var] = 0
        return ''

def do_rating_by_request(parser, token):
    """
    Retrieves the ``Vote`` cast by a user on a particular object and
    stores it in a context variable. If the user has not voted, the
    context variable will be 0.
    
    Example usage::
    
        {% rating_by_request request on instance as vote %}
    """
    
    bits = token.contents.split()
    if len(bits) != 6:
        raise template.TemplateSyntaxError("'%s' tag takes exactly five arguments" % bits[0])
    if bits[2] != 'on':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'on'" % bits[0])
    if bits[4] != 'as':
        raise template.TemplateSyntaxError("fourth argument to '%s' tag must be 'as'" % bits[0])
    return RatingByRequestNode(bits[1], bits[3], bits[5])
register.tag('rating_by_request', do_rating_by_request)

class RatingByUserNode(RatingByRequestNode):
    def render(self, context):
        try:
            user = template.resolve_variable(self.request, context)
            obj = template.resolve_variable(self.obj, context)
            field = getattr(obj, self.field_name)
        except template.VariableDoesNotExist:
            return ''
        try:
            vote = field.get_rating_for_user(user)
            context[self.context_var] = vote
        except ObjectDoesNotExist:
            context[self.context_var] = 0
        return ''

def do_rating_by_user(parser, token):
    """
    Retrieves the ``Vote`` cast by a user on a particular object and
    stores it in a context variable. If the user has not voted, the
    context variable will be 0.
    
    Example usage::
    
        {% rating_by_user user on instance as vote %}
    """
    
    bits = token.contents.split()
    if len(bits) != 6:
        raise template.TemplateSyntaxError("'%s' tag takes exactly five arguments" % bits[0])
    if bits[2] != 'on':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'on'" % bits[0])
    if bits[4] != 'as':
        raise template.TemplateSyntaxError("fourth argument to '%s' tag must be 'as'" % bits[0])
    return RatingByUserNode(bits[1], bits[3], bits[5])
register.tag('rating_by_user', do_rating_by_user)

@register.simple_tag
def generate_options(ratemanager, request):
    '''
    Display the options in a dropdown input such that if the user has already
    voted, the vote they made previously will be be selected by default.

    '''
    attributes = [None]
    attributes.extend(['value="%d"' % i for i in
        range(1, ratemanager.field.range + 1)])
    user_score = ratemanager.get_rating_for_user(user=request.user, ip_address=request.META['REMOTE_ADDR'])
    if user_score:
        attributes[int(user_score)] += ' selected="selected"'
    lines = ['<option %s>1 star</option>' % attributes[1]]
    lines.extend(['<option %s>%d stars</option>' % (attributes[i], i)
        for i in range(2, ratemanager.field.range + 1)])
    return ''.join(lines)
