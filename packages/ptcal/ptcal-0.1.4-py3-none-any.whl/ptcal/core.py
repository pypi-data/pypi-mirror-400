# src/ptcal/core.py
"""
Mathematischer Kern für Pt-Kalibrierung.
Enthält Konstanten und Formeln für:
- ITS-90 (International Temperature Scale of 1990)
- CVD (Callendar-Van-Dusen / IEC 60751)
Keine Abhängigkeiten zu Pandas oder Plotting-Libraries, nur NumPy.
"""

import numpy as np

# =============================================================================
# KONSTANTEN ITS-90 (Tabelle 1 aus ITS-90 Text)
# =============================================================================

# Für Referenzfunktion W_r(T90) im Bereich 12 (13.8033 K bis 273.16 K)
# Formel: Wr(T90) = Summe(Ai * [(ln(T/273.16)+1.5)/1.5]^i)
ITS90_A = [
    -2.13534729,
    3.18324720,
    -1.80143597,
    0.71727204,
    0.50344027,
    -0.61899395,
    -0.05332322,
    0.28021362,
    0.10715224,
    -0.29302865,
    0.04459872,
    0.11868632,
    -0.05248134
]

# Für Inversfunktion T90(Wr) im Bereich 12 (Optional, hier nicht zwingend genutzt,
# da wir meist T->W rechnen oder Newton nutzen)
ITS90_B = [
    0.183324722, 0.240975303, 0.209108771, 0.190439972, 
    0.142648498, 0.077993465, 0.012475611, -0.032267127, 
    -0.075291522, -0.056470670, 0.076201285, 0.123893204, 
    -0.029201193, -0.091173542, 0.001317696, 0.026025526
]

# Für Referenzfunktion W_r(T90) im Bereich 13 (0°C bis 961.78°C)
# Formel: Wr(T90) = C0 + Summe(Ci * [(T/K - 754.15)/481]^i)
ITS90_C_REF = [
    2.78157254,
    1.64650916,
    -0.13714390,
    -0.00649767,
    -0.00234444,
    0.00511868,
    0.00187982,
    -0.00204472,
    -0.00046122,
    0.00045724
]

# Für Inversfunktion T90(Wr) im Bereich 13
ITS90_D_REF = [
    439.93285400, 472.41802000, 37.68449400, 7.47201800, 
    2.92082800, 0.00518400, -0.96386400, -0.18873200, 
    0.19120300, 0.04902500
]

# =============================================================================
# KONSTANTEN CVD (IEC 60751)
# =============================================================================

CVD_A_NORM = 3.9083e-3
CVD_B_NORM = -5.775e-7
CVD_C_NORM = -4.183e-12


# =============================================================================
# ITS-90 FUNKTIONEN (MATHE)
# =============================================================================

def its90_w_ref_calc(t_celsius):
    """
    Berechnet die Referenzfunktion W_r(T90) für eine gegebene Temperatur.
    Deckt den Bereich < 0°C (Gl. 9b) und >= 0°C (Gl. 10b) ab.
    
    Args:
        t_celsius (float): Temperatur in °C
        
    Returns:
        float: Referenz-Widerstandsverhältnis W_r
    """
    # Tripelpunkt Wasser (0.01°C) ist die Grenze, wir nehmen 0.01 als Cutoff
    if t_celsius < 0.01: 
        # Bereich 12: 13.8K bis 273.16K
        t_k = t_celsius + 273.15
        # Variable x für das Polynom
        x = (np.log(t_k/273.16) + 1.5) / 1.5
        w = 0.0
        for i, a in enumerate(ITS90_A):
            w += a * (x**i)
        return w
    else:
        # Bereich 13: 0°C bis 961.78°C
        w = 0.0
        for i, c in enumerate(ITS90_C_REF):
            w += c * (((t_celsius + 273.15 - 754.15) / 481.0)**i)
        return w

def its90_dev_pos(w, a, b, c):
    """
    Berechnet Delta W für den positiven Bereich (Bereiche 8, 9, 10, 11).
    Gl 10c: dW = a(W-1) + b(W-1)^2 + c(W-1)^3
    """
    wm1 = w - 1.0
    return a*wm1 + b*(wm1**2) + c*(wm1**3)

def its90_dev_neg(w, a, b):
    """
    Berechnet Delta W für den negativen Bereich (Bereiche 12, 13, 14).
    Gl 9b: dW = a(W-1) + b(W-1)ln(W)
    """
    wm1 = w - 1.0
    # Logarithmus von W muss positiv sein, W ist bei Pt100 immer > 0.
    # Sicherheitshalber clipping, falls numerische Fehler auftreten.
    safe_w = np.maximum(w, 1e-12)
    return a*wm1 + b*wm1*np.log(safe_w)


# =============================================================================
# CVD FUNKTIONEN (MATHE)
# =============================================================================

def cvd_r(t, r0, a, b, c):
    """
    Berechnet den Widerstand R(t) nach Callendar-Van-Dusen.
    Vektorisiert (kann float oder numpy array verarbeiten).
    
    Args:
        t: Temperatur in °C (float oder array)
        r0, a, b, c: Koeffizienten
        
    Returns:
        R: Widerstand in Ohm
    """
    t = np.asarray(t)
    res = np.zeros_like(t, dtype=float)
    
    mask_pos = t >= 0
    mask_neg = t < 0
    
    if np.any(mask_pos):
        tp = t[mask_pos]
        res[mask_pos] = r0 * (1 + a*tp + b*tp**2)
        
    if np.any(mask_neg):
        tn = t[mask_neg]
        res[mask_neg] = r0 * (1 + a*tn + b*tn**2 + c*(tn-100.0)*tn**3)
        
    # Falls input scalar war, return scalar
    if res.ndim == 0:
        return float(res)
    return res

def solve_temp_from_r_cvd_pos_approx(r, r0, a, b):
    """
    Berechnet T aus R mit der quadratischen Lösungsformel (nur positiver Ast).
    Wird oft als Näherung für Abweichungsplots genutzt oder wenn T > 0.
    
    0 = R0*B*t^2 + R0*A*t + (R0-R)
    """
    # Diskriminante: A^2 - 4*B*(1 - R/R0)
    # Da R = R0(1+At+Bt2) -> R/R0 - 1 = At + Bt2 -> Bt2 + At + (1 - R/R0) = 0
    # Lösung t = (-A + sqrt(A^2 - 4B(1 - R/R0))) / 2B
    
    term = a**2 - 4*b*(1 - r/r0)
    # Schutz vor negativen Wurzeln bei unsinnigen R-Werten
    term = np.maximum(term, 0)
    
    return (-a + np.sqrt(term)) / (2*b)

def solve_temp_from_r_cvd_iterative(r, r0, a, b, c):
    """
    Berechnet T aus R iterativ (Newton), korrekt auch für C != 0 (Negativbereich).
    Kann für Arrays verwendet werden.
    """
    r = np.asarray(r)
    # Startwert-Schätzung: Linear T = (R/R0 - 1) / A
    t_est = (r/r0 - 1) / a
    
    # Newton Iteration: t_new = t - f(t)/f'(t)
    # f(t) = CVD(t) - R
    for _ in range(5):
        # r_calc berechnen
        r_calc = cvd_r(t_est, r0, a, b, c)
        
        # Ableitung f'(t)
        # Pos: R0(A + 2Bt)
        # Neg: R0(A + 2Bt + C(4t^3 - 300t^2))
        deriv = np.zeros_like(t_est)
        mask_pos = t_est >= 0
        mask_neg = t_est < 0
        
        if np.any(mask_pos):
            t = t_est[mask_pos]
            deriv[mask_pos] = r0 * (a + 2*b*t)
        
        if np.any(mask_neg):
            t = t_est[mask_neg]
            deriv[mask_neg] = r0 * (a + 2*b*t + c*(4*t**3 - 300*t**2))
            
        diff = r_calc - r
        t_est = t_est - diff / deriv
        
    if t_est.ndim == 0:
        return float(t_est)
    return t_est
