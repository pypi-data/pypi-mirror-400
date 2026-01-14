"""
Steps para integración con Jira y Xray
"""
from behave import step
from hakalab_framework.integrations.jira_integration import JiraIntegration
from hakalab_framework.integrations.xray_integration import XrayIntegration


@step('verifico la conexión con Jira')
@step('I verify Jira connection')
def step_verify_jira_connection(context):
    """Verificar que la conexión con Jira funciona correctamente"""
    jira = JiraIntegration()
    
    if not jira.is_configured:
        raise Exception("Jira no está configurado. Verifica las variables de entorno.")
    
    if not jira.test_connection():
        raise Exception("No se pudo conectar con Jira. Verifica las credenciales.")
    
    print("✅ Conexión con Jira verificada exitosamente")


@step('verifico que la issue "{issue_key}" existe en Jira')
@step('I verify that issue "{issue_key}" exists in Jira')
def step_verify_issue_exists(context, issue_key):
    """Verificar que una issue específica existe en Jira"""
    jira = JiraIntegration()
    
    if not jira.is_configured:
        raise Exception("Jira no está configurado")
    
    if not jira.issue_exists(issue_key):
        raise Exception(f"Issue {issue_key} no existe en Jira")
    
    print(f"✅ Issue {issue_key} encontrada en Jira")


@step('agrego un comentario "{comment}" a la issue "{issue_key}"')
@step('I add comment "{comment}" to issue "{issue_key}"')
def step_add_comment_to_issue(context, comment, issue_key):
    """Agregar un comentario a una issue de Jira"""
    jira = JiraIntegration()
    
    if not jira.is_configured:
        raise Exception("Jira no está configurado")
    
    success = jira.add_comment_to_issue(issue_key, comment)
    
    if not success:
        raise Exception(f"No se pudo agregar comentario a la issue {issue_key}")
    
    print(f"✅ Comentario agregado a issue {issue_key}")


@step('adjunto el archivo "{file_path}" a la issue "{issue_key}"')
@step('I attach file "{file_path}" to issue "{issue_key}"')
def step_attach_file_to_issue(context, file_path, issue_key):
    """Adjuntar un archivo a una issue de Jira"""
    jira = JiraIntegration()
    
    if not jira.is_configured:
        raise Exception("Jira no está configurado")
    
    # Resolver variables en la ruta del archivo
    resolved_path = context.variable_manager.resolve_variables(file_path)
    
    success = jira.attach_file_to_issue(issue_key, resolved_path)
    
    if not success:
        raise Exception(f"No se pudo adjuntar archivo a la issue {issue_key}")
    
    print(f"✅ Archivo adjuntado a issue {issue_key}")


@step('verifico la configuración de Xray')
@step('I verify Xray configuration')
def step_verify_xray_configuration(context):
    """Verificar que Xray está configurado correctamente"""
    jira = JiraIntegration()
    xray = XrayIntegration(jira)
    
    if not jira.is_configured:
        raise Exception("Jira no está configurado (requerido para Xray)")
    
    if not xray.is_configured:
        raise Exception("Xray no está configurado o habilitado")
    
    print("✅ Xray configurado correctamente")


@step('creo un test execution "{summary}" en Xray')
@step('I create test execution "{summary}" in Xray')
def step_create_test_execution(context, summary):
    """Crear un Test Execution en Xray"""
    jira = JiraIntegration()
    xray = XrayIntegration(jira)
    
    if not xray.is_configured:
        raise Exception("Xray no está configurado")
    
    execution_key = xray.create_test_execution(summary)
    
    if not execution_key:
        raise Exception("No se pudo crear el Test Execution")
    
    # Guardar la clave del execution en el contexto para uso posterior
    context.current_test_execution = execution_key
    print(f"✅ Test Execution creado: {execution_key}")


@step('agrego los tests "{test_keys}" al test execution actual')
@step('I add tests "{test_keys}" to current test execution')
def step_add_tests_to_execution(context, test_keys):
    """Agregar tests a un Test Execution"""
    if not hasattr(context, 'current_test_execution'):
        raise Exception("No hay un Test Execution activo. Crea uno primero.")
    
    jira = JiraIntegration()
    xray = XrayIntegration(jira)
    
    if not xray.is_configured:
        raise Exception("Xray no está configurado")
    
    # Convertir string de claves separadas por coma a lista
    test_list = [key.strip() for key in test_keys.split(',')]
    
    success = xray.add_tests_to_execution(context.current_test_execution, test_list)
    
    if not success:
        raise Exception("No se pudieron agregar los tests al Test Execution")
    
    print(f"✅ Tests agregados al Test Execution {context.current_test_execution}")


@step('actualizo el estado del test "{test_key}" a "{status}" en el test execution actual')
@step('I update test "{test_key}" status to "{status}" in current test execution')
def step_update_test_status(context, test_key, status):
    """Actualizar el estado de un test en un Test Execution"""
    if not hasattr(context, 'current_test_execution'):
        raise Exception("No hay un Test Execution activo. Crea uno primero.")
    
    jira = JiraIntegration()
    xray = XrayIntegration(jira)
    
    if not xray.is_configured:
        raise Exception("Xray no está configurado")
    
    # Validar estado
    valid_statuses = ['PASS', 'FAIL', 'TODO']
    status_upper = status.upper()
    
    if status_upper not in valid_statuses:
        raise Exception(f"Estado inválido: {status}. Estados válidos: {', '.join(valid_statuses)}")
    
    success = xray.update_test_status(context.current_test_execution, test_key, status_upper)
    
    if not success:
        raise Exception(f"No se pudo actualizar el estado del test {test_key}")
    
    print(f"✅ Estado del test {test_key} actualizado a {status_upper}")


@step('verifico que el test "{test_key}" es de tipo Test en Jira')
@step('I verify that test "{test_key}" is of type Test in Jira')
def step_verify_test_type(context, test_key):
    """Verificar que una issue es de tipo Test"""
    jira = JiraIntegration()
    
    if not jira.is_configured:
        raise Exception("Jira no está configurado")
    
    issue = jira.get_issue(test_key)
    
    if not issue:
        raise Exception(f"Issue {test_key} no encontrada")
    
    issue_type = issue.get('fields', {}).get('issuetype', {}).get('name', '')
    
    if issue_type.lower() not in ['test', 'teste']:
        raise Exception(f"Issue {test_key} no es de tipo Test (tipo actual: {issue_type})")
    
    print(f"✅ Issue {test_key} es de tipo Test")


@step('busco issues en Jira con JQL "{jql}"')
@step('I search issues in Jira with JQL "{jql}"')
def step_search_issues_jql(context, jql):
    """Buscar issues usando JQL y guardar resultados"""
    jira = JiraIntegration()
    
    if not jira.is_configured:
        raise Exception("Jira no está configurado")
    
    # Resolver variables en el JQL
    resolved_jql = context.variable_manager.resolve_variables(jql)
    
    issues = jira.search_issues(resolved_jql)
    
    # Guardar resultados en el contexto
    context.jira_search_results = issues
    
    print(f"✅ Búsqueda JQL completada. {len(issues)} issues encontradas")


@step('verifico que la búsqueda JQL encontró "{expected_count}" issues')
@step('I verify that JQL search found "{expected_count}" issues')
def step_verify_jql_results_count(context, expected_count):
    """Verificar el número de resultados de una búsqueda JQL"""
    if not hasattr(context, 'jira_search_results'):
        raise Exception("No hay resultados de búsqueda JQL. Ejecuta una búsqueda primero.")
    
    expected = int(expected_count)
    actual = len(context.jira_search_results)
    
    if actual != expected:
        raise Exception(f"Se esperaban {expected} issues, pero se encontraron {actual}")
    
    print(f"✅ Búsqueda JQL encontró {actual} issues como se esperaba")


@step('muestro información de la integración Jira/Xray')
@step('I show Jira/Xray integration information')
def step_show_integration_info(context):
    """Mostrar información sobre el estado de la integración"""
    jira = JiraIntegration()
    
    print("\n" + "="*50)
    print("📋 INFORMACIÓN DE INTEGRACIÓN JIRA/XRAY")
    print("="*50)
    
    # Información de Jira
    print(f"🔗 Jira URL: {jira.jira_url or 'No configurado'}")
    print(f"📧 Jira Email: {jira.jira_email or 'No configurado'}")
    print(f"🏷️ Jira Project: {jira.jira_project or 'No configurado'}")
    print(f"💬 Mensaje de comentario: {jira.jira_comment_message}")
    print(f"✅ Jira configurado: {'Sí' if jira.is_configured else 'No'}")
    
    if jira.is_configured:
        connection_ok = jira.test_connection()
        print(f"🔌 Conexión Jira: {'OK' if connection_ok else 'Error'}")
    
    # Información de Xray
    xray = XrayIntegration(jira)
    print(f"🧪 Xray habilitado: {'Sí' if xray.xray_enabled else 'No'}")
    print(f"📋 Xray Test Plan: {xray.xray_test_plan or 'No configurado'}")
    print(f"✅ Xray configurado: {'Sí' if xray.is_configured else 'No'}")
    
    print("="*50)