from __future__ import (
    annotations,
)

import inspect
import logging
from dataclasses import dataclass

from fa_purity import Cmd, Coproduct, FrozenDict, Result, cast_exception
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import int_to_str
from fluidattacks_etl_utils.smash import right_map

from fluidattacks_gitlab_sdk._decoders import assert_single
from fluidattacks_gitlab_sdk._handlers import NotFound, handle_not_found
from fluidattacks_gitlab_sdk._http_client import (
    ClientFactory,
    Credentials,
    HttpJsonClient,
    RelativeEndpoint,
)
from fluidattacks_gitlab_sdk.ids import JobId, ProjectId

from ._decode import decode_job_obj
from .core import JobClient, JobObj

LOG = logging.getLogger(__name__)


def get_job(
    client: HttpJsonClient,
    project: ProjectId,
    job_id: JobId,
) -> Cmd[Result[JobObj, Coproduct[NotFound, Exception]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.value),
        "jobs",
        int_to_str(job_id.job_id.value),
    )
    msg = Cmd.wrap_impure(lambda: LOG.info("[API] get_job(%s, %s)", project, job_id))
    return msg + client.get(endpoint, FrozenDict({})).map(
        lambda r: r.alt(
            lambda e: e.map(handle_not_found, lambda e: Coproduct.inr(cast_exception(e))),
        )
        .bind(lambda v: assert_single(v).alt(Coproduct.inr))
        .bind(lambda v: decode_job_obj(v).alt(Coproduct.inr))
        .alt(
            lambda c: right_map(
                c,
                lambda e: cast_exception(
                    Bug.new(
                        "_get_job",
                        inspect.currentframe(),
                        e,
                        (),
                    ),
                ),
            ),
        ),
    )


def _from_client(client: HttpJsonClient) -> JobClient:
    return JobClient(lambda p, j: get_job(client, p, j))


@dataclass(frozen=True)
class JobClientFactory:
    @staticmethod
    def new(creds: Credentials) -> JobClient:
        return _from_client(ClientFactory.new(creds))
