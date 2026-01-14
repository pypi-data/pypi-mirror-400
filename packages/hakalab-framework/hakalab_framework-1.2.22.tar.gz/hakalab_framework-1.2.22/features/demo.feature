@TEST
Feature: Demo del Framework Hakalab
  Como usuario del framework
  Quiero verificar que la navegación funciona correctamente
  Para poder usar el framework en mis pruebas

  @TEST @smoke
  Scenario: Navegación básica
    Given I go to the url "https://httpbin.org/html"
    Then the current url should contain "httpbin"