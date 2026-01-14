from datetime import datetime, UTC
from typing import Dict, Tuple
import pandas as pd
from bb_integrations_lib.protocols.pipelines import Step



class JoinDistributionOrderDosStep(Step):
    def __init__(self, client_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_name = client_name

    def describe(self) -> str:
        return "Join Distribution Order with DOS"

    async def execute(self, latest_model: dict | list) -> Tuple[pd.DataFrame, pd.DataFrame]:
        tc_df = self.pipeline_context.extra_data["tank_configs"]
        orders_data = self.pipeline_context.extra_data["orders_by_site_product"]

        if isinstance(latest_model, dict):
            pivot_df = orders_data
            df_detailed = pd.merge(
                pivot_df,
                tc_df,
                how='left',
                left_on=['site', 'component_product'],
                right_on=['store_number', 'product'],
            )

            df_detailed['dos_bucket'] = df_detailed['dos_bucket'].fillna('N/A')
            df_summary = df_detailed.groupby(['dos_bucket'])[
                ['component_volume_contract', 'component_volume_rack']].sum().reset_index()
            df_detailed = df_detailed.groupby(['dos_bucket', 'component_product'])[
                ['component_volume_contract', 'component_volume_rack']].sum().reset_index()

            df_summary = self.contract_rack_split(df_summary, latest_model)
            df_detailed = self.contract_rack_split(df_detailed, latest_model)

            return df_summary, df_detailed
        else:
            all_summaries = []
            all_details = []

            for i, model in enumerate(latest_model):
                pivot_df = orders_data[i]

                df_detailed = pd.merge(
                    pivot_df,
                    tc_df,
                    how='left',
                    left_on=['site', 'component_product'],
                    right_on=['store_number', 'product'],
                )

                df_detailed['dos_bucket'] = df_detailed['dos_bucket'].fillna('N/A')
                df_summary = df_detailed.groupby(['dos_bucket'])[
                    ['component_volume_contract', 'component_volume_rack']].sum().reset_index()
                df_detailed_agg = df_detailed.groupby(['dos_bucket', 'component_product'])[
                    ['component_volume_contract', 'component_volume_rack']].sum().reset_index()

                df_summary = self.contract_rack_split(df_summary, model)
                df_detailed_agg = self.contract_rack_split(df_detailed_agg, model)

                all_summaries.append(df_summary)
                all_details.append(df_detailed_agg)

            combined_summary = pd.concat(all_summaries, ignore_index=True)
            combined_detailed = pd.concat(all_details, ignore_index=True)

            return combined_summary, combined_detailed

    def contract_rack_split(self, df, latest_model):
        markets = latest_model['markets']
        _id = str(latest_model['_id'])
        time_ran = latest_model['time_ran']

        df['total'] = df['component_volume_contract'] + df['component_volume_rack']
        df['pct_contract'] = df['component_volume_contract'] / df['total']
        df['pct_rack'] = df['component_volume_rack'] / df['total']
        df['ingested_at'] = datetime.now(UTC).replace(tzinfo=None)
        df['markets'] = markets
        df['model_id'] = _id
        df['run_time'] = time_ran
        df['client_name'] = self.client_name
        return df
