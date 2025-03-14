#  斜率K + 单调性 + 支点数量 + 长度?
# find and sort

# filter by slope of pivot

import sys
sys.path.append(r"/home/yao/workspace/Stock/01_basic")
sys.path.append(r"/home/yao/workspace/Stock/00_data")

import akshare as ak
import numpy as np
import matplotlib.pyplot as plt
from  tqdm import tqdm
import datetime as dt

from my_zigzag import get_pivots, plot_pivots, plot_pivot_line
from stock_data_utils import get_sh_sz_A_name, LoadPickleData


def filter_raise_pivot_line(src_data, pivots, k_thresh, verbose = False):
  
  low_pivots_index = [k for k, v in pivots.items() if v == -1]
  high_pivots_index = [k for k, v in pivots.items() if v == 1]
  if (len(low_pivots_index) < 3):
    return
  
  if (len(high_pivots_index) < 2):
    return
  
  if (high_pivots_index[-1] > low_pivots_index[-1]):
    del high_pivots_index[-1]
    
  k_sup_last1 = (src_data[low_pivots_index[-1]] - src_data[low_pivots_index[-2]]) / (low_pivots_index[-1] - low_pivots_index[-2])  # 支撑斜率
  k_sup_last2 = (src_data[low_pivots_index[-2]] - src_data[low_pivots_index[-3]]) / (low_pivots_index[-2] - low_pivots_index[-3])
  
  k_res_last1 = (src_data[high_pivots_index[-1]] - src_data[high_pivots_index[-2]]) / (high_pivots_index[-1] - high_pivots_index[-2]) # 阻力斜率
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
  
# 涨势
def daily_raise_long_buy(src_data, pivots, df_daily):
  '''
  日k线上看多,
  判断买点
  '''
  p_list = list(pivots.items())
  # 判断最后一个支点属性
  last_pivot_index, last_pivot_class = p_list[-1]
  if last_pivot_class == 1: # 最后一个支点是高点，则不考虑
    return False
  else:
    if len(src_data) - last_pivot_index > 4:  # 最后一个支点是低点，但是后续不涨天数不多
      return False
    # 涨幅不超过3%
    if (src_data[-1] / src_data[last_pivot_index] -1) > 0.05:
      return False
    # TODO: 涨的时间和幅度来排序
    
  # 最近3个低点抬升
  low_pivots_index = [k for k, v in pivots.items() if v == -1]
  if (len(low_pivots_index) < 3):
    return False

  
  high_pivots_index = [k for k, v in pivots.items() if v == 1]
  if (len(high_pivots_index) < 3):
    return False

  if src_data[low_pivots_index[-1]] < src_data[low_pivots_index[-2]] or \
     src_data[low_pivots_index[-2]] < src_data[low_pivots_index[-3]] :
    return False
  
  if src_data[high_pivots_index[-1]] < src_data[high_pivots_index[-2]] or \
     src_data[high_pivots_index[-2]] < src_data[high_pivots_index[-3]] :
    return False

  # 涨跌幅比例变化不大
  raise_2 = src_data[high_pivots_index[-1]] - src_data[low_pivots_index[-2]]
  raise_1 = src_data[high_pivots_index[-2]] - src_data[low_pivots_index[-3]]
  if abs((raise_2 / raise_1) -1) > 0.25:  # 涨幅变化不大
    return False

  decade_1 = src_data[high_pivots_index[-1]] - src_data[low_pivots_index[-1]]
  decade_2 = src_data[high_pivots_index[-2]] - src_data[low_pivots_index[-2]]
  if abs((decade_1 / decade_2)-1 ) > 0.25:  
    return False
  
  # 偏度变化不大
  raise_2_datas = high_pivots_index[-1] - low_pivots_index[-2]
  raise_1_datas = high_pivots_index[-2] - low_pivots_index[-3]
  if abs((raise_2_datas / raise_1_datas) -1) > 0.25:  # 涨幅变化不大
    return False

  decade_1_datas = low_pivots_index[-2] - high_pivots_index[-2]
  decade_2_datas = low_pivots_index[-1] - high_pivots_index[-1]
  if abs((decade_1_datas / decade_2_datas)-1 ) > 0.25:
    return False
  
  # 上升趋势不要有回撤超过5%



  # 成交量变化设置TODO

  # 买点判断，pinbar


  return True
  
# 水平震荡
def daily_hor_osc_long_buy(src_data, pivots):
  if len(pivots) < 1:
    return False
  
  p_list = list(pivots.items())
  
  # 判断最后一个支点属性
  last_pivot_index, last_pivot_class = p_list[-1]
  if last_pivot_class == 1: # 最后一个支点是高点，则不考虑
    return False
  else:
    if len(src_data) - last_pivot_index > 4:  # 最后一个支点是低点，但是后续不涨天数不多
      return False
    # 最新价格至低点涨幅不超过3%
    if (src_data[-1] / src_data[last_pivot_index] -1) > 0.025:
      return False

  # 判断支点涨跌
  low_pivots_index = [k for k, v in pivots.items() if v == -1]
  high_pivots_index = [k for k, v in pivots.items() if v == 1]
  if (len(low_pivots_index) < 3):
    return False
  
  if (len(high_pivots_index) < 2):
    return False
  
  # 底部3个数浮动不超过4%
  low_pivot_val = [src_data[low_pivots_index[-1]], src_data[low_pivots_index[-2]], src_data[low_pivots_index[-3]]]
  low_pivot_val.sort()
  if (low_pivot_val[1] - low_pivot_val[0])/ low_pivot_val[1] > 0.04 or \
     (low_pivot_val[2] - low_pivot_val[1])/ low_pivot_val[2] > 0.04:
    return False
  
  if abs(src_data[high_pivots_index[-1]] - src_data[high_pivots_index[-2]]) / src_data[high_pivots_index[-2]] > 0.05:
    return False
  

  # 涨跌的天数不能差别太大
  raise1_days = high_pivots_index[-2] - low_pivots_index[-3]
  raise2_days = high_pivots_index[-1] - low_pivots_index[-2]
  fail1_days = low_pivots_index[-1] - high_pivots_index[-1]
  fail2_days = low_pivots_index[-2] - high_pivots_index[-2]

  if abs(raise1_days-fail1_days) > 5 or abs(raise2_days - fail2_days) > 5:
    return False

  # 涨跌要满足一定幅度
  if (src_data[high_pivots_index[-1]] / low_pivot_val[1]) > 0.1:
    return True

def weekly_hor_osc_long_buy(src_data, pivots):
  if len(pivots) < 1:
    return False
  
  p_list = list(pivots.items())
  
  # 判断最后一个支点属性
  last_pivot_index, last_pivot_class = p_list[-1]
  if last_pivot_class == 1: # 最后一个支点是高点，则不考虑
    return False
  else:
    if len(src_data) - last_pivot_index > 4:  # 最后一个支点是低点，但是后续不涨天数不多
      return False
    # 最新价格至低点涨幅不超过3%
    if (src_data[-1] / src_data[last_pivot_index] -1) > 0.025:
      return False

  # 判断支点涨跌
  low_pivots_index = [k for k, v in pivots.items() if v == -1]
  high_pivots_index = [k for k, v in pivots.items() if v == 1]
  if (len(low_pivots_index) < 3):
    return False
  
  if (len(high_pivots_index) < 2):
    return False
  
  # 底部3个数浮动不超过4%
  low_pivot_val = [src_data[low_pivots_index[-1]], src_data[low_pivots_index[-2]], src_data[low_pivots_index[-3]]]
  low_pivot_val.sort()
  if (low_pivot_val[1] - low_pivot_val[0])/ low_pivot_val[1] > 0.06 or \
     (low_pivot_val[2] - low_pivot_val[1])/ low_pivot_val[2] > 0.06:
    return False
  
  # 顶部浮动不超过
  if abs(src_data[high_pivots_index[-1]] - src_data[high_pivots_index[-2]]) / src_data[high_pivots_index[-2]] > 0.08:
    return False
  
  # 涨跌幅比例变化不大
  raise_2 = src_data[high_pivots_index[-1]] - src_data[low_pivots_index[-2]]
  raise_1 = src_data[high_pivots_index[-2]] - src_data[low_pivots_index[-3]]
  if abs((raise_2 / raise_1) -1) > 0.25:  # 涨幅变化不大
    return False
  
  decade_1 = src_data[high_pivots_index[-1]] - src_data[low_pivots_index[-1]]
  decade_2 = src_data[high_pivots_index[-2]] - src_data[low_pivots_index[-2]]
  if abs((decade_1 / decade_2)-1 ) > 0.25:  
    return False

  # 偏度变化不大
  raise_2_datas = high_pivots_index[-1] - low_pivots_index[-2]
  raise_1_datas = high_pivots_index[-2] - low_pivots_index[-3]
  if abs((raise_2_datas / raise_1_datas) -1) > 0.25:  # 涨幅变化不大
    return False

  decade_1_datas = low_pivots_index[-2] - high_pivots_index[-2]
  decade_2_datas = low_pivots_index[-1] - high_pivots_index[-1]
  if abs((decade_1_datas / decade_2_datas)-1 ) > 0.25:
    return False


  # 高低点涨跌要满足一定幅度
  if (src_data[high_pivots_index[-1]] / low_pivot_val[1]) > 0.15:
    return True
  


def long_sell(src_data, pivots):
  pass
  

if __name__ == "__main__":
  pickle_path = '/home/yao/workspace/Stock/51_10天系列/01_数据操作/dfw_0830.pickle' 
  df_dict = LoadPickleData(pickle_path)
  for code, val in tqdm(df_dict.items()):
    # if code < "000400":
    #   continue
    # val.drop([len(val)-1],inplace=True)

    end_day = dt.date(dt.date.today().year,dt.date.today().month,dt.date.today().day)
    end_day = end_day.strftime("%Y%m%d")   
    start_date_str = '01-01-2024'
    start_day = dt.datetime.strptime(start_date_str, '%m-%d-%Y').date()
    # val = ak.stock_zh_a_hist(symbol=code, start_date=start_day, end_date="20241207" ,period = "daily", adjust= 'qfq')
    # val = ak.stock_zh_a_hist(symbol=code, start_date=start_day, end_date="20241207", period = "weekly", adjust= 'qfq')
    # print(val.tail())
    
    
    df_daily = val[val["Date"]> start_day]
    
    X = df_daily["收盘"]
    # print(df_daily[:-35].tail(1))
    data = np.asarray(X)    
    daily_raise_thresh_val = 0.08
    daily_fail_thresh_val = 0.06
    weekly_raise_thresh_val = 0.15
    weekly_fail_thresh_val = 0.15
    # pivots = get_pivots(data, daily_raise_thresh_val, daily_fail_thresh_val)
    pivots = get_pivots(data, weekly_raise_thresh_val, weekly_fail_thresh_val)
    # print(pivots)
    # print(data[list(pivots.keys())])
    # sel = daily_raise_long_buy(data, pivots, df_daily)
    # pivots = get_pivots(data, weekly_raise_thresh_val, weekly_fail_thresh_val)
    # sel = daily_hor_osc_long_buy(data, pivots)
    sel = weekly_hor_osc_long_buy(data, pivots)
    # 进一步筛选
    # sel = True
    #TODO 显示比例修改
    if sel:
      # tobuy = raise_long_buy(data, pivots)
      # if not tobuy:
        # continue
      print(code)
      plt.clf()
      plot_pivots(data, pivots)
      plot_pivot_line(data, pivots)
      plt.savefig('./workdata/'+code + '.jpg')
      # break
      # plt.show()
