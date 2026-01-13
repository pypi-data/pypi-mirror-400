from mako.lookup import TemplateLookup

class Renderer(object):
    def __init__(self):
        super(Renderer, self).__init__()

    def render(self, lookup: TemplateLookup, template, **kwargs):
        t = lookup.get_template(template)
        return t.render(lookup=lookup, **kwargs)
