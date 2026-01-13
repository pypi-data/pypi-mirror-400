import pandas as pd

from .kawa_action_processor import ActionProcessor
from ...server.kawa_directory_manager import KawaDirectoryManager
from ...server.kawa_log_manager import get_kawa_logger


class PythonScriptWithJsonOutputProcessor(ActionProcessor):
    def __init__(self,
                 job_id: str,
                 kawa_directory_manager: KawaDirectoryManager):
        self.kawa_directory_manager: KawaDirectoryManager = kawa_directory_manager
        self.job_id: str = job_id

    def retrieve_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def load(self, df: pd.DataFrame = pd.DataFrame(), json: str = '{}'):
        get_kawa_logger().info(f'Start to dump json output for jobId: {self.job_id}')
        self.kawa_directory_manager.write_json_script_output(self.job_id, json)
        get_kawa_logger().info(f'End to dump json output for jobId: {self.job_id}')

    def need_defined_outputs(self) -> bool:
        return False

    def force_load_without_outputs(self) -> bool:
        return True
