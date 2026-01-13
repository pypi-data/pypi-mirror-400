# src/ptcal/calibrator.py

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from time import strftime
from pathlib import Path

from . import core
from .plotting import PtPlotter

class PtCalibrator:
    """
    Hauptklasse zur Kalibrierung.
    Verwaltet Daten, führt Fits durch (CVD & ITS-90) und steuert Plotting/Export.
    """

    def __init__(self, dataframe: pd.DataFrame, sensor_type: str = "AUTO"):
        """
        Initialisiert den Calibrator mit Rohdaten.
        
        Args:
            dataframe: Muss Spalten enthalten. Erwartet wird:
                       [SN, (Medium), Temp, Unsicherheit, Widerstand]
                       oder [SN, Temp, Unsicherheit, Widerstand]
            sensor_type: 'Pt100', 'Pt25', 'Pt10', 'Pt500', 'Pt1000' oder 'AUTO'
        """
        self.raw_data = dataframe.copy()
        
        # Spaltenbereinigung: Wir brauchen SN, Temp, Unsicherheit, Widerstand
        # Falls 5 Spalten (mit Medium), nimm 0, 2, 3, 4
        if self.raw_data.shape[1] >= 5:
             self.raw_data = self.raw_data.iloc[:, [0, 2, 3, 4]]
        
        self.raw_data.columns = ['Seriennummer', 'Temperatur', 'Messunsicherheit', 'Widerstand']
        self.raw_data['Seriennummer'] = self.raw_data['Seriennummer'].astype(str)
        
        # Ergebnis-Container
        self.coeffs_cvd = pd.DataFrame()
        self.coeffs_its90 = pd.DataFrame()
        self.residuen_its = pd.DataFrame()
        self.residuen_cvd = pd.DataFrame()
        
        # Referenz-Widerstand (R0_Norm) bestimmen
        self.r0_norm_val = 100.0
        if sensor_type == "AUTO":
            # Mittelwert im Bereich -5 bis 30 Grad suchen
            mask = self.raw_data['Temperatur'].between(-5, 30)
            if mask.any():
                avg_r = self.raw_data.loc[mask, 'Widerstand'].mean()
                if 8 < avg_r < 12: self.r0_norm_val = 10.0
                elif 20 < avg_r < 30: self.r0_norm_val = 25.0
                elif 400 < avg_r < 600: self.r0_norm_val = 500.0
                elif 800 < avg_r < 1200: self.r0_norm_val = 1000.0
        else:
            mapping = {'Pt10': 10.0, 'Pt25': 25.0, 'Pt100': 100.0, 'Pt500': 500.0, 'Pt1000': 1000.0}
            self.r0_norm_val = mapping.get(sensor_type, 100.0)
            
        print(f"[{strftime('%H:%M:%S')}] Sensor-Typ initialisiert: R0_REF = {self.r0_norm_val} Ohm")

    # =========================================================================
    # ITS-90 BERECHNUNG
    # =========================================================================

    def calculate_its90(self, force_c_fit: bool = False):
        """
        Führt den ITS-90 Fit durch (Abweichungsfunktionen).
        """
        print(f"[{strftime('%H:%M:%S')}] Starte ITS-90 Berechnung (Force C: {force_c_fit})...")
        res_list = []
        calc_data = []

        for serial, group in self.raw_data.groupby('Seriennummer'):
            df_g = group.copy()
            
            # 1. R(TPW) finden (Widerstand am Wassertripelpunkt 0.01°C)
            mask_tpw = df_g['Temperatur'].between(-0.05, 0.05)
            if mask_tpw.any():
                r_tpw = df_g.loc[mask_tpw, 'Widerstand'].mean()
            else:
                # Fallback über R0 (0°C) -> Korrekturfaktor zu TPW
                mask_r0 = df_g['Temperatur'].between(-0.1, 0.1)
                r0 = df_g.loc[mask_r0, 'Widerstand'].mean() if mask_r0.any() else self.r0_norm_val
                r_tpw = r0 * 1.000039 

            # W_obs und W_ref berechnen
            df_g['W_obs'] = df_g['Widerstand'] / r_tpw
            df_g['W_ref'] = df_g['Temperatur'].apply(core.its90_w_ref_calc)
            df_g['Delta_W'] = df_g['W_obs'] - df_g['W_ref']
            
            pos_data = df_g[df_g['Temperatur'] > 0.1]
            neg_data = df_g[df_g['Temperatur'] < -0.1]
            
            a7, b7, c7 = 0.0, 0.0, 0.0
            a_neg, b_neg = 0.0, 0.0
            
            # --- Fit Positiv ---
            if not pos_data.empty:
                max_t = pos_data['Temperatur'].max()
                # Nutze C wenn Temp > 650°C oder erzwungen, und genug Punkte da sind
                use_c = (max_t > 650 or force_c_fit) and len(pos_data) >= 4
                
                try:
                    if use_c:
                        popt, _ = curve_fit(core.its90_dev_pos, pos_data['W_obs'], pos_data['Delta_W'])
                        a7, b7, c7 = popt
                    else:
                        # Lambda Wrapper um C=0 zu erzwingen
                        popt, _ = curve_fit(lambda w,a,b: core.its90_dev_pos(w,a,b,0), 
                                          pos_data['W_obs'], pos_data['Delta_W'])
                        a7, b7 = popt
                        c7 = 0.0
                except RuntimeError:
                    pass # Fit fehlgeschlagen

            # --- Fit Negativ ---
            if not neg_data.empty and len(neg_data) >= 2:
                try:
                    popt, _ = curve_fit(core.its90_dev_neg, neg_data['W_obs'], neg_data['Delta_W'])
                    a_neg, b_neg = popt
                except RuntimeError:
                    pass
            
            res_list.append({
                'Seriennummer': serial, 'R_TPW': r_tpw,
                'a7': a7, 'b7': b7, 'c7': c7, 
                'a_neg': a_neg, 'b_neg': b_neg
            })
            
            # --- Residuen Berechnung ---
            for idx, row in df_g.iterrows():
                t = row['Temperatur']
                w_meas = row['W_obs']
                
                # Delta W Fit berechnen
                if t < 0:
                    dw_fit = core.its90_dev_neg(w_meas, a_neg, b_neg)
                else:
                    dw_fit = core.its90_dev_pos(w_meas, a7, b7, c7)
                
                # W_pred = W_ref(t) + dW_fit
                w_pred = core.its90_w_ref_calc(t) + dw_fit
                
                res_w = w_meas - w_pred
                # Empfindlichkeit ca 250 K/Einheit W für Pt100/Pt25
                calc_data.append({
                    'Seriennummer': serial, 
                    'Temperatur': t, 
                    'ITS90_Residuum_mK': res_w * 250.0 * 1000
                })

        self.coeffs_its90 = pd.DataFrame(res_list).set_index('Seriennummer')
        self.residuen_its = pd.DataFrame(calc_data)

    # =========================================================================
    # CVD BERECHNUNG
    # =========================================================================

    def calculate_cvd(self):
        """
        Führt den Callendar-Van-Dusen Fit durch.
        """
        print(f"[{strftime('%H:%M:%S')}] Starte CVD Berechnung...")
        res_list = []
        res_calc = []
        
        # Fit-Wrapper um core.cvd_r kompatibel mit curve_fit zu machen
        def fit_wrapper_all(t, r0, a, b, c):
            return core.cvd_r(t, r0, a, b, c)

        def fit_wrapper_pos(t, r0, a, b):
            return core.cvd_r(t, r0, a, b, 0.0)

        for serial, group in self.raw_data.groupby('Seriennummer'):
            t_vals = group['Temperatur'].values
            r_vals = group['Widerstand'].values
            
            # Startwerte: Normkoeffizienten
            p0 = [self.r0_norm_val, core.CVD_A_NORM, core.CVD_B_NORM, 0.0]
            
            try:
                # Entscheidung: C fitten oder nicht?
                if np.min(t_vals) >= 0:
                    # Nur positiver Bereich -> C=0
                    popt, _ = curve_fit(fit_wrapper_pos, t_vals, r_vals, p0=p0[:3])
                    r0_f, a_f, b_f = popt
                    c_f = 0.0
                else:
                    # Negativer Bereich vorhanden -> C fitten
                    popt, _ = curve_fit(fit_wrapper_all, t_vals, r_vals, p0=p0)
                    r0_f, a_f, b_f, c_f = popt
                
                res_list.append({
                    'Seriennummer': serial, 
                    'R0': r0_f, 'A': a_f, 'B': b_f, 'C': c_f
                })
                
                # Residuen
                r_calc = core.cvd_r(t_vals, r0_f, a_f, b_f, c_f)
                diff_r = r_vals - r_calc
                # dT approx dR / (R0 * alpha)
                dt_mk = (diff_r / (r0_f * 3.9e-3)) * 1000
                
                for tv, dmk in zip(t_vals, dt_mk):
                    res_calc.append({
                        'Seriennummer': serial, 
                        'Temperatur': tv, 
                        'CVD_Residuum_mK': dmk
                    })
            except RuntimeError:
                print(f"Fit fehlgeschlagen für Sensor {serial}")

        self.coeffs_cvd = pd.DataFrame(res_list).set_index('Seriennummer')
        self.residuen_cvd = pd.DataFrame(res_calc)

    # =========================================================================
    # EXPORT & PLOTTING DELEGATION
    # =========================================================================

    def plot(self, output_dir, din_class='A', mode='BOTH', graphs=['SINGLE', 'RESIDUALS', 'ALL']):
        """
        Erstellt Graphen mithilfe der PtPlotter Klasse.
        
        Args:
            output_dir: Pfad zum Speicherort
            din_class: Toleranzklasse ('AA', 'A', 'B' oder 0)
            mode: 'CVD', 'ITS' oder 'BOTH'
            graphs: Liste der gewünschten Graphentypen
        """
        plotter = PtPlotter(self)
        
        if 'SINGLE' in graphs:
            plotter.plot_single_sensors(output_dir, din_class, mode)
            
        if 'RESIDUALS' in graphs:
            plotter.plot_residuals(output_dir, mode)
            
        if 'ALL' in graphs:
            plotter.plot_all_sensors(output_dir, din_class, mode)

    def export_excel(self, filepath, mode='BOTH'):
        """
        Exportiert Ergebnisse in eine Excel-Datei mit formatieren Zellen.
        """
        # Daten zusammenführen
        df_out = self.raw_data.copy()
        
        # Merge CVD Residuen
        if mode in ["CVD", "BOTH"] and not self.residuen_cvd.empty:
            df_out = pd.merge(df_out, self.residuen_cvd, on=['Seriennummer', 'Temperatur'], how='left')
            
        # Merge ITS Residuen
        if mode in ["ITS", "BOTH"] and not self.residuen_its.empty:
            df_out = pd.merge(df_out, self.residuen_its[['Seriennummer', 'Temperatur', 'ITS90_Residuum_mK']], 
                              on=['Seriennummer', 'Temperatur'], how='left')

        # Pfad vorbereiten
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        try:
            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                wb = writer.book
                fmt_sci = wb.add_format({'num_format': '0.000000E+00'}) 
                
                # Sheet: CVD Koeffizienten
                if mode in ["CVD", "BOTH"] and not self.coeffs_cvd.empty:
                    self.coeffs_cvd.reset_index().to_excel(writer, sheet_name='Coeffs_CVD', index=False)
                    ws = writer.sheets['Coeffs_CVD']
                    ws.set_column('C:E', 15, fmt_sci) # A, B, C formatieren

                # Sheet: ITS Koeffizienten
                if mode in ["ITS", "BOTH"] and not self.coeffs_its90.empty:
                    self.coeffs_its90.reset_index().to_excel(writer, sheet_name='Coeffs_ITS90', index=False)
                    ws = writer.sheets['Coeffs_ITS90']
                    ws.set_column('C:H', 15, fmt_sci) # a7...b_neg formatieren

                # Sheet: Daten & Residuen
                df_out.to_excel(writer, sheet_name='Residuen_Data', index=False)
                
            print(f"[{strftime('%H:%M:%S')}] Excel Exportiert: {filepath}")
            
        except Exception as e:
            print(f"Fehler beim Excel-Export: {e}")
