import json
from typing import Optional, Union, Callable, Tuple, Any
from flask import Response
import requests
from http import HTTPStatus
from atk_common.enums import *
from atk_common.utils import *
from atk_common.interfaces import *
from opentelemetry import trace
from opentelemetry.propagate import extract, inject
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace import SpanKind
from werkzeug.exceptions import BadRequest
from atk_common.enums.api_error_type_enum import ApiErrorType
from atk_common.utils.http_utils import is_http_status_internal, is_http_status_ok
from atk_common.utils.internal_response_utils import is_response_http
from atk_common.classes.request_context import RequestContext

class HttpResponseHandler(IHttpResponseHandler):
    def __init__(self, logger: ILogger, error_handler: IErrorHandler, env_handler: IEnvHandler, my_tracer):
        self.error_handler = error_handler
        self.env_handler = env_handler
        self.logger = logger
        self.my_tracer = my_tracer
        self._timeout = 5.0

    def _get_url(self, key):
        url = self.env_handler.get_env_value(key)
        return url

    def _normalize_param_value(self, v):
        # Preserve multi-values and convert None -> "" so it becomes ?k=
        if isinstance(v, (list, tuple)):
            return [("" if x is None else x) for x in v]
        return ["" if v is None else v]

    def _build_params_from_query_list(self, query_list):
        # query_list is expected to be a dict
        params = {}
        for k, v in (query_list or {}).items():
            params[k] = self._normalize_param_value(v)
        return params

    def _resolve_send_as_and_payload(self, ctx: RequestContext) -> Tuple[str, Union[dict, bytes]]:
        """
        Decide whether to send as JSON or as raw bytes.
        Returns ('json'|'data', payload).
        """
        if isinstance(ctx.body, dict):
            return "json", ctx.body
        # bytes or anything else -> raw
        if isinstance(ctx.body, (bytes, bytearray)):
            return "data", bytes(ctx.body)
        # last resort: stringify to bytes
        return "data", (str(ctx.body).encode("utf-8") if ctx.body is not None else b"")

    def _convert_response_data(self, data):
        # Dict/list -> JSON string
        if isinstance(data, (dict, list)):
            return json.dumps(data)
        # String: try to normalize to JSON string, else return as-is
        if isinstance(data, str):
            try:
                return json.dumps(json.loads(data))
            except Exception:
                return data
        # Bytes or anything else: pass through
        return data
    
    def _ctx_from_http(self, request, body_arg: Optional[Union[dict, bytes]], accept_header: Optional[str]) -> RequestContext:
        headers = {k: v for k, v in request.headers.items()}
        params = request.args.to_dict(flat=False)
        # Decide body: prefer explicit arg; otherwise try request.json / raw
        if body_arg is not None:
            body = body_arg
        else:
            # Try JSON; if not JSON, fall back to raw bytes
            body = request.get_json(silent=True)
            if body is None:
                body = request.get_data()
        return RequestContext(
            headers=headers,
            params=params,
            body=body,
            accept=(accept_header if accept_header is not None else headers.get("Accept")),
            content_type=headers.get("Content-Type"),
        )

    def _ctx_from_amqp(self, body, message, accept_header: Optional[str], content_type_override: Optional[str] = None,) -> RequestContext:
        # 'body' is whatever your Kombu producer sent (bytes or dict)
        headers = dict(getattr(message, "headers", {}) or {})
        return RequestContext(
            headers=headers,
            params={},
            body=body,
            accept=accept_header,
            content_type=content_type_override or headers.get("content-type") or headers.get("Content-Type"),
        )

    # If response['status'] == 0 (OK, http status = 200): create Response and return response['responseMsg']   
    # If http status == 500: 
    #   If response['status'] == 1 (HTTP): resend received error entity
    #   If response['status'] == 2 (INTERNAL): create new error entity and return as response
    # If http status other value: create new error entity and return as response
    def http_response(self, method, fn_response):
        resp = fn_response or {}
        status_code = resp.get("statusCode")
        body = resp.get("responseMsg")
        mimetype = resp.get("contentType") or "application/json"
        headers = resp.get("httpHeaders") or {}
        api_error_type = resp.get("apiErrorType")
        self.logger.debug(f"http_response: method={method}, statusCode={status_code}")

        if is_http_status_ok(status_code):
            return Response(
                response=self._convert_response_data(body),
                status=HTTPStatus.OK,
                mimetype=mimetype,
                headers=headers,
            )
        if api_error_type is None:
            api_error_type = ApiErrorType.INTERNAL
        if is_http_status_internal(status_code):
            if is_response_http(resp):
                return self.error_handler.resend_error_entity(body)
            return self.error_handler.get_error_entity(body, method, api_error_type, status_code)
        return self.error_handler.get_error_entity(body, method, api_error_type, status_code)

    # Wrapper that opens a span and returns a Flask Response
    def http_handler(
            self, request, 
            endpoint: str, 
            fn: Callable[..., dict], 
            *,
            socketio: Optional[Any] = None,):
        ctx = extract(request.headers)
        with self.my_tracer.start_as_current_span(endpoint, context=ctx) as span:
            try:
                if socketio is None:
                    payload = fn(request, endpoint)
                else:
                    payload = fn(request, endpoint, socketio=socketio)
                return self.http_response(endpoint, payload)
            except BadRequest as br:
                span.record_exception(br)
                span.set_status(Status(StatusCode.ERROR, str(br)))
                return self.http_response(endpoint, create_response(ResponseStatusType.INTERNAL, HTTPStatus.BAD_REQUEST, str(br)))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                return self.http_response(endpoint, create_response(ResponseStatusType.INTERNAL, HTTPStatus.INTERNAL_SERVER_ERROR, get_message(e)))
    
    # Helper to create response headers exposing x-* headers
    def _create_response_headers(self, api_response, extra_expose=("Content-Length",)):
        # Collect only custom x-* headers (case-insensitive)
        xhdrs = {k: v for k, v in api_response.headers.items()
                if k.lower().startswith("x-") and v is not None}

        # Add Access-Control-Expose-Headers only when we have X-* headers to expose
        if xhdrs:
            expose = list(dict.fromkeys(list(xhdrs.keys()) + list(extra_expose)))  # de-dup, keep order
            xhdrs["Access-Control-Expose-Headers"] = ", ".join(expose)

        return xhdrs
    
    def _first_param_as_kv(self, params) -> Optional[str]:
        """Return 'key=value' for the first param; supports list/tuple values; empty allowed."""
        for k, v in (params or {}).items():
            first_val = (v[0] if isinstance(v, (list, tuple)) and v else v)
            val_str = "" if first_val is None else str(first_val)
            return f"{k}={val_str}"
        return None

    # Core GET request logic used by both HTTP and AMQP clients
    def _client_get_http_request_core(
            self, 
            ctx: RequestContext,
            query_list, 
            url_key, 
            endpoint, 
            item_id: Optional[str] = None):
        try:
            params = ctx.params if query_list is None else self._build_params_from_query_list(query_list)

            item_id_str: Optional[str] = item_id if item_id is not None else self._first_param_as_kv(params)
                
            self.logger.info('IN: ' + endpoint, item_id_str)
        
            headers = {}
            inject(headers)
            if ctx.accept:
                headers["Accept"] = ctx.accept

            url = f"{self._get_url(url_key)}{endpoint}"
            resp = requests.get(url, headers=headers, params=params, timeout=self._timeout)            
            if not is_http_status_ok(resp.status_code):
                return self.error_handler.handle_error(resp, ResponseStatusType.HTTP)

            content_type = (resp.headers.get("Content-Type") or "").lower()

            # JSON
            if "application/json" in content_type:
                try:
                    payload = resp.json()
                except ValueError:
                    payload = resp.text  # malformed json -> return text
                self.logger.info("OUT: " + endpoint, item_id_str)
                return create_response(ResponseStatusType.OK, resp.status_code, payload)

            # Text-like (html, plain, xml, csv, etc.)
            if content_type.startswith("text/") or "xml" in content_type or "csv" in content_type:
                self.logger.info("OUT: " + endpoint, item_id_str)
                return create_response(ResponseStatusType.OK, resp.status_code, resp.text)

            # Binary (pdf, images, octet-stream, etc.)
            forward_headers = {}
            for h in ("Content-Type", "Content-Disposition", "Cache-Control"):
                if h in resp.headers:
                    forward_headers[h] = resp.headers[h]
            forward_headers.update(self._create_response_headers(resp))                    

            self.logger.info("OUT: " + endpoint, item_id_str)
            return create_response(
                ResponseStatusType.OK,
                resp.status_code,
                resp.content,                        # bytes
                http_headers=forward_headers,
                content_type=resp.headers.get("Content-Type"),
            )
        except (Exception) as error:
            self.logger.error(get_message(error), item_id_str)
            return create_response(ResponseStatusType.INTERNAL, HTTPStatus.INTERNAL_SERVER_ERROR, get_message(error))

    # GET request via HTTP
    def client_get_http_request(
            self, 
            request, 
            query_list, 
            url_key, 
            endpoint, 
            item_id: Optional[str] = None,
            accept_header: Optional[str] = None):
        http_ctx = self._ctx_from_http(request, None, accept_header)
        return self._client_get_http_request_core(http_ctx, query_list, url_key, endpoint, item_id)

    # GET request via HTTP with tracing span
    def get_http_request(
            self, 
            request, 
            query_list, 
            url_key, 
            endpoint, 
            item_id: Optional[str] = None,
            accept_header: Optional[str] = None):
        ctx = extract(request.headers)
        with self.my_tracer.start_as_current_span(endpoint, context=ctx):
            upstream = self.client_get_http_request(
                request, query_list, url_key, endpoint, item_id, accept_header
            )
            return self.http_response(endpoint, upstream)

    # GET request via AMQP        
    def client_get_amqp_request(
            self, 
            message, 
            query_list, 
            url_key, 
            endpoint,
            item_id: Optional[str] = None,
            accept_header: Optional[str] = None):
        ctx = self._ctx_from_amqp(None, message, accept_header, None)
        return self._client_get_http_request_core(ctx, query_list, url_key, endpoint, item_id)

    def _derive_item_id_safe(
            self, 
            params,
            item_id: Optional[str]) -> Optional[str]:
        item_id_str: Optional[str] = None
        if item_id_str is None and item_id is not None:
            item_id_str = str(item_id)

        if item_id_str is None:
            item_id_str = self._first_param_as_kv(params)
        return item_id_str            

    def _client_post_http_request_core(
            self,
            ctx: RequestContext,
            query_list, 
            url_key, 
            endpoint, 
            item_id: Optional[str] = None,):
        try:
            params = self._build_params_from_query_list(query_list) if query_list is not None else ctx.params
                
            headers = {}
            inject(headers)  # propagate current context
            if ctx.accept:
                headers["Accept"] = ctx.accept

            # Decide body + how to send
            send_as, payload = self._resolve_send_as_and_payload(ctx)

            if send_as == "data" and ctx.content_type and "Content-Type" not in headers:
                headers["Content-Type"] = ctx.content_type

            item_id_str = self._derive_item_id_safe(params, item_id)

            self.logger.info('IN: ' + endpoint, item_id_str)

            url = f"{self._get_url(url_key)}{endpoint}"
            if send_as == "json":
                resp = requests.post(url, headers=headers, params=params, json=payload, timeout=self._timeout)
            else:
                resp = requests.post(url, headers=headers, params=params, data=payload, timeout=self._timeout)
            if not is_http_status_ok(resp.status_code):
                return self.error_handler.handle_error(resp, ResponseStatusType.HTTP)

            content_type = (resp.headers.get("Content-Type") or "").lower()

            # JSON
            if "application/json" in content_type:
                try:
                    payload = resp.json()
                except ValueError:
                    payload = resp.text  # malformed json -> return text
                self.logger.info("OUT: " + endpoint, item_id_str)
                return create_response(ResponseStatusType.OK, resp.status_code, payload)

            # Text-like (html, plain, xml, csv, etc.)
            if content_type.startswith("text/") or "xml" in content_type or "csv" in content_type:
                self.logger.info("OUT: " + endpoint, item_id_str)
                return create_response(ResponseStatusType.OK, resp.status_code, resp.text)

            # Binary (pdf, images, octet-stream, etc.)
            forward_headers = {}
            for h in ("Content-Type", "Content-Disposition", "Cache-Control"):
                if h in resp.headers:
                    forward_headers[h] = resp.headers[h]
            forward_headers.update(self._create_response_headers(resp))                    

            self.logger.info("OUT: " + endpoint, item_id_str)
            return create_response(
                ResponseStatusType.OK,
                resp.status_code,
                resp.content,                        # bytes
                http_headers=forward_headers,
                content_type=resp.headers.get("Content-Type"),
            )
        except (Exception) as error:
            self.logger.error(get_message(error), item_id_str)
            return create_response(ResponseStatusType.INTERNAL, HTTPStatus.INTERNAL_SERVER_ERROR, get_message(error))

    # POST request via HTTP handler
    def client_post_http_request(
            self,
            request,
            body: Optional[Union[dict, bytes]],
            query_list,
            url_key,
            endpoint,
            item_id: Optional[str] = None,
            accept_header: Optional[str] = None):
        ctx = self._ctx_from_http(request, body, accept_header=accept_header)
        return self._client_post_http_request_core(ctx, query_list, url_key, endpoint, item_id)

    # POST request via HTTP with tracing span
    def post_http_request(
            self, 
            request, 
            body, 
            query_list, 
            url_key, 
            endpoint, 
            item_id: Optional[str] = None,
            accept_header: Optional[str] = None):
        ctx = extract(request.headers)
        with self.my_tracer.start_as_current_span(endpoint, context=ctx):
            upstream = self.client_post_http_request(
                request, body, query_list, url_key, endpoint, item_id, accept_header
            )
            return self.http_response(endpoint, upstream)
            
    # POST request via HTTP handler
    def client_post_amqp_request(
            self,
            body,
            message,
            query_list,
            url_key,
            endpoint,
            item_id: Optional[str] = None,
            content_type: Optional[str] = None,
            accept_header: Optional[str] = None):
        ctx = self._ctx_from_amqp(body, message, accept_header=accept_header, content_type_override=content_type)
        return self._client_post_http_request_core(ctx, query_list, url_key, endpoint, item_id)
