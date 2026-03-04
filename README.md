# Tandoor Automation Test Project

Automation test project for the **Tandoor Recipes** web application.

## Stack

- Python
- Pytest
- Selenium
- Requests
- Allure Report
- Page Object Model

## Test Coverage

### API Tests
- Get recipes
- Create recipe
- Delete recipe

### UI Tests
- Open homepage
- Login
- Open meal plan page

### UI + API Flow
- Create meal plan via UI
- Validate via API
- Delete meal plan

## Project Structure

## How to run

### 1) Install dependencies
```bash
pip install -r requirements.txt

## Allure report

Run:
```bash
pytest --alluredir=allure-results
allure serve allure-results
![img.png](img.png)