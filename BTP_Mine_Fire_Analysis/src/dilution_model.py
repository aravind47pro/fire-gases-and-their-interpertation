"""
Theoretical N2 Dilution Model for BTP Mine Fire Analysis
Academic simulation of pure nitrogen inertisation in a sealed mine atmosphere.
Calculates dilution trajectory on the Coward diagram and nominal turnover time.
Includes comprehensive scientific caveats and operational limitations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

def simulate_n2_dilution(initial_ch4: float = 15.0,
                         initial_o2: float = 10.0,
                         f_steps: int = 20) -> pd.DataFrame:
    """
    Simulate theoretical pure N2 dilution path for a sealed mine void.
    f represents the fraction of original atmosphere remaining (from 1.00 down to 0.05).
    Pure N2 diluent contains 0% CH4 and 0% O2.

    CH4(f) = initial_ch4 * f
    O2(f) = initial_o2 * f
    N2(f) = 100 - CH4(f) - O2(f)

    Returns:
        DataFrame of theoretical trajectory points
    """
    f_values = np.linspace(1.00, 0.05, f_steps)
    records = []

    for f in f_values:
        ch4 = round(initial_ch4 * f, 4)
        o2 = round(initial_o2 * f, 4)
        n2 = round(100.0 - ch4 - o2, 4)
        records.append({
            "Fraction_Remaining_f": round(float(f), 4),
            "Dilution_Ratio_1_minus_f": round(float(1.0 - f), 4),
            "CH4_percent": ch4,
            "O2_percent": o2,
            "N2_percent": n2,
            "Inert_Status": "Moving toward pure N2 origin (0, 0)"
        })

    return pd.DataFrame(records)


def compute_nominal_turnover(volume_m3: float = 27000.0,
                            flow_rate_m3_s: float = 5.0) -> Dict[str, Any]:
    """
    Calculate nominal volume-to-flow turnover ratio:
    V / Q = 27,000 / 5 = 5,400 seconds = 90.0 minutes = 1.50 hours.

    Explicit Scientific Limitations:
    - This is purely an idealized macroscopic residence time (plug-flow assumption).
    - In reality, complete inertisation requires 3 to 5+ atmospheric volume changes due to exponential dilution mixing.
    - Factors preventing instantaneous or uniform flushing:
      1. Dead zones, deep goaf pockets, and irregular underground roadway geometry.
      2. Methane gas desorption and strata emission continually replenishing fuel.
      3. Surface and inter-seam leakage through ventilation stoppings, cracks, and packwalls.
      4. Gas stratification: Methane (density ~0.716 kg/m3) collects near roof; Nitrogen (~1.25 kg/m3) stratifies below.
      5. Barometric breathing caused by diurnal surface atmospheric pressure fluctuations.
    """
    seconds = volume_m3 / flow_rate_m3_s
    minutes = seconds / 60.0
    hours = minutes / 60.0

    return {
        "Volume_m3": volume_m3,
        "Flow_Rate_m3_s": flow_rate_m3_s,
        "Nominal_Turnover_Seconds": seconds,
        "Nominal_Turnover_Minutes": minutes,
        "Nominal_Turnover_Hours": hours,
        "Model_Nature": "Idealized Academic Simulation (Theoretical)",
        "Is_Operational_Procedure": False,
        "Safety_Warning": (
            "CRITICAL: 90 minutes is purely a nominal mathematical turnover ratio (V/Q). "
            "It must NEVER be treated as an operational mine-sealing or inertisation duration. "
            "Actual field flushing requires continuous gas chromatography monitoring, pressure balancing, "
            "and professional mine rescue assessment."
        )
    }
