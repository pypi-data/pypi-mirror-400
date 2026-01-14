"""add an operator extra link to the AlloyEcsRunTaskOperator via the Airflow plugin system."""
import logging
from datetime import datetime, timezone, timedelta
from typing import ClassVar


from airflow.models.taskinstancekey import TaskInstanceKey
from airflow.plugins_manager import AirflowPlugin
from airflow.models.baseoperator import BaseOperator
from airflow.models.baseoperatorlink import BaseOperatorLink
from airflow.utils.session import create_session
from airflow.models import TaskInstance


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


BASE_LOGZIO_LINK = (
    "https://app-eu.logz.io/#/dashboard/osd/discover/"
    "?_a=("
    "  columns:!(level,message,software_component),"
    "  filters:!("
    "    ("
    "      '$state':(store:appState),"
    "      meta:("
    "        alias:!n,"
    "        disabled:!f,"
    "        index:'logzioCustomerIndex*',"
    "        key:dag_run_id,"
    "        negate:!f,"
    "        params:(query:'{dag_run_id}'),"
    "        type:phrase"
    "      ),"
    "      query:("
    "        match_phrase:(dag_run_id:'{dag_run_id}')"
    "      )"
    "    ),"
    # "    ("
    # "      '$state':(store:appState),"
    # "      meta:("
    # "        alias:!n,"
    # "        disabled:!f,"
    # "        index:'logzioCustomerIndex*',"
    # "        key:attempt_no,"
    # "        negate:!f,"
    # "        params:(query:'{attempt_no}'),"
    # "        type:phrase"
    # "      ),"
    # "      query:("
    # "        match_phrase:(attempt_no:{attempt_no})"
    # "      )"
    # "    ),"
    "    ("
    "      '$state':(store:appState),"
    "      meta:("
    "        alias:!n,"
    "        disabled:!f,"
    "        index:'logzioCustomerIndex*',"
    "        key:task_id,"
    "        negate:!f,"
    "        params:(query:'{task_id}'),"
    "        type:phrase"
    "      ),"
    "      query:("
    "        match_phrase:(task_id:{task_id})"
    "      )"
    "    )"
    "  ),"
    "  index:'logzioCustomerIndex*',"
    "  interval:auto,"
    "  query:(language:lucene,query:''),"
    "  sort:!(!('@timestamp',asc))"
    ")&"
    "_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:{start_date},to:{end_date}))&"
    "accountIds=519784&"
    "switchToAccountId=519784".replace(" ", "")
)


def to_iso8601_with_milliseconds(dt: datetime, delta=None) -> str:
    """Convert datetime to ISO8601 format with milliseconds precision"""
    if delta:
        dt += delta
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class BaseAlloyLink(BaseOperatorLink):
    """Logz.io ECS Task link."""

    name: ClassVar[str]
    format_str: ClassVar[str]

    def get_task_instance_details(
        self,
        task_id: str,
        dag_id: str,
        run_id: str,
        map_index: int,
    ):
        with create_session() as session:
            task_instance = (
                session.query(TaskInstance)
                .filter(TaskInstance.task_id == task_id)
                .filter(TaskInstance.dag_id == dag_id)
                .filter(TaskInstance.run_id == run_id)
                .filter(TaskInstance.map_index == map_index)
                .order_by(TaskInstance.try_number.desc())  # type: ignore
                .first().__dict__
            )
            if task_instance:
                return task_instance
        return {}

    def format_link(self, **kwargs) -> str:
        """
        Format AWS Service Link
        Some AWS Service Link should require additional escaping
        in this case this method should be overridden.
        """
        try:
            return self.format_str.format(**kwargs)
        except KeyError:
            return ""

    def get_link(self, operator: BaseOperator, *, ti_key: TaskInstanceKey) -> str:
        ti = self.get_task_instance_details(
            task_id=ti_key.task_id,
            dag_id=ti_key.dag_id,
            run_id=ti_key.run_id,
            map_index=ti_key.map_index,
        )

        conf = {
            "dag_run_id": ti_key.run_id.replace("+", "%2B"),
            "task_id": ti_key.task_id,
            # "attempt_no": ti["_try_number"] if "_try_number" in ti and ti["_try_number"] else 1,
        }
        if "start_date" in ti and ti["start_date"]:
            # delta in order to account for logz.io lag
            start_date = to_iso8601_with_milliseconds(ti["start_date"])
            conf["start_date"] = f"'{start_date}'"
        else:
            conf["start_date"] = "now-14d"
        if "end_date" in ti and ti["end_date"]:
            # delta in order to account for logz.io lag
            end_date = to_iso8601_with_milliseconds(ti["end_date"], delta=timedelta(minutes=1))
            conf["end_date"] = f"'{end_date}'"
        else:
            conf["end_date"] = "now"
        return self.format_link(**conf) if conf else ""


class AlloyLogzioLink(BaseAlloyLink):
    name = "Logz.io"

    format_str = BASE_LOGZIO_LINK.format(
        start_date="{start_date}",
        end_date="{end_date}",
        dag_run_id="{dag_run_id}",
        task_id="{task_id}",
        # attempt_no="{attempt_no}",
    )

    def format_link(self, **kwargs) -> str:
        try:
            return self.format_str.format(**kwargs)
        except KeyError as e:
            logger.info(f"Error formatting link: {e}")
            return ""


class AlloyOperatorsPlugin(AirflowPlugin):
    """AlloyEcsRunTaskOperator plugin."""

    name = "alloy_logzio_operator_plugin"
    global_operator_extra_links = [
        AlloyLogzioLink(),
    ]
