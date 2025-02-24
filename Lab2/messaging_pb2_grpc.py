# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import messaging_pb2 as messaging__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in messaging_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class RoverServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetMap = channel.unary_unary(
                '/messaging.RoverService/GetMap',
                request_serializer=messaging__pb2.Null.SerializeToString,
                response_deserializer=messaging__pb2.MapData.FromString,
                _registered_method=True)
        self.GetCommandStream = channel.unary_stream(
                '/messaging.RoverService/GetCommandStream',
                request_serializer=messaging__pb2.CommandRequest.SerializeToString,
                response_deserializer=messaging__pb2.Command.FromString,
                _registered_method=True)
        self.GetMineSerialNumber = channel.unary_unary(
                '/messaging.RoverService/GetMineSerialNumber',
                request_serializer=messaging__pb2.Null.SerializeToString,
                response_deserializer=messaging__pb2.Serial.FromString,
                _registered_method=True)
        self.ReportCommandExecutionStatus = channel.unary_unary(
                '/messaging.RoverService/ReportCommandExecutionStatus',
                request_serializer=messaging__pb2.Status.SerializeToString,
                response_deserializer=messaging__pb2.Null.FromString,
                _registered_method=True)
        self.ShareMinePIN = channel.unary_unary(
                '/messaging.RoverService/ShareMinePIN',
                request_serializer=messaging__pb2.PIN.SerializeToString,
                response_deserializer=messaging__pb2.Null.FromString,
                _registered_method=True)


class RoverServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetMap(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCommandStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMineSerialNumber(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReportCommandExecutionStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ShareMinePIN(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RoverServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetMap': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMap,
                    request_deserializer=messaging__pb2.Null.FromString,
                    response_serializer=messaging__pb2.MapData.SerializeToString,
            ),
            'GetCommandStream': grpc.unary_stream_rpc_method_handler(
                    servicer.GetCommandStream,
                    request_deserializer=messaging__pb2.CommandRequest.FromString,
                    response_serializer=messaging__pb2.Command.SerializeToString,
            ),
            'GetMineSerialNumber': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMineSerialNumber,
                    request_deserializer=messaging__pb2.Null.FromString,
                    response_serializer=messaging__pb2.Serial.SerializeToString,
            ),
            'ReportCommandExecutionStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.ReportCommandExecutionStatus,
                    request_deserializer=messaging__pb2.Status.FromString,
                    response_serializer=messaging__pb2.Null.SerializeToString,
            ),
            'ShareMinePIN': grpc.unary_unary_rpc_method_handler(
                    servicer.ShareMinePIN,
                    request_deserializer=messaging__pb2.PIN.FromString,
                    response_serializer=messaging__pb2.Null.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'messaging.RoverService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('messaging.RoverService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class RoverService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetMap(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/messaging.RoverService/GetMap',
            messaging__pb2.Null.SerializeToString,
            messaging__pb2.MapData.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetCommandStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/messaging.RoverService/GetCommandStream',
            messaging__pb2.CommandRequest.SerializeToString,
            messaging__pb2.Command.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetMineSerialNumber(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/messaging.RoverService/GetMineSerialNumber',
            messaging__pb2.Null.SerializeToString,
            messaging__pb2.Serial.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReportCommandExecutionStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/messaging.RoverService/ReportCommandExecutionStatus',
            messaging__pb2.Status.SerializeToString,
            messaging__pb2.Null.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ShareMinePIN(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/messaging.RoverService/ShareMinePIN',
            messaging__pb2.PIN.SerializeToString,
            messaging__pb2.Null.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
