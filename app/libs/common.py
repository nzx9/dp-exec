from fastapi import Request
from datetime import datetime, timedelta
from time import process_time_ns
from libs.proto_handler import ResourceUsageManager
import psutil
import zlib
from pydantic import ValidationError
import pandas as pd
import base64
import zlib
import io

def safe_get(var, key, default=None):
    return var.get(key, default) if var else default


def get_api_key(req: Request) -> str:
    return req.headers.get("X-Api-Key", None)


def usage_counter(func):
    def wrapper(*args, **kwargs):
        start_ts = datetime.now()
        ps_start = process_time_ns()
        start_mem = psutil.virtual_memory().used
        result = func(*args, **kwargs)
        end_mem = psutil.virtual_memory().used
        ps_end = process_time_ns()
        end_ts = datetime.now()
        try:
            ru_man = ResourceUsageManager(args[0].user.id)
            cur = ru_man.create_usage_proto(
                get_api_key(args[0].request),
                f"{args[0].request.client.host}:{args[0].request.client.port}",
                args[0].section,
                args[0].type,
                start_ts,
                end_ts,
                timedelta(microseconds=(ps_end - ps_start) / 1000),
                end_mem - start_mem,
            )
            response = ru_man.log_usage("127.0.0.1", 8080, cur)
            if not response.success:
                # return result
                raise Exception("Failed to log usage")
            print(response)
            return result
        except Exception as e:
            print(e)
            return result

    return wrapper


def compress(data: str):
    print(type(data.encode("utf-8")))
    # return data
    return zlib.compress(data.encode("utf-8"))


def decompress(data: bytes):
    return zlib.decompress(data).decode("utf-8")


def valid_hyper_params(HyperParamModel, hyper_params: dict, model_name: str):
    try:
        hyper_params = {} if hyper_params is None else hyper_params
        data = HyperParamModel(**hyper_params).dict()
        return (True, data, None, None)
    except ValidationError as e:
        return (False, None, f"Invalid hyper paramters for {model_name}", e.json())


def create_df_if_not_df(data):
    return pd.DataFrame(data) if type(data) != pd.DataFrame else data

def inp_handler(data, compressed):
    if(type(data) == str):
        try:
            dd = base64.b64decode(data)
            if(compressed):
                dd = zlib.decompress(dd)
                dd = base64.b64decode(dd)
            return pd.read_csv(io.BytesIO(dd))
        except Exception as e:
            error = "Make sure to use gzip. Also make sure to follow `Byte data -> base64 encode -> gzip -> base64 encode -> data to send` process" if compressed else "Make sure to follow `Byte data -> base64 encode -> data to send` process"
            # return MLError(error, {"reason": str(e)}).response()
            raise ValueError(error + ". Reason: " + str(e))
    else:
        return data