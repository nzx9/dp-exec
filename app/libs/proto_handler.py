from proto import usage_pb2, usage_pb2_grpc
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.duration_pb2 import Duration
import grpc


class ResourceUsageManager:
    Type = usage_pb2.CreateUsageRequest.Type
    Section = usage_pb2.CreateUsageRequest.Section
    Action = usage_pb2.GetUsageRequest.Action
    Duration = usage_pb2.google_dot_protobuf_dot_duration__pb2.Duration
    Timestamp = usage_pb2.google_dot_protobuf_dot_timestamp__pb2.Timestamp
    user = None

    def __init__(self, user_id: str):
        self.user = user_id

    def __str__(self):
        return f"""
        ResourceUsage(user: {self.user})
        """

    def create_usage_proto(
        self,
        key_associated: str,
        req_url: str,
        section: Section,
        type: Type,
        start_ts: datetime,
        end_ts: datetime,
        cpu_time: Duration = 0,
        gpu_time: Duration = 0,
        sys_mem: float = 0.0,
        gpu_mem: float = 0.0,
    ):
        _start_ts = Timestamp()
        _start_ts.FromDatetime(start_ts)

        _end_ts = Timestamp()
        _end_ts.FromDatetime(end_ts)

        _cpu_time = Duration()
        _cpu_time.FromTimedelta(cpu_time)

        _gpu_time = Duration()
        _gpu_time.FromNanoseconds(gpu_time)

        cur = usage_pb2.CreateUsageRequest()
        cur.user = self.user
        cur.key_associated = key_associated
        cur.req_url = req_url
        cur.section = section
        cur.type = type
        cur.start_ts.CopyFrom(_start_ts)
        cur.end_ts.CopyFrom(_end_ts)
        cur.cpu_time.CopyFrom(_cpu_time)
        cur.gpu_time.CopyFrom(_gpu_time)
        cur.sys_mem = sys_mem
        cur.gpu_mem = gpu_mem
        return cur

    def get_usage_proto(
        self,
        start: str | None = None,
        end: str | None = None,
        action: Action = 0,
        value1: str | None = None,
        value2: str | None = None,
    ):
        cur = usage_pb2.GetUsageRequest()
        if start is None:
            start = ""
        if end is None:
            end = ""
        if value1 is None:
            value1 = ""
        if value2 is None:
            value2 = ""
        cur.user = self.user
        cur.start = start
        cur.end = end
        cur.action = action
        cur.value1 = value1
        cur.value2 = value2
        return cur

    def log_usage(self, ip: str, port: str, cur):
        with grpc.insecure_channel(f"{ip}:{port}") as channel:
            client = usage_pb2_grpc.UsagerStub(channel)
            response = client.CreateUsage(cur)
            return response

    def retrive_usage(self, ip: str, port: str, cur):
        with grpc.insecure_channel(f"{ip}:{port}") as channel:
            client = usage_pb2_grpc.UsagerStub(channel)
            response = client.GetUsage(cur)
            return response
