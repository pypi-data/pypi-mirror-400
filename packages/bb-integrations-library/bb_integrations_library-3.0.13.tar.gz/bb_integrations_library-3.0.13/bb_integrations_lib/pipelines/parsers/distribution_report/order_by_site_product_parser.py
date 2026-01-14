from io import StringIO
import numpy as np
import pandas as pd
from bb_integrations_lib.protocols.pipelines import Parser
from typing import override
from pandas import DataFrame


class OrderBySiteProductParser(Parser):
    def __init__(self, tenant_name: str, source_system: str | None = None):
        super().__init__(source_system, tenant_name)

    def __repr__(self) -> str:
        return "Order by site and product parser"

    @override
    async def parse(self, data: str, mapping_type: str | None = None) -> DataFrame:
        orders = pd.read_csv(StringIO(data))
        orders_columns = ['order_number', 'site', 'site_name', 'component_product', 'finished_product',
                          'component_volume',
                          'contract', 'market']
        orders = orders[orders_columns]
        orders['contract_type'] = np.where(orders['contract'].isna(), 'rack', 'contract')
        grouped_sum = orders.groupby(['site', 'component_product', 'contract_type', 'market'])[
            'component_volume'].sum().reset_index()

        pivot_df = grouped_sum.pivot_table(
            index=['site', 'component_product'],
            values=['component_volume'],
            columns=['contract_type'],
            aggfunc='sum',
            fill_value=0
        )
        pivot_df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in pivot_df.columns]
        pivot_df['component_volume_contract'] = pivot_df.get('component_volume_contract', 0)
        pivot_df['component_volume_rack'] = pivot_df.get('component_volume_rack', 0)
        pivot_df['total_product'] = pivot_df['component_volume_contract'] + pivot_df['component_volume_rack']
        pivot_df['pct_contract'] = pivot_df['component_volume_contract'] / pivot_df['total_product']
        pivot_df['pct_rack'] = pivot_df['component_volume_rack'] / pivot_df['total_product']
        pivot_df = pivot_df.reset_index()
        pivot_df['component_product'] = pivot_df['component_product'].apply(OrderBySiteProductParser.normalize_product)
        pivot_df['site'] = pivot_df['site'].astype(str)
        return pivot_df

    @staticmethod
    def normalize_product(val):
        try:
            return str(int(float(val)))
        except (ValueError, TypeError):
            return str(val).strip()