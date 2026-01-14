from dataclasses import dataclass

from h2o_audit_trail.gen.model.googlerpc_status import GooglerpcStatus


@dataclass
class RPCStatus:
    """
    Representation of google.rpc.Status.
    """

    code: int
    """
    Status code of the request.
    Should be an enum value of google.rpc.Code.
    """

    message: str = ""
    """Error message of the request."""


def rpc_status_to_google_rpc_status(status: RPCStatus) -> GooglerpcStatus:
    return GooglerpcStatus(
        code=status.code,
        message=status.message,
    )


def rpc_status_from_google_rpc_status(google_rpc_status: GooglerpcStatus) -> RPCStatus:
    return RPCStatus(
        code=google_rpc_status.code,
        message=google_rpc_status.message,
    )
