@TEST
Feature: Test Simple
  Test básico para verificar el framework

  @TEST @smoke
  Scenario: Test navegación simple
    Given I go to the url "https://httpbin.org/html"
    Then I should see text "Herman Melville"