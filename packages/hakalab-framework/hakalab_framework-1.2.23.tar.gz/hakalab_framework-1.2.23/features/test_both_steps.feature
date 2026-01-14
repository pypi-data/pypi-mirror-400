@TEST
Feature: Test Both Steps
  Test para comparar ambos steps

  @TEST @smoke
  Scenario: Test con navigate
    Given I navigate to "https://httpbin.org/html"
    Then the current url should contain "httpbin"

  @TEST @smoke  
  Scenario: Test con go to url
    Given I go to the url "https://httpbin.org/html"
    Then the current url should contain "httpbin"