import contextvars

# for audit logs
user_id = contextvars.ContextVar("user_id", default=None)
transaction_id = contextvars.ContextVar("transaction_id", default=None)

# file key during session
file_key = contextvars.ContextVar("file_key", default=None)

# for headers to enable tracing
token = contextvars.ContextVar("token", default=None)
request_id_header = contextvars.ContextVar("request_id_header", default=None)


# for schema for a tenant
schema = contextvars.ContextVar("schema", default=None)


def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {token.get()}",
        "x-request-id": request_id_header.get(),
    }
