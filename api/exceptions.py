from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):

    # Get the default DRF error response
    response = exception_handler(exc, context)

    if response is not None:

        status_code = response.status_code

        message = "An error occurred."

        if isinstance(response.data, dict):

            # For errors containing "detail"
            if "detail" in response.data:
                message = str(
                    response.data["detail"]
                )

            # Validation errors
            elif status_code == 400:
                message = "Validation failed."

        return Response(
            {
                "success": False,
                "status_code": status_code,
                "message": message,
                "errors": response.data,
            },
            status=status_code
        )

    # Unexpected server errors
    return Response(
        {
            "success": False,
            "status_code": 500,
            "message": "Internal server error.",
            "errors": None,
        },
        status=500
    )