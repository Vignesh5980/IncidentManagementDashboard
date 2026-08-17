from rest_framework.permissions import BasePermission


class ServiceRequestAPIPermission(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        role = getattr(
            request.user,
            "role",
            None
        )

        # Everyone authenticated can view
        if request.method == "GET":
            return True

        # These roles can create requests
        if request.method == "POST":
            return role in [
                "ADMIN",
                "TEAM_LEAD",
                "SUPPORT_ENGINEER",
            ]

        # Object-level permissions will handle these
        if request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            return True

        return False


    def has_object_permission(
        self,
        request,
        view,
        obj
    ):

        role = getattr(
            request.user,
            "role",
            None
        )

        # Admin has full access
        if role == "ADMIN":
            return True

        # Team Lead
        if role == "TEAM_LEAD":

            if request.method in [
                "GET",
                "PUT",
                "PATCH",
            ]:
                return True

            return False

        # Support Engineer
        if role == "SUPPORT_ENGINEER":

            if request.method == "GET":
                return True

            if request.method in [
                "PUT",
                "PATCH",
            ]:

                return (
                    obj.assigned_to_id
                    == request.user.id
                )

            return False

        return False