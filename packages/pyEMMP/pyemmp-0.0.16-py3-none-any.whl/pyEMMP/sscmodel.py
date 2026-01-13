import xml.etree.ElementTree as ET
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
from typing import List
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import traceback

from .adcp import ADCP as ADCPDataset
from .obs import OBS as OBSDataset
from .watersample import WaterSample as WaterSampleDataset
from .utils_xml import XMLUtils
from .plotting import PlottingShell

import numpy as np
import pandas as pd


def NTU2SSC(project: ET.Element, sscmodel: ET.Element) -> dict:
    time_mappers = {"Second": "S", "Minute": "min", "Hour": "h", "Day": "D"}
    proj_xml = XMLUtils(project)
    ssc_params = {}
    mode = sscmodel.find("Mode").text
    if mode == "Manual":
        A = float(sscmodel.find("A").text)
        B = float(sscmodel.find("B").text)
        ssc_params['A'] = A
        ssc_params['B'] = B
        return ssc_params
    elif mode == "Auto":
        depth_threshold = XMLUtils._get_value(sscmodel, "DepthThreshold", None)
        if depth_threshold is not None:
            depth_threshold = float(depth_threshold)
        time_threshold = XMLUtils._get_value(sscmodel, "TimeThreshold", None)
        time_threshold_unit = XMLUtils._get_value(sscmodel, "TimeThresholdUnit", "Second")
        if time_threshold is not None:
            time_threshold = f"{float(time_threshold)}{time_mappers.get(time_threshold_unit, 'S')}"
        obss = []
        obsIDs = []
        watersamples = []
        watersampleIDs = []
        for inst in sscmodel.findall("Instrument"):
            inst_id = inst.find("ID").text
            inst_type = inst.find("Type").text
            if inst_type == "OBSVerticalProfile":
                cfg = proj_xml.get_cfg_by_instrument(inst_type, None, inst_id, add_ssc=False)
                obss.append(OBSDataset(cfg))
                obsIDs.append(inst_id)
            elif inst_type == "WaterSample":
                watersamples.append(WaterSampleDataset(proj_xml.find_element(elem_id=inst_id, _type=inst_type)))
                watersampleIDs.append(inst_id)
        if len(watersamples) == 0:
            return {"Error": "No water samples found for SSC calibration"}
        if len(obss) == 0:
            return {"Error": "No OBS data found for SSC calibration"}
        df_obs = combine_obs(obss, obsIDs)
        df_water = combine_watersamples(watersamples, watersampleIDs)
        parameters = calculate_params(x_df=df_obs,
                                      x_col_name="ntu",
                                      x_id_name="NTU",
                                      water_df=df_water,
                                      ssc_col_name="ssc",
                                      ssc_id_name="SSC",
                                      time_tolerance=time_threshold,
                                      depth_tolerance=depth_threshold,
                                      fit_intercept=False,
                                      relation="linear",
                                      weighted=True)

        for key, value in parameters.items():
            ssc_params[key] = value
        return ssc_params

def PlotNTU2SSC(project: ET.Element, sscmodelid: str, title: str = None):
    proj_xml = XMLUtils(project)
    settings, _ = proj_xml.parse_settings()
    sscmodel = proj_xml.find_element(elem_id=sscmodelid, _type='NTU2SSC')
    if sscmodel is None:
        return {"Error": f"No NTU2SSC model found with ID {sscmodelid}"}
    try:
        A = float(sscmodel.find("A").text)
        B = float(sscmodel.find("B").text)
        RMSE = float(sscmodel.find("RMSE").text)
        R2 = float(sscmodel.find("R2").text)

        # Extract data points
        ssc = []
        ntu = []
        for pt in sscmodel.find("Data").findall("Point"):
            ssc.append(float(pt.find("SSC").text))
            ntu.append(float(pt.find("NTU").text))
        ssc = np.array(ssc)
        ntu = np.array(ntu)

        fig, ax = PlottingShell.subplots(figheight=8, figwidth=8)
        ax.scatter(ntu, ssc, color="black", marker="s", s=10, facecolor="none")
        all_data = np.concatenate([ssc, ntu])
        lims = nice_log_limits(all_data)
        x = np.linspace(lims[0], lims[1], 100)
        y = B * x + A
        ax.plot(x, y, label=fr'Linear Model: $y={B:.2f}x$', color=PlottingShell.gray3)
        model_info = fr'$n={len(ntu)}$'+'\n'+fr'$RMSE={RMSE:.2f}$'+'\n'+fr'$R^2={R2:.2f}$'
        ax.text(0.95, 0.05, model_info, transform=ax.transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.5))

        ax.legend(fontsize=10)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('NTU', fontsize=10)
        ax.set_ylabel('SSC (mg/L)', fontsize=10)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.grid(True, lw=0.5, color=PlottingShell.gray1, alpha=0.5)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:g}'))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:g}'))
        ax.tick_params(axis='both', which='major', labelsize=10)
        title = settings["name"] if title is None else title
        ax.set_title(title)
        
        plt.show()
        return {"Result": "Success"}
    except Exception as e:
        return {"Error": str(e)}

def BKS2SSC(project: ET.Element, sscmodel: ET.Element) -> dict:
    time_mappers = {"Second": "S", "Minute": "min", "Hour": "h", "Day": "D"}
    proj_xml = XMLUtils(project)
    ssc_params = {}
    mode = sscmodel.find("Mode").text
    if mode == "Manual":
        A = float(sscmodel.find("A").text)
        B = float(sscmodel.find("B").text)
        ssc_params['A'] = A
        ssc_params['B'] = B
        return ssc_params
    elif mode == "Auto":
        depth_threshold = XMLUtils._get_value(sscmodel, "DepthThreshold", None)
        if depth_threshold is not None:
            depth_threshold = float(depth_threshold)
        time_threshold = XMLUtils._get_value(sscmodel, "TimeThreshold", None)
        time_threshold_unit = XMLUtils._get_value(sscmodel, "TimeThresholdUnit", "Second")
        if time_threshold is not None:
            time_threshold = f"{float(time_threshold)}{time_mappers.get(time_threshold_unit, 'S')}"
        adcps = []
        adcpIDs = []
        watersamples = []
        watersampleIDs = []
        for inst in sscmodel.findall("Instrument"):
            inst_id = inst.find("ID").text
            inst_type = inst.find("Type").text
            if inst_type == "VesselMountedADCP":
                cfg = proj_xml.get_cfg_by_instrument("VesselMountedADCP", instrument_id=inst_id, add_ssc=False)
                adcps.append(ADCPDataset(cfg))
                adcpIDs.append(inst_id)
            elif inst_type == "WaterSample":
                watersamples.append(WaterSampleDataset(proj_xml.find_element(elem_id=inst_id, _type=inst_type)))
                watersampleIDs.append(inst_id)
        if len(watersamples) == 0:
            return {"Error": "No water samples found for SSC calibration"}
        if len(adcps) == 0:
            return {"Error": "No ADCP data found for SSC calibration"}
        df_adcp = combine_adcps(adcps, adcpIDs)
        df_adcp["depth"] = -df_adcp["depth"]  # Convert to positive down
        df_adcp = df_adcp.sort_values("datetime")
        df_water = combine_watersamples(watersamples, watersampleIDs)

        parameters = calculate_params(x_df=df_adcp,
                                      x_col_name="bks",
                                      x_id_name="AbsoluteBackscatter",
                                      water_df=df_water,
                                      ssc_col_name="ssc",
                                      ssc_id_name="SSC",
                                      time_tolerance=time_threshold,
                                      depth_tolerance=depth_threshold,
                                      fit_intercept=True,
                                      relation="loglinear",
                                      weighted=True)

        for key, value in parameters.items():
            ssc_params[key] = value
        
        return ssc_params

def PlotBKS2SSC(project: ET.Element, sscmodelid: str, title: str) -> dict:
    proj_xml = XMLUtils(project)
    settings, _ = proj_xml.parse_settings()
    sscmodel = proj_xml.find_element(elem_id=sscmodelid, _type='BKS2SSC')
    if sscmodel is None:
        return {"Error": f"No BKS2SSC model found with ID {sscmodelid}"}
    try:
        A = float(sscmodel.find("A").text)
        B = float(sscmodel.find("B").text)
        RMSE = float(sscmodel.find("RMSE").text)
        R2 = float(sscmodel.find("R2").text)

        # Extract data points
        ssc = []
        bks = []
        for pt in sscmodel.find("Data").findall("Point"):
            ssc.append(float(pt.find("SSC").text))
            bks.append(float(pt.find("AbsoluteBackscatter").text))
        ssc = 10 ** (np.array(ssc))
        bks = np.array(bks)

        fig, ax = PlottingShell.subplots(figheight=8, figwidth=8)
        ax.scatter(bks, ssc, color='black', marker='s', s=10, facecolor='none')
        ylim = nice_log_limits(ssc)

        y = np.linspace(ylim[0], ylim[-1], 100)
        x = (np.log10(y) - A) / B
        ax.plot(x, y, label=fr'$\log_{{10}}(y) = {A:.3f} + {B:.3f}x$', color=PlottingShell.gray3)
        ax.set_yscale('log')
        ax.set_xlim(np.min(x), np.max(x))
        ax.set_ylim(ylim)
        ax.legend(fontsize=10)
        ax.set_ylabel('SSC (mg/L)', fontsize=10)
        ax.set_xlabel('Absolute Backscatter', fontsize=10)
        model_info = fr'$n={len(bks)}$'+'\n'+fr'$RMSE={RMSE:.2f}$'+'\n'+fr'$R^2={R2:.2f}$'
        ax.text(0.05, 0.95, model_info, transform=ax.transAxes, fontsize=10, verticalalignment='top', horizontalalignment='left',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.5))
        ax.grid(True, lw=0.5, color=PlottingShell.gray1, alpha=0.5)
        title = settings["name"] if title is None else title
        ax.set_title(title)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:g}'))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:g}'))
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        plt.show()
        return {"Result": "Success"}
    except Exception as e:
        return {"Error": str(e)}

def PlotBKS2SSCTrans(project, sscmodelid, beam_sel, field_name, yAxisMode, cmap, vmin, vmax, title, mask):
    field_name_map = {
        "Velocity": "velocity",
        "Echo Intensity": "echo_intensity",
        "Correlation Magnitude": "correlation_magnitude",
        "Percent Good": "percent_good",
        "Absolute Backscatter": "absolute_backscatter",
        "Alpha S": "alpha_s",
        "Alpha W": "alpha_w",
        "Signal to Noise Ratio": "signal_to_noise_ratio",
        "SSC": "suspended_solids_concentration",
    }
    try:
        proj_xml = XMLUtils(project)
        sscmodel = proj_xml.find_element(elem_id=sscmodelid, _type='BKS2SSC')
        if sscmodel is None:
            return {"Error": f"No BKS2SSC model found with ID {sscmodelid}"}
        pairs = sscmodel.find("Pairs").findall("Pair")
        for pair in pairs:
            water_sample_id = pair.find("WaterSample").text
            adcp_id = pair.find("VesselMountedADCP").text
            if water_sample_id is None or adcp_id is None:
                return {"Error": "No valid WaterSample-ADCP pairs found in the SSC model"}
            adcp_cfg = proj_xml.get_cfg_by_instrument("VesselMountedADCP", instrument_id=adcp_id, add_ssc=False)
            adcp_cfg['ssc_params']['A'] = float(sscmodel.find("A").text)
            adcp_cfg['ssc_params']['B'] = float(sscmodel.find("B").text)
            if 'Error' in adcp_cfg.keys():
                return adcp_cfg
            water_sample_cfg = proj_xml.find_element(elem_id=water_sample_id, _type="WaterSample")
            if water_sample_cfg is None:
                return {"Error": f"No WaterSample found with ID {water_sample_id}"}
            adcp = ADCPDataset(adcp_cfg)
            water_sample = WaterSampleDataset(water_sample_cfg)

            fig, (ax, ax_cbar) = adcp.plot.single_beam_flood_plot(
                beam = beam_sel,
                field_name = field_name_map[field_name],
                y_axis_mode = yAxisMode.lower(),
                cmap = cmap,
                vmin = vmin,
                vmax = vmax,
                n_time_ticks = 6,
                title = title, 
                mask = mask
                )
            t_num = mdates.date2num(water_sample.data.datetime.astype("M8[ms]").astype("O"))
            x_min, x_max = ax.get_xlim()
            y_min, y_max = ax.get_ylim()
            t_mask = (t_num >= x_min) & (t_num <= x_max) & (water_sample.data.depth >= min(y_min, y_max)) & (water_sample.data.depth <= max(y_min, y_max))

            # Filter data
            t_num = t_num[t_mask]
            depth = water_sample.data.depth[t_mask]
            sample = water_sample.data.sample[t_mask]
            if len(t_num) == 0:
                plt.close(fig)
                continue
            ax.scatter(t_num, depth, marker="*", zorder=100, label="Water Samples", s=20)
            for t, d, s in zip(t_num, depth, sample):
                ax.text(t, d, s, va="bottom", ha="center", fontsize=7,
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.7))
            fig.canvas.draw()
            ax.legend(loc="lower right", fontsize=8)
        plt.show()
        return {"Result": str(adcp._cfg)}
    except Exception as e:
        tb_str = traceback.format_exc()
        return {"Error": tb_str + "\n" + str(e)}

def BKS2NTU(project: ET.Element, sscmodel: ET.Element) -> dict:
    time_mappers = {"Second": "S", "Minute": "min", "Hour": "h", "Day": "D"}
    proj_xml = XMLUtils(project)
    ssc_params = {}
    mode = sscmodel.find("Mode").text
    if mode == "Manual":
        A = float(sscmodel.find("A").text)
        B = float(sscmodel.find("B").text)
        ssc_params['A'] = A
        ssc_params['B'] = B
        return ssc_params
    elif mode == "Auto":
        depth_threshold = XMLUtils._get_value(sscmodel, "DepthThreshold", None)
        if depth_threshold is not None:
            depth_threshold = float(depth_threshold)
        time_threshold = XMLUtils._get_value(sscmodel, "TimeThreshold", None)
        time_threshold_unit = XMLUtils._get_value(sscmodel, "TimeThresholdUnit", "Second")
        if time_threshold is not None:
            time_threshold = f"{float(time_threshold)}{time_mappers.get(time_threshold_unit, 'S')}"
        adcps = []
        adcpIDs = []
        obss = []
        obsIDs = []
        for inst in sscmodel.findall("Instrument"):
            inst_id = inst.find("ID").text
            inst_type = inst.find("Type").text
            if inst_type == "VesselMountedADCP":
                cfg = proj_xml.get_cfg_by_instrument(inst_type, instrument_id=inst_id, add_ssc=False)
                adcps.append(ADCPDataset(cfg))
                adcpIDs.append(inst_id)
            elif inst_type == "OBSVerticalProfile":
                cfg = proj_xml.get_cfg_by_instrument(inst_type, None, inst_id, add_ssc=True)
                obss.append(OBSDataset(cfg))
                obsIDs.append(inst_id)
        if len(obss) == 0:
            return {"Error": "No OBSVerticalProfile found for SSC calibration"}
        if len(adcps) == 0:
            return {"Error": "No ADCP data found for SSC calibration"}
        df_adcp = combine_adcps(adcps, adcpIDs)
        df_adcp["depth"] = -df_adcp["depth"]  # Convert to positive down
        df_adcp = df_adcp.sort_values("datetime")
        df_obs = combine_obs(obss, obsIDs, by_ssc=True)

        parameters = calculate_params(x_df=df_adcp,
                                      x_col_name="bks",
                                      x_id_name="AbsoluteBackscatter",
                                      water_df=df_obs,
                                      ssc_col_name="ntu",
                                      ssc_id_name="SSC",
                                      time_tolerance=time_threshold,
                                      depth_tolerance=depth_threshold,
                                      fit_intercept=True,
                                      relation="loglinear",
                                      weighted=True)
        
        for key, value in parameters.items():
            ssc_params[key] = value
        for key, value in ssc_params.items():
            print(f"{key}: {value}")
        
        return ssc_params

def PlotBKS2NTU(project: ET.Element, sscmodelid: str, title: str) -> dict:
    proj_xml = XMLUtils(project)
    settings, _ = proj_xml.parse_settings()
    sscmodel = proj_xml.find_element(elem_id=sscmodelid, _type='BKS2NTU')
    if sscmodel is None:
        return {"Error": f"No BKS2NTU model found with ID {sscmodelid}"}
    try:
        A = float(sscmodel.find("A").text)
        B = float(sscmodel.find("B").text)
        RMSE = float(sscmodel.find("RMSE").text)
        R2 = float(sscmodel.find("R2").text)

        # Extract data points
        ssc = []
        bks = []
        for pt in sscmodel.find("Data").findall("Point"):
            ssc.append(float(pt.find("SSC").text))
            bks.append(float(pt.find("AbsoluteBackscatter").text))
        ssc = 10 ** (np.array(ssc))
        bks = np.array(bks)

        fig, ax = PlottingShell.subplots(figheight=8, figwidth=8)
        ax.scatter(bks, ssc, color='black', marker='s', s=10, facecolor='none')
        ylim = nice_log_limits(ssc)

        y = np.linspace(ylim[0], ylim[-1], 100)
        x = (np.log10(y) - A) / B
        ax.plot(x, y, label=fr'$\log_{{10}}(y) = {A:.3f} + {B:.3f}x$', color=PlottingShell.gray3)
        ax.set_yscale('log')
        ax.set_xlim(np.min(x), np.max(x))
        ax.set_ylim(ylim)
        ax.legend(fontsize=10)
        ax.set_ylabel('SSC (mg/L)', fontsize=10)
        ax.set_xlabel('Absolute Backscatter', fontsize=10)
        model_info = fr'$n={len(bks)}$'+'\n'+fr'$RMSE={RMSE:.2f}$'+'\n'+fr'$R^2={R2:.2f}$'
        ax.text(0.05, 0.95, model_info, transform=ax.transAxes, fontsize=10, verticalalignment='top', horizontalalignment='left',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.5))
        ax.grid(True, lw=0.5, color=PlottingShell.gray1, alpha=0.5)
        title = settings["name"] if title is None else title
        ax.set_title(title)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:g}'))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:g}'))
        ax.tick_params(axis='both', which='major', labelsize=10)
        plt.show()
        return {"Result": "Success"}
    except Exception as e:
        return {"Error": str(e)}

def PlotBKS2NTUTrans(project, sscmodelid, beam_sel, field_name, yAxisMode, cmap, vmin, vmax, title, mask):
    field_name_map = {
        "Velocity": "velocity",
        "Echo Intensity": "echo_intensity",
        "Correlation Magnitude": "correlation_magnitude",
        "Percent Good": "percent_good",
        "Absolute Backscatter": "absolute_backscatter",
        "Alpha S": "alpha_s",
        "Alpha W": "alpha_w",
        "Signal to Noise Ratio": "signal_to_noise_ratio",
        "SSC": "suspended_solids_concentration",
    }
    try:
        proj_xml = XMLUtils(project)
        sscmodel = proj_xml.find_element(elem_id=sscmodelid, _type='BKS2NTU')
        if sscmodel is None:
            return {"Error": f"No BKS2NTU model found with ID {sscmodelid}"}
        pairs = sscmodel.find("Pairs").findall("Pair")
        for pair in pairs:
            obs_id = pair.find("OBSVerticalProfile").text
            adcp_id = pair.find("VesselMountedADCP").text
            if obs_id is None or adcp_id is None:
                return {"Error": "No valid OBS-ADCP pairs found in the SSC model"}
            adcp_cfg = proj_xml.get_cfg_by_instrument("VesselMountedADCP", instrument_id=adcp_id, add_ssc=False)
            adcp_cfg['ssc_params']['A'] = float(sscmodel.find("A").text)
            adcp_cfg['ssc_params']['B'] = float(sscmodel.find("B").text)
            if 'Error' in adcp_cfg.keys():
                return adcp_cfg
            obs_cfg = proj_xml.get_cfg_by_instrument("OBSVerticalProfile", instrument_id=obs_id, add_ssc=True)
            if 'Error' in obs_cfg.keys():
                return obs_cfg
            adcp = ADCPDataset(adcp_cfg)
            obs = OBSDataset(obs_cfg)
            fig, (ax, ax_cbar) = adcp.plot.single_beam_flood_plot(
                beam = beam_sel,
                field_name = field_name_map[field_name],
                y_axis_mode = yAxisMode.lower(),
                cmap = cmap,
                vmin = vmin,
                vmax = vmax,
                n_time_ticks = 6,
                title = title, 
                mask = mask
                )
            t_num = mdates.date2num(obs.data.datetime.astype("M8[ms]").astype("O"))
            depth = obs.data.depth
            if yAxisMode.lower() == "depth":
                depth = -depth  # Convert to positive down
            x_min, x_max = ax.get_xlim()
            y_min, y_max = ax.get_ylim()
            data_mask = (t_num >= x_min) & (t_num <= x_max) & (depth >= min(y_min, y_max)) & (depth <= max(y_min, y_max))
            im = ax.images[0]
            norm = im.norm
            cmap = im.cmap

            # Filter data
            t_num = t_num[data_mask]
            depth = depth[data_mask]
            if len(t_num) == 0:
                plt.close(fig)
                continue
            ssc = obs.data.ssc[data_mask]
            ax.scatter(t_num, depth, marker="*", zorder=100, label=obs.name, s=20, c=ssc, cmap=cmap, norm=norm)
            fig.canvas.draw()
            ax.legend(loc="lower right", fontsize=8)
        plt.show()
        return {"Result": str(adcp._cfg)}
    except Exception as e:
        tb_str = traceback.format_exc()
        return {"Error": tb_str + "\n" + str(e)}

# -- Helper functions for sscmodel.py --

def combine_adcps(adcp_list: List[ADCPDataset], adcp_ids: List[str]):
    dfs = []
    for i, adcp in enumerate(adcp_list):
        datetimes = adcp.time.ensemble_datetimes
        abs_bks = adcp.get_beam_data(field_name="absolute_backscatter", mask=True)
        depths = adcp.geometry.geographic_beam_midpoint_positions.z
        abs_bks = np.nanmean(abs_bks, axis=2)  # average across beams (n_ensembels, n_bins, n_beams) -> (n_ensembles * n_bins * n_beams)
        depths = np.nanmean(depths, axis=2)  # average across beams
        datetimes = np.repeat(datetimes[:, None], abs_bks.shape[1], axis=1)
        df = pd.DataFrame({
            "datetime": datetimes.ravel(),
            "depth": depths.ravel(),
            "bks": abs_bks.ravel(),
            "id": adcp_ids[i],
            "type": "VesselMountedADCP"
        })
        dfs.append(df)
    output = pd.concat(dfs, ignore_index=True)
    output = output.dropna(subset=["bks"])
    return output

def combine_obs(obs_list: List[OBSDataset], obs_ids: List[str], by_ssc: bool = False):
    dfs = []
    for i, obs in enumerate(obs_list):
        if by_ssc:
            data = obs.data.ssc
        else:
            data = obs.data.ntu
        df = pd.DataFrame({
            "datetime": obs.data.datetime,
            "depth": obs.data.depth,
            "ntu": data,
            "id": obs_ids[i],
            "type": "OBSVerticalProfile"
        })
        dfs.append(df)
    output = pd.concat(dfs, ignore_index=True)
    output = output.dropna(subset=["ntu"])
    return output

def combine_watersamples(water_list: List[WaterSampleDataset], water_ids: List[str]):
    dfs = []
    for i, water in enumerate(water_list):
        df = pd.DataFrame({
            "datetime": water.data.datetime,
            "depth": water.data.depth,
            "ssc": water.data.ssc,
            "id": water_ids[i],
            "type": "WaterSample"
        })
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def match_datasets(
    df1: pd.DataFrame,
    df_water: pd.DataFrame,
    time_col: str = "datetime",
    depth_col: str = "depth",
    value_col: str = "ntu",
    time_tolerance: str | pd.Timedelta = "5min",
    depth_tolerance: float = 0.5,
    out_value_col: str = "ntu_mean",
    out_depth_col: str = "depth_mean_df1",
    out_time_col: str = "datetime_mean_df1",
    out_count_col: str = "match_count"
) -> pd.DataFrame:
    df1 = df1.copy()
    df2 = df_water.copy()
    df1[time_col] = pd.to_datetime(df1[time_col])
    df2[time_col] = pd.to_datetime(df2[time_col])

    df1 = df1.sort_values(time_col).reset_index(drop=True)

    t1 = df1[time_col].to_numpy().astype("int64")  # ns since epoch
    z1 = df1[depth_col].to_numpy()
    v1 = df1[value_col].to_numpy()
    ids1 = df1["id"].to_numpy()

    dt_ns = pd.to_timedelta(time_tolerance).value
    dz = float(depth_tolerance)

    n = len(df2)
    out_val = np.full(n, np.nan).astype(float)
    out_dep = np.full(n, np.nan).astype(float)
    out_tim = np.full(n, np.datetime64("NaT")).astype("datetime64[ns]")
    out_cnt = np.zeros(n).astype(int)
    out_ids = [None] * n

    t2 = df2[time_col].to_numpy().astype("int64")  # ns since epoch
    z2 = df2[depth_col].to_numpy()

    left_idx = np.searchsorted(t1, t2 - dt_ns, side="left")
    right_idx = np.searchsorted(t1, t2 + dt_ns, side="right")

    for i, (L, R) in enumerate(zip(left_idx, right_idx)):
        if L >= R:
            continue
        slice_depths = z1[L:R]
        m = np.abs(slice_depths - z2[i]) <= dz
        if not m.any():
            continue

        out_cnt[i] = int(m.sum())
        out_val[i] = np.nanmean(v1[L:R][m])
        out_dep[i] = np.nanmean(slice_depths[m])
        matched_ids = np.unique(ids1[L:R][m]).tolist()
        out_ids[i] = matched_ids

        # average datetime (in ns) from df1 matches
        mean_ns = int(np.round(np.mean(t1[L:R][m].astype(np.float64))))
        out_tim[i] = np.datetime64(mean_ns, "ns")

    df2[out_value_col] = out_val
    df2[out_depth_col] = out_dep
    df2[out_time_col] = out_tim
    df2[out_count_col] = out_cnt
    df2["matched_ids"] = out_ids
    return df2

def calculate_params(x_df: pd.DataFrame,
                     x_col_name: str,
                     x_id_name: str,
                     water_df: pd.DataFrame,
                     ssc_col_name: str,
                     ssc_id_name: str,
                     time_tolerance: str,
                     depth_tolerance: float,
                     fit_intercept: bool,
                     relation: str,
                     weighted: bool):
    mapper = {'ssc': 'WaterSample', 'ntu': 'OBSVerticalProfile', 'bks': 'VesselMountedADCP'}
    np.set_printoptions(threshold=np.inf)

    df_water_matched = match_datasets(df1=x_df,
                                      df_water=water_df,
                                      time_col="datetime",
                                      depth_col="depth",
                                      value_col=x_col_name,
                                      time_tolerance=time_tolerance,
                                      depth_tolerance=depth_tolerance,
                                      out_value_col=f"{x_col_name}_mean",
                                      out_depth_col="depth_mean",
                                      out_time_col="datetime_mean",
                                      out_count_col="match_count")
    df_water_matched = df_water_matched.dropna(subset=[f"{x_col_name}_mean", ssc_col_name])
    x_vals = df_water_matched[f"{x_col_name}_mean"].to_numpy()
    y_vals = df_water_matched[ssc_col_name].to_numpy()
    
    if len(y_vals) == 0:
        return {"Error": "No valid data points found for SSC calibration"}
    if relation == "linear":
        y_vals = df_water_matched[ssc_col_name].to_numpy()
    else:
        y_vals = np.log10(df_water_matched[ssc_col_name].to_numpy())
    X = x_vals.reshape(-1, 1)
    Y = y_vals.reshape(-1, 1)
    if weighted:
        dt = (df_water_matched["datetime"] - df_water_matched["datetime_mean"]).dt.total_seconds().abs()
        reg = LinearRegression(fit_intercept=fit_intercept).fit(X, Y, sample_weight=1/(dt+1))  # add 1 to avoid division by zero
    else:
        reg = LinearRegression(fit_intercept=fit_intercept).fit(X, Y)
    B = reg.coef_[0]
    if isinstance(B, list) or isinstance(B, np.ndarray):
        B = B[0]
    A = reg.intercept_
    if isinstance(A, list) or isinstance(A, np.ndarray):
        A = A[0]
    ssc_params = {}
    ssc_params['A'] = A
    ssc_params['B'] = B
    ssc_params['RMSE'] = np.sqrt(np.mean((A + x_vals * B - y_vals) ** 2))
    ssc_params['R2'] = reg.score(X, Y)
    ssc_params[x_id_name] = x_vals
    ssc_params[ssc_id_name] = y_vals
    
    typed_pairs = []
    for index, row in df_water_matched.iterrows():
        matched_ids = row["matched_ids"]
        if matched_ids is None:
            continue
        for mid in matched_ids:
            data = {mapper[x_col_name]: mid, mapper[ssc_col_name]: row["id"]}
            if data not in typed_pairs:
                typed_pairs.append(data)
    # Format nicely: {"WaterSample": 26, "VesselMountedADCP": 13}
    ssc_params["Pairs"] = str(typed_pairs)

    if len(ssc_params[x_id_name]) < 2:
        ssc_params['Error'] = "Not enough data points to perform regression. Please update depth and time thresholds and try again."
    return ssc_params

def nice_log_limits(data):
    finite = np.array(data)[np.isfinite(data) & (np.array(data) > 0)]
    if finite.size == 0:
        return 0.1, 100
    min_exp = np.floor(np.log10(finite.min()))
    max_exp = np.ceil(np.log10(finite.max()))
    return 10**min_exp, 10**max_exp

if __name__ == "__main__":
    project = r"C:\Users\abja\AppData\Roaming\PlumeTrack\Test Project 1.mtproj"
    sscmodelid = "26"
    project_xml = XMLUtils(project)
    print("Done")