import matplotlib.pyplot as plt
import os
import pyvisa as visa
import pandas as pd
from datetime import datetime
from osciloscopio import TDS1002B, OSCI_SIM
now = datetime.now()
from comunicacion import osci_setup, osci_test, data_run

# INICIALIZAR COMUNICACIÓN
print(visa.ResourceManager().list_resources())
osci = TDS1002B("USB0::0x0699::0x0363::C108011::INSTR")
#osci = OSCI_SIM()

# CONFIGURACIÓN
# -------------------------------------------------------
num_screens = 500
num_acq = num_screens * 2500
channel = 1
t_scale = None
v_scale = None
# -------------------------------------------------------

osci_setup(osci, channel, t_scale, v_scale)
t_init, v_init, t_config, v_config, comm_time = osci_test(osci, channel) 

# VERIFICAR CONFIGURACION
config_str = f"\nCONFIG:\n{t_config}\n{v_config}"
print(config_str)
print("\ncomm_time:", comm_time)

# GRAFICO INICIAL
plt.plot(t_init, v_init)
plt.show()

# ARCHIVO
if input("Continuar midiendo? [s/n] ") != "s": exit()
dir = "sim"
if not os.path.exists(dir): os.makedirs(dir)
time_id = now.strftime("%Y-%m-%d_%H:%M:%S")
guardar_como = input(f"Guardar como: [{time_id}]")

# PANTALLA (con suerte funciona, creo que no)
screen_file_name = f"[{time_id}] [pantalla]" + guardar_como
osci._osci.set("SAVe:IMAge:FILEFormat TIFF")
osci._osci.set(f'SAVe:IMAge "{screen_file_name}.tiff"')
print(f"Se guardó la pantalla en {screen_file_name}")

# BARRIDO
run_file_name = f"[{time_id}] [barrido]" + guardar_como + ".txt"
file = open(dir + os.sep + run_file_name, "a")
file.write(config_str + "\n\nDATA: \nt,v,split\n")
data_run(osci, channel, num_acq, comm_time, file)
print(f"Se guardó el barrido en {run_file_name}")

# GUARDADO
file.close()
