"""
Module contains the decorators which is used in the generic flow for validating allowed request methods and
form validation.
"""
from django.http import HttpResponse


# ----------------------------------------------------------------------------------------------------------------------
def process_method(allowed_method, err_code):
    """
    Decorates the request for the views. Checks if the request method is allowed. If it's allowed returns the
    result of the view's flow. If not, returns the status code defined in the decorator's 'err_code' parameter.

    :param str allowed_method: The allowed method for the selected view.
    :param int err_code:       The error status code which must be returned if the method is not allowed.
    """
    def process_view(func):
        def inner(*args, **kwargs):
            # The first argument of the view is always request.
            if args[0].method == allowed_method:
                return func(*args, **kwargs)
            else:
                return HttpResponse(status=err_code)
        return inner
    return process_view


# ----------------------------------------------------------------------------------------------------------------------
def process_ajax(err_code):
    """
    Decorates the request for the views. Checks if the request method type is ajax. If it's ajax returns the
    result of the view's flow. If not, returns the status code defined in the decorator's 'err_code' parameter.

    :param int err_code: The error status code which must be returned if the method is not allowed.
    """
    def process_view(func):
        def inner(*args, **kwargs):
            # The first argument of the view is always request.
            if args[0].is_ajax():
                return func(*args, **kwargs)
            else:
                return HttpResponse(status=err_code)
        return inner
    return process_view


# ----------------------------------------------------------------------------------------------------------------------
def process_form(method, request_form, err_code):
    """
    Decorates the views by checking if the form passed in the 'request_form' param is valid.
    if yes, returns the execution flow of the view. If no' returns the status code which defined in the 'err_code'
    param.

    :param method:       The method which will be used to fetch data for the form.
    :param request_form: The form to be processed/validated.
    :param err_code:     The error status code which must be returned if the form data is not valid.
    """
    def process_view(func):
        def inner(*args, **kwargs):
            # The first argument of the view is always request.
            request = args[0]

            form = request_form(getattr(request, method), request.FILES)
            if form.is_valid():
                kwargs['form'] = form
                return func(*args, **kwargs)
            else:
                return HttpResponse(status=err_code)
        return inner
    return process_view
