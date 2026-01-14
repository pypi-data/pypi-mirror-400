@TEST
Feature: Demo
  Como usuario del framework
  Quiero verificar que la navegación funciona correctamente
  Para poder usar el framework en mis pruebas

  @TEST @smoke
  Scenario: Navegación básica
    Given I go to the url "https://www.hakalab.com"
    When I go to the url "https://www.hakalab.com/productos"
    Then I go to the url "https://www.hakalab.com/productos"