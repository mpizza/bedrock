from django.conf import settings
from django.http import HttpResponseRedirect

import jingo
from funfactory.urlresolvers import split_path
from jinja2.exceptions import TemplateNotFound

from dotlang import get_lang_path, lang_file_is_active


def render(request, template, context={}, **kwargs):
    """
    Same as jingo's render() shortcut, but with l10n template support.
    If used like this::

        return l10n_utils.render(request, 'myapp/mytemplate.html')

    ... this helper will render the following template::

        l10n/LANG/myapp/mytemplate.html

    if present, otherwise, it'll render the specified (en-US) template.
    """
    # Every template gets its own .lang file, so figure out what it is
    # and pass it in the context
    context['langfile'] = get_lang_path(template)

    # Look for localized template if not default lang.
    if request.locale != settings.LANGUAGE_CODE:

        # redirect to default lang if locale not active
        if not (settings.DEV or
                lang_file_is_active(context['langfile'], request.locale)):
            return HttpResponseRedirect('/' + '/'.join([
                settings.LANGUAGE_CODE,
                split_path(request.get_full_path())[1]
            ]))

        localized_tmpl = '%s/templates/%s' % (request.locale, template)
        try:
            return jingo.render(request, localized_tmpl, context, **kwargs)
        except TemplateNotFound:
            # If not found, just go on and try rendering the parent template.
            pass

    return jingo.render(request, template, context, **kwargs)
