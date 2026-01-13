from __future__ import annotations
import logging
import threading
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Collection, List, Optional, Any

from clickzetta_ingestion.bulkload.bulkload_context import BulkLoadContext
from clickzetta_ingestion.bulkload.bulkload_conf import BulkLoadConf, BulkLoadFileConf
from clickzetta_ingestion.bulkload.bulkload_stats import BulkLoadStats
from clickzetta_ingestion.bulkload.bulkload_writer import BulkLoadWriter
from clickzetta_ingestion.bulkload.storage import Format
from clickzetta_ingestion.bulkload.storage.load_options import LoadOptions
from clickzetta_ingestion.bulkload.storage.output_format import OutputFormat
from clickzetta_ingestion.bulkload.table_parser import BulkLoadTable

InputT = TypeVar('InputT')
CommT = TypeVar('CommT')

logger = logging.getLogger(__name__)


class AbstractBulkLoadWriter(BulkLoadWriter[InputT, CommT], ABC, Generic[InputT, CommT]):
    """Abstract base class for BulkLoad writers."""

    def __init__(self, context: BulkLoadContext, conf: BulkLoadConf, table: BulkLoadTable = None):
        self.context = context
        self.conf = conf
        self.table = table
        self._initialized = False

        self._committables: List[CommT] = []
        self._output_format: Optional[OutputFormat[InputT]] = None
        self._lock = threading.RLock()

    def open(self):
        """Open the writer."""
        with self._lock:
            if self._initialized:
                return

            if self.table is None:
                self.table = self.get_target_table()

            self._committables = []

            # Initialize output format based on configuration
            self._output_format = self._create_output_format()
            if self._output_format:
                self._output_format.open()

            self._initialized = True

        logger.info(f"BulkLoadWriter {self.context.stream_id} partitionId {self.context.partition_id} "
                    f"{self.context.schema_name} {self.context.table_name} open success.")

    def _create_output_format(self):
        """Create output format for writing data."""
        from clickzetta_ingestion.bulkload.storage.output_format import FileSplitOutputFormat

        # Build load options from configuration
        load_options = LoadOptions(
            format_type=Format[self.conf.get_load_format().upper()] if self.conf.get_load_format() else Format.PARQUET,
            uri=self.conf.get_load_uri(),
            file_name_prefix=self.conf.get_load_prefix() or 'part',
            max_row_count=self.conf.get_max_row_count() or 100000,
            max_file_size=self.conf.get_max_file_size() or (128 * 1024 * 1024),  # 128MB default
            properties=self.conf.get_properties() or {}
        )

        # Create FileSplitOutputFormat
        return FileSplitOutputFormat(
            partition_id=self.context.partition_id,
            load_options=load_options,
            storage_writer_factory_function=self.get_storage_writer_factory_function(),
            next_file_caller=self._get_next_committable
        )

    def _get_next_committable(self, request):
        """Get next committable from handler."""
        from clickzetta_ingestion.bulkload.storage.output_format import FileConf

        # Convert FileConf.Request to BulkLoadFileConf.Request
        bulk_request = BulkLoadFileConf.Request(
            partition=request.partition(),
            uri=request.uri(),
            base_path=request.base_path(),
            prefix=request.prefix(),
            format_name=request.format()
        )

        # Get response from handler
        bulk_response = self.generate_next_committable(bulk_request)

        # Store committable
        if bulk_response.committable():
            self._committables.append(bulk_response.committable())

        # Convert to FileConf.Response
        return FileConf.Response(
            path=bulk_response.path,
            file_properties=bulk_response.file_properties,
            committable_obj=bulk_response.committable()
        )

    @abstractmethod
    def get_target_table(self):
        """Get the target table."""
        pass

    @abstractmethod
    def get_storage_writer_factory_function(self):
        """Get storage writer factory function."""
        pass

    @abstractmethod
    def generate_next_committable(self, request: BulkLoadFileConf.Request) -> BulkLoadFileConf.Response[CommT]:
        """Generate next committable."""
        pass

    @abstractmethod
    def create_input_with_table(self, table) -> InputT:
        """Create input with table."""
        pass

    def get_stream_id(self) -> str:
        """Get stream ID."""
        return self.context.stream_id

    def get_partition_id(self) -> int:
        """Get partition ID."""
        return self.context.partition_id

    def get_table(self):
        """Get table."""
        return self.table

    def create_input(self) -> InputT:
        """Create input object."""
        return self.create_input_with_table(self.table)

    def write(self, obj: InputT):
        """Write object."""
        if not self._initialized:
            raise RuntimeError("Writer not opened")
        if self._output_format:
            # Fill static partition values before writing
            # This ensures partition_specs values cannot be overridden by user set_value() calls
            obj = self._fill_static_partition_values(obj)
            self._output_format.write(obj)

    def _fill_static_partition_values(self, obj: InputT) -> InputT:
        """
        Fill static partition values into the object before writing.
        This method overrides any user-provided values for partition columns
        with the values from partition_specs.

        Args:
            obj: Input object (dict or IcebergRow)

        Returns:
            Modified object with static partition values filled
        """
        if not self.table:
            return obj

        partition_keys = self.table.get_partition_key_names()
        partition_values = self.table.get_partition_spec_values()

        if not partition_keys or not partition_values:
            return obj

        # Handle dict objects (V1 API uses dict)
        if isinstance(obj, dict):
            for i in range(min(len(partition_keys), len(partition_values))):
                partition_key = partition_keys[i]
                partition_value = partition_values[i]

                if partition_value is not None:
                    # Warn if user tried to override partition value
                    if partition_key in obj and obj[partition_key] != partition_value:
                        logger.warning(
                            f"Overriding user-provided value for partition column '{partition_key}' "
                            f"(user value: {obj[partition_key]}) with static partition value from "
                            f"partition_specs: {partition_value}"
                        )
                    # Override with static partition value
                    obj[partition_key] = partition_value

        # Handle IcebergRow objects (V2 direct API)
        elif hasattr(obj, 'set_value'):
            # Fallback: use regular set_value for IcebergRow-like objects
            for i in range(min(len(partition_keys), len(partition_values))):
                partition_key = partition_keys[i]
                partition_value = partition_values[i]

                if partition_value is not None:
                    # Check if value differs and warn
                    if hasattr(obj, 'get_value'):
                        current_value = obj.get_value(partition_key)
                        if current_value is not None and current_value != partition_value:
                            logger.warning(
                                f"Overriding user-provided value for partition column '{partition_key}' "
                                f"(user value: {current_value}) with static partition value from "
                                f"partition_specs: {partition_value}"
                            )
                    obj.set_value(partition_key, partition_value)

        return obj

    def flush(self):
        """Flush pending writes."""
        if self._output_format:
            self._output_format.flush()

    def stats(self) -> BulkLoadStats:
        """Get statistics."""
        if self._output_format:
            return BulkLoadStats(self._output_format.stats())
        return BulkLoadStats()

    def get_committables(self) -> Collection[CommT]:
        """Get committables."""
        return self._committables

    def close(self, wait_time_ms: int = 0):
        """Close the writer."""
        logger.info(f"BulkLoadWriter {self.context.stream_id} partitionId {self.context.partition_id} "
                    f"{self.context.schema_name} {self.context.table_name} is closing...")

        with self._lock:
            if not self._initialized:
                logger.info(f"BulkLoadWriter {self.context.stream_id} partitionId {self.context.partition_id} "
                            f"{self.context.schema_name} {self.context.table_name} already closed.")
                return
            self._initialized = False

        if self._output_format:
            try:
                self._output_format.close()
            except Exception:
                pass

        logger.info(f"BulkLoadWriter {self.context.stream_id} partitionId {self.context.partition_id} "
                    f"{self.context.schema_name} {self.context.table_name} close success.")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
