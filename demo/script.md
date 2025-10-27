# Testcoveragent


## Criando uma aplicação e melhorando a cobertura de testes com um Agente usando o GitHub Copilot CLI e o GitHub Copilot Coding Agent.

1. Clone esse repositorio localmente no seu computador e abra o Visual Studio Code a partir do repositorio clonado. Garanta que voce tenha o Python 3.13 + PIP instalado no seu computador.

2. Crie um virtual environment do Python e inicie ele. Comandos abaixo:
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Execute a aplicação Django localmente.
    ```
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    ```
4. Crie a pasta chamada .github e outra chamada .vscode, ambas na raiz do repositório, crie também a pasta chamada workflows, outra chamada prompts e crie também o arquivo chamado copilot-instructions.md.

4. Crie um novo arquivo de prompt chamado `testcoveragent.prompt.md` com o seguinte conteúdo:

    ```
    ---
    mode: 'agent'
    description: 'Analisa a cobertura de código e sugere testes unitários para melhorar a cobertura geral.'
    tools: ['search', 'runCommands', 'runTests']
    ---

    # Análise de melhoria de cobertura de código por testcoveragent 

    Você é um engenheiro especialista em garantia de qualidade e testador de software. Sua tarefa é analisar o code coverage do código fornecido APENAS nos diretórios apps/ e propor testes unitários que melhorem a cobertura geral dos testes.

    RESTRIÇÕES IMPORTANTES:
    - Acesse APENAS arquivos dentro do diretório apps/
    - Use APENAS os relatórios de coverage existentes (coverage.xml, htmlcov/)
    - NÃO tente criar ou acessar arquivos fora do workspace do projeto
    - NÃO acesse arquivos de sistema ou paths absolutos

    Sua análise deve:
    1. Verificar os relatórios de coverage existentes
    2. Identificar funções, métodos ou classes não testadas no diretório apps/
    3. Sugerir casos de teste específicos para melhorar a cobertura
    4. Criar um relatório estruturado focado apenas no código do projeto Django

    Crie uma nova Issue no repositório octocaio/testcoveragent com o título "Análise de melhoria de cobertura de código por testcoveragent - [Data Atual]" e inclua o relatório compilado no corpo da issue. Certifique-se de que o relatório esteja bem formatado e fácil de ler.
    ```
5. Crie um novo workflow dentro da pasta .github/workflows chamado build.yml com o seguinte conteúdo:

    ```yaml
    name: Build and Test with Copilot CLI

    on:
    workflow_dispatch:

    jobs:
    copilot-cli-build-and-test:
        runs-on: ubuntu-latest

        steps:
        - name: Checkout repository
            uses: actions/checkout@v3

        - name: Set up Node.js
            uses: actions/setup-node@v4
            with:
            node-version: '20'

        - name: Install GitHub Copilot CLI 
            run: |
            npm install -g @github/copilot

        - name: Run Copilot CLI 
            env:
            GITHUB_TOKEN: ${{ secrets.COPILOT_TOKEN }}
            GH_TOKEN: ${{ secrets.COPILOT_TOKEN }}
            run: |
            echo "Testing Copilot CLI..."

            # User Copilot CLI
            copilot -p "Porque o ceu é azul?" --allow-all-tools
    ```

    Este workflow vai instalar e executar o GitHub Copilot CLI e executar um prompt simples para validar se está funcionando corretamente.
6. Agora peça ao GitHub Copilot para adicionar um arquivo .gitignore no seu repositorio.
7. Adicione também no arquivo copilot-instructions.md o seguinte conteúdo:

    ```
    ## Instruções gerais para o GitHub Copilot

    # Informações do repositório
    - Organização/Usuário: `octodemo`
    - Nome do repositório: `testcoveragent`

    ## instruções gerais

        ** 1. Garanta que o arquivo .gitignore esteja configurado para ignorar arquivos desnecessários, como arquivos temporários, binários e dependências, sempre pergunte se deve atualizar o .gitignore ao adicionar novos tipos de arquivos ao projeto.

        ** 2. Mantenha o README.md atualizado com informações relevantes sobre o projeto, incluindo instruções, sempre pergunte se deve atualizar o README.md ao fazer mudanças significativas.
    ```
8. Agora execute os comandos abaixo para adicionar, commitar e dar push nas mudanças para o repositório remoto.

    ```bash
    git add .
    git commit -m "Commit inicial com o app Django e a configuração do Copilot CLI"
    git push origin demo-<seu-nome-de-usuario>
    ```
7. Agora vá até o repositorio remoto no GitHub e crie um Personal Access Token (Fine-grained - GitHub -> Settings -> Developer Settings -> Personal Access Tokens -> Fine-grained tokens) com as permissões necessárias para o GitHub Copilot CLI funcionar corretamente para analisar nosso código e criar issues. As permissões necessarias para que o Copilot possa operar da forma que o nosso agente precisa são:

    - **Actions**: Read
    - **Contents**: Read
    - **Issues**: Write
    - **Metadata**: Read
    - **Pull requests**: Write (se for criar PRs)

8. Adicione o token criado como um segredo do repositório (GitHub -> Settings -> Secrets and variables -> Actions -> New repository secret) com o nome `COPILOT_TOKEN`.

9. Execute o workflow manualmente (GitHub -> Actions -> Build and Test with Copilot CLI -> Run workflow) para validar se o GitHub Copilot CLI está funcionando corretamente.

10. Você deve ver a saída do passo "Run Copilot CLI" com a resposta para o prompt "Porque o ceu é azul?".

11. Agora peça ao Copilot para adicionar os passos de Build do Django no workflow build.yml, incluindo a instalação das dependências, migrações e execução dos testes, utilize o prompt abaixo

    ````
    Adicione ao workflow #file:build.yml os passos para fazer o setup do Python, instalar as dependências do Python incluindo coverage, pytest-cov e pytest-django, que execute o django migrate, rode os testes Django com coverage usando o comando nativo do Django (manage.py test), faça verificações de code quality com isort e black, e upload dos coverage reports usando upload-artifact@v4.

    Garanta que:
    1. A variável DJANGO_SETTINGS_MODULE seja configurada nos passos de migrate e test coverage
    2. Use 'coverage run --source="apps" manage.py test' ao invés de pytest para evitar erros de AppRegistryNotReady
    3. Gere os relatórios de coverage com 'coverage xml', 'coverage html' e 'coverage report'
    4. Crie um arquivo setup.cfg com configuração do pytest-django para uso futuro
    5. Instale as dependências: pytest-cov, pytest-django, coverage
    ````

12. Agora temos um artefato com o coverage reports, vamos utilizar o Copilot CLI para analisar o coverage report e sugerir melhorias na cobertura de código. Para isso, vamos alterar o nosso workflow para enviar um novo prompt ao Copilot CLI.

    ```yaml
    - name: Generate Weekly Copilot Report and Create Issue
        env: 
            GITHUB_TOKEN: ${{ secrets.COPILOT_TOKEN }}
            GH_TOKEN: ${{ secrets.COPILOT_TOKEN }}
        run: |
          echo "Testing Copilot CLI..."

          # Use Copilot CLI 
          copilot -p "Execute the testcoveragent.prompt.md prompt file" --allow-all-tools --log-dir /tmp/logs --log-level debug


    ```
13. Execute o workflow manualmente novamente (GitHub -> Actions -> Build and Test with Copilot CLI -> Run workflow) para validar se o GitHub Copilot CLI está funcionando corretamente e criando a issue com o relatório de cobertura sugerido pelo agente.

14. Agora vá até a issue criada e atribua a issue ao Copilot, dessa modo vamos disparar uma execução do GitHub Copilot Coding Agent, que vai gerar uma pull requetest com os testes sugeridos para melhorar a cobertura de código do app Django..

## Utilizando um agent de Behavior Driven Development (BDD) e Playwright para descobrir e executar testes E2E automatizados.

1. Crie um novo arquivo de prompt chamado `bdd-agent.prompt.md` com o seguinte conteúdo:

    ```
    ---
    description: 'Help me create a BDD feature file based on user requirements.'
    tools: ['changes', 'codebase', 'editFiles', 'fetch', 'githubRepo', 'runCommands', 'search', 'usages', 'playwright', 'github', 'Azure MCP Server']
    ---
    # BDD Feature File Generator

    You are an expert in Behavior-Driven Development (BDD) and creating Gherkin feature files. Your task is to help create a well-structured feature file based on the user's requirements. Leverage the [architecture doc](../../docs/architecture.md).

    ## Clarification Phase

    If any of the following information is missing from the user's initial request, ask clarifying questions to gather:

    1. **Feature Name**: What is the name of the feature you want to describe?
    2. **Business Value**: What business value does this feature provide? (As a [role], I want [feature], so that [benefit])
    3. **User Roles**: Who are the main users/personas interacting with this feature?
    4. **Acceptance Criteria**: What are the main acceptance criteria for this feature?
    5. **Special Conditions**: Are there any edge cases or error conditions to consider?
    6. **Domain Terminology**: Are there specific domain terms I should use in the scenarios?

    ## Output Guidelines

    - Generate ONLY the feature file content in Gherkin syntax, no implementation code
    - Use the standard Gherkin keywords: Feature, Scenario, Given, When, Then, And, But
    - Include a clear feature description that explains the business value
    - Create concise, clear scenarios that cover the main acceptance criteria
    - Format the feature file properly with correct indentation

    ## Example Structure

        ```gherkin
        Feature: [Feature Name]
        As a [role]
        I want [feature]
        So that [benefit]

        Scenario: [Scenario Name]
            Given [precondition]
            When [action]
            Then [expected result]

        Scenario: [Another Scenario Name]
            Given [another precondition]
            When [another action]
            Then [another expected result]
        ```

    Remember to focus solely on the feature specification and not on implementation details or automation code.
    ```

2. Agora vá até .vscode/mcp.json e adicione o servidor MCP do PlayWright:
   
    ```json
    {

    "servers": {
        "playwright": {
        "command": "npx",
        "args": [
            "@playwright/mcp@latest"
         ]
        }
     }
    }
    ```
3. Inicie o servidor MCP usando a opção start que vai aparecer no arquivo mcp.json.

4. Agora arraste o arquivo bdd.prompt.md e execute o prompt abaixo: 

    ```
    Crie um feature file com alguns cenarios de testes em /apps/finance

    ```
5.Agora veja que o agente criou um arquivo .feature com os cenarios de testes usando Gherkin, agora peça para o agente executar alguns dos cenarios via Playwright:

    ```
    Execute os cenarios de testes do arquivo .feature criado anteriormente usando Playwright.

    ```
6. Acompanhe enquanto o Copilot da comandos para executar os testes E2E via Playwright em um browser!.


