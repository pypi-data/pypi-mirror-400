#!/usr/bin/env python3
"""
Steps para manejo de archivos, uploads, descargas y verificación de contenido
"""
from behave import step
from playwright.sync_api import expect
import os
import time
import json
import csv
import zipfile
import tempfile
from pathlib import Path

@step('I upload file "{file_path}" to element "{element_name}" with identifier "{identifier}"')
@step('subo el archivo "{file_path}" al elemento "{element_name}" con identificador "{identifier}"')
def step_upload_file(context, file_path, element_name, identifier):
    """Sube un archivo a un elemento input[type=file]"""
    locator = context.element_locator.get_locator(identifier)
    resolved_path = context.variable_manager.resolve_variables(file_path)
    
    # Verificar que el archivo existe
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Archivo no encontrado: {resolved_path}")
    
    # Subir archivo
    context.page.locator(locator).set_input_files(resolved_path)

@step('I upload multiple files "{file_paths}" to element "{element_name}" with identifier "{identifier}"')
@step('subo múltiples archivos "{file_paths}" al elemento "{element_name}" con identificador "{identifier}"')
def step_upload_multiple_files(context, file_paths, element_name, identifier):
    """Sube múltiples archivos a un elemento input[type=file][multiple]"""
    locator = context.element_locator.get_locator(identifier)
    
    # Separar rutas de archivos
    file_list = [path.strip() for path in file_paths.split(',')]
    resolved_paths = []
    
    for file_path in file_list:
        resolved_path = context.variable_manager.resolve_variables(file_path)
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"Archivo no encontrado: {resolved_path}")
        resolved_paths.append(resolved_path)
    
    # Subir archivos
    context.page.locator(locator).set_input_files(resolved_paths)

@step('I start download by clicking element "{element_name}" with identifier "{identifier}"')
@step('inicio descarga haciendo click en el elemento "{element_name}" con identificador "{identifier}"')
def step_start_download(context, element_name, identifier):
    """Inicia una descarga haciendo click en un elemento"""
    locator = context.element_locator.get_locator(identifier)
    
    # Configurar captura de descarga
    with context.page.expect_download() as download_info:
        context.page.locator(locator).click()
    
    # Guardar información de descarga
    context.last_download = download_info.value

@step('I wait for download to complete')
@step('espero a que complete la descarga')
def step_wait_download_complete(context):
    """Espera a que complete la descarga actual"""
    if not hasattr(context, 'last_download'):
        raise AssertionError("No hay descarga activa")
    
    # Esperar a que complete la descarga
    download_path = context.last_download.path()
    
    # Guardar ruta para verificaciones posteriores
    context.last_download_path = download_path

@step('I save download as "{filename}"')
@step('guardo la descarga como "{filename}"')
def step_save_download(context, filename):
    """Guarda la descarga con un nombre específico"""
    if not hasattr(context, 'last_download'):
        raise AssertionError("No hay descarga activa")
    
    resolved_filename = context.variable_manager.resolve_variables(filename)
    
    # Crear directorio downloads si no existe
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    # Guardar archivo
    save_path = downloads_dir / resolved_filename
    context.last_download.save_as(save_path)
    
    # Actualizar ruta guardada
    context.last_download_path = str(save_path)

@step('I verify download file exists')
@step('verifico que existe el archivo descargado')
def step_verify_download_exists(context):
    """Verifica que el archivo descargado existe"""
    if not hasattr(context, 'last_download_path'):
        raise AssertionError("No hay ruta de descarga guardada")
    
    assert os.path.exists(context.last_download_path), f"Archivo descargado no existe: {context.last_download_path}"

@step('I verify download filename is "{expected_filename}"')
@step('verifico que el nombre del archivo descargado es "{expected_filename}"')
def step_verify_download_filename(context, expected_filename):
    """Verifica que el archivo descargado tiene el nombre esperado"""
    if not hasattr(context, 'last_download'):
        raise AssertionError("No hay descarga activa")
    
    resolved_filename = context.variable_manager.resolve_variables(expected_filename)
    actual_filename = context.last_download.suggested_filename()
    
    assert actual_filename == resolved_filename, f"Nombre de archivo '{actual_filename}' no coincide con '{resolved_filename}'"

@step('I verify download file size is greater than "{min_size}" bytes')
@step('verifico que el tamaño del archivo descargado es mayor a "{min_size}" bytes')
def step_verify_download_size(context, min_size):
    """Verifica que el archivo descargado tiene un tamaño mínimo"""
    if not hasattr(context, 'last_download_path'):
        raise AssertionError("No hay ruta de descarga guardada")
    
    min_size_bytes = int(min_size)
    actual_size = os.path.getsize(context.last_download_path)
    
    assert actual_size > min_size_bytes, f"Archivo de {actual_size} bytes es menor que {min_size_bytes} bytes"

@step('I verify download file contains text "{text}"')
@step('verifico que el archivo descargado contiene el texto "{text}"')
def step_verify_download_contains_text(context, text):
    """Verifica que el archivo descargado contiene un texto específico"""
    if not hasattr(context, 'last_download_path'):
        raise AssertionError("No hay ruta de descarga guardada")
    
    resolved_text = context.variable_manager.resolve_variables(text)
    
    try:
        with open(context.last_download_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert resolved_text in content, f"Texto '{resolved_text}' no encontrado en el archivo"
    except UnicodeDecodeError:
        # Intentar con diferentes encodings
        encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                with open(context.last_download_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    assert resolved_text in content, f"Texto '{resolved_text}' no encontrado en el archivo"
                    return
            except:
                continue
        raise AssertionError(f"No se pudo leer el archivo con ningún encoding")

@step('I verify download is valid JSON')
@step('verifico que la descarga es JSON válido')
def step_verify_download_json(context):
    """Verifica que el archivo descargado es JSON válido"""
    if not hasattr(context, 'last_download_path'):
        raise AssertionError("No hay ruta de descarga guardada")
    
    try:
        with open(context.last_download_path, 'r', encoding='utf-8') as f:
            json.load(f)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Archivo no es JSON válido: {e}")

@step('I verify download JSON contains key "{key}" with value "{value}"')
@step('verifico que el JSON descargado contiene la clave "{key}" con valor "{value}"')
def step_verify_download_json_content(context, key, value):
    """Verifica que el JSON descargado contiene una clave con valor específico"""
    if not hasattr(context, 'last_download_path'):
        raise AssertionError("No hay ruta de descarga guardada")
    
    resolved_key = context.variable_manager.resolve_variables(key)
    resolved_value = context.variable_manager.resolve_variables(value)
    
    try:
        with open(context.last_download_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Navegar por claves anidadas (ej: "user.name")
        keys = resolved_key.split('.')
        current_data = data
        
        for k in keys:
            if isinstance(current_data, dict) and k in current_data:
                current_data = current_data[k]
            else:
                raise AssertionError(f"Clave '{resolved_key}' no encontrada en JSON")
        
        assert str(current_data) == resolved_value, f"Valor '{current_data}' no coincide con '{resolved_value}'"
        
    except json.JSONDecodeError as e:
        raise AssertionError(f"Archivo no es JSON válido: {e}")

@step('I verify download is valid CSV with "{expected_columns}" columns')
@step('verifico que la descarga es CSV válido con "{expected_columns}" columnas')
def step_verify_download_csv(context, expected_columns):
    """Verifica que el archivo descargado es CSV válido con columnas específicas"""
    if not hasattr(context, 'last_download_path'):
        raise AssertionError("No hay ruta de descarga guardada")
    
    expected_cols = [col.strip() for col in expected_columns.split(',')]
    
    try:
        with open(context.last_download_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            actual_cols = reader.fieldnames
            
            for expected_col in expected_cols:
                assert expected_col in actual_cols, f"Columna '{expected_col}' no encontrada. Columnas disponibles: {actual_cols}"
                
    except Exception as e:
        raise AssertionError(f"Error leyendo CSV: {e}")

@step('I verify download CSV has "{expected_rows}" rows')
@step('verifico que el CSV descargado tiene "{expected_rows}" filas')
def step_verify_csv_rows(context, expected_rows):
    """Verifica que el CSV tiene un número específico de filas"""
    if not hasattr(context, 'last_download_path'):
        raise AssertionError("No hay ruta de descarga guardada")
    
    expected_count = int(expected_rows)
    
    try:
        with open(context.last_download_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            actual_count = len(rows) - 1  # Restar header
            
            assert actual_count == expected_count, f"CSV tiene {actual_count} filas, esperado {expected_count}"
            
    except Exception as e:
        raise AssertionError(f"Error leyendo CSV: {e}")

@step('I extract and verify ZIP file contains "{expected_files}"')
@step('extraigo y verifico que el ZIP contiene los archivos "{expected_files}"')
def step_verify_zip_contents(context, expected_files):
    """Verifica que un archivo ZIP contiene archivos específicos"""
    if not hasattr(context, 'last_download_path'):
        raise AssertionError("No hay ruta de descarga guardada")
    
    expected_file_list = [f.strip() for f in expected_files.split(',')]
    
    try:
        with zipfile.ZipFile(context.last_download_path, 'r') as zip_file:
            actual_files = zip_file.namelist()
            
            for expected_file in expected_file_list:
                assert expected_file in actual_files, f"Archivo '{expected_file}' no encontrado en ZIP. Archivos disponibles: {actual_files}"
                
    except zipfile.BadZipFile:
        raise AssertionError("Archivo no es un ZIP válido")

@step('I create test file "{filename}" with content "{content}"')
@step('creo archivo de prueba "{filename}" con contenido "{content}"')
def step_create_test_file(context, filename, content):
    """Crea un archivo de prueba para usar en uploads"""
    resolved_filename = context.variable_manager.resolve_variables(filename)
    resolved_content = context.variable_manager.resolve_variables(content)
    
    # Crear directorio test_files si no existe
    test_files_dir = Path("test_files")
    test_files_dir.mkdir(exist_ok=True)
    
    # Crear archivo
    file_path = test_files_dir / resolved_filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(resolved_content)
    
    # Guardar ruta para uso posterior
    context.variable_manager.set_variable('last_created_file', str(file_path))

@step('I delete test file "{filename}"')
@step('elimino archivo de prueba "{filename}"')
def step_delete_test_file(context, filename):
    """Elimina un archivo de prueba"""
    resolved_filename = context.variable_manager.resolve_variables(filename)
    
    test_files_dir = Path("test_files")
    file_path = test_files_dir / resolved_filename
    
    if file_path.exists():
        file_path.unlink()

@step('I verify file "{filename}" exists in directory "{directory}"')
@step('verifico que el archivo "{filename}" existe en el directorio "{directory}"')
def step_verify_file_exists(context, filename, directory):
    """Verifica que un archivo existe en un directorio específico"""
    resolved_filename = context.variable_manager.resolve_variables(filename)
    resolved_directory = context.variable_manager.resolve_variables(directory)
    
    file_path = Path(resolved_directory) / resolved_filename
    assert file_path.exists(), f"Archivo no encontrado: {file_path}"

@step('I get file size of "{filename}" and store in variable "{variable_name}"')
@step('obtengo el tamaño del archivo "{filename}" y lo guardo en la variable "{variable_name}"')
def step_get_file_size(context, filename, variable_name):
    """Obtiene el tamaño de un archivo y lo guarda en una variable"""
    resolved_filename = context.variable_manager.resolve_variables(filename)
    
    if not os.path.exists(resolved_filename):
        raise FileNotFoundError(f"Archivo no encontrado: {resolved_filename}")
    
    file_size = os.path.getsize(resolved_filename)
    context.variable_manager.set_variable(variable_name, file_size)