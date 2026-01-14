"""
Integración con Jira para el Hakalab Framework
"""
import os
import requests
import base64
import json
from typing import Optional, Dict, Any, List
from datetime import datetime


class JiraIntegration:
    """Clase para manejar la integración con Jira"""
    
    def __init__(self):
        """Inicializar la integración con Jira usando variables de entorno"""
        self.jira_url = os.getenv('JIRA_URL')
        self.jira_email = os.getenv('JIRA_EMAIL')
        self.jira_token = os.getenv('JIRA_TOKEN')
        self.jira_project = os.getenv('JIRA_PROJECT')
        self.jira_comment_message = os.getenv('JIRA_COMMENT_MESSAGE', 'Reporte prueba de QA')
        
        self.is_configured = self._validate_configuration()
        self.session = None
        
        if self.is_configured:
            self._setup_session()
    
    def _validate_configuration(self) -> bool:
        """Validar que todas las variables de entorno necesarias estén configuradas"""
        required_vars = [
            self.jira_url,
            self.jira_email, 
            self.jira_token,
            self.jira_project
        ]
        
        if not all(required_vars):
            missing = []
            if not self.jira_url:
                missing.append('JIRA_URL')
            if not self.jira_email:
                missing.append('JIRA_EMAIL')
            if not self.jira_token:
                missing.append('JIRA_TOKEN')
            if not self.jira_project:
                missing.append('JIRA_PROJECT')
            
            print(f"⚠️ Jira no configurado. Variables faltantes: {', '.join(missing)}")
            return False
        
        return True
    
    def _setup_session(self):
        """Configurar la sesión HTTP con autenticación"""
        self.session = requests.Session()
        
        # Crear credenciales básicas
        credentials = f"{self.jira_email}:{self.jira_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        self.session.headers.update({
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_connection(self) -> bool:
        """Probar la conexión con Jira"""
        if not self.is_configured:
            return False
        
        try:
            response = self.session.get(f"{self.jira_url}/rest/api/3/myself")
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ Conexión exitosa con Jira. Usuario: {user_info.get('displayName', 'N/A')}")
                return True
            else:
                print(f"❌ Error de conexión con Jira: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error al conectar con Jira: {str(e)}")
            return False
    
    def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Obtener información de una issue de Jira"""
        if not self.is_configured:
            return None
        
        try:
            response = self.session.get(f"{self.jira_url}/rest/api/3/issue/{issue_key}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"⚠️ Issue {issue_key} no encontrada en Jira")
                return None
            else:
                print(f"❌ Error al obtener issue {issue_key}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error al obtener issue {issue_key}: {str(e)}")
            return None
    
    def issue_exists(self, issue_key: str) -> bool:
        """Verificar si una issue existe en Jira"""
        issue = self.get_issue(issue_key)
        return issue is not None
    
    def add_comment_to_issue(self, issue_key: str, comment_text: str) -> bool:
        """Agregar un comentario a una issue de Jira"""
        if not self.is_configured:
            return False
        
        try:
            comment_data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment_text
                                }
                            ]
                        }
                    ]
                }
            }
            
            response = self.session.post(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment",
                json=comment_data
            )
            
            if response.status_code == 201:
                print(f"✅ Comentario agregado a issue {issue_key}")
                return True
            else:
                print(f"❌ Error al agregar comentario a {issue_key}: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error al agregar comentario a {issue_key}: {str(e)}")
            return False
    
    def attach_file_to_issue(self, issue_key: str, file_path: str, filename: str = None) -> bool:
        """Adjuntar un archivo a una issue de Jira"""
        if not self.is_configured:
            return False
        
        if not os.path.exists(file_path):
            print(f"❌ Archivo no encontrado: {file_path}")
            return False
        
        try:
            if filename is None:
                filename = os.path.basename(file_path)
            
            # Configurar headers para upload de archivo
            headers = {
                'Authorization': self.session.headers['Authorization'],
                'X-Atlassian-Token': 'no-check'
            }
            
            with open(file_path, 'rb') as file:
                files = {'file': (filename, file, 'application/octet-stream')}
                
                response = requests.post(
                    f"{self.jira_url}/rest/api/3/issue/{issue_key}/attachments",
                    headers=headers,
                    files=files
                )
            
            if response.status_code == 200:
                print(f"✅ Archivo {filename} adjuntado a issue {issue_key}")
                return True
            else:
                print(f"❌ Error al adjuntar archivo a {issue_key}: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error al adjuntar archivo a {issue_key}: {str(e)}")
            return False
    
    def attach_report_to_issue(self, issue_key: str, report_path: str) -> bool:
        """Adjuntar reporte HTML a una issue con comentario personalizado"""
        if not self.is_configured:
            return False
        
        # Verificar que la issue existe
        if not self.issue_exists(issue_key):
            print(f"⚠️ Issue {issue_key} no existe, saltando adjunto de reporte")
            return False
        
        # Adjuntar el archivo
        success = self.attach_file_to_issue(issue_key, report_path)
        
        if success:
            # Agregar comentario
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            comment = f"{self.jira_comment_message} - {timestamp}"
            self.add_comment_to_issue(issue_key, comment)
        
        return success
    
    def search_issues(self, jql: str) -> List[Dict[str, Any]]:
        """Buscar issues usando JQL"""
        if not self.is_configured:
            return []
        
        try:
            params = {
                'jql': jql,
                'maxResults': 100,
                'fields': 'key,summary,status,issuetype'
            }
            
            response = self.session.get(
                f"{self.jira_url}/rest/api/3/search",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('issues', [])
            else:
                print(f"❌ Error en búsqueda JQL: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error en búsqueda JQL: {str(e)}")
            return []
    
    def get_project_issues(self, issue_type: str = None) -> List[Dict[str, Any]]:
        """Obtener issues del proyecto configurado"""
        jql = f"project = {self.jira_project}"
        if issue_type:
            jql += f" AND issuetype = '{issue_type}'"
        
        return self.search_issues(jql)
    
    def extract_issue_key_from_tag(self, tag: str) -> Optional[str]:
        """Extraer clave de issue de un tag de Behave"""
        # Remover @ si está presente
        clean_tag = tag.lstrip('@')
        
        # Verificar formato de issue key (PROJECT-NUMBER)
        if '-' in clean_tag and clean_tag.replace('-', '').replace(self.jira_project, '').isdigit():
            return clean_tag.upper()
        
        return None
    
    def process_feature_tags(self, feature_tags: List[str], report_path: str) -> Dict[str, bool]:
        """Procesar tags de feature y adjuntar reportes a issues válidas"""
        results = {}
        
        if not self.is_configured:
            print("⚠️ Jira no configurado, saltando procesamiento de tags")
            return results
        
        for tag in feature_tags:
            issue_key = self.extract_issue_key_from_tag(tag)
            if issue_key:
                print(f"🔍 Procesando tag {tag} como issue {issue_key}")
                success = self.attach_report_to_issue(issue_key, report_path)
                results[issue_key] = success
            else:
                print(f"⚠️ Tag {tag} no es una clave de issue válida")
        
        return results