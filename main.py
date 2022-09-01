"""

  """

##

import sys
from datetime import date
from datetime import datetime as dt

import pandas as pd
import pyspark.sql.functions as sfunc
from githubdata import GithubData
from mirutil.df_utils import read_data_according_to_type as read_data
from mirutil.df_utils import save_as_prq_wo_index as sprq
from pyspark.sql import SparkSession
from pyspark.sql import Window
from pyspark.sql.functions import concat_ws

from testmini import ColNames
from testmini import market_end_time
from testmini import market_start_time
from testmini import RepoAddresses
from testmini import Status
from testmini import status_simplified


spark = SparkSession.builder.getOrCreate()

ra = RepoAddresses()
c = ColNames()
s = Status()

def main() :

  pass

  ##
  rp_stch = GithubData(ra.stch)
  rp_stch.clone()
  ##
  dstp = rp_stch.data_fp
  dst = read_data(dstp)
  ##
  dst[c.trdble] = dst[c.ns].map(status_simplified)
  ##
  msk = dst[c.trdble].isna()
  df1 = dst[msk]
  assert df1.empty
  ##
  dst = dst[[c.id , c.dt , c.trdble]]
  ##
  rp_twd = GithubData(ra.twd)
  ##
  rp_twd.clone()
  ##
  dtwfp = rp_twd.data_fp
  dtw = read_data(dtwfp)
  dtw = dtw.reset_index()
  dtw = dtw[[c.d]]
  ##
  rp_i2f = GithubData(ra.i2f)
  ##
  rp_i2f.clone()
  ##
  difp = rp_i2f.data_fp
  did = read_data(difp)
  did = did[[c.id]]
  ##
  arbt_day = date(2018 , 1 , 1)

  strtdt = dt.combine(arbt_day , market_start_time)
  enddt = dt.combine(arbt_day , market_end_time)
  dti = pd.date_range(start = strtdt , end = enddt , freq = 's')

  dti = dti.to_frame()
  dti = dti.reset_index(drop = True)

  dti[c.t] = dti[0].dt.time
  dti[c.t] = dti[c.t].astype(str)

  dti[c.ismktopen] = True
  ##
  sdt = spark.createDataFrame(dti)
  sdw = spark.createDataFrame(dtw)
  sdi = spark.createDataFrame(did)
  ##
  sd = sdi.crossJoin(sdw)
  sd = sd.crossJoin(sdt)
  ##
  newcol = concat_ws(' ' , sd.Date , sd.Time).alias(c.dt)
  sd = sd.select(c.id , newcol , c.ismktopen)
  ##
  sds = spark.createDataFrame(dst)
  ##
  sd = sd.join(sds , [c.id , c.dt] , how = 'outer')
  ##
  sd = sd.sort([c.id , c.dt])
  ##
  window = Window.partitionBy(c.id).orderBy(c.dt).rowsBetween(-sys.maxsize , 0)
  filled_column = sfunc.last(sd[c.trdble] , ignorenulls = True).over(window)
  sdf_filled = sd.withColumn('filled' , filled_column)
  ##
  sd = sdf_filled
  ##
  msk = sd['filled'] == True
  msk &= sd[c.ismktopen] == True
  sd = sd.filter(msk)
  ##
  sd = sd.select(c.id , c.dt)
  ##
  sd = sd.withColumn(c.d , sfunc.substring(c.dt , 1 , 10))
  ##
  sd = sd.groupBy([c.id , c.d]).count()
  ##
  sdv = sd.toPandas()
  ##
  sprq(sdv , 'temp.prq')

  ##

  rp_stch.rmdir()
  rp_twd.rmdir()
  rp_i2f.rmdir()

  ##


  ##


  ##


  ##


  ##


  ##


  ##

##


##


if __name__ == '__main__' :
  main()
  print('done')


##