# src/ptcal/sensor.py
import pandas as pd
import numpy as np
from . import core  # Importiert die Mathe-Formeln aus core.py

class PtSensor:
    def __init__(self, serial_number: str, standard: str = "CVD", **coeffs):
        """
        Initialisiert einen Sensor manuell.
        
        Args:
            serial_number: Name/SN des Fühlers
            standard: "CVD" oder "ITS90"
            **coeffs: Die Koeffizienten als Keyword Arguments.
                      CVD: R0, A, B, C
                      ITS90: R_TPW, a7, b7, c7, a_neg, b_neg
        """
        self.serial = str(serial_number)
        self.standard = standard.upper()
        self.coeffs = coeffs
        
        # Validierung
        if self.standard == "CVD":
            if 'R0' not in coeffs: raise ValueError("CVD benötigt R0")
            # Setze C auf 0, falls nicht angegeben
            self.coeffs.setdefault('C', 0.0)
            
        elif self.standard == "ITS90":
            if 'R_TPW' not in coeffs: raise ValueError("ITS90 benötigt R_TPW")
            # Setze ITS Parameter auf 0 falls nicht da
            for k in ['a7', 'b7', 'c7', 'a_neg', 'b_neg']:
                self.coeffs.setdefault(k, 0.0)

    @classmethod
    def from_excel(cls, filepath: str, serial_number: str, standard: str = "CVD"):
        """
        Lädt Koeffizienten direkt aus der Excel-Ergebnisdatei.
        """
        serial_number = str(serial_number)
        sheet_name = "Coeffs_ITS90" if standard.upper() == "ITS90" else "Coeffs_CVD"
        
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            # Sicherstellen, dass SN String ist
            df['Seriennummer'] = df['Seriennummer'].astype(str)
            
            row = df[df['Seriennummer'] == serial_number]
            if row.empty:
                raise ValueError(f"Seriennummer {serial_number} in {sheet_name} nicht gefunden.")
            
            data = row.iloc[0].to_dict()
            # Entferne SN aus den Coeffs, da separat übergeben
            del data['Seriennummer']
            
            return cls(serial_number, standard, **data)
            
        except Exception as e:
            raise IOError(f"Fehler beim Laden aus Excel: {e}")

    def get_temperature(self, resistance: float) -> float:
        """Berechnet Temperatur aus Widerstand."""
        if self.standard == "CVD":
            # Nutze Core-Funktion
            # Für hohe Präzision im Negativen müsste man hier iterieren, 
            # für dieses Beispiel nutzen wir die analytische Lösung (pos)
            return core.solve_temp_from_r_cvd(
                resistance, 
                self.coeffs['R0'], 
                self.coeffs['A'], 
                self.coeffs['B']
            )
            
        elif self.standard == "ITS90":
            # ITS-90 Iteration (R -> W -> Iteration -> T)
            r_tpw = self.coeffs['R_TPW']
            w_obs = resistance / r_tpw
            
            # Startwert schätzen (CVD Näherung)
            t_est = (w_obs - 1) * 250.0 
            
            # Fixpunkt-Iteration für T
            for _ in range(5):
                # 1. Berechne W_ref für geschätztes T
                w_ref = core.its90_w_ref_calc(t_est) # Funktion aus core.py
                
                # 2. Berechne Deviation
                if t_est < 0:
                    dw = core.its90_dev_neg(w_ref, self.coeffs['a_neg'], self.coeffs['b_neg'])
                else:
                    dw = core.its90_dev_pos(w_ref, self.coeffs['a7'], self.coeffs['b7'], self.coeffs['c7'])
                
                # 3. Neues W_ref Ziel
                w_ref_target = w_obs - dw
                
                # 4. Invers W_ref -> T (Das ist komplex, wir nutzen hier eine simple Newton Korrektur)
                # dT/dW_ref ist ca 250 K/Einheit
                t_new = t_est + (w_ref_target - w_ref) * 250.0 # Besser wäre exakte Ableitung
                
                if abs(t_new - t_est) < 0.0001:
                    return t_new
                t_est = t_new
            
            return t_est

    def get_resistance(self, temperature: float) -> float:
        """Berechnet Widerstand aus Temperatur."""
        if self.standard == "CVD":
            arr = core.cvd_r([temperature], self.coeffs['R0'], self.coeffs['A'], self.coeffs['B'], self.coeffs['C'])
            return float(arr[0])
            
        elif self.standard == "ITS90":
            # T -> W_ref -> Dev -> W_obs -> R
            w_ref = core.its90_w_ref_calc(temperature)
            if temperature < 0:
                dw = core.its90_dev_neg(w_ref, self.coeffs['a_neg'], self.coeffs['b_neg'])
            else:
                dw = core.its90_dev_pos(w_ref, self.coeffs['a7'], self.coeffs['b7'], self.coeffs['c7'])
            
            w_obs = w_ref + dw
            return w_obs * self.coeffs['R_TPW']
