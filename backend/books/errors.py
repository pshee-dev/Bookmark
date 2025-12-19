
class BookExceptionHandler(Exception): 
    code = "exception"
    user_message = "현재 서비스 이용이 불가하오니, 나중에 다시 시도해 주세요."
    http_status = 400

    def __init__(self, *, dev_message=None, cause=None, user_message=None):
        self.dev_message = dev_message
        self.cause = cause
        if self.dev_message: # 로거가 없으므로 에러찾기용으로 임시적용
            print(self.dev_message)
        if user_message:
            self.user_message=user_message
        super().__init__(dev_message)

class InvalidQuery(BookExceptionHandler):
    code = "invalid_query"
    http_status = 400

class InvalidIsbn(BookExceptionHandler):
    code = "invalid_isbn"
    http_status = 400

class MissingTTBKey(BookExceptionHandler):
    code = "missing_key_error"
    http_status = 500

class ExternalAPIError(BookExceptionHandler):
    code = "external_api_error"
    http_status = 502

class TimeoutError(BookExceptionHandler):
    code = "timeout"
    http_status = 504

class NotFoundError(BookExceptionHandler):
    code = "book_not_found"
    http_status = 404