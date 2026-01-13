import time
import typing

import pandas as pd
import pyarrow as pa
from kywy.client.data_loader import KawaDataLoader
from kywy.client.dsl import KawaColumn
from kywy.client.kawa_client import KawaClient

from .kawa_action_processor import ActionProcessor
from ...server.kawa_directory_manager import KawaDirectoryManager
from ...server.kawa_log_manager import get_kawa_logger
from ...server.kawa_metadata import Metadata


class PythonWorkflowProcessor(ActionProcessor):
    def __init__(self,
                 job_id: str,
                 dataset_count: int,
                 kawa_directory_manager: KawaDirectoryManager,
                 metadata: Metadata,
                 kawa_client: KawaClient,
                 datasource_id: typing.Optional[str],
                 input_data_source_map: typing.Dict[str, typing.Dict],
                 workflow_instance_id: str):
        self.job_id = job_id
        self.metadata = metadata
        self.dataset_count = dataset_count
        self.kawa_directory_manager: KawaDirectoryManager = kawa_directory_manager
        self.k: KawaClient = kawa_client
        self.datasource_id = datasource_id
        self.input_data_source_map = input_data_source_map
        self.workflow_instance_id = workflow_instance_id

    def retrieve_data(self) -> list[pd.DataFrame]:
        dataframes: list[pd.DataFrame] = []
        for dataset_index in range(0, self.dataset_count):
            data_source_id_with_mapping = self.input_data_source_map.get(str(dataset_index))
            if data_source_id_with_mapping:
                data_source_id = data_source_id_with_mapping.get('dataSourceId')
                data_source = self.k.entities.datasources().get_entity_by_id(data_source_id)
                data_source_indicator_mapping = data_source.get('workflowContext', {}).get('indicatorIdMappings', [])
                indicator_id_to_output_mapping = {indicatorIdMapping['indicatorId']: indicatorIdMapping['outputId']
                                                  for indicatorIdMapping in data_source_indicator_mapping}

                mapping = data_source_id_with_mapping.get('mapping')
                output_to_column_name = {
                    indicator_id_to_output_mapping.get(indicator['indicatorId'], indicator['indicatorId']):
                        indicator['displayInformation']['displayName'] for
                    indicator in data_source['indicators']}
                if isinstance(mapping, dict):
                    kawa_columns = [KawaColumn(column_name=output_to_column_name.get(source_name),
                                               column_alias=target_name) for target_name, source_name in
                                    mapping.items()]

                    compute_request = (self.k
                                       .datasource(datasource_id=data_source_id)
                                       .select(*kawa_columns)
                                       .no_limit())
                    if self.workflow_instance_id:
                        compute_request = (compute_request
                                           .workflow_instance_id(self.workflow_instance_id))

                    df = compute_request.compute()
                    dataframes.append(df)
                else:
                    dataframes.append(pd.DataFrame())

            else:
                arrow_table = self.kawa_directory_manager.read_table(self.job_id, dataset_index)
                dataframes.append(arrow_table.to_pandas())
        return dataframes

    def load(self, df: pd.DataFrame = pd.DataFrame(), json: str = '{}'):
        if self.datasource_id:
            self._load_in_datasource(df)
        else:
            arrow_table = pa.Table.from_pandas(df)
            self.kawa_directory_manager.write_output(self.job_id, arrow_table)

    def _load_in_datasource(self, df: pd.DataFrame = pd.DataFrame()):
        datasource = self.k.entities.datasources().get_entity_by_id(self.datasource_id)
        loading_mode = datasource.get('workflowContext', {}).get('loadingMode')
        if not loading_mode:
            raise Exception('Cannot find the loading mode for the datasource')
        if loading_mode != 'RESET_BEFORE_INSERT':
            raise Exception('Loading mode should be reset before insert')
        reset_before_insert = True

        try:
            start_time = time.time()
            get_kawa_logger().info(f'Start data loading (arrow streaming) for jobId: {self.job_id}')
            self._load_with_arrow_streaming(df, reset_before_insert)
            t = round(time.time() - start_time, 1)
            get_kawa_logger().info(f'End of data loading in {t} for jobId: {self.job_id}')
            return

        except Exception as e:
            get_kawa_logger().info(f'Error while data loading with arrow streaming: {e}')
            get_kawa_logger().info(f'Start data loading (with parquet), jobId: {self.job_id}')
            self._load_with_parquet(df, reset_before_insert=reset_before_insert)
            get_kawa_logger().info(f'End of data loading, jobId: {self.job_id}')

    def _load_with_arrow_streaming(self,
                                   df: pd.DataFrame,
                                   reset_before_insert: bool):
        table = pa.Table.from_pandas(df)
        data_loader = KawaDataLoader(
            self.k,
            df=None,
            arrow_table=table,
            datasource_name=None,
            datasource_id=self.datasource_id,
            workflow_instance_id=self.workflow_instance_id
        )
        data_loader.load_data(reset_before_insert=reset_before_insert,
                              job_id=self.job_id,
                              optimize_after_insert=False)

    def _load_with_parquet(self,
                           df: pd.DataFrame,
                           reset_before_insert: bool):
        data_loader = KawaDataLoader(
            self.k,
            df=df,
            datasource_name=None,
            datasource_id=self.datasource_id,
            workflow_instance_id=self.workflow_instance_id
        )
        data_loader.load_data(reset_before_insert=reset_before_insert,
                              job_id=self.job_id,
                              optimize_after_insert=False)

    def need_defined_outputs(self) -> bool:
        return self.metadata.outputs and True

    def data_source_id(self) -> typing.Optional[str]:
        if self.datasource_id:
            return self.datasource_id
