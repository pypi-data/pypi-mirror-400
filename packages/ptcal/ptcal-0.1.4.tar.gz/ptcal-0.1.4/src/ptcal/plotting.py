# src/ptcal/plotting.py
import matplotlib.pyplot as plt
import matplotlib.style as style
import numpy as np
from pathlib import Path
from . import core # Importiere Mathe für Toleranzlinien etc.

style.use('bmh')

class PtPlotter:
    def __init__(self, calibrator_instance):
        """
        Nimmt eine Instanz von PtCalibrator entgegen, um auf dessen Ergebnisse zuzugreifen.
        """
        self.cal = calibrator_instance
        self.data = self.cal.raw_data
        
    def _get_tolerance(self, t, din_class):
        """Berechnet Toleranzband."""
        t_abs = np.abs(t)
        if str(din_class) == 'AA': return 0.10 + 0.0017 * t_abs
        elif str(din_class) == 'A': return 0.15 + 0.0020 * t_abs
        elif str(din_class) == 'B': return 0.30 + 0.0050 * t_abs
        return np.zeros_like(t) # Klasse 0

    def _dev_from_norm_helper(self, r_val, t_val):
        """Berechnet Abweichung zur Normkurve."""
        # T_din - T_echt
        # Wir nutzen die core Funktion oder implementieren es hier direkt
        a, b = core.CVD_A_NORM, core.CVD_B_NORM
        # Analytische Lösung CVD für T_din
        term = a**2 - 4*b*(1 - r_val/self.cal.r0_norm_val)
        # Schutz vor negativen Wurzeln bei defekten Daten
        valid = term >= 0
        t_din = np.full_like(r_val, np.nan)
        t_din[valid] = (-a + np.sqrt(term[valid])) / (2*b)
        return t_din - t_val

    def plot_single_sensors(self, output_dir: str, din_class='A', mode='BOTH'):
        """Erstellt Einzelplots (Compare) pro Sensor."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        
        for serial, group in self.data.groupby('Seriennummer'):
            fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
            t_min, t_max = group['Temperatur'].min(), group['Temperatur'].max()
            t_smooth = np.linspace(t_min, t_max, 300)

            # --- Toleranz ---
            tol = self._get_tolerance(t_smooth, din_class)
            if np.sum(tol) > 0:
                ax.fill_between(t_smooth, tol, -tol, color='gray', alpha=0.1, label=f'DIN {din_class}')
                ax.plot(t_smooth, tol, 'k--', lw=0.5)
                ax.plot(t_smooth, -tol, 'k--', lw=0.5)

            # --- CVD Kurve ---
            if mode in ["CVD", "BOTH"] and not self.cal.coeffs_cvd.empty:
                try:
                    cc = self.cal.coeffs_cvd.loc[serial]
                    r_cvd = core.cvd_r(t_smooth, cc['R0'], cc['A'], cc['B'], cc['C'])
                    curve_cvd = self._dev_from_norm_helper(r_cvd, t_smooth)
                    ax.plot(t_smooth, curve_cvd, 'b-', label='CVD', lw=1.5)
                    
                    # Textbox
                    txt = "\n".join([r"$\bf{CVD}$", f"R0: {cc['R0']:.4f}", f"A: {cc['A']:.5e}", f"B: {cc['B']:.5e}", f"C: {cc['C']:.5e}"])
                    ax.text(0.02, 0.98, txt, transform=ax.transAxes, va='top', 
                            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8), fontsize=8)
                except KeyError: pass

            # --- ITS Kurve ---
            if mode in ["ITS", "BOTH"] and not self.cal.coeffs_its90.empty:
                try:
                    ic = self.cal.coeffs_its90.loc[serial]
                    # Berechnung der ITS Kurve via Core
                    r_its = []
                    for t in t_smooth:
                        # Hier rufen wir eine Hilfsfunktion im Calibrator auf oder rechnen manuell
                        # Um Code-Duplikate zu vermeiden, sollte die Logik "T -> R_its" im core sein
                        # Hier vereinfacht inline:
                        w_ref = core.its90_w_ref_calc(t)
                        # Einfache Iteration
                        w_est = w_ref
                        for _ in range(3):
                            if t < 0: dw = core.its90_dev_neg(w_est, ic['a_neg'], ic['b_neg'])
                            else: dw = core.its90_dev_pos(w_est, ic['a7'], ic['b7'], ic['c7'])
                            w_est = w_ref + dw
                        r_its.append(w_est * ic['R_TPW'])
                    
                    curve_its = self._dev_from_norm_helper(np.array(r_its), t_smooth)
                    ax.plot(t_smooth, curve_its, 'g--', label='ITS-90', lw=1.5)

                    txt = "\n".join([r"$\bf{ITS-90}$", f"R_TPW: {ic['R_TPW']:.4f}", f"a: {ic['a7']:.4e}", f"b: {ic['b7']:.4e}"])
                    x_pos = 0.15 if mode == "BOTH" else 0.02
                    ax.text(x_pos, 0.98, txt, transform=ax.transAxes, va='top', 
                            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8), fontsize=8)
                except KeyError: pass

            # --- Messpunkte ---
            dev_meas = self._dev_from_norm_helper(group['Widerstand'].values, group['Temperatur'].values)
            ax.errorbar(group['Temperatur'], dev_meas, yerr=group['Messunsicherheit'], fmt='ko', capsize=3, label='Messdaten')

            ax.set_title(f"Sensor: {serial}")
            ax.set_ylabel("Abweichung [K]")
            ax.set_xlabel("Temperatur [°C]")
            ax.legend()
            
            fig.savefig(out / f"{serial}_{mode}.png")
            plt.close(fig)

    def plot_residuals(self, output_dir, mode='BOTH'):
        """Plottet Residuen (Scatter)."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
        
        sensors = self.data['Seriennummer'].unique()
        colors = plt.cm.tab20(np.linspace(0, 1, len(sensors)))
        
        for idx, serial in enumerate(sensors):
            c = colors[idx]
            
            # CVD
            if mode in ["CVD", "BOTH"] and not self.cal.residuen_cvd.empty:
                d = self.cal.residuen_cvd[self.cal.residuen_cvd['Seriennummer'] == serial]
                ax.scatter(d['Temperatur'], d['CVD_Residuum_mK'], 
                           label=f"{serial} (CVD)", color=c, marker='o', s=60, alpha=0.6)
            
            # ITS
            if mode in ["ITS", "BOTH"] and not self.cal.residuen_its.empty:
                d = self.cal.residuen_its[self.cal.residuen_its['Seriennummer'] == serial]
                ax.scatter(d['Temperatur'], d['ITS90_Residuum_mK'], 
                           label=f"{serial} (ITS)", facecolors='none', edgecolors=c, marker='D', s=40, linewidths=1.5)

        ax.axhline(0, color='black', lw=1)
        ax.set_title(f'Residuen Übersicht ({mode})')
        ax.set_ylabel('Residuum [mK]')
        ax.set_xlabel('Temperatur [°C]')
        ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
        
        fig.tight_layout()
        fig.savefig(out / f"Residuen_Combined_{mode}.png")
        plt.close(fig)

    def plot_all_sensors(self, output_dir, din_class='A', mode='BOTH'):
        """
        Plottet alle Kennlinien (Abweichung zur Norm) in ein gemeinsames Diagramm.
        Erzeugt je nach Mode ein Bild für CVD und/oder eins für ITS.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        
        # Globales Temperaturband für alle Sensoren
        t_min = self.data['Temperatur'].min()
        t_max = self.data['Temperatur'].max()
        t_glob = np.linspace(t_min, t_max, 300)
        
        tol = self._get_tolerance(t_glob, din_class)
        
        # Hilfsfunktion zum Plotten eines Typs (CVD oder ITS)
        def create_multi_plot(type_name):
            fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
            
            # Toleranzband
            if np.sum(tol) > 0:
                ax.fill_between(t_glob, tol, -tol, color='gray', alpha=0.1, label=f'DIN {din_class}')
                ax.plot(t_glob, tol, 'k--', lw=0.5)
                ax.plot(t_glob, -tol, 'k--', lw=0.5)
            
            # Farben für die Sensoren
            sensors = self.data['Seriennummer'].unique()
            colors = plt.cm.tab20(np.linspace(0, 1, len(sensors)))
            
            for idx, (serial, group) in enumerate(self.data.groupby('Seriennummer')):
                # Individueller Bereich für jeden Sensor (damit Linie nicht ins Leere läuft)
                t_smooth = np.linspace(group['Temperatur'].min(), group['Temperatur'].max(), 200)
                curve = None
                
                try:
                    if type_name == "CVD":
                        cc = self.cal.coeffs_cvd.loc[serial]
                        r = core.cvd_r(t_smooth, cc['R0'], cc['A'], cc['B'], cc['C'])
                        curve = self._dev_from_norm_helper(r, t_smooth)
                    
                    elif type_name == "ITS":
                        ic = self.cal.coeffs_its90.loc[serial]
                        # ITS Berechnung (T -> R)
                        r_list = []
                        for t in t_smooth:
                            w_ref = core.its90_w_ref_calc(t)
                            w_est = w_ref
                            # Kurze Iteration
                            for _ in range(3):
                                if t < 0: dw = core.its90_dev_neg(w_est, ic['a_neg'], ic['b_neg'])
                                else: dw = core.its90_dev_pos(w_est, ic['a7'], ic['b7'], ic['c7'])
                                w_est = w_ref + dw
                            r_list.append(w_est * ic['R_TPW'])
                        curve = self._dev_from_norm_helper(np.array(r_list), t_smooth)

                    if curve is not None:
                        ax.plot(t_smooth, curve, color=colors[idx], label=str(serial), lw=1.5)
                except KeyError:
                    pass # Falls Koeffizienten fehlen

            ax.set_title(f'Alle Sensoren: {type_name} Abweichung')
            ax.set_xlabel('Temperatur [°C]')
            ax.set_ylabel('Abweichung [K]')
            ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
            
            fig.tight_layout()
            fig.savefig(out / f"All_Sensors_{type_name}.png")
            plt.close(fig)

        # Ausführen je nach Mode
        if mode in ["CVD", "BOTH"] and not self.cal.coeffs_cvd.empty:
            create_multi_plot("CVD")
            
        if mode in ["ITS", "BOTH"] and not self.cal.coeffs_its90.empty:
            create_multi_plot("ITS")
