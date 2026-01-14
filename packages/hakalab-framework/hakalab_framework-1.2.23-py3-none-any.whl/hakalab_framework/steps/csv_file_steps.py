#!/usr/bin/env python3
"""
Steps para manejo de archivos CSV
Incluye verificación, búsqueda, navegación y manipulación de datos CSV
"""
import os
import csv
import pandas as pd
from pathlib import Path
from behave import step
from datetime import datetime

@step('verifico que el archivo CSV "{file_path}" existe')
@step('que el archivo CSV "{file_path}" existe')
def step_verify_csv_exists(context, file_path):
    """Verifica que un archivo CSV existe"""
    # Resolver variables de entorno si están presentes
    if hasattr(context, 'variable_manager'):
        file_path = context.variable_manager.resolve_variables(file_path)
    
    file_path = Path(file_path)
    assert file_path.exists(), f"El archivo CSV {file_path} no existe"
    assert file_path.suffix.lower() == '.csv', f"El archivo {file_path} no es un CSV"
    print(f"✅ Archivo CSV encontrado: {file_path}")

@step('verifico que el archivo CSV "{file_path}" tiene un peso de al menos {min_size:d} bytes')
@step('que el archivo CSV "{file_path}" pesa al menos {min_size:d} bytes')
def step_verify_csv_size(context, file_path, min_size):
    """Verifica el tamaño mínimo de un archivo CSV"""
    if hasattr(context, 'variable_manager'):
        file_path = context.variable_manager.resolve_variables(file_path)
    
    file_path = Path(file_path)
    assert file_path.exists(), f"El archivo CSV {file_path} no existe"
    
    actual_size = file_path.stat().st_size
    assert actual_size >= min_size, f"El archivo {file_path} pesa {actual_size} bytes, menor que {min_size}"
    print(f"✅ Archivo CSV {file_path} pesa {actual_size} bytes (mínimo: {min_size})")

@step('cargo el archivo CSV "{file_path}" en la variable "{variable_name}"')
@step('que cargo el CSV "{file_path}" como "{variable_name}"')
def step_load_csv_to_variable(context, file_path, variable_name):
    """Carga un archivo CSV completo en una variable"""
    if hasattr(context, 'variable_manager'):
        file_path = context.variable_manager.resolve_variables(file_path)
    
    file_path = Path(file_path)
    assert file_path.exists(), f"El archivo CSV {file_path} no existe"
    
    # Cargar CSV con pandas para mejor manejo
    df = pd.read_csv(file_path)
    
    # Guardar en variable_manager si está disponible
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(variable_name, df)
    else:
        # Fallback: guardar en context
        if not hasattr(context, 'csv_data'):
            context.csv_data = {}
        context.csv_data[variable_name] = df
    
    print(f"✅ CSV cargado: {len(df)} filas, {len(df.columns)} columnas en variable '{variable_name}'")

@step('busco en el CSV "{csv_variable}" el valor "{search_value}" en la columna "{column_name}"')
@step('que busco "{search_value}" en columna "{column_name}" del CSV "{csv_variable}"')
def step_search_value_in_csv_column(context, csv_variable, search_value, column_name):
    """Busca un valor específico en una columna del CSV"""
    # Obtener datos del CSV
    df = None
    if hasattr(context, 'variable_manager'):
        df = context.variable_manager.get_variable(csv_variable)
    elif hasattr(context, 'csv_data') and csv_variable in context.csv_data:
        df = context.csv_data[csv_variable]
    
    assert df is not None, f"No se encontró el CSV '{csv_variable}'. Cárgalo primero."
    assert column_name in df.columns, f"La columna '{column_name}' no existe en el CSV"
    
    # Resolver variables en search_value
    if hasattr(context, 'variable_manager'):
        search_value = context.variable_manager.resolve_variables(search_value)
    
    # Buscar valor
    matches = df[df[column_name].astype(str).str.contains(str(search_value), na=False)]
    
    assert len(matches) > 0, f"No se encontró '{search_value}' en la columna '{column_name}'"
    print(f"✅ Encontradas {len(matches)} coincidencias de '{search_value}' en columna '{column_name}'")
    
    # Guardar resultados de búsqueda
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(f"{csv_variable}_search_results", matches)

@step('obtengo el valor de la fila {row_index:d} columna "{column_name}" del CSV "{csv_variable}" y lo guardo en "{result_variable}"')
def step_get_csv_cell_value(context, row_index, column_name, csv_variable, result_variable):
    """Obtiene el valor de una celda específica del CSV"""
    # Obtener datos del CSV
    df = None
    if hasattr(context, 'variable_manager'):
        df = context.variable_manager.get_variable(csv_variable)
    elif hasattr(context, 'csv_data') and csv_variable in context.csv_data:
        df = context.csv_data[csv_variable]
    
    assert df is not None, f"No se encontró el CSV '{csv_variable}'"
    assert column_name in df.columns, f"La columna '{column_name}' no existe"
    assert 0 <= row_index < len(df), f"Fila {row_index} fuera de rango (0-{len(df)-1})"
    
    # Obtener valor
    value = df.iloc[row_index][column_name]
    
    # Guardar en variable
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(result_variable, str(value))
    else:
        if not hasattr(context, 'test_variables'):
            context.test_variables = {}
        context.test_variables[result_variable] = str(value)
    
    print(f"✅ Valor obtenido: fila {row_index}, columna '{column_name}' = '{value}' → variable '{result_variable}'")

@step('filtro el CSV "{csv_variable}" donde "{column_name}" contiene "{filter_value}" y guardo como "{result_variable}"')
def step_filter_csv_by_column(context, csv_variable, column_name, filter_value, result_variable):
    """Filtra un CSV por valor en columna específica"""
    # Obtener datos del CSV
    df = None
    if hasattr(context, 'variable_manager'):
        df = context.variable_manager.get_variable(csv_variable)
    elif hasattr(context, 'csv_data') and csv_variable in context.csv_data:
        df = context.csv_data[csv_variable]
    
    assert df is not None, f"No se encontró el CSV '{csv_variable}'"
    assert column_name in df.columns, f"La columna '{column_name}' no existe"
    
    # Resolver variables en filter_value
    if hasattr(context, 'variable_manager'):
        filter_value = context.variable_manager.resolve_variables(filter_value)
    
    # Filtrar datos
    filtered_df = df[df[column_name].astype(str).str.contains(str(filter_value), na=False)]
    
    # Guardar resultado filtrado
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(result_variable, filtered_df)
    else:
        if not hasattr(context, 'csv_data'):
            context.csv_data = {}
        context.csv_data[result_variable] = filtered_df
    
    print(f"✅ CSV filtrado: {len(filtered_df)} filas donde '{column_name}' contiene '{filter_value}' → '{result_variable}'")

@step('verifico que el CSV "{csv_variable}" tiene {expected_rows:d} filas')
@step('que el CSV "{csv_variable}" contiene {expected_rows:d} filas')
def step_verify_csv_row_count(context, csv_variable, expected_rows):
    """Verifica el número de filas en un CSV"""
    # Obtener datos del CSV
    df = None
    if hasattr(context, 'variable_manager'):
        df = context.variable_manager.get_variable(csv_variable)
    elif hasattr(context, 'csv_data') and csv_variable in context.csv_data:
        df = context.csv_data[csv_variable]
    
    assert df is not None, f"No se encontró el CSV '{csv_variable}'"
    
    actual_rows = len(df)
    assert actual_rows == expected_rows, f"El CSV tiene {actual_rows} filas, se esperaban {expected_rows}"
    print(f"✅ CSV '{csv_variable}' tiene {actual_rows} filas como se esperaba")

@step('verifico que el CSV "{csv_variable}" contiene las columnas "{column_list}"')
def step_verify_csv_columns(context, csv_variable, column_list):
    """Verifica que un CSV contiene las columnas especificadas"""
    # Obtener datos del CSV
    df = None
    if hasattr(context, 'variable_manager'):
        df = context.variable_manager.get_variable(csv_variable)
    elif hasattr(context, 'csv_data') and csv_variable in context.csv_data:
        df = context.csv_data[csv_variable]
    
    assert df is not None, f"No se encontró el CSV '{csv_variable}'"
    
    # Parsear lista de columnas
    expected_columns = [col.strip() for col in column_list.split(',')]
    
    # Verificar cada columna
    missing_columns = []
    for col in expected_columns:
        if col not in df.columns:
            missing_columns.append(col)
    
    assert len(missing_columns) == 0, f"Columnas faltantes en CSV: {missing_columns}"
    print(f"✅ CSV '{csv_variable}' contiene todas las columnas esperadas: {expected_columns}")

@step('exporto el CSV "{csv_variable}" a "{output_path}"')
def step_export_csv(context, csv_variable, output_path):
    """Exporta un CSV (o resultado filtrado) a un archivo"""
    # Obtener datos del CSV
    df = None
    if hasattr(context, 'variable_manager'):
        df = context.variable_manager.get_variable(csv_variable)
        output_path = context.variable_manager.resolve_variables(output_path)
    elif hasattr(context, 'csv_data') and csv_variable in context.csv_data:
        df = context.csv_data[csv_variable]
    
    assert df is not None, f"No se encontró el CSV '{csv_variable}'"
    
    # Crear directorio si no existe
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Exportar
    df.to_csv(output_file, index=False)
    print(f"✅ CSV exportado: {len(df)} filas a '{output_path}'")

@step('muestro un resumen del CSV "{csv_variable}"')
@step('que muestro información del CSV "{csv_variable}"')
def step_show_csv_summary(context, csv_variable):
    """Muestra un resumen del CSV cargado"""
    # Obtener datos del CSV
    df = None
    if hasattr(context, 'variable_manager'):
        df = context.variable_manager.get_variable(csv_variable)
    elif hasattr(context, 'csv_data') and csv_variable in context.csv_data:
        df = context.csv_data[csv_variable]
    
    assert df is not None, f"No se encontró el CSV '{csv_variable}'"
    
    print(f"\n📊 Resumen del CSV '{csv_variable}':")
    print(f"   📏 Dimensiones: {len(df)} filas × {len(df.columns)} columnas")
    print(f"   📋 Columnas: {', '.join(df.columns.tolist())}")
    print(f"   📈 Tipos de datos:")
    for col, dtype in df.dtypes.items():
        print(f"      {col}: {dtype}")
    
    # Mostrar primeras filas como ejemplo
    print(f"\n📄 Primeras 3 filas:")
    print(df.head(3).to_string(index=False))

# Steps adicionales para casos avanzados
@step('busco en el CSV "{csv_variable}" múltiples valores "{values_list}" en columna "{column_name}"')
def step_search_multiple_values_in_csv(context, csv_variable, values_list, column_name):
    """Busca múltiples valores en una columna del CSV"""
    # Obtener datos del CSV
    df = None
    if hasattr(context, 'variable_manager'):
        df = context.variable_manager.get_variable(csv_variable)
    elif hasattr(context, 'csv_data') and csv_variable in context.csv_data:
        df = context.csv_data[csv_variable]
    
    assert df is not None, f"No se encontró el CSV '{csv_variable}'"
    assert column_name in df.columns, f"La columna '{column_name}' no existe"
    
    # Parsear lista de valores
    search_values = [val.strip() for val in values_list.split(',')]
    
    # Buscar cada valor
    all_matches = pd.DataFrame()
    for value in search_values:
        if hasattr(context, 'variable_manager'):
            value = context.variable_manager.resolve_variables(value)
        
        matches = df[df[column_name].astype(str).str.contains(str(value), na=False)]
        all_matches = pd.concat([all_matches, matches]).drop_duplicates()
    
    print(f"✅ Búsqueda múltiple: {len(all_matches)} coincidencias para valores {search_values}")
    
    # Guardar resultados
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(f"{csv_variable}_multi_search", all_matches)

@step('ordeno el CSV "{csv_variable}" por columna "{column_name}" de forma "{order_type}" y guardo como "{result_variable}"')
def step_sort_csv_by_column(context, csv_variable, column_name, order_type, result_variable):
    """Ordena un CSV por una columna específica"""
    # Obtener datos del CSV
    df = None
    if hasattr(context, 'variable_manager'):
        df = context.variable_manager.get_variable(csv_variable)
    elif hasattr(context, 'csv_data') and csv_variable in context.csv_data:
        df = context.csv_data[csv_variable]
    
    assert df is not None, f"No se encontró el CSV '{csv_variable}'"
    assert column_name in df.columns, f"La columna '{column_name}' no existe"
    assert order_type.lower() in ['ascendente', 'descendente', 'asc', 'desc'], "Orden debe ser 'ascendente' o 'descendente'"
    
    # Determinar orden
    ascending = order_type.lower() in ['ascendente', 'asc']
    
    # Ordenar
    sorted_df = df.sort_values(by=column_name, ascending=ascending)
    
    # Guardar resultado
    if hasattr(context, 'variable_manager'):
        context.variable_manager.set_variable(result_variable, sorted_df)
    else:
        if not hasattr(context, 'csv_data'):
            context.csv_data = {}
        context.csv_data[result_variable] = sorted_df
    
    print(f"✅ CSV ordenado por '{column_name}' ({order_type}) → '{result_variable}'")