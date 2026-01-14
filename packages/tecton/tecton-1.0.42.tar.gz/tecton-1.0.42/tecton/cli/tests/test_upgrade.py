from datetime import timedelta
from pathlib import Path
from unittest import TestCase
from unittest import mock

from tecton import RedshiftConfig
from tecton import v09_compat
from tecton.cli.upgrade_utils import BatchFeatureViewGuidance
from tecton.cli.upgrade_utils import DataSourceGuidance
from tecton.cli.upgrade_utils import _get_imports_for_type
from tecton.types import Array
from tecton.types import Field
from tecton.types import Int64
from tecton.types import Map
from tecton.types import String
from tecton.types import Struct
from tecton.types import Timestamp
from tecton_core import conf


class TestUpgrade(TestCase):
    def mockPatch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def setUp(self) -> None:
        conf.set("TECTON_OFFLINE_RETRIEVAL_COMPUTE_MODE", "spark")
        self.mock_metadata_service = mock.MagicMock()
        self.mockPatch("tecton._internals.metadata_service.instance", return_value=self.mock_metadata_service)

        self.batch_source = v09_compat.BatchSource(
            name="redshift_ds", batch_config=RedshiftConfig(endpoint="test_uri", table="test_table")
        )
        self.entity = v09_compat.Entity(name="user", join_keys=["user_id"])

    def test_push_source(self):
        push_source = v09_compat.PushSource(
            name="PushSource",
            schema=[
                Field(name="content_keyword", dtype=String),
                Field(name="timestamp", dtype=Timestamp),
                Field(name="clicked", dtype=Int64),
            ],
        )

        push_source_guidance = DataSourceGuidance(push_source, str(Path()))._get_upgrade_guidance()
        self.assertEqual(len(push_source_guidance), 2)
        self.assertIn(
            "Replace `PushSource` with `StreamSource` and set `stream_config=PushConfig()", push_source_guidance[0]
        )
        self.assertIn("Update import from `tecton.v09_compat` to `tecton`.", push_source_guidance[1])

    def test_data_source(self):
        push_source_guidance = DataSourceGuidance(self.batch_source, str(Path()))._get_upgrade_guidance()
        self.assertEqual(len(push_source_guidance), 1)
        self.assertIn(
            "No code change needed - please manually update import from `tecton.v09_compat` to `tecton`.",
            push_source_guidance[0],
        )

    def test_filtered_sources(self):
        @v09_compat.batch_feature_view(
            sources=[
                v09_compat.FilteredSource(self.batch_source),
                self.batch_source,
                v09_compat.FilteredSource(self.batch_source, start_time_offset=timedelta(days=-10)),
                # more than 100 years of lookback makes it unbounded_past
                v09_compat.FilteredSource(self.batch_source, start_time_offset=timedelta(days=-365 * 100 - 1)),
            ],
            entities=[self.entity],
            mode="spark_sql",
            batch_schedule=timedelta(hours=1),
            run_transformation_validation=False,
            timestamp_field="timestamp",
            schema=[Field("user_id", String), Field("event_id", String), Field("timestamp", Timestamp)],
        )
        def v09_compat_bfv(filtered_source, unbounded_source, start_time_offset_source, unbounded_past_source):
            pass

        with mock.patch("tecton.cli.upgrade_utils._get_feature_view", return_value=v09_compat_bfv):
            bfv_guidance = BatchFeatureViewGuidance(v09_compat_bfv, str(Path()))._get_upgrade_guidance()
            self.assertEqual(len(bfv_guidance), 5)
            filtered_source_guidance = bfv_guidance[2]
            # Looks like the below ---
            # Replace data sources:
            # ```
            # sources=[FilteredSource(filtered_source), unbounded_source, FilteredSource(start_time_offset_source, start_time_offset=-timedelta(days=10)), FilteredSource(unbounded_past_source, start_time_offset=timedelta())],
            # ```
            # with:
            # ```
            # sources=[filtered_source, unbounded_source.unfiltered(), start_time_offset_source.select_range(
            #     start_time = TectonTimeConstant.MATERIALIZATION_START_TIME-timedelta(days=10),
            #     end_time = TectonTimeConstant.MATERIALIZATION_END_TIME
            # ), unbounded_past_source.select_range(
            #     start_time = TectonTimeConstant.UNBOUNDED_PAST,
            #     end_time = TectonTimeConstant.MATERIALIZATION_END_TIME
            # )],
            # ```
            self.assertIn(
                "Replace data sources:\n```\nsources=[FilteredSource(filtered_source), unbounded_source, FilteredSource(start_time_offset_source, start_time_offset=-timedelta(days=10)), FilteredSource(unbounded_past_source, start_time_offset=timedelta())],\n```\nwith: \n```\nsources=[filtered_source, unbounded_source.unfiltered(), start_time_offset_source.select_range(\n\tstart_time = TectonTimeConstant.MATERIALIZATION_START_TIME-timedelta(days=10),\n\tend_time = TectonTimeConstant.MATERIALIZATION_END_TIME\n), unbounded_past_source.select_range(\n\tstart_time = TectonTimeConstant.UNBOUNDED_PAST,\n\tend_time = TectonTimeConstant.MATERIALIZATION_END_TIME\n)],\n```",
                filtered_source_guidance,
            )

    def test_aggregation(self):
        @v09_compat.batch_feature_view(
            sources=[self.batch_source],
            entities=[self.entity],
            mode="spark_sql",
            batch_schedule=timedelta(hours=1),
            run_transformation_validation=False,
            timestamp_field="timestamp",
            aggregations=[
                v09_compat.Aggregation(
                    name="aggy_ag", column="event_id", function="count", time_window=timedelta(days=1)
                ),
                v09_compat.Aggregation(column="event_id", function="count", time_window=timedelta(days=2)),
            ],
            schema=[Field("user_id", String), Field("event_id", String), Field("timestamp", Timestamp)],
        )
        def v09_compat_bfv_aggregation(batch_source):
            pass

        with mock.patch("tecton.cli.upgrade_utils._get_feature_view", return_value=v09_compat_bfv_aggregation):
            bfv_guidance = BatchFeatureViewGuidance(v09_compat_bfv_aggregation, str(Path()))._get_upgrade_guidance()
            self.assertEqual(len(bfv_guidance), 6)
            self.assertIn("Remove `schema=[...]`", bfv_guidance[1])
            self.assertIn(
                'Aggregate(name="aggy_ag", input_column=Field("event_id", String), function="count", time_window=timedelta(days=1))',
                bfv_guidance[2],
            )
            self.assertIn(
                'Aggregate(input_column=Field("event_id", String), function="count", time_window=timedelta(days=2))',
                bfv_guidance[2],
            )

    def test_no_schema(self):
        conf.set("TECTON_REQUIRE_SCHEMA", False)

        @v09_compat.batch_feature_view(
            sources=[self.batch_source],
            entities=[self.entity],
            mode="spark_sql",
            batch_schedule=timedelta(hours=1),
            run_transformation_validation=False,
            timestamp_field="timestamp",
            aggregations=[
                v09_compat.Aggregation(
                    name="aggy_ag", column="event_id", function="count", time_window=timedelta(days=1)
                ),
                v09_compat.Aggregation(column="event_id", function="count", time_window=timedelta(days=2)),
            ],
        )
        def v09_compat_bfv_aggregation(batch_source):
            pass

        with mock.patch("tecton.cli.upgrade_utils._get_feature_view", return_value=v09_compat_bfv_aggregation):
            bfv_guidance = BatchFeatureViewGuidance(v09_compat_bfv_aggregation, str(Path()))._get_upgrade_guidance()
            for guidance_line in bfv_guidance:
                self.assertNotIn("schema", guidance_line)

    def test_get_imports_for_type(self):
        test_cases = [
            (Array(String), {"Array", "String"}),
            (Array(Array(String)), {"Array", "String"}),
            (Struct([Field("string", String)]), {"String", "Field", "Struct"}),
            (Struct([Field("string", Array(String))]), {"String", "Array", "Field", "Struct"}),
            (Map(String, Array(Int64)), {"Array", "String", "Map", "Int64"}),
        ]

        for test_case in test_cases:
            imports = _get_imports_for_type(test_case[0])
            assert imports == test_case[1]
