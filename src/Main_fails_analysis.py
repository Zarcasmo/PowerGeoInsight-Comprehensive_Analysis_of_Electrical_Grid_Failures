# -*- coding: utf-8 -*-

"""
Module Main_analysis_failure.py

This module serves as the main entry point for the failure analysis program. Import functions
of the analysis and data(load_data and clear_data) modules to process user input, filter data, and perform
failure analysis.

Use:
1. Run this script to interactively analyze crashes based on user input.

Module Dependencies:
- analysis.analysis: Provides the 'failure_analysis' function for failure analysis.
- data.load_data: Use the 'process_input' function to process user input.
- data.clear_data: Implements 'filter_dates' and 'event_report' for data filtering.

Features:
1. `get_user_input()`: Requests user input and returns the entered value.
2. Main execution: Processes user input, filters data, and performs fault analysis for each circuit.

Example:
    To use this script, run it in a Python environment and follow the prompts to enter values.
"""

#Principal
# Main_analisis_falla.py
from analysis.analysis import analisis_fallas
from data.load_data import procesar_entrada
#call clear_data for dataframes that need data processing
from data.clear_data import filtrar_fechas,reporte_eventos

def get_user_input():
    """
    Function that requests user input and returns the entered value.

    Returns:
        str: Value entered by the user.
    """
    # Ask the user for input
    # Example values ​​CARQ0155,CARQ0122,CARQ0124
    user_input =input("Enter a value: ")
    return user_input

# Process user input and filter events based on dates
user_input = get_user_input()
processed_input = procesar_entrada(user_input)
leaked_event_report=filtrar_fechas(reporte_eventos)

# Analyze faults for each circuit
circuits = processed_input["circuito"].unique()
for i in circuits:
    input_x_circuits = processed_input.loc[processed_input['circuito']==i]
    analisis_fallas(input_x_circuits,leaked_event_report, i)