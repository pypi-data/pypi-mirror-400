import logging

import pandas as pd
import pyodbc

from .aquarius_ts import PARAM_SUBS_AQ_TO_SAGD
from .utils import *

logger = logging.getLogger(__name__)


def get_swims_metadata_connection():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=sql2019-prod.env.sa.gov.au;"
        "Database=SWIMS_Metadata;"
        "Trusted_Connection=yes;"
    )
    return conn


class SWIMSMetadata(SQLServerDb):
    API_ENDPOINT_NAME = "query_swims_metadata"

    def __init__(self, *args, sagd_conn=None, **kwargs):
        super(SWIMSMetadata, self).__init__(*args, **kwargs)
        if sagd_conn is None:
            from .sageodata_database import connect

            self.sagd_conn = connect()
        else:
            self.sagd_conn = sagd_conn

    def connect(self):
        self.conn = get_swims_metadata_connection()

    def run_query_for_drillholes(self, sql, dh_nos):
        logger.debug(f"Finding unit_hyphens for dh_nos={dh_nos}")
        wells = self.sagd_conn.wells_summary(dh_nos)
        unit_hyphens = list(wells.unit_hyphen.unique())
        dfs = []
        query = SQL(sql, unit_hyphen=unit_hyphens)
        query.chunksize = 1000
        for subquery in query:
            dfs.append(self.query(subquery))
        return pd.concat(dfs)

    def datasets(self, dh_nos, add_well_ids=True, **kwargs):
        sql = """
        select  Id as id,
                LocationId as locid,
                LocationName as loc_name,
                LocationType as loc_type,
                TimeSeriesIdentifier as tsid,
                Label as label,
                LabelFirstPart as label_first_part,
                TimeSeriesType as ts_type,
                "Parameter" as aq_param,
                Unit as unit,
                InterpolationType as interpolation_type,
                UtcOffset as utc_offset,
                FirstDataPointValue as first_data_value,
                FirstDataPointDateTime as first_data_timestamp,
                FirstDataPointGrade as first_data_grade,
                LastDataPointValue as last_data_value,
                LastDataPointDateTime as last_data_timestamp,
                LastDataPointGrade as last_data_grade,
                "Comment" as "comment",
                Description as descr,
                Publish as publish,
                Latitude as lat,
                Longitude as lon,
                TimeSeriesUniqueId as ts_uid,
                LocationUniqueId as loc_uid
        from SWIMS_Metadata.dbo.DataSets
        where LocationId in {UNIT_HYPHEN}
        """
        wells = self.sagd_conn.wells_summary(dh_nos)
        df = self.run_query_for_drillholes(sql, dh_nos)
        df["sagd_param"] = df.aq_param.map(PARAM_SUBS_AQ_TO_SAGD)
        id_cols = ["dh_no", "unit_hyphen", "obs_no", "dh_name"]
        fdf = pd.merge(
            df, wells[id_cols], left_on="locid", right_on="unit_hyphen", how="left"
        )
        cols = [c for c in fdf.columns if not c in id_cols]
        return fdf[id_cols + cols]
