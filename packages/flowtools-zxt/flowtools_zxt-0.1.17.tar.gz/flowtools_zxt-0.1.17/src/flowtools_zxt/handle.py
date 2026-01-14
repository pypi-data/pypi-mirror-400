import pandas as pd
import numpy as np
import xarray as xr
import warnings
import smbclient
import os

from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from io import BytesIO

warnings.filterwarnings("ignore")


def get_dem(
        vars=["z"],
        get_values=False,
        interp_lon=None,
        interp_lat=None,
        around_radius=0,
        file_path="/mnt/external_disk0/Auxiliary_data/etopo2_new.nc",
):
    """
    获取地形高程数据(DEM)，支持周边方阵

    参数:
        vars: 变量列表 (默认为 ["z"])
        get_values: 是否返回 numpy 值而不是 DataArray (默认为 False)
        interp_lon: 插值目标经度 (可选)
        interp_lat: 插值目标纬度 (可选)
        around_radius: 方阵半径
                        0 = 只中心点
                        1 = 3x3 方阵
                        21 = 43x43 方阵 等
        file_path: 数据文件路径

    返回:
        dict，key 为变量名，偏移点后缀为 _shift_lat±i_lon±j
    """
    if around_radius < 0:
        raise ValueError("around_radius 必须为非负整数")

    # 生成所有偏移组合
    shifts = [(di, dj) for di in range(-around_radius, around_radius + 1)
              for dj in range(-around_radius, around_radius + 1)]

    with xr.open_dataset(file_path) as ds:
        # 统一坐标名（适配 x/y 等情况）
        if 'x' in ds.dims and 'y' in ds.dims:
            ds = ds.rename({'x': 'lon', 'y': 'lat'})

        result = {}

        for base_var in vars:
            if base_var not in ds:
                raise KeyError(f"变量 {base_var} 不存在于文件中")

            da_base = ds[base_var]

            # 判断是否需要局部提取
            use_interp = interp_lon is not None and interp_lat is not None

            if use_interp:
                # 先插值到精确位置（得到单点 DataArray，带坐标）
                da_center = da_base.interp(lon=interp_lon, lat=interp_lat, method="linear")
            else:
                # 未提供位置 → 返回全局
                if around_radius > 0:
                    raise ValueError("未提供 interp_lon 和 interp_lat 时，around_radius 必须为 0")
                da_center = da_base

            # 为每个偏移生成结果
            for di, dj in shifts:
                if di == 0 and dj == 0:
                    da_shifted = da_center
                    var_name = base_var
                else:
                    da_shifted = da_center.shift(lat=di, lon=dj)  # 边界自动产生 nan
                    sign_i = "+" if di >= 0 else "-"
                    sign_j = "+" if dj >= 0 else "-"
                    var_name = f"{base_var}_shift_lat{sign_i}{abs(di)}_lon{sign_j}{abs(dj)}"

                da_shifted = da_shifted.rename(var_name)

                if get_values:
                    result[var_name] = da_shifted.values  # 直接返回 numpy array（标量/小阵/全局阵）
                else:
                    result[var_name] = da_shifted  # 返回 DataArray

    return result


def get_cra_surface_meteos(
        year=None,
        month=None,
        day=None,
        hour=None,
        vars=["t2m", "sh2", "u10", "v10"],
        get_values=True,
        interp_lon=None,
        interp_lat=None,
        around_radius=0,
        file_structure="/data/CRA/surface/{YYYY}/{YYYYMMDD}/ART_ATM_GLB_0P10_6HOR_SANL_{YYYYMMDDHH}.grib2"
):
    """
    获取 CRA 表面气象要素（2m 温湿 + 10m 风）

    参数:
        year, month, day, hour: 时间（未提供时默认当前或最小值，仅用于构建路径）
        vars: 需要提取的变量列表
        get_values: 是否返回 numpy 值 (默认为 True)
        interp_lon / interp_lat: 精确插值位置（可选）
        around_radius: 周边方阵半径
                        0 = 只中心点
                        1 = 3x3 方阵
                        21 = 43x43 方阵 等
        file_structure: 文件路径模板（支持 {YYYY} 等占位符）

    返回:
        dict，key 为变量名，偏移点后缀为 _shift_lat±i_lon±j
    """
    if around_radius < 0:
        raise ValueError("around_radius 必须为非负整数")

    # 1. 构建文件路径
    year = int(year) if year is not None else datetime.now().year
    month = int(month) if month is not None else 1
    day = int(day) if day is not None else 1
    hour = int(hour) if hour is not None else 0

    file_path = file_structure.format(
        YYYY=year,
        YY=str(year)[-2:],
        MM=f"{month:02d}",
        DD=f"{day:02d}",
        HH=f"{hour:02d}",
        YYYYMMDD=f"{year}{month:02d}{day:02d}",
        YYYYMMDDHH=f"{year}{month:02d}{day:02d}{hour:02d}"
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"数据文件不存在: {file_path}")

    # 生成所有偏移组合
    shifts = [(di, dj) for di in range(-around_radius, around_radius + 1)
              for dj in range(-around_radius, around_radius + 1)]

    # 2. 打开两个高度层的数据（2m 和 10m）
    f1 = xr.open_dataset(file_path, backend_kwargs={'indexpath': '', 'filter_by_keys': {'typeOfLevel': 'heightAboveGround', 'level': 2}})
    f2 = xr.open_dataset(file_path, backend_kwargs={'indexpath': '', 'filter_by_keys': {'typeOfLevel': 'heightAboveGround', 'level': 10}})

    # 统一坐标名
    f1 = f1.rename({'longitude': 'lon', 'latitude': 'lat'})
    f2 = f2.rename({'longitude': 'lon', 'latitude': 'lat'})

    result = {}
    use_interp = interp_lon is not None and interp_lat is not None

    for base_var in vars:
        # 确定变量来源
        if base_var in ["t2m", "sh2"]:
            ds = f1
        elif base_var in ["u10", "v10"]:
            ds = f2
        else:
            raise KeyError(f"不支持的变量: {base_var}（目前仅支持 t2m, sh2, u10, v10）")

        da_base = ds[base_var]

        if use_interp:
            # 先插值到精确位置 → 得到单点 DataArray
            da_center = da_base.interp(lon=interp_lon, lat=interp_lat, method="linear")
        else:
            # 未提供位置 → 返回全局（强制 around_radius=0）
            if around_radius > 0:
                raise ValueError("未提供 interp_lon 和 interp_lat 时，around_radius 必须为 0")
            da_center = da_base

        # 为每个偏移生成结果
        for di, dj in shifts:
            if di == 0 and dj == 0:
                da_shifted = da_center
                var_name = base_var
            else:
                da_shifted = da_center.shift(lat=di, lon=dj)  # 边界自动 nan
                sign_i = "+" if di >= 0 else "-"
                sign_j = "+" if dj >= 0 else "-"
                var_name = f"{base_var}_shift_lat{sign_i}{abs(di)}_lon{sign_j}{abs(dj)}"

            da_shifted = da_shifted.rename(var_name)

            if get_values:
                result[var_name] = da_shifted.values  # 标量 或 小数组
            else:
                result[var_name] = da_shifted

    # 关闭数据集
    f1.close()
    f2.close()

    return result


def get_cra_atmos_meteos(
        year=None,
        month=None,
        day=None,
        hour=None,
        vars=["RH", "UGRD", "VGRD", "HGT", "SPFH", "TMP", "PRES", "PWAT"],
        pressure_levels=["1000", "900", "800", "700", "600", "500"],
        get_values=True,
        interp_lon=None,
        interp_lat=None,
        around_radius=0,
        file_structure="/data2/CRA/atmos/{YYYY}/{YYYYMMDD}/ART_ATM_GLB_0P10_6HOR_ANAL_{YYYYMMDDHH}.grib2",
):
    """
    获取 CRA 大气层气象要素（等压面 + 单层变量，每个变量单独 GRIB2 文件）

    参数:
        year, month, day, hour: 时间
        vars: 变量列表（支持 "TMP", "UGRD", "RH", "HGT", "SPFH", "PRES", "PWAT" 等）
        pressure_levels: 等压面列表，仅对等压面变量生效（如 TMP, UGRD 等）
        get_values: 是否返回 numpy 值 (默认为 True)
        interp_lon / interp_lat: 精确插值位置（可选）
        around_radius: 周边方阵半径（0=只中心，1=3x3，21=43x43 等）
        file_structure: 文件路径模板

    返回:
        dict，key 格式：
          - 等压面变量中心: "TMP_500"
          - 单层变量: "PWAT"（无 level）
          - 偏移: "..._shift_lat±i_lon±j"
    """
    if around_radius < 0:
        raise ValueError("around_radius 必须为非负整数")

    # 时间处理
    year = int(year) if year is not None else datetime.now().year
    month = int(month) if month is not None else 1
    day = int(day) if day is not None else 1
    hour = int(hour) if hour is not None else 0

    # GRIB shortName 映射
    var_dict = {
        "HGT": "gh",
        "SPFH": "q",
        "TMP": "t",
        "UGRD": "u",
        "VGRD": "v",
        "RH": "r",
        "PRES": "pres",
        "PWAT": "pwat",
    }

    # 等压面变量（需要 pressure_levels 和 shortName 过滤）
    isobaric_vars = ["RH", "UGRD", "VGRD", "HGT", "SPFH", "TMP"]
    # 单层变量（atmosphereSingleLayer）
    single_layer_vars = ["PRES", "PWAT"]

    # 生成偏移组合
    shifts = [(di, dj) for di in range(-around_radius, around_radius + 1)
              for dj in range(-around_radius, around_radius + 1)]

    use_interp = interp_lon is not None and interp_lat is not None
    if not use_interp and around_radius > 0:
        raise ValueError("未提供 interp_lon 和 interp_lat 时，around_radius 必须为 0")

    result = {}

    for base_var in vars:
        if base_var not in var_dict:
            raise KeyError(f"不支持的变量: {base_var}")

        mapped_var = var_dict[base_var]

        # 构建文件路径
        file_path = file_structure.format(
            YYYY=year,
            MM=f"{month:02d}",
            DD=f"{day:02d}",
            HH=f"{hour:02d}",
            YYYYMM=f"{year}{month:02d}",
            YYYYMMDD=f"{year}{month:02d}{day:02d}",
            YYYYMMDDHH=f"{year}{month:02d}{day:02d}{hour:02d}",
        )

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"数据文件不存在: {file_path}")

        # 根据变量类型设置 filter_by_keys
        if base_var in isobaric_vars:
            filter_keys = {'typeOfLevel': 'isobaricInhPa', 'shortName': mapped_var}
            levels_to_process = [float(lev) for lev in pressure_levels]
        elif base_var in single_layer_vars:
            filter_keys = {'typeOfLevel': 'atmosphereSingleLayer'}
            levels_to_process = [None]  # 单层变量无 level
        else:
            raise ValueError(f"变量 {base_var} 类型未知")

        # 打开文件（使用过滤）
        with xr.open_dataset(file_path, backend_kwargs={'indexpath': '', 'filter_by_keys': filter_keys}) as ds:
            ds = ds.rename({'longitude': 'lon', 'latitude': 'lat'})
            if 'isobaricInhPa' in ds.dims:
                ds = ds.rename({'isobaricInhPa': 'level'})

            # 直接取第一个变量（过滤后通常只有一个）
            da_full = list(ds.data_vars.values())[0]
            # da_full = ds[mapped_var]

            # 处理每个层（单层变量只有一次循环）
            for level in levels_to_process:
                if level is not None:
                    # 等压面变量：选择指定层
                    da_layer = da_full.sel(level=level)
                    base_name = f"{base_var}_{int(level)}"
                else:
                    # 单层变量：直接使用
                    da_layer = da_full
                    base_name = base_var

                if use_interp:
                    da_center = da_layer.interp(lon=interp_lon, lat=interp_lat, method="linear")
                else:
                    da_center = da_layer

                # 生成偏移结果
                for di, dj in shifts:
                    if di == 0 and dj == 0:
                        da_shifted = da_center
                        var_name = base_name
                    else:
                        da_shifted = da_center.shift(lat=di, lon=dj)
                        sign_i = "+" if di >= 0 else "-"
                        sign_j = "+" if dj >= 0 else "-"
                        var_name = f"{base_name}_shift_lat{sign_i}{abs(di)}_lon{sign_j}{abs(dj)}"

                    da_shifted = da_shifted.rename(var_name)

                    if get_values:
                        result[var_name] = da_shifted.values
                    else:
                        result[var_name] = da_shifted

    return result




# def get_gem_emissions(
#         year=None,
#         month=None,
#         lon=None,
#         lat=None,
#         vars=["BC", "CO", "CO2", "NOx", "OC", "PM10", "PM25", "SO2", "TSP"],
#         get_values=True,
#         interp_lon=None,
#         interp_lat=None,
#         add_arounds=False,
#         file_structure="/mnt/external_disk0/GEMS/nc_month/{VAR}/tot/GEMS_tot_{VAR}_{YYYY}_monthly.nc"
# ):
#     """
#     通用化的GEMS排放数据获取函数
#
#     Parameters:
#     file_structure: 文件路径模板，支持以下占位符：
#         {YYYY} - 4位年份
#         {MM} - 2位月份
#         {VAR} - 变量名
#     """
#
#     # 确保输入是整数
#     year = int(year) if year else datetime.now().year
#     month = int(month) if month else 1
#
#     # 年份限制（保持原有逻辑）
#     if year >= 2019:
#         year = 2019
#
#     # 1. 扩展变量列表
#     extended_vars = []
#     for var in vars:
#         extended_vars.append(var)
#         if add_arounds:
#             extended_vars.extend([f"{var}_{i}" for i in range(1, 9)])
#
#     # 2. 构建完整字典
#     data_dict = {}
#     for var in extended_vars:
#         if "_" in var:
#             base_var, shift_idx = var.split("_")
#             shift_idx = int(shift_idx)
#             shifts = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
#             lon_shift, lat_shift = shifts[shift_idx - 1]
#         else:
#             base_var = var
#             lon_shift, lat_shift = 0, 0
#
#         # 加载并重命名DataArray
#         if base_var not in data_dict:
#             # 构建文件路径
#             if file_structure:
#                 file_path = file_structure.format(
#                     YYYY=year,
#                     MM=f"{month:02d}",
#                     VAR=base_var
#                 )
#             else:
#                 # 使用原来的固定路径（向后兼容）
#                 file_path = f"/mnt/external_disk0/GEMS/nc_month/{base_var}/tot/GEMS_tot_{base_var}_{year}_monthly.nc"
#
#             # 检查文件是否存在
#             if not os.path.exists(file_path):
#                 raise FileNotFoundError(f"排放数据文件不存在: {file_path}")
#
#             # 打开文件并读取数据
#             with xr.open_dataset(file_path) as f:
#                 # 这里重命名DataArray
#                 data_dict[base_var] = f["emission"][month - 1].rename({'lon': 'lon','lat': 'lat'}).rename(base_var)
#
#         # 应用偏移
#         if lon_shift != 0 or lat_shift != 0:
#             data_dict[var] = data_dict[base_var].shift(
#                 lon=lon_shift, lat=lat_shift, fill_value=np.nan
#             ).rename(var)  # 偏移后的DataArray也重命名
#         else:
#             # 确保原始数据使用正确的名称
#             data_dict[var] = data_dict[base_var].rename(var)
#
#     # 3. 应用插值
#     if interp_lon is not None and interp_lat is not None:
#         for var, da in data_dict.items():
#             data_dict[var] = da.interp(lon=interp_lon, lat=interp_lat)
#
#     # 4. 提取结果
#     result = {}
#     if lon is not None and lat is not None:
#         for var, da in data_dict.items():
#             result[var] = da.sel(lon=lon, lat=lat, method="nearest")
#             if get_values:
#                 result[var] = result[var].values
#     else:
#         for var, da in data_dict.items():
#             result[var] = da.values if get_values else da
#
#     return result


def get_cams_chms(
        year=None,
        month=None,
        day=None,
        hour=None,
        vars=["PM10", "PM25", "AOD"],
        get_values=True,
        interp_lon=None,
        interp_lat=None,
        around_radius=0,
        file_structure_fcst00H="/mnt/external_disk0/ECMWF-CAMS/fcst-00H/{YYYY}-{MM}-{DD}.grib",
        file_structure_fcst12H="/mnt/external_disk0/ECMWF-CAMS/fcst-12H/{YYYY}-{MM}-{DD}.grib"
):
    """
    获取 ECMWF CAMS 化学成分数据（PM10, PM2.5, AOD 等）

    参数:
        year, month, day, hour: 时间
        vars: 变量列表（如 "PM10", "PM25", "AOD" 等）
        get_values: 是否返回 numpy 值 (默认为 True)
        interp_lon / interp_lat: 精确插值位置（可选）
        around_radius: 周边方阵半径（0=只中心，1=3x3，21=43x43 等）
        file_structure_fcst00H / fcst12H: 00Z 和 12Z 预报文件路径模板

    返回:
        dict，key 格式：
          - 中心: "PM25"
          - 偏移: "PM25_shift_lat±i_lon±j"
    """
    if around_radius < 0:
        raise ValueError("around_radius 必须为非负整数")

    # 时间处理
    year = int(year) if year is not None else datetime.now().year
    month = int(month) if month is not None else 1
    day = int(day) if day is not None else 1
    hour = int(hour) if hour is not None else 0

    current_date = datetime(year=year, month=month, day=day, hour=hour)

    # 生成所有偏移组合
    shifts = [(di, dj) for di in range(-around_radius, around_radius + 1)
              for dj in range(-around_radius, around_radius + 1)]

    use_interp = interp_lon is not None and interp_lat is not None
    if not use_interp and around_radius > 0:
        raise ValueError("未提供 interp_lon 和 interp_lat 时，around_radius 必须为 0")

    # CAMS GRIB 中的原始变量名映射（这里直接使用传入的 vars 名）
    # 注意：函数假设传入的 vars 就是 GRIB 文件中的变量名（如 pm2p5 → PM25 已在前处理中重命名）
    grib_var_map = {
        "PM10": "pm10",
        "PM25": "pm2p5",
        "AOD": "aod550",
        "columnO3": "gtco3",
        "columnCH2O": "tchcho",
        "columnNO2": "tcno2",
    }

    result = {}

    for base_var in vars:
        if base_var not in grib_var_map:
            raise KeyError(f"不支持的 CAMS 变量: {base_var}（目前支持 PM10, PM25, AOD）")

        grib_var_name = grib_var_map[base_var]

        # ===== 智能选择文件和 step =====
        if 6 <= hour <= 17:
            # 06-17 时使用当天 00Z 预报
            file_path = file_structure_fcst00H.format(
                YYYY=year, MM=f"{month:02d}", DD=f"{day:02d}"
            )
            step = hour  # 06H → step=6
        elif 18 <= hour <= 23:
            # 18-23 时使用当天 12Z 预报
            file_path = file_structure_fcst12H.format(
                YYYY=year, MM=f"{month:02d}", DD=f"{day:02d}"
            )
            step = hour - 12
        else:
            # 00-05 时使用前一天 12Z 预报
            prev_date = current_date - timedelta(days=1)
            file_path = file_structure_fcst12H.format(
                YYYY=prev_date.year,
                MM=f"{prev_date.month:02d}",
                DD=f"{prev_date.day:02d}"
            )
            step = hour + 12  # 00H → step=12

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CAMS 数据文件不存在: {file_path}")

        # 打开文件并提取指定 step 和变量
        with xr.open_dataset(file_path, backend_kwargs={'indexpath': ''}) as ds:
            ds = ds.rename({'longitude': 'lon', 'latitude': 'lat'})
            da_full = ds[grib_var_name].isel(step=step)

            # PM 类变量单位转换：μg/m³ → ng/m³ (×1e9)
            if base_var.startswith("PM"):
                da_full = da_full * 1e9

            if use_interp:
                # 先插值到精确位置 → 单点 DataArray
                da_center = da_full.interp(lon=interp_lon, lat=interp_lat, method="linear")
            else:
                # 返回全局场
                da_center = da_full

            # 为每个偏移生成结果
            for di, dj in shifts:
                if di == 0 and dj == 0:
                    da_shifted = da_center
                    var_name = base_var
                else:
                    da_shifted = da_center.shift(lat=di, lon=dj)  # 边界自动 nan
                    sign_i = "+" if di >= 0 else "-"
                    sign_j = "+" if dj >= 0 else "-"
                    var_name = f"{base_var}_shift_lat{sign_i}{abs(di)}_lon{sign_j}{abs(dj)}"

                da_shifted = da_shifted.rename(var_name)

                if get_values:
                    result[var_name] = da_shifted.values  # 标量 / 小数组 / 全局数组
                else:
                    result[var_name] = da_shifted

    return result



def get_geos_asm(
        year=None,
        month=None,
        day=None,
        hour=None,
        minute=None,
        lon=None,
        lat=None,
        get_values=True,
        interp_lon=None,
        interp_lat=None,
        file_structure="/mnt/external_disk1/GOES-FP/GEOS.fp.asm.{type}/GEOS.fp.asm.{type}.{YYYYMMDD}_{HHMM}.V01.hdf",
        vars={
            "tavg3_2d_aer_Nx": ['BCEXTTAU', 'BCSMASS', 'DUEXTTAU', 'DUSMASS', 'OCEXTTAU',
                                'OCSMASS', 'SO4SMASS', 'SSEXTTAU', 'SSSMASS', 'SUEXTTAU',
                                'TOTEXTTAU', 'TOTSCATAU'],
            "tavg1_2d_flx_Nx": ['QLML', 'TLML', 'ULML', 'VLML', 'PRECTOT'],
            "tavg3_3d_asm_Nv": {"var": ["QV", "SLP", "T", "U", "V"],
                                "level": [45, 48, 51, 53, 56, 60, 63, 68, 72]}
        }
):
    """
    简化的GEOS数据获取函数，支持字典格式的变量配置
    """
    # 确保输入是整数
    year = int(year) if year else datetime.now().year
    month = int(month) if month else 1
    day = int(day) if day else 1
    hour = int(hour) if hour else 0
    minute = int(minute) if minute else 0

    # 构建数据字典
    data_dict = {}

    for data_type, var_config in vars.items():
        # 构建文件路径
        file_path = file_structure.format(
            type=data_type,
            YYYY=year,
            MM=f"{month:02d}",
            DD=f"{day:02d}",
            HH=f"{hour:02d}",
            MIN=f"{minute:02d}",
            YYYYMMDD=f"{year}{month:02d}{day:02d}",
            HHMM=f"{hour:02d}{minute:02d}"
        )

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"GEOS数据文件不存在: {file_path}")

        # 打开文件并读取数据
        with xr.open_dataset(file_path) as f:
            # 处理字典格式的变量配置
            if isinstance(var_config, dict) and "var" in var_config:
                var_list = var_config["var"]
                levels = var_config.get("level", None)

                for var in var_list:
                    if var in f.variables:
                        # 重命名坐标以保持一致性
                        da = f[var]

                        # 检查是否有高度维度
                        if 'lev' in da.dims:
                            # 处理有高度层的数据
                            target_levels = levels if levels is not None else da.lev.values

                            for lev in target_levels:
                                # 选择特定高度层
                                da_lev = da.sel(lev=lev)
                                # 创建变量_高度的键名
                                key = f"{var}_{int(lev)}"
                                data_dict[key] = da_lev
                        else:
                            # 没有高度层的变量直接存储
                            data_dict[var] = da
            else:
                # 向后兼容：处理列表格式的变量配置
                for var in var_config:
                    if var in f.variables:
                        da = f[var]
                        data_dict[var] = da

    # 应用插值（如果需要）
    if interp_lon is not None and interp_lat is not None:
        for var, da in data_dict.items():
            data_dict[var] = da.interp(lon=interp_lon, lat=interp_lat)

    # 提取结果
    result = {}
    if lon is not None and lat is not None:
        for var, da in data_dict.items():
            result[var] = da.sel(lon=lon, lat=lat, method="nearest")
            if get_values:
                result[var] = result[var].values
    else:
        for var, da in data_dict.items():
            result[var] = da.values if get_values else da

    return result



def get_retrieval(
        year=None,
        month=None,
        day=None,
        hour=None,
        vars=["VIS"],
        get_values=True,
        interp_lon=None,
        interp_lat=None,
        around_radius=0,
        file_structure="/mnt/external_disk0/Asian_{var_name}/{YYYYMMDDHH}.nc",
):
    """
    获取反演数据（如 VIS 等），每个变量一个独立的 .nc 文件

    参数:
        year, month, day, hour: 时间（用于构建路径）
        vars: 变量列表（如 ["VIS", "IR", "WV"]）
        get_values: 是否返回 numpy 值 (默认为 True)
        interp_lon / interp_lat: 精确插值位置（可选）
        around_radius: 周边方阵半径（0=只中心，1=3x3，21=43x43 等）
        file_structure: 文件路径模板，必须包含 {var_name} 和时间占位符

    返回:
        dict，key 格式：
          - 中心: "VIS"
          - 偏移: "VIS_shift_lat±i_lon±j"
        当 get_values=False 时，每个 DataArray 的 .name 与 key 一致
    """
    if around_radius < 0:
        raise ValueError("around_radius 必须为非负整数")

    # 时间处理
    year = int(year) if year is not None else datetime.now().year
    month = int(month) if month is not None else 1
    day = int(day) if day is not None else 1
    hour = int(hour) if hour is not None else 0

    # 生成所有偏移组合
    shifts = [(di, dj) for di in range(-around_radius, around_radius + 1)
              for dj in range(-around_radius, around_radius + 1)]

    use_interp = interp_lon is not None and interp_lat is not None
    if not use_interp and around_radius > 0:
        raise ValueError("未提供 interp_lon 和 interp_lat 时，around_radius 必须为 0")

    result = {}

    for base_var in vars:
        # 构建该变量的文件路径（替换 var_name）
        file_path = file_structure.format(
            var_name=base_var,
            YYYY=year,
            YY=str(year)[-2:],
            MM=f"{month:02d}",
            DD=f"{day:02d}",
            HH=f"{hour:02d}",
            YYYYMMDD=f"{year}{month:02d}{day:02d}",
            YYYYMMDDHH=f"{year}{month:02d}{day:02d}{hour:02d}"
        )

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"反演数据文件不存在: {file_path}")

        # 打开单个变量的 .nc 文件
        with xr.open_dataset(file_path) as ds:
            # 统一坐标名（防止不同文件坐标名不一致）
            if 'longitude' in ds.dims:
                ds = ds.rename({'longitude': 'lon', 'latitude': 'lat'})
            elif 'x' in ds.dims and 'y' in ds.dims:
                ds = ds.rename({'x': 'lon', 'y': 'lat'})

            if base_var not in ds:
                raise KeyError(f"变量 {base_var} 不存在于文件 {file_path}")

            da_base = ds[base_var]

            if use_interp:
                # 先插值到精确位置 → 单点 DataArray
                da_center = da_base.interp(lon=interp_lon, lat=interp_lat, method="linear")
            else:
                # 返回全局场
                da_center = da_base

            # 为每个偏移生成结果
            for di, dj in shifts:
                if di == 0 and dj == 0:
                    da_shifted = da_center
                    var_name = base_var
                else:
                    da_shifted = da_center.shift(lat=di, lon=dj)  # 边界自动 nan
                    sign_i = "+" if di >= 0 else "-"
                    sign_j = "+" if dj >= 0 else "-"
                    var_name = f"{base_var}_shift_lat{sign_i}{abs(di)}_lon{sign_j}{abs(dj)}"

                # 关键：确保 DataArray 的 name 与字典 key 一致
                da_shifted = da_shifted.rename(var_name)

                if get_values:
                    result[var_name] = da_shifted.values  # 标量 / 小数组 / 全局数组
                else:
                    result[var_name] = da_shifted  # name 已正确设置

    return result





if __name__ == "__main__":

    interp_lon = np.arange(70, 140.1, 0.1)
    interp_lat = np.arange(10, 50.1, 0.1)

    # # 测试气象场数据读取
    # data = get_cra_surface_meteos(
    #     2013,
    #     1,
    #     1,
    #     0,
    #     get_values=False,
    #     around_radius=10,
    #     interp_lon=interp_lon,
    #     interp_lat=interp_lat,
    #     file_structure="/data/CRA/surface/{YYYY}/{YYYYMMDD}/ART_ATM_GLB_0P10_6HOR_SANL_{YYYYMMDDHH}.grib2",
    # )
    # print("debug")
    # data = get_cra_surface_80m_meteos(
    #     2013,
    #     1,
    #     1,
    #     12,
    #     get_values=False,
    #     around_radius=10,
    #     interp_lon=interp_lon,
    #     interp_lat=interp_lat,
    #     file_structure="/data2/CRA/surface_80m/{YYYY}/{YYYYMM}/{YYYYMMDD}/ART_ATM_GLB_0P10_1HOR_ANAL_{YYYYMMDDHH}_{VAR}.grib2",
    # )
    # print("debug")

    # # 测试排放数据读取
    # data = get_gem_emissions(1980, 1, lon=100, lat=50, get_values=True, interp_lon=interp_lon, interp_lat=interp_lat, add_arounds=True)

    # # 测试CAMS化学场数据读取
    # data = get_cams_chms(2016, 7, 2, 7, get_values=True, around_radius=10, interp_lon=interp_lon, interp_lat=interp_lat)
    # print("debug")

    # # 测试气象场数据读取
    # data = get_cra_atmos_meteos(2013, 1, 1, 0, get_values=False, around_radius=10, interp_lon=interp_lon, interp_lat=interp_lat)
    # print("debug")

    # # 测试读取GEOS-FP数据
    # data = get_geos_asm(
    #     2015, 1, 1, 1, 30,
    #     get_values=False
    # )

    # dem = get_dem(
    #     get_values=False,
    #     interp_lon=np.arange(70, 140, 0.1),
    #     interp_lat=np.arange(10, 60, 0.1),
    #     around_radius=10,
    # )
    #
    # print("debug")

    data = get_retrieval(
        year=2017,
        month=1,
        day=1,
        hour=1,
        vars=["VIS"],
        interp_lon=interp_lon,
        interp_lat=interp_lat,
        around_radius=0,
        get_values=False
    )

    print("debug")



