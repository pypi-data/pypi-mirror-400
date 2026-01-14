from datetime import datetime, timedelta, UTC

import pandas as pd
from loguru import logger

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import GetOrderBolsAndDropsRequest


class TRTouchUpStep(Step):
    """Superclass for tank reading touchup steps"""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

class NouriaDayDropsTRTouchUpStep(TRTouchUpStep):
    """
    Touch up a standardized tank readings report to add a "Order Number + Drop Index" column, which Nouria uses to get
    tank levels just before they dropped product.

    Note that the tenant/environment is hard coded to Nouria.

    """
    def __init__(
            self,
            sd_client: GravitateSDAPI,
            *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.sd_client = sd_client

    def describe(self) -> str:
        return "Touchup Nouria tank readings for day drops report"

    async def execute(self, i: pd.DataFrame) -> pd.DataFrame:
        df = i.copy()
        when = datetime.now(UTC)
        recent_drops_resp = await self.sd_client.get_bols_and_drops(GetOrderBolsAndDropsRequest(
            order_date_start=when - timedelta(days=1),
            order_date_end=when
        ))
        recent_drops = recent_drops_resp.json()
        dfg = df.groupby(["Store Number", "Tank Id"])
        out_series = []
        for bol in recent_drops:
            for drop_idx, drop in enumerate(bol["drops"]):
                site_no = str(drop["location"])
                tank_id = str(drop["tank_id"])
                try:
                    # Gets the readings rows for this drop's specific site/tank
                    group = dfg.get_group((site_no, tank_id))
                    # Keep reads that are before the before_stick timestamp, then get the index of the reading
                    # row that has the most recent (closest to before_stick_time) timestamp.
                    idx = group[group["Read Time"] < drop["before_stick_time"]]["Read Time"].idxmax()
                    # Copy it to avoid pandas grumbling
                    row = df.iloc[idx].copy()
                    row["Order Number + Drop Index"] = f"{bol['order_number']}-{drop_idx + 1}"
                    out_series.append(row)
                except KeyError:
                    logger.warning(f"{site_no}, tank {tank_id} in drops but not tank readings, skipping record")
                except ValueError as e:
                    logger.warning(f"{site_no}, tank {tank_id} could not be processed: {e}")
        # If there are no data rows, create a fake empty df with the same columns the actual data would have
        # (since there are no series items to infer headers from, the whole file would be empty)
        if len(out_series) == 0:
            empty_df = pd.DataFrame(data=None, columns=df.columns + ["Order Number + Drop Index"])
            return empty_df
        # Otherwise reconstitute the relevant rows (with newly added order number/drop index column)
        return pd.DataFrame.from_records(out_series).sort_values(["Store Number", "Tank Id"])
