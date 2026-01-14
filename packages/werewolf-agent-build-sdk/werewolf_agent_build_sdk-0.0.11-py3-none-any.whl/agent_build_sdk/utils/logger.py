import json
import logging
from logging import Formatter
from agent_build_sdk.utils.config import trace_id_context, rpc_id_context, TRACE_ID_HEADER, RPC_ID_HEADER, app_name_context, \
    request_type_context
import traceback


class JsonFormatter(Formatter):
    def __init__(self):
        super(JsonFormatter, self).__init__()

    def format(self, record):
        json_record = {}
        json_record["message"] = record.getMessage()
        if "req" in record.__dict__:
            json_record["req"] = record.__dict__["req"]
        if "res" in record.__dict__:
            json_record["res"] = record.__dict__["res"]
        if "trace_id" in record.__dict__:
            json_record["trace_id"] = record.__dict__["trace_id"]
        if record.levelno == logging.ERROR and record.exc_info:
            json_record["err"] = self.formatException(record.exc_info)
        json_record["trace_id"] = trace_id_context.get(TRACE_ID_HEADER)
        json_record["rpc_id"] = rpc_id_context.get(RPC_ID_HEADER)
        return json.dumps(json_record)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.trace_id = trace_id_context.get(TRACE_ID_HEADER)
        record.rpc_id = rpc_id_context.get(RPC_ID_HEADER)
        record.app_name = app_name_context.get("")
        record.request_type = request_type_context.get("")
        return super().format(record)


logger = logging.getLogger("agent.builder")
handler = logging.StreamHandler()
formatter = RequestFormatter(
    '%(asctime)s|%(levelname)s|%(filename)s|%(lineno)s|%(message)s')
handler.setFormatter(formatter)

logger.handlers = [handler]
logger.setLevel(logging.INFO)


class Log:
    def __init__(self, name):
        self.name = name

    def info(self, msg, *args):
        self.format_info_log(msg, args)

    def format_info_log(self, msg, *args):
        log_msg = msg.replace('\n', '2f2f2f') + '|' + '|'.join(str(arg).replace('\n', '2f2f2f') for arg in args)
        logger.info(log_msg)
        print(log_msg)

    def format_error_log(self, msg, *args):
        log_msg = msg.replace('\n', '2f2f2f') + '|' + '|'.join(str(arg).replace('\n', '2f2f2f') for arg in args)
        logger.error(log_msg)
        print(log_msg)


    def format_warn_log(self, msg, *args):
        log_msg = msg.replace('\n', '2f2f2f') + '|' + '|'.join(str(arg).replace('\n', '2f2f2f') for arg in args)
        logger.warn(log_msg)
        print(log_msg)


    def format_exception_log(self, msg):
        logger.error("EXCEPTION" + "|" + msg.replace('\n', '2f2f2f') + traceback.format_exc().replace("\n", "2f2f2f"))
        print(msg)

    def format_metric_log(self, msg, *args):
        log_msg = "METRIC_LOG" + "|" + msg.replace('\n', '2f2f2f') + '|' + '|'.join(str(arg) for arg in args)
        logger.info(log_msg)
        print(log_msg)
