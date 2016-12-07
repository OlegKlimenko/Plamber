from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from django.contrib.auth.models import User
from app.models import TheUser, AddedBook


# ----------------------------------------------------------------------------------------------------------------------
def profile(request, profile_id):
    """
    Renders the profile page.

    :param django.core.handlers.wsgi.WSGIRequest request: The request for looking profile.
    :param int profile_id: The id profile we want to look.
    :return: HTML page.
    """

    if request.method == 'GET':
        if request.user.is_authenticated():
            user = get_object_or_404(User, id=profile_id)
            profile_user = get_object_or_404(TheUser, id_user=user)

            added_books = AddedBook.objects.filter(id_user=profile_user)

            context = {'profile_user': profile_user, 'added_books': added_books}

            if request.user.username == profile_user.id_user.username:
                context['owner'] = True

            else:
                print('nooo')

            return render(request, 'profile.html', context)

        else:
            return redirect('index')
    else:
        return HttpResponse(status=404)