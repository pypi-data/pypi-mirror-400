from enum import Enum


class ErrorCode(Enum):
    """
    Unified error code definition.
    Code range:
        1xxx — System errors
        2xxx — Network / HTTP errors
        3xxx — Database errors
        4xxx — Authentication / permission errors
        5xxx — Input / validation errors
        6xxx — Business logic errors
        7xxx — File / IO errors
        8xxx — Third-party API errors
        9xxx — General errors
    """

    # ----------------------------------------------------------------------------------------------
    # 1xxx — System errors
    # ----------------------------------------------------------------------------------------------
    SYSTEM_ERROR = (1000, "Unknown system error")  # Generic / unknown system failure
    SYSTEM_BUSY = (1001, "System busy, try again")  # Server under heavy load
    INTERNAL_ERROR = (1002, "Internal server error")  # Unhandled server exception
    SYSTEM_TIMEOUT = (1003, "System timeout")  # Global timeout
    RESOURCE_EXCEEDED = (1004, "Resource limit exceeded")  # Memory/CPU limit reached
    CONFIG_ERROR = (1005, "Configuration error")  # Invalid settings or missing config
    ENV_MISSING = (1006, "Environment variable missing")  # Missing env variable
    TASK_FAILED = (1007, "Task execution failed")  # Background task failed
    WORKER_ERROR = (1008, "Worker exception")  # Worker/cron error
    DEPENDENCY_FAILURE = (1009, "Dependency failure")  # Internal dependency not available

    # ----------------------------------------------------------------------------------------------
    # 2xxx — Network / HTTP errors
    # ----------------------------------------------------------------------------------------------
    NETWORK_ERROR = (2000, "Unknown network error")  # General network error
    NETWORK_UNREACHABLE = (2001, "Network unreachable")  # No network route
    DNS_ERROR = (2002, "DNS resolution failed")  # Domain lookup error
    CONNECT_TIMEOUT = (2003, "Connection timeout")  # Cannot connect to remote host
    READ_TIMEOUT = (2004, "Read timeout")  # Response too slow
    HTTP_ERROR = (2005, "HTTP request error")  # Generic HTTP failure
    INVALID_URL = (2006, "Invalid URL")  # Malformed URL
    TOO_MANY_REDIRECTS = (2007, "Too many redirects")  # Infinite redirect loop
    SSL_ERROR = (2008, "SSL verification failed")  # Certificate failure
    PROXY_ERROR = (2009, "Proxy error")  # Proxy malfunction
    REMOTE_UNAVAILABLE = (2010, "Remote service unavailable")  # Remote host not responding
    RATE_LIMITED = (2011, "Network rate limit reached")  # Server throttling

    # ----------------------------------------------------------------------------------------------
    # 3xxx — Database errors
    # ----------------------------------------------------------------------------------------------
    DB_ERROR = (3000, "Unknown database error")  # Generic DB error
    DB_CONNECT_FAIL = (3001, "Database connection failed")  # Cannot connect
    DB_TIMEOUT = (3002, "Database timeout")  # Slow query
    DB_SYNTAX_ERROR = (3003, "SQL syntax error")  # Invalid SQL
    DB_TRANSACTION_FAIL = (3004, "Transaction failed")  # Commit/rollback error
    DB_NOT_FOUND = (3005, "Record not found")  # Query returned no rows
    DB_DUPLICATE = (3006, "Duplicate record")  # Unique constraint failed
    DB_CONSTRAINT = (3007, "Constraint violation")  # FK/PK constraint failed
    DB_TABLE_MISSING = (3008, "Table not found")  # Missing table
    DB_MAPPING_ERROR = (3009, "ORM mapping error")  # SQLAlchemy mapping failure
    DB_LOCKED = (3010, "Database locked")  # Database locked (SQLite)
    DB_PK_CONFLICT = (3011, "Primary key conflict")  # PK duplication

    # ----------------------------------------------------------------------------------------------
    # 4xxx — Authentication / permission errors
    # ----------------------------------------------------------------------------------------------
    AUTH_ERROR = (4000, "Authentication error")  # Generic auth error
    UNAUTHORIZED = (4001, "Unauthorized")  # Not logged in
    FORBIDDEN = (4002, "Forbidden")  # No permission
    TOKEN_MISSING = (4003, "Token missing")  # No token provided
    TOKEN_EXPIRED = (4004, "Token expired")  # Token expired
    TOKEN_INVALID = (4005, "Token invalid")  # Invalid signature/format
    PERMISSION_DENIED = (4006, "Permission denied")  # Lacking access rights
    USER_NOT_FOUND = (4007, "User not found")  # Username not found
    PASSWORD_INCORRECT = (4008, "Password incorrect")  # Wrong password
    SESSION_EXPIRED = (4009, "Session expired")  # Session timeout
    LOGIN_REQUIRED = (4010, "Login required")  # Must login

    # ----------------------------------------------------------------------------------------------
    # 5xxx — Input / validation errors
    # ----------------------------------------------------------------------------------------------
    VALIDATION_ERROR = (5000, "Validation error")  # Generic validation error
    INVALID_PARAM = (5001, "Invalid parameter")  # Value incorrect
    MISSING_PARAM = (5002, "Missing parameter")  # Required param missing
    INVALID_TYPE = (5003, "Invalid type")  # Wrong data type
    OUT_OF_RANGE = (5004, "Value out of range")  # Too large / too small
    INVALID_FORMAT = (5005, "Invalid format")  # e.g., phone/email
    EMPTY_DATA = (5006, "Empty data")  # No data
    REQUIRED_FIELD = (5007, "Required field missing")  # Missing required field
    JSON_PARSE_ERROR = (5008, "JSON parse error")  # Invalid JSON
    UNSUPPORTED_VALUE = (5009, "Unsupported value")  # Value not allowed
    DATA_CONFLICT = (5010, "Data conflict")  # Conflicting values

    # ----------------------------------------------------------------------------------------------
    # 6xxx — Business logic errors
    # ----------------------------------------------------------------------------------------------
    BUSINESS_ERROR = (6000, "Business logic error")  # Generic business error
    OP_NOT_ALLOWED = (6001, "Operation not allowed")  # Operation forbidden
    INSUFFICIENT_BALANCE = (6002, "Insufficient balance")
    ALREADY_EXISTS = (6003, "Already exists")
    DEPENDENCY_NOT_READY = (6004, "Dependency not ready")
    INVALID_STATE = (6005, "Invalid state")
    PERMISSION_LIMIT = (6006, "Permission limitation")
    CONCURRENT_CONFLICT = (6007, "Concurrent update conflict")
    BUSINESS_RATE_LIMIT = (6008, "Rate limit exceeded")
    DATA_UNAVAILABLE = (6009, "Data unavailable")
    OPERATION_FAILED = (6010, "Operation failed")

    # ----------------------------------------------------------------------------------------------
    # 7xxx — File / IO errors
    # ----------------------------------------------------------------------------------------------
    FILE_ERROR = (7000, "File error")  # Generic file error
    FILE_NOT_FOUND = (7001, "File not found")
    FILE_PERMISSION = (7002, "Permission denied")
    FILE_READ_ERROR = (7003, "File read error")
    FILE_WRITE_ERROR = (7004, "File write error")
    PATH_NOT_EXIST = (7005, "Path does not exist")
    DISK_FULL = (7006, "Disk full")
    INVALID_FILE_FORMAT = (7007, "Invalid file format")
    FILE_ENCODING_ERROR = (7008, "File encoding error")
    FILE_LOCKED = (7009, "File locked")
    DIR_NOT_WRITABLE = (7010, "Directory not writable")

    # ----------------------------------------------------------------------------------------------
    # 8xxx — Third-party API errors
    # ----------------------------------------------------------------------------------------------
    API_ERROR = (8000, "Third-party API error")  # Generic API error
    API_AUTH_FAIL = (8001, "API authentication failed")
    API_QUOTA_EXCEEDED = (8002, "API quota exceeded")
    API_INVALID_RESPONSE = (8003, "API response invalid")
    API_TIMEOUT = (8004, "API timeout")
    API_RATE_LIMIT = (8005, "API rate limited")
    API_NOT_FOUND = (8006, "API resource not found")
    API_BUSINESS_ERROR = (8007, "Third-party business error")
    API_SCHEMA_ERROR = (8008, "API schema mismatch")
    API_MAINTENANCE = (8009, "API under maintenance")
    API_PERMISSION_DENIED = (8010, "API permission denied")

    # ----------------------------------------------------------------------------------------------
    # 9xxx — General / utility errors
    # ----------------------------------------------------------------------------------------------
    UNKNOWN_ERROR = (9000, "Unknown error")
    CANCELLED = (9001, "Operation cancelled")
    RETRY_LATER = (9002, "Retry later")
    NOT_IMPLEMENTED = (9003, "Not implemented")
    DEPRECATED = (9004, "Deprecated API")
    DATA_FORMAT_ERROR = (9005, "Data format error")
    TIMEOUT = (9006, "Operation timeout")
    SERVICE_UNAVAILABLE = (9007, "Service unavailable")
    INVALID_TRANSITION = (9008, "Invalid state transition")
    PARAM_MISMATCH = (9009, "Parameter mismatch")
    UNSAFE_OPERATION = (9010, "Unsafe operation blocked")

    # ----------------------------------------------------------------------------------------------
    # helper methods
    # ----------------------------------------------------------------------------------------------
    def code(self) -> int:
        """Return error code."""
        return self.value[0]

    def message(self) -> str:
        """Return error message."""
        return self.value[1]


if __name__ == "__main__":
    print(ErrorCode.UNKNOWN_ERROR)
    print(ErrorCode.UNKNOWN_ERROR.code())
    print(ErrorCode.UNKNOWN_ERROR.message())
