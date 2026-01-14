@TEST
Feature: Test Custom Step
  Test con step personalizado

  @TEST @smoke
  Scenario: Test navegación personalizada
    Given I test navigation to "https://httpbin.org/html"
    Then the current url should contain "httpbin"