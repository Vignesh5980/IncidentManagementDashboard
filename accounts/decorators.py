from django.http import HttpResponseForbidden

def role_required(roles=[]):

    def decorator(view):

        def wrapper(request,*args,**kwargs):

            if request.user.role in roles:

                return view(
                    request,
                    *args,
                    **kwargs
                )

            return HttpResponseForbidden(
                "Access Denied"
            )

        return wrapper

    return decorator