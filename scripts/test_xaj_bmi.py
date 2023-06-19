import os
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)
from xaj_bmi import xajBmi
from datetime import date
import pandas as pd


model = xajBmi()
print(model.get_component_name())


model.initialize("scripts/runxaj.yaml")
print("Start time:", model.get_start_time())
print("End time:", model.get_end_time())
print("Current time:", model.get_current_time())
print("Time step:", model.get_time_step())
print("Time units:", model.get_time_units())
print(model.get_input_var_names())
print(model.get_output_var_names())

discharge = []
ET = []
time = []                                          
while model.get_current_time() <= model.get_end_time():
    time.append(model.get_current_time())
    model.update()

discharge=model.get_value("discharge")
ET=model.get_value("ET")

results = pd.DataFrame({
                'discharge': discharge.flatten(),
                'ET': ET.flatten(),  
            })
results.to_csv('/home/wangjingyi/code/hydro-model-xaj/hydromodel/example/results.csv')
model.finalize()
