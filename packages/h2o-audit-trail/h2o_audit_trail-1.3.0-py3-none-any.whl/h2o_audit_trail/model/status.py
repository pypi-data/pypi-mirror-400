from dataclasses import dataclass

from h2o_audit_trail.gen.model.audittrailv1_status import Audittrailv1Status


@dataclass
class Status:
    """
    Status of the audit request.
    """

    code: int
    """
    Status code of the audit request.
    Should be an enum value of google.rpc.Code.
    """

    message: str = ""
    """Error message of the audit request."""


def status_to_api_status(status: Status) -> Audittrailv1Status:
    return Audittrailv1Status(
        code=status.code,
        message=status.message,
    )


def status_from_api_status(api_status: Audittrailv1Status) -> Status:
    return Status(
        code=api_status.code,
        message=api_status.message,
    )

