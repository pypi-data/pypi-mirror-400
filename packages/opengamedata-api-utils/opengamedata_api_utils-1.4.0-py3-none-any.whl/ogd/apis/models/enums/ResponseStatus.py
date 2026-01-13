from enum import IntEnum
from typing import Set

class ResponseStatus(IntEnum):
    """Enumerated type to track the status of an API request result.
    """
    NONE          =   1
    CONTINUE      = 100
    OK            = 200
    MULTI_CHOICES = 300
    BAD_REQUEST   = 400
    INTERNAL_ERR  = 500

    # 100s
    SWITCHING_PROTOCOLS = 101
    PROCESSING          = 102
    EARLY_HINTS         = 103

    # 200s
    CREATED           = 201
    ACCEPTED          = 202
    NON_AUTHORITATIVE = 203
    NO_CONTENT        = 204
    RESET             = 205
    PARTIAL           = 206
    MULTI_STATUS      = 207
    ALREADY_REPORTED  = 208
    IM_USED           = 226

    # 300s
    MOVED           = 301
    FOUND           = 302
    SEE_OTHER       = 303
    NOT_MODIFIED    = 304
    TEMPORARY_REDIR = 307
    PERMANENT_REDIR = 308

    # 400s
    UNAUTORIZED         = 401
    PAYMENT_REQUIRED    = 402
    FORBIDDEN           = 403
    NOT_FOUND           = 404
    METHOD_NOT_ALLOWED  = 405
    NOT_ACCEPTABLE      = 406
    PROXY_AUTH_REQUIRED = 407
    REQUEST_TIMEOUT     = 408
    CONFLICT            = 409
    GONE                = 410
    LENGTH_REQUIRED     = 411
    PRECONDITION_FAILED = 412
    CONENT_TOO_LARGE    = 413
    URI_TOO_LONG        = 414
    UNSUPPORTED_MEDIA   = 415
    RANGE_INVALID       = 416
    EXPECTATION_FAIL    = 417
    IM_A_TEAPOT         = 418
    MISDIRECTED         = 421
    TOO_EARLY           = 425
    UPGRADE_REQUIRED    = 426
    PRECONDITION_REQUIRED = 428
    TOO_MANY_REQUESTS   = 429
    HEADERS_TOO_LARGE   = 431
    ILLEGAL             = 451

    # 400s WebDAV
    UNPROCESSABLE     = 422
    LOCKED            = 423
    FAILED_DEPENDENCY = 424

    # 500s
    NOT_IMPLEMENTED          = 501
    BAD_GATEWAY              = 502
    UNAVAILABLE              = 503
    GATEWAY_TIMEOUT          = 504
    UNSUPPORTED_HTTP_VERSION = 505
    VARIANT_NEGOTIATES       = 506
    NOT_EXTENDED             = 510
    NETWORK_AUTH_REQUIRED    = 511
        
    # 500s WebDAV
    INSUFFICIENT_STORAGE = 507
    LOOP_DETECTED        = 508

    @staticmethod
    def ClientErrors() -> Set["ResponseStatus"]:
        return {status for status in set(ResponseStatus) if status in range(400, 499)}

    @staticmethod
    def ServerErrors() -> Set["ResponseStatus"]:
        return {status for status in set(ResponseStatus) if status in range(500, 599)}

    def __str__(self):
        """Stringify function for ResponseStatus objects.

        :return: Simple string version of the name of a ResponseStatus
        :rtype: _type_
        """
        return self.name
