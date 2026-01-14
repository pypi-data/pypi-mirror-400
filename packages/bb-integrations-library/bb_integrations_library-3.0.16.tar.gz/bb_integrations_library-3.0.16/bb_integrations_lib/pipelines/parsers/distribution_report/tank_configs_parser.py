import numpy as np
import pandas as pd
from bb_integrations_lib.protocols.pipelines import Parser
from typing import override, Dict, List
from pandas import DataFrame


class TankConfigsParser(Parser):
    def __init__(self, tenant_name: str, source_system: str | None = None):
        super().__init__(source_system, tenant_name)

    def __repr__(self) -> str:
        return "Tank configs parser"

    @override
    async def parse(self, data: List[Dict], mapping_type: str | None = None) -> DataFrame:
        tc_df = pd.DataFrame(data)
        dos_columns = ['store_number', 'product', 'daily_lifting_estimate', 'measured_inventory']
        tc_df = tc_df[dos_columns]

        tc_df = tc_df.groupby(['store_number', 'product'])[
            ['daily_lifting_estimate', 'measured_inventory']].sum().reset_index()
        tc_df['dos'] = np.where(
            (tc_df['measured_inventory'] == 0) | (tc_df['daily_lifting_estimate'] == 0),
            'N/A',
            tc_df['measured_inventory'] / tc_df['daily_lifting_estimate']
        )
        tc_df['dos'] = pd.to_numeric(tc_df['dos'], errors='coerce')
        tc_df['dos_bucket'] = np.where(
            tc_df['dos'] <= 2, '0-2',
            np.where(tc_df['dos'] <= 4, '2-4',
                     np.where(tc_df['dos'] <= 6, '4-6',
                              np.where(tc_df['dos'] <= 8, '6-8',
                                       np.where(tc_df['dos'] <= 10, '8-10',
                                                np.where(tc_df['dos'].isna(), 'N/A', '10+')))))
        )
        tc_df['product'] = tc_df['product'].apply(TankConfigsParser.normalize_product)
        tc_df['store_number'] = tc_df['store_number'].astype(str)

        return tc_df

    @staticmethod
    def normalize_product(val):
        try:
            return str(int(float(val)))
        except (ValueError, TypeError):
            return str(val).strip()