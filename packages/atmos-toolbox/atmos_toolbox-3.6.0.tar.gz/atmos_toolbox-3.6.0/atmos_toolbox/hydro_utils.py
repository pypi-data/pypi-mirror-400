import numpy as np
import pandas as pd

def fill_missing_daily(dates, values, start=None, end=None):
    """
    补齐日尺度缺失日期，并用 NaN 填充缺测值。

    参数
    ----
    dates : array-like
        日期序列，支持字符串/datetime/np.datetime64/pd.Timestamp（无需连续）。
    values : array-like
        与 dates 对应的数据。形状可以是:
        - (N,)  一维
        - (N, K) 二维：每天K个变量
    start, end : 可选
        补齐的起止日期。若不传，则使用 dates 的最小/最大日期。

    返回
    ----
    full_dates : np.ndarray (datetime64[ns])
        连续的每日日期数组
    full_values : np.ndarray
        对应数据，缺测处为 NaN。形状为 (M,) 或 (M, K)
    """
    dates = pd.to_datetime(np.asarray(dates))
    vals = np.asarray(values)

    if len(dates) != len(vals):
        raise ValueError(f"dates 长度({len(dates)})必须等于 values 第一维长度({len(vals)})")

    # 确定补齐范围
    start = pd.to_datetime(start) if start is not None else dates.min()
    end = pd.to_datetime(end) if end is not None else dates.max()

    full_index = pd.date_range(start=start, end=end, freq="D")

    # 兼容一维/二维
    if vals.ndim == 1:
        s = pd.Series(vals.astype(float, copy=False), index=dates)
        s = s[~s.index.duplicated(keep="last")]  # 若重复日期，保留最后一个
        out = s.reindex(full_index).to_numpy()
    elif vals.ndim == 2:
        df = pd.DataFrame(vals.astype(float, copy=False), index=dates)
        df = df[~df.index.duplicated(keep="last")]
        out = df.reindex(full_index).to_numpy()
    else:
        raise ValueError("values 只支持 1维或2维数组 (N,) 或 (N,K)")

    return full_index.to_numpy(dtype="datetime64[ns]"), out


def fix_nonpos(series, method="linear", limit=None, inplace=False):
    """
    功能：
        将一维序列中 <= 0 的值标为 NaN 并插值修复，
        但保持原始 NaN 不被插值。
    返回：
        s_filled : 修复后的 ndarray
        idx_fixed: 被修复的位置索引（原 <=0 的位置）
    """
    # 转为 Series
    s = series if inplace and isinstance(series, pd.Series) \
        else pd.Series(series, dtype=float).copy()

    # 记录原始 NaN 位置（关键）
    orig_nan = s.isna()

    # 记录需要修复的位置（<=0 且不是原 NaN）
    mask_fix = (s <= 0) & (~orig_nan)

    if mask_fix.any():
        # 只把 <=0 的值置为 NaN
        s[mask_fix] = np.nan

        # 插值（此时会填所有 NaN）
        s_interp = s.interpolate(
            method=method,
            limit=limit,
            limit_direction="both"
        )

        # 把原始 NaN 位置还原为 NaN（关键一步）
        s_interp[orig_nan] = np.nan

        s = s_interp

    return s.values, mask_fix[mask_fix].index


def fix_spike(series, alpha=0.9, method="linear", inplace=False):
    """
    检测并修复“孤立尖点”极小值（不覆盖原始 NaN）
    """
    s = series if inplace and isinstance(series, pd.Series) \
        else pd.Series(series, dtype=float).copy()

    # 记录原始 NaN（关键）
    orig_nan = s.isna()

    idx_spikes = []

    # 仅在三点齐备且都 > 0 时才判断
    for t in range(1, len(s) - 1):
        x_prev, x_cur, x_next = s.iloc[t-1], s.iloc[t], s.iloc[t+1]

        # 跳过含 NaN 的窗口（更稳健）
        if pd.isna(x_prev) or pd.isna(x_cur) or pd.isna(x_next):
            continue

        if (x_prev > 0) and (x_cur > 0) and (x_next > 0):
            is_local_min = (x_cur < x_prev) and (x_cur < x_next)
            big_drop = (x_prev - x_cur) / x_prev > alpha
            big_rebound = (x_next - x_cur) / x_cur > alpha

            if is_local_min and big_drop and big_rebound:
                idx_spikes.append(s.index[t])

    if idx_spikes:
        # 只把尖点设为 NaN
        s.loc[idx_spikes] = np.nan

        # 插值
        s_interp = s.interpolate(
            method=method,
            limit_direction="both"
        )

        # 还原原始 NaN（关键一步）
        s_interp[orig_nan] = np.nan
        s = s_interp

    return s.values, idx_spikes



def insert_feb29(arr365):
    """
    对闰年日序列(365天、不含2/29)插入2/29，其值为(2/28与3/1均值)，输出366天。

    约定：arr365 是闰年日历但缺少2/29，也就是：
      index 0 -> 1/1
      index 58 -> 2/28
      index 59 -> 3/1
    """
    a = np.asarray(arr365, dtype=float)
    if a.ndim not in (1, 2):
        raise ValueError("arr365 只支持形状 (365,) 或 (365, K)")
    if a.shape[0] != 365:
        raise ValueError(f"arr365 第一维必须是365，但得到 {a.shape[0]}")

    feb28_idx = 31 + 28 - 1  # 2/28 在 0-based 的位置 = 58
    mar1_idx  = feb28_idx + 1  # 3/1 在缺闰日的序列中 = 59

    feb29_val = (a[feb28_idx] + a[mar1_idx]) / 2.0

    # 2/29 应插入到 2/28 之后，也就是插入位置 = 59
    out = np.insert(a, mar1_idx, feb29_val, axis=0)
    return out

def mask_consec_nonpos(arr, N):
    """
    将一维数组中连续 N 个及以上的 <=0 值标记为 NaN

    Parameters
    ----------
    arr : array-like
        一维数组（list / numpy array）
    N : int
        连续长度阈值（>=N 即标记）

    Returns
    -------
    out : np.ndarray
        处理后的数组（float，<=0 的连续段被置为 NaN）
    idx_masked : np.ndarray
        被标记为 NaN 的索引
    """
    arr = np.asarray(arr, dtype=float)
    out = arr.copy()

    # <=0 的位置
    mask = arr <= 0

    # 找连续段
    idx = np.where(mask)[0]
    if len(idx) == 0:
        return out, np.array([], dtype=int)

    # 按是否连续分组
    groups = np.split(idx, np.where(np.diff(idx) != 1)[0] + 1)

    idx_masked = []
    for g in groups:
        if len(g) >= N:
            out[g] = np.nan
            idx_masked.extend(g)

    return out, np.array(idx_masked)