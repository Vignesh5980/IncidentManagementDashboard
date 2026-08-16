from rest_framework.permissions import BasePermission


class IncidentAPIPermission(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        role = getattr(
            request.user,
            "role",
            None
        )

        if request.method == "POST":

            return role in [
                "ADMIN",
                "TEAM_LEAD",
                "SUPPORT_ENGINEER",
            ]

        return True

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

        # Admin can do everything
        if role == "ADMIN":
            return True

        # Team Lead can view/update/assign
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