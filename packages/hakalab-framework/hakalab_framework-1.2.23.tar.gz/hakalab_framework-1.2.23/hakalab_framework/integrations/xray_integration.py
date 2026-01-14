"""
Integración con Xray (by Blend) para el Hakalab Framework
"""
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from .jira_integration import JiraIntegration


class XrayIntegration:
    """Clase para manejar la integración con Xray"""
    
    def __init__(self, jira_integration: JiraIntegration):
        """Inicializar la integración con Xray"""
        self.jira = jira_integration
        self.xray_enabled = os.getenv('XRAY_ENABLED', 'false').lower() == 'true'
        self.xray_test_plan = os.getenv('XRAY_TEST_PLAN')
        
        # Mapeo de estados de Behave a Xray
        self.status_mapping = {
            'passed': 'PASS',
            'failed': 'FAIL', 
            'skipped': 'TODO',
            'undefined': 'TODO',
            'pending': 'TODO'
        }
        
        self.is_configured = self._validate_configuration()
    
    def _validate_configuration(self) -> bool:
        """Validar que Xray esté configurado correctamente"""
        if not self.xray_enabled:
            print("ℹ️ Xray deshabilitado")
            return False
        
        if not self.jira.is_configured:
            print("❌ Xray requiere Jira configurado")
            return False
        
        print("✅ Xray configurado correctamente")
        return True
    
    def create_test_execution(self, summary: str, description: str = None) -> Optional[str]:
        """Crear un Test Execution en Xray"""
        if not self.is_configured:
            return None
        
        try:
            # Datos para crear el Test Execution
            execution_data = {
                "fields": {
                    "project": {"key": self.jira.jira_project},
                    "summary": summary,
                    "issuetype": {"name": "Test Execution"},
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": description or f"Test Execution creado automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
            
            # Si hay un test plan configurado, asociarlo
            if self.xray_test_plan:
                execution_data["fields"]["customfield_testplan"] = {"key": self.xray_test_plan}
            
            response = self.jira.session.post(
                f"{self.jira.jira_url}/rest/api/3/issue",
                json=execution_data
            )
            
            if response.status_code == 201:
                execution_key = response.json()["key"]
                print(f"✅ Test Execution creado: {execution_key}")
                return execution_key
            else:
                print(f"❌ Error al crear Test Execution: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error al crear Test Execution: {str(e)}")
            return None
    
    def add_tests_to_execution(self, execution_key: str, test_keys: List[str]) -> bool:
        """Agregar tests a un Test Execution"""
        if not self.is_configured:
            return False
        
        try:
            # Usar la API de Xray para agregar tests
            xray_data = {
                "add": test_keys
            }
            
            response = self.jira.session.post(
                f"{self.jira.jira_url}/rest/raven/1.0/api/testexec/{execution_key}/test",
                json=xray_data
            )
            
            if response.status_code == 200:
                print(f"✅ Tests agregados al Test Execution {execution_key}: {', '.join(test_keys)}")
                return True
            else:
                print(f"❌ Error al agregar tests al Test Execution: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error al agregar tests al Test Execution: {str(e)}")
            return False
    
    def update_test_status(self, execution_key: str, test_key: str, status: str, comment: str = None) -> bool:
        """Actualizar el estado de un test en un Test Execution"""
        if not self.is_configured:
            return False
        
        try:
            # Mapear estado si es necesario
            xray_status = self.status_mapping.get(status.lower(), status.upper())
            
            # Datos para actualizar el estado
            status_data = {
                "status": xray_status
            }
            
            if comment:
                status_data["comment"] = comment
            
            response = self.jira.session.put(
                f"{self.jira.jira_url}/rest/raven/1.0/api/testexec/{execution_key}/test/{test_key}/status",
                json=status_data
            )
            
            if response.status_code == 200:
                print(f"✅ Estado actualizado para {test_key} en {execution_key}: {xray_status}")
                return True
            else:
                print(f"❌ Error al actualizar estado de {test_key}: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error al actualizar estado de {test_key}: {str(e)}")
            return False
    
    def get_test_issues(self, test_keys: List[str]) -> List[str]:
        """Filtrar y validar que las claves correspondan a issues de tipo Test"""
        if not self.is_configured:
            return []
        
        valid_tests = []
        
        for test_key in test_keys:
            issue = self.jira.get_issue(test_key)
            if issue:
                issue_type = issue.get('fields', {}).get('issuetype', {}).get('name', '')
                if issue_type.lower() in ['test', 'teste']:
                    valid_tests.append(test_key)
                else:
                    print(f"⚠️ {test_key} no es un issue de tipo Test (tipo actual: {issue_type})")
            else:
                print(f"⚠️ {test_key} no encontrado en Jira")
        
        return valid_tests
    
    def process_scenario_results(self, execution_key: str, scenario_results: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Procesar resultados de escenarios y actualizar estados en Xray"""
        results = {}
        
        if not self.is_configured:
            print("⚠️ Xray no configurado, saltando actualización de estados")
            return results
        
        for scenario_result in scenario_results:
            test_key = scenario_result.get('test_key')
            status = scenario_result.get('status')
            scenario_name = scenario_result.get('name', 'N/A')
            error_message = scenario_result.get('error_message')
            
            if test_key and status:
                # Crear comentario con información del escenario
                comment_parts = [f"Escenario: {scenario_name}"]
                if error_message:
                    comment_parts.append(f"Error: {error_message}")
                
                comment = " | ".join(comment_parts)
                
                success = self.update_test_status(execution_key, test_key, status, comment)
                results[test_key] = success
            else:
                print(f"⚠️ Escenario sin test_key o status válido: {scenario_name}")
        
        return results
    
    def create_execution_from_feature(self, feature_name: str, scenario_results: List[Dict[str, Any]]) -> Optional[str]:
        """Crear un Test Execution completo a partir de resultados de feature"""
        if not self.is_configured:
            return None
        
        # Extraer test keys de los escenarios
        test_keys = []
        for result in scenario_results:
            test_key = result.get('test_key')
            if test_key:
                test_keys.append(test_key)
        
        if not test_keys:
            print("⚠️ No se encontraron test keys válidos en los escenarios")
            return None
        
        # Validar que son issues de tipo Test
        valid_test_keys = self.get_test_issues(test_keys)
        
        if not valid_test_keys:
            print("⚠️ No se encontraron issues de tipo Test válidos")
            return None
        
        # Crear Test Execution
        timestamp = datetime.now().strftime("%d-%m %H:%M")
        summary = f"Test execution - {feature_name} - {timestamp}"
        description = f"Ejecución automática de tests para feature: {feature_name}"
        
        execution_key = self.create_test_execution(summary, description)
        
        if not execution_key:
            return None
        
        # Agregar tests al execution
        if self.add_tests_to_execution(execution_key, valid_test_keys):
            # Actualizar estados
            self.process_scenario_results(execution_key, scenario_results)
        
        return execution_key
    
    def extract_test_key_from_tags(self, tags: List[str]) -> Optional[str]:
        """Extraer clave de test de los tags de un escenario"""
        for tag in tags:
            test_key = self.jira.extract_issue_key_from_tag(tag)
            if test_key:
                # Verificar que es un issue de tipo Test
                issue = self.jira.get_issue(test_key)
                if issue:
                    issue_type = issue.get('fields', {}).get('issuetype', {}).get('name', '')
                    if issue_type.lower() in ['test', 'teste']:
                        return test_key
        
        return None