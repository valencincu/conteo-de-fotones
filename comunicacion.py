import numpy as np
import pandas as pd
import time
from tqdm import tqdm

# ADQUIRIR DATOS

def osci_setup(osci, channel, t_scale, v_scale):
    if t_scale is not None:
        osci.set_time(scale = t_scale, zero = 0)
    if v_scale is not None:
        osci.set_channel(channel = channel, scale = v_scale)
    return None

def osci_test(osci, channel):
    # VER CUANTO SE DEMORA EN TOMAR DATOS
    start_time = time.time()
    t, v = osci.read_data(channel)
    end_time = time.time()
    comm_time = end_time - start_time

    # TOMAR DATOS DE CONFIGURACIÓN
    t_config = osci.get_time()
    v_config = osci.get_channel(channel)

    return t, v, t_config, v_config, comm_time

def data_run(osci, channel, num_acq, comm_time, file):
    t, v       = osci.read_data(channel)
    win_time   = max(t) - min(t)
    win_points = len(t)
    s          = np.zeros(win_points)
    s[-1]      = 1

    wait = win_time - comm_time if win_time > comm_time else 0
    init_time = time.time()
    
    N = int(num_acq / win_points)
    for i in tqdm(range(N), ncols = 50):
        osci.force_trigger()
        now = time.time() - init_time
        t, v = osci.read_data(channel)
        t += now

        data = pd.DataFrame({"t": t, "v": v, "s": s})
        file.write(data.to_csv(header = False, index = False, lineterminator='\n'))
        time.sleep(wait)