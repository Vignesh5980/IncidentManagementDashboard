import logging
import time


logger = logging.getLogger("api")


class APIRequestLoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):

        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        # Log only API requests
        if request.path.startswith("/api/"):

            user = (
                request.user.username
                if request.user.is_authenticated
                else "Anonymous"
            )

            logger.info(
                "method=%s path=%s user=%s "
                "status=%s duration=%.3fs",
                request.method,
                request.path,
                user,
                response.status_code,
                duration,
            )

        return response