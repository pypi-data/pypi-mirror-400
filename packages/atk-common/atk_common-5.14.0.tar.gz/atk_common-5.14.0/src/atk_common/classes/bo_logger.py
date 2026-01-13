
import os
import json
import sys
import threading
from typing import Optional, Union
from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import get_current_span
from atk_common.interfaces import ILogger
from atk_common.enums import LogLevel
from atk_common.utils.datetime_utils import get_utc_iso_date_time
from atk_common.utils.str_utils import parse_component_name

class BoLogger(ILogger):
    _write_lock = threading.Lock()  # process-local lock for atomic writes

    def __init__(self, log_level: LogLevel, component, version):
        self.log_level = log_level or LogLevel.INFO
        self.component = parse_component_name(component)
        self.version = version

    def _get_trace_context(self):
        span = get_current_span()
        sc = span.get_span_context() if span else None
        if sc and sc.is_valid:
            trace_id = f"{sc.trace_id:032x}"
            span_id  = f"{sc.span_id:016x}"
            return {
                "trace_id": trace_id,
                "span_id": span_id,
                "traceparent": f"00-{trace_id}-{span_id}-01",
            }
        return {"trace_id": None, "span_id": None, "traceparent": None}

    def _create_log_json(self, timestamp, level: LogLevel, message: str):
        log_entry = {
            "timestamp": timestamp,
            "level": level.name,
            "message": message,
            "component": self.component,
            "version": self.version,
            "pid": os.getpid(),
            "thread": threading.current_thread().name,
        }
        log_entry.update(self._get_trace_context())
        return log_entry

    def _emit(self, payload: dict):
        line = json.dumps(payload, separators=(",", ":"))
        with self._write_lock:
            sys.stdout.write(line + "\n")
            sys.stdout.flush()

    def _log(self, level: LogLevel, message: str, item_id: Optional[str] = None):
        if level.value < self.log_level.value:
            return
        if item_id is not None:
            sid = str(item_id).strip()
            if sid:
                message = f"{message}, {sid}"
        ts = str(get_utc_iso_date_time())
        self._emit(self._create_log_json(ts, level, message))

    def debug(self, message: str, item_id: Optional[str] = None):
        self._log(LogLevel.DEBUG, message, item_id)

    def info(self, message: str, item_id: Optional[str] = None):
        self._log(LogLevel.INFO, message, item_id)

    def warning(self, message: str, item_id: Optional[str] = None):
        self._log(LogLevel.WARNING, message, item_id)

    def error(self, message: str, item_id: Optional[str] = None):
        self._log(LogLevel.ERROR, message, item_id)

    def set_level(self, log_level: LogLevel):
        self.log_level = log_level

    def get_level(self):
        return self.log_level
