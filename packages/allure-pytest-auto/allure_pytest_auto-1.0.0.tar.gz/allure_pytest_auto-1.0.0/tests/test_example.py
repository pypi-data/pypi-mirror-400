import allure

#Steps for allure report

@allure.step("Initialize numbers: {a} and {b}")
def initialize_numbers(a, b):
    return a, b

@allure.step("Add numbers {a} + {b}")
def add_numbers(a, b):
    return a + b

@allure.step("Multiply numbers {a} * {b}")
def multiply_numbers(a, b):
    return a * b

@allure.step("Divide numbers {a} + {b}")
def divide_numbers(a, b):
    return a / b

@allure.step("Substract numbers {a} - {b}")
def substract_numbers(a, b):
    return a - b

@allure.step("Verify result")
def verify_result(actual, expected):
    assert actual == expected

#Tests

@allure.feature("Math - Addition and Substraction")
@allure.story("Addition")
@allure.title("Addition of numbers")
@allure.severity(allure.severity_level.CRITICAL)

def test_addition():
    a, b = initialize_numbers(5, 3)
    result = add_numbers(a, b)
    verify_result(result, a + b)


@allure.feature("Math - Addition and Substraction")
@allure.story("Substraction")
@allure.title("Substraction of numbers")
@allure.severity(allure.severity_level.NORMAL)

def test_substraction():
    a, b = initialize_numbers(5, 3)
    result = substract_numbers(a, b)
    verify_result(result, a - b)

@allure.feature("Math - Multiplication and Division")
@allure.story("Multiplication")
@allure.title("Multiplication of numbers")
@allure.severity(allure.severity_level.MINOR)

def test_multiplication():
    a, b = initialize_numbers(5, 3)
    result = multiply_numbers(a, b)
    verify_result(result, a * b)

@allure.feature("Math - Multiplication and Division")
@allure.story("Division")
@allure.title("Division of numbers")
@allure.severity(allure.severity_level.MINOR)

def test_division():
    a, b = initialize_numbers(6, 3)
    result = divide_numbers(a, b)
    verify_result(result, a / b)