#  斜率K + 单调性 + 支点数量 + 长度?
# find and sort

# filter by slope of pivot

import sys
sys.path.append(r"/home/yao/myproject/Stock/01_basic")
sys.path.append(r"/home/yao/myproject/Stock/00_data")

import akshare as ak
import numpy as np
import matplotlib.pyplot as plt
from  tqdm import tqdm
import datetime as dt

from my_zigzag import get_pivots, plot_pivots, plot_pivot_line
from stock_data_utils import get_sh_sz_A_name, LoadPickleData


def filter_pivot_line(src_data, pivots, k_thresh, verbose = False):
  
  low_pivots_index = [k for k, v in pivots.items() if v == -1]
  high_pivots_index = [k for k, v in pivots.items() if v == 1]
  if (len(low_pivots_index) < 3):
    return
  if (high_pivots_index[-1] > low_pivots_index[-1]):
    del high_pivots_index[-1]
    
  k_sup_last1 = (src_data[low_pivots_index[-1]] - src_data[low_pivots_index[-2]]) / (low_pivots_index[-1] - low_pivots_index[-2])
  k_sup_last2 = (src_data[low_pivots_index[-2]] - src_data[low_pivots_index[-3]]) / (low_pivots_index[-2] - low_pivots_index[-3])
  
  k_res_last1 = (src_data[high_pivots_index[-1]] - src_data[high_pivots_index[-2]]) / (high_pivots_index[-1] - high_pivots_index[-2])
  if verbose:
    print(f"k_sup_last1 {k_sup_last1}, k_sup_last2 {k_sup_last2}, k_res_last1 {k_res_last1}")
  # 增加涨幅比例限制
  raise_1 = (src_data[high_pivots_index[-2]]/src_data[low_pivots_index[-3]])
  raise_2 = (src_data[high_pivots_index[-1]]/src_data[low_pivots_index[-2]])
  if max(raise_1, raise_2) / min(raise_2, raise_1)  > 2:
    return False
  
  # 增加跌幅比例限制
  fail_1 = (src_data[high_pivots_index[-2]]/src_data[low_pivots_index[-2]])
  fail_2 = (src_data[high_pivots_index[-1]]/src_data[low_pivots_index[-1]])
  if max(fail_1, fail_2) / min(fail_2, fail_1)  > 1.6:
    return False
    
  # 两边时间间隔，不要差太多
  if k_thresh < k_sup_last1  and  k_thresh < k_sup_last2  and  \
     k_thresh < k_res_last1 and k_res_last1 < max(k_sup_last1, k_sup_last2)+0.1 and \
     1 < abs(low_pivots_index[-1] - high_pivots_index[-1]) and  abs(low_pivots_index[-1] - high_pivots_index[-1]) < 15 and \
     1 < abs(low_pivots_index[-2] - high_pivots_index[-1]) and  abs(low_pivots_index[-2] - high_pivots_index[-1]) < 15 and \
     1 < abs(low_pivots_index[-2] - high_pivots_index[-2]) and  abs(low_pivots_index[-2] - high_pivots_index[-2]) < 15 and \
     1 < abs(low_pivots_index[-3] - high_pivots_index[-2]) and  abs(low_pivots_index[-3] - high_pivots_index[-2]) < 15 and \
     True:
    return True
  
  return False
  
def long_buy(src_data, pivots):
  p_list = list(pivots.items())
  last_pivot_index, last_pivot_class = p_list[-1]
  if last_pivot_class == 1: # 最后一个支点是高点，则不考虑
    return False
  else:
    if len(src_data) - last_pivot_index > 4:  # 最后一个是低点，但是后续不涨天数不多
      return False
    # 涨幅不超过3%
    if (src_data[-1] / src_data[last_pivot_index] -1) > 0.025:
      return False
  
  return True
  
  
def long_sell(src_data, pivots):
  pass
  

if __name__ == "__main__":
  pickle_path = '/home/yao/myproject/Stock/51_10天系列/01_数据操作/df_0606.pickle' 
  df_dict = LoadPickleData(pickle_path)
  for code, val in tqdm(df_dict.items()):
    # if "603713" not in code:
      # continue
    # val.drop([len(val)-1],inplace=True)

    end_day = dt.date(dt.date.today().year,dt.date.today().month,dt.date.today().day)
    end_day = end_day.strftime("%Y%m%d")   
    start_date_str = '01-01-2024'
    start_day = dt.datetime.strptime(start_date_str, '%m-%d-%Y').date()
    val = ak.stock_zh_a_hist(symbol=code, start_date=start_day, period = "daily", adjust= 'qfq')
    # print(val.tail())
    
    
    df_daily = val[val["日期"]> start_day]
    
    X = df_daily["收盘"]
    data = np.asarray(X)    
    pivots = get_pivots(data, 0.06, 0.06)
    # print(pivots)
    # print(data[list(pivots.keys())])
    sel =  filter_pivot_line(data, pivots, 0.05)
    
    # sel = True
    #TODO 显示比例修改
    if sel:
      tobuy = long_buy(data, pivots)
      if not tobuy:
        continue
      print(code)
      plt.clf()
      plot_pivots(data, pivots)
      plot_pivot_line(data, pivots)
      plt.savefig('./workdata/'+code + '_0607.jpg')
      # break
      # plt.show()
