
import contextvars

REQUEST_ID_HEADER = 'x-fc-request-id'
TRACE_ID_HEADER = 'X-Fc-Eagleeye-Traceid'
RPC_ID_HEADER = 'X-Fc-Eagleeye-Rpcid'
APP_NAME_HEADER = 'X-Fc-App-Name'


request_id_context = contextvars.ContextVar(REQUEST_ID_HEADER)
trace_id_context = contextvars.ContextVar(TRACE_ID_HEADER)
rpc_id_context = contextvars.ContextVar(RPC_ID_HEADER)

app_name_context = contextvars.ContextVar(APP_NAME_HEADER)
request_type_context = contextvars.ContextVar("requestType")

