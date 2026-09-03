# 📦 Autonomous Inventory Agent

Sistema de gerenciamento e simulação autônoma de estoque desenvolvido em Python, PostgreSQL e Streamlit.

O projeto combina análise de vendas, monitoramento de estoque, agentes autônomos, decisões de reposição, simulação de vendas e fornecedores e uma interface analítica para acompanhar toda a operação.

A proposta é demonstrar como um sistema de estoque pode observar a operação, identificar problemas, tomar decisões e executar ações automaticamente.

---

## 🎯 Objetivo

O Autonomous Inventory Agent simula uma operação de estoque baseada em dados históricos de vendas.

O sistema utiliza uma base histórica de e-commerce para construir uma operação inicial e, a partir dela, permite executar uma simulação controlada na qual:

- vendas são geradas automaticamente;
- o estoque é atualizado;
- produtos com estoque baixo são identificados;
- tarefas de reposição são criadas;
- agentes analisam as necessidades de reposição;
- compras são realizadas automaticamente;
- fornecedores possuem tempo de entrega;
- pedidos de compra podem sofrer atrasos;
- entregas atualizam o estoque;
- eventos e decisões são registrados;
- diferentes cenários de demanda podem ser simulados;
- métricas da operação podem ser acompanhadas pelo dashboard.

O projeto foi desenvolvido principalmente como uma demonstração de arquitetura de agentes autônomos aplicada a operações de estoque.

---

## 🧠 Conceito

O fluxo principal do sistema pode ser resumido como:

    Dados históricos
          ↓
    Banco PostgreSQL
          ↓
    Análise da operação
          ↓
    Monitoramento do estoque
          ↓
    Agentes autônomos
          ↓
    Decisão de reposição
          ↓
    Compra automática
          ↓
    Fornecedor
          ↓
    Entrega
          ↓
    Atualização do estoque
          ↓
    Nova operação

A simulação permite observar esse ciclo continuamente.

---

## 🏗️ Arquitetura

A arquitetura do projeto é organizada em camadas.

    ┌──────────────────────────────┐
    │          Streamlit           │
    │         Dashboard            │
    └──────────────┬───────────────┘
                   │
                   ▼
    ┌──────────────────────────────┐
    │       Simulation Engine      │
    │     Motor da Simulação       │
    └──────────────┬───────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
    ┌─────────────┐   ┌───────────────┐
    │   Agents    │   │  Simulation   │
    │             │   │   Generators  │
    └──────┬──────┘   └───────┬───────┘
           │                  │
           └────────┬─────────┘
                    ▼
           ┌─────────────────┐
           │   PostgreSQL    │
           │    Database     │
           └─────────────────┘

---

# 🖥️ Interface

O sistema utiliza Streamlit como interface principal.

A aplicação possui diferentes páginas para visualizar os aspectos da operação.

## 📊 Dashboard

Página principal do sistema.

Apresenta uma visão geral da operação e serve como ponto de entrada para as demais funcionalidades.

---

## 📈 Analytics

Área destinada à análise geral da operação.

Inclui indicadores relacionados a:

- vendas;
- receita;
- estoque;
- produtos;
- estoque baixo;
- produtos sem estoque;
- evolução temporal das vendas;
- evolução temporal da receita.

A página permite observar tanto os dados históricos quanto os efeitos produzidos pela simulação.

---

## 📦 Inventory

Apresenta informações relacionadas ao estoque atual.

Entre os dados acompanhados estão:

- quantidade disponível;
- estoque mínimo;
- ponto de reposição;
- quantidade recomendada para reposição;
- produtos com estoque baixo;
- produtos sem estoque.

---

## 🛒 Sales

Página dedicada às vendas.

Permite acompanhar:

- vendas históricas;
- vendas simuladas;
- quantidade vendida;
- produtos vendidos;
- datas das vendas;
- valores das vendas.

---

## 🚚 Purchases

Apresenta as compras realizadas pelo sistema.

As compras podem ser geradas automaticamente pelo processo de reposição.

Informações acompanhadas incluem:

- produto;
- fornecedor;
- quantidade;
- custo;
- status;
- previsão de entrega;
- entrega realizada.

---

## 🤖 Agents

Página dedicada aos agentes responsáveis pela operação autônoma.

Os agentes possuem responsabilidades diferentes dentro do sistema.

---

## 🧠 AI Analyst

Área destinada à análise utilizando LLM.

A camada de IA pode receber informações estruturadas produzidas pelo sistema e gerar análises em linguagem natural.

A ideia é manter o processamento quantitativo no Python/SQL e utilizar o LLM principalmente para interpretação e comunicação dos resultados.

---

## 🎯 Decisions

Apresenta as decisões tomadas pelos agentes.

Exemplos:

- necessidade de reposição;
- produto com estoque crítico;
- quantidade recomendada;
- prioridade da decisão.

Cada decisão pode armazenar informações que explicam o motivo da ação.

---

## 📋 Tasks

Apresenta as tarefas criadas pelos agentes.

Um exemplo importante é:

    REPLENISHMENT

Essa tarefa representa a necessidade de reposição de determinado produto.

---

## 📡 Events

Registra eventos relevantes da operação.

Exemplos:

    SALE
    LOW_STOCK
    OUT_OF_STOCK
    PURCHASE_CREATED
    SUPPLIER_DELIVERY

Os eventos permitem acompanhar o histórico da operação e entender o que aconteceu durante a simulação.

---



---

## 🏪 Suppliers

Apresenta os fornecedores utilizados pela operação.

Os fornecedores possuem características como:

- tempo de entrega;
- confiabilidade;
- custo dos produtos.

Essas características influenciam a simulação de compras e entregas.

---


## 🧪 Simulation**

É uma das principais funcionalidades do projeto.

A página permite controlar a simulação diretamente pelo Streamlit.

### 🖥️ Desktop

No ambiente Desktop, a aplicação utiliza o motor de simulação em execução contínua.

Controles incluem:

- iniciar;

- pausar;

- reiniciar;

- alterar velocidade;

- selecionar cenário;

- controlar a quantidade de produtos processados por ciclo;

- limpar dados gerados pela simulação.

A simulação é executada pelo `SimulationWorker`, que mantém o `SimulationEngine` funcionando em segundo plano enquanto a interface acompanha seu estado.

O fluxo permite observar continuamente:

```
Vendas

  ↓

Estoque

  ↓

Monitoramento

  ↓

Reposição

  ↓

Compra

  ↓

Fornecedor

  ↓

Entrega

  ↓

Estoque
```

**---**

### ☁️ Streamlit Cloud — Demo Mode

No Streamlit Cloud, a aplicação utiliza um **Demo Mode**.

O ambiente Cloud não executa a simulação contínua com `SimulationWorker`. Em vez disso, utiliza um **Demo Dataset pré-gerado** para apresentar o comportamento completo do sistema de forma estável e reproduzível.

O Demo Dataset contém dados simulados previamente produzidos pelo motor de simulação, incluindo:

- vendas;

- movimentos de estoque;

- eventos;

- tarefas;

- decisões;

- compras;

- entregas;

- diferentes situações de demanda e fornecimento.

Dessa forma, o visitante pode navegar pelo dashboard e observar os resultados da operação simulada sem depender de uma simulação contínua sendo executada no Streamlit Cloud.

O Demo Mode permite demonstrar o fluxo completo do agente:

```
Dados históricos

      ↓

Simulação pré-gerada

      ↓

Vendas

      ↓

Estoque

      ↓

LOW\_STOCK

      ↓

Task REPLENISHMENT

      ↓

Decision

      ↓

Purchase

      ↓

Supplier

      ↓

Delivery
```

O Demo Dataset é armazenado no PostgreSQL utilizado pela aplicação Cloud e serve como estado inicial da demonstração.

Isso mantém a experiência do visitante consistente, mesmo quando diferentes pessoas acessam a aplicação.

**---**

### 🎯 Objetivo do Demo Mode

O Demo Mode existe principalmente para disponibilizar uma demonstração pública estável do projeto.

Enquanto o Desktop permite experimentar a simulação em tempo real, o Streamlit Cloud apresenta um estado pré-gerado que permite visualizar os resultados da operação sem exigir processamento contínuo.

Assim, os dois ambientes possuem objetivos diferentes:

```
Desktop

→ Simulação real e contínua

→ Controle da execução

→ Experimentação de cenários

→ Geração dinâmica de dados



Streamlit Cloud

→ Demo Mode

→ Dataset pré-gerado

→ Experiência estável

→ Visualização dos resultados da simulação


---

# 🤖 Agentes Autônomos

Os agentes estão localizados em:

    src/agents/

Cada agente possui uma responsabilidade específica.

---

## 👁️ Monitor Agent

Arquivo:

    src/agents/monitor.py

Responsável por monitorar o estoque.

O agente identifica produtos cujo estoque está abaixo ou no ponto de reposição.

Quando identifica uma necessidade, pode:

1. registrar um evento de estoque baixo;
2. criar uma tarefa de reposição;
3. evitar duplicação de tarefas quando já existe uma reposição pendente.

Fluxo:

    Estoque baixo
          ↓
    Monitor Agent
          ↓
    Evento LOW_STOCK
          ↓
    Task REPLENISHMENT

---

## 🔄 Replenishment Agent

Arquivo:

    src/agents/replenishment_agent.py

Analisa tarefas de reposição pendentes.

O agente verifica:

- estoque atual;
- ponto de reposição;
- quantidade recomendada;
- prioridade;
- existência de compras pendentes.

Se a reposição for necessária, registra uma decisão.

Exemplo conceitual:

    Estoque atual: 5
    Reorder Point: 20
    Reorder Quantity: 50

    ↓

    REPLENISH

    "Estoque abaixo do ponto de reposição.
     Recomendada reposição de 50 unidades."

---

## 📊 Sales Analyst

Arquivo:

    src/agents/sales_analyst.py

Responsável por análises relacionadas às vendas.

Pode ser utilizado para produzir informações como:

- produtos mais vendidos;
- desempenho de vendas;
- comportamento histórico;
- indicadores para apoiar decisões.

---

## 📈 Demand Agent

Arquivo:

    src/agents/demand_agent.py

Responsável por analisar informações relacionadas à demanda.

O objetivo é fornecer uma visão sobre o comportamento esperado das vendas e apoiar decisões de estoque.

---

## ⚙️ Executor

Arquivo:

    src/agents/executor.py

Responsável pela execução das ações decididas pelos agentes.

Ele representa a camada responsável por transformar decisões em ações operacionais.

---

## 🎛️ Agent Orchestrator

Arquivo:

    src/agents/agent_orchestrator.py

Responsável por organizar o fluxo entre os diferentes agentes.

Conceitualmente:

    Monitor
       ↓
    Task
       ↓
    Replenishment
       ↓
    Decision
       ↓
    Executor
       ↓
    Operation

---

# 🔄 Motor de Simulação

Arquivo:

    src/simulation/simulation_engine.py

O Simulation Engine coordena o ciclo da simulação.

Um ciclo pode executar:

    1. Seleção do cenário
    2. Geração de vendas
    3. Processamento de entregas
    4. Monitoramento do estoque
    5. Análise das tarefas de reposição
    6. Criação de compras
    7. Avanço do tempo simulado

O motor utiliza:

    SalesGenerator
    PurchaseGenerator
    SupplierSimulator
    MonitorAgent
    ReplenishmentAgent
    SimulationState

---

# 🛒 Sales Generator

Arquivo:

    src/simulation/sales_generator.py

Responsável por gerar vendas durante a simulação.

Os produtos são selecionados com base no comportamento histórico de vendas.

O gerador utiliza os dados históricos para determinar o peso de cada produto.

Assim, produtos que possuem maior participação nas vendas históricas possuem maior probabilidade de aparecer na simulação.

Exemplo:

    Produto A → maior histórico de vendas
    Produto B → médio histórico
    Produto C → menor histórico

A probabilidade de seleção acompanha esses pesos.

Quando uma venda é gerada:

    Estoque
       ↓
    -1 unidade
       ↓
    Registro de movimento
       ↓
    Registro da venda
       ↓
    Registro do evento

As vendas geradas pela simulação são identificadas como simuladas.

---

# 📦 Purchase Generator

Arquivo:

    src/simulation/purchase_generator.py

Responsável por criar pedidos de compra.

O gerador seleciona um fornecedor adequado e calcula a previsão de entrega.

Critérios considerados incluem:

- confiabilidade;
- tempo de entrega;
- custo do produto.

Fluxo:

    Decision
       ↓
    PurchaseGenerator
       ↓
    Supplier
       ↓
    Purchase ORDERED
       ↓
    Expected Delivery

---

# 🚚 Supplier Simulator

Arquivo:

    src/simulation/supplier_simulator.py

Simula o comportamento dos fornecedores.

Quando o tempo simulado chega à data prevista:

    Purchase ORDERED
          ↓
    Supplier Simulator
          ↓
    DELIVERY
          ↓
    Estoque +
          ↓
    Purchase DELIVERED

O simulador também suporta atrasos de fornecedores através dos cenários da simulação.

---

# ⏱️ Simulation State

Arquivo:

    src/simulation/simulation_state.py

Mantém o estado atual da simulação.

Entre as informações controladas estão:

- execução;
- velocidade;
- cenário;
- tempo simulado;
- eventos processados;
- vendas processadas;
- compras processadas;
- entregas processadas;
- produtos processados por ciclo.

O tempo da simulação é independente do relógio real.

Isso permite acelerar a operação.

Por exemplo:

    1x
    2x
    5x
    10x

A velocidade representa quanto tempo simulado avança a cada ciclo.

---

# 🎯 Cenários

Arquivo:

    src/simulation/scenarios.py

O sistema possui cenários que alteram o comportamento da simulação.

Os cenários podem representar situações como:

    Normal
    Alta demanda
    Baixa demanda
    Demand Shock
    Supplier Delay
    Ruptura de estoque

Cada cenário pode modificar parâmetros como:

- intensidade das vendas;
- atraso dos fornecedores;
- comportamento da demanda.

Isso permite testar como o sistema reage a diferentes condições operacionais.

---

# 🗄️ Banco de Dados

O projeto utiliza PostgreSQL como banco operacional.

A estrutura SQL está localizada em:

    sql/

Arquivos principais:

    schema.sql
    operational_schema.sql
    schema_raw.sql
    views.sql

---

# 🧱 Estrutura do Banco

O banco contém entidades relacionadas à operação de estoque.

Entre elas:

    products
    inventory
    suppliers
    sales
    purchases
    inventory_movements
    events
    tasks
    decisions

O banco separa os dados históricos da operação simulada através de registros identificados como simulados quando aplicável.

---

# 👁️ Views

Arquivo:

    sql/views.sql

As views facilitam consultas analíticas e operacionais.

Entre os conceitos utilizados estão:

    sales_ranking
    inventory_health

Essas views permitem obter informações agregadas sem precisar repetir toda a lógica SQL nas páginas do dashboard.

---

# 📊 Camada de Analytics

Localização:

    src/analytics/

Arquivos:

    demand_analysis.py
    forecasting.py
    inventory_analysis.py
    sales_ranking.py

Essa camada concentra análises utilizadas pelo dashboard e pelos agentes.

---

## 📈 Sales Ranking

Arquivo:

    src/analytics/sales_ranking.py

Responsável por análises relacionadas ao ranking de vendas.

Pode ser utilizado para identificar produtos com maior desempenho.

---

## 📦 Inventory Analysis

Arquivo:

    src/analytics/inventory_analysis.py

Responsável pela análise da situação do estoque.

---

## 📊 Demand Analysis

Arquivo:

    src/analytics/demand_analysis.py

Responsável por análises relacionadas à demanda.

---


---

# 🧠 LLM

Localização:

    src/llm/

Arquivos:

    groq_client.py
    prompts.py

O projeto utiliza um LLM como camada de análise e interpretação.

A arquitetura evita enviar toda a base de dados diretamente ao modelo.

Em vez disso:

    PostgreSQL
          ↓
    Python / SQL
          ↓
    Métricas estruturadas
          ↓
    LLM
          ↓
    Análise em linguagem natural

Essa abordagem reduz o volume de informações enviado ao modelo e mantém os cálculos quantitativos sob controle do sistema.

---

# 🛢️ Dados

Os dados históricos utilizados no projeto são provenientes do dataset Brazilian E-Commerce Public Dataset by Olist.

Os arquivos estão em:

    data/raw/

Incluem:

    olist_customers_dataset.csv
    
    olist_orders_dataset.csv
    olist_order_items_dataset.csv
    olist_order_payments_dataset.csv
    olist_order_reviews_dataset.csv
    olist_products_dataset.csv
    olist_sellers_dataset.csv
    product_category_name_translation.csv

Os dados históricos são utilizados como base para construir a operação e orientar a geração das vendas simuladas.

---

# 🔁 Dados históricos x dados simulados

Uma característica importante do projeto é a separação entre os dados históricos e os dados produzidos pela simulação.

Os registros simulados possuem identificação própria.

Isso permite:

    Dados históricos
          +
    Dados simulados

sem perder a capacidade de distinguir os dois conjuntos.

Essa separação é importante para que análises históricas não sejam contaminadas pelos resultados produzidos durante uma demonstração da simulação.

---

# 🧹 Limpeza da simulação

O projeto possui mecanismo para limpar os dados produzidos pela simulação.

A limpeza remove os dados operacionais gerados durante a demonstração e restaura o estado operacional baseado nos dados originais.

Isso é especialmente importante porque a simulação pode gerar continuamente:

- vendas;
- compras;
- entregas;
- eventos;
- decisões;
- tarefas;
- movimentos de estoque.

A funcionalidade de limpeza permite executar novamente a demonstração sem acumular indefinidamente dados simulados.

---

# 📊 Analytics e período histórico

Os dados históricos possuem um período próprio.

A simulação possui um tempo simulado separado.

Portanto, os gráficos podem apresentar:

    Histórico
    2016 ─────────────── 2018

    Simulação
                         2026 ───────────────>

O dashboard pode tratar essa diferença de forma visual sem alterar os dados originais.

---

# 🗂️ Estrutura do projeto

    .
    ├── .env
    ├── .gitattributes
    ├── .gitignore
    ├── projeto.txt
    ├── README.md
    ├── requirements.txt
    ├── run_simulation.py
    ├── setup_project.py
    ├── streamlit_app.py
    ├── test_database.py
    │
    ├── dashboard/
    │   ├── Agents.py
    │   ├── AI_Analyst.py
    │   ├── Analytics.py
    │   ├── Decisions.py
    │   ├── Events.py
    │   ├── Forecast.py
    │   ├── Home.py
    │   ├── Inventory.py
    │   ├── OriginalData.py
    │   ├── Products.py
    │   ├── Purchases.py
    │   ├── Reports.py
    │   ├── Sales.py
    │   ├── Simulation.py
    │   ├── Suppliers.py
    │   ├── Tasks.py
    │   └── __init__.py
    │
    ├── data/
    │   └── raw/
    │       ├── olist_customers_dataset.csv
    │       ├── 
    │       ├── olist_orders_dataset.csv
    │       ├── olist_order_items_dataset.csv
    │       ├── olist_order_payments_dataset.csv
    │       ├── olist_order_reviews_dataset.csv
    │       ├── olist_products_dataset.csv
    │       ├── olist_sellers_dataset.csv
    │       └── product_category_name_translation.csv
    │
    ├── sql/
    │   ├── operational_schema.sql
    │   ├── schema.sql
    │   ├── schema_raw.sql
    │   └── views.sql
    │
    └── src/
        ├── agents/
        │   ├── agent_orchestrator.py
        │   ├── demand_agent.py
        │   ├── executor.py
        │   ├── monitor.py
        │   ├── replenishment_agent.py
        │   ├── sales_analyst.py
        │   └── __init__.py
        │
        ├── analytics/
        │   ├── demand_analysis.py
        │   ├── forecasting.py
        │   ├── inventory_analysis.py
        │   ├── sales_ranking.py
        │   └── __init__.py
        │
        ├── database/
        │   ├── check_database.py
        │   ├── check_operational_database.py
        │   ├── connection.py
        │   ├── initialize_operational_data.py
        │   ├── initialize_operational_database.py
        │   ├── init_database.py
        │   ├── load_olist.py
        │   ├── load_olist_data.py
        │   ├── models.py
        │   ├── repositories.py
        │   ├── seed_operational_data.py
        │   ├── setup_database.py
        │   └── __init__.py
        │
        ├── llm/
        │   ├── groq_client.py
        │   ├── prompts.py
        │   └── __init__.py
        │
        └── simulation/
            ├── purchase_generator.py
            ├── sales_generator.py
            ├── scenarios.py
            ├── simulation_engine.py
            ├── simulation_state.py
            ├── supplier_simulator.py
            └── __init__.py

---

# ⚙️ Tecnologias

## Linguagem

    Python

## Interface

    Streamlit

## Banco de dados

    PostgreSQL

## ORM / conexão

    SQLAlchemy

## Manipulação de dados

    pandas

## Inteligência Artificial

    Groq / LLM

## SQL

    PostgreSQL SQL

---

# 📦 Dependências

As dependências estão definidas em:

    requirements.txt

Entre as principais tecnologias utilizadas estão:

    streamlit
    pandas
    sqlalchemy
    psycopg2
    groq
    python-dotenv

As versões efetivamente utilizadas devem seguir o arquivo requirements.txt do projeto.

---

# 🔐 Variáveis de ambiente

O projeto utiliza arquivo:

    .env

para armazenar configurações sensíveis.

Exemplo conceitual:

    DATABASE_URL=...
    GROQ_API_KEY=...

O arquivo .env não deve ser versionado no Git.

---

# 🚀 Instalação

## 1. Clonar o projeto

    git clone <URL_DO_REPOSITORIO>

    cd autonomous-inventory-agent

---

## 2. Criar ambiente virtual

    python -m venv .venv

---

## 3. Ativar o ambiente

Windows:

    .venv\Scripts\activate

Linux/macOS:

    source .venv/bin/activate

---

## 4. Instalar dependências

    pip install -r requirements.txt

---

# 🗄️ Configuração do PostgreSQL

Crie um banco PostgreSQL para o projeto.

Depois configure a conexão através do arquivo:

    .env

A conexão utilizada pela aplicação está centralizada em:

    src/database/connection.py

---

# 🏗️ Inicialização do banco

O projeto possui scripts de inicialização dentro de:

    src/database/

Entre eles:

    setup_database.py
    init_database.py
    initialize_operational_database.py
    initialize_operational_data.py
    load_olist.py
    load_olist_data.py

A ordem exata de inicialização depende da configuração utilizada no ambiente.

O objetivo desses scripts é:

    Criar estrutura
          ↓
    Criar tabelas
          ↓
    Carregar dados
          ↓
    Preparar operação
          ↓
    Executar dashboard

---

# ▶️ Executando o Streamlit

A aplicação principal é:

    streamlit_app.py

Execute:

    streamlit run streamlit_app.py

Depois abra a URL fornecida pelo Streamlit no navegador.

---

# ▶️ Executando a simulação

Também existe:

    run_simulation.py

O projeto também permite controlar a simulação diretamente através da página:

    Simulation

dentro do Streamlit.

Isso permite executar a demonstração sem depender exclusivamente do terminal.

---

# 🎮 Como utilizar a simulação

Depois de iniciar o Streamlit:

    1. Abra a página Simulation.
    2. Escolha um cenário.
    3. Defina a velocidade.
    4. Defina a quantidade de produtos processados por ciclo.
    5. Clique em Iniciar.
    6. Observe as vendas.
    7. Observe a redução do estoque.
    8. Aguarde o Monitor Agent identificar estoque baixo.
    9. Observe a criação da tarefa.
    10. Observe a decisão de reposição.
    11. Observe a criação da compra.
    12. Aguarde a entrega.
    13. Observe o estoque sendo atualizado.

---

# 🔄 Exemplo de ciclo completo

Imagine:

    Produto X
    Estoque: 10
    Reorder Point: 20
    Reorder Quantity: 50

O sistema detecta:

    10 <= 20

O Monitor Agent cria:

    Task
    REPLENISHMENT

O Replenishment Agent analisa:

    Estoque abaixo do ponto de reposição.

E registra:

    Decision
    REPLENISH

O Purchase Generator cria:

    Purchase
    ORDERED
    Quantity: 50

O fornecedor possui:

    Lead Time: X dias

O Supplier Simulator aguarda o tempo simulado.

Quando chega a data:

    Purchase
    DELIVERED

E o estoque recebe:

    +50 unidades

---

# 🧪 Cenários de demonstração

## Normal

Representa uma operação normal.

Útil para observar o comportamento padrão do sistema.

---

## Alta demanda

Aumenta a pressão sobre o estoque.

É útil para observar:

- aumento das vendas;
- redução mais rápida do estoque;
- maior quantidade de reposições.

---

## Baixa demanda

Reduz a pressão sobre o estoque.

Permite observar uma operação com menor volume de vendas.

---

## Demand Shock

Representa uma alteração mais forte e repentina na demanda.

É útil para testar a capacidade do sistema de reagir rapidamente.

---

## Supplier Delay

Introduz atrasos no processo de fornecimento.

Permite observar o impacto de fornecedores atrasados sobre o estoque.

---

## Ruptura de estoque

Representa uma situação na qual produtos podem chegar a estoque zero.

Isso permite observar eventos como:

    OUT_OF_STOCK

e a reação dos agentes.

---

# 📋 Rastreamento da operação

O projeto mantém diferentes registros para permitir rastreabilidade.

## Events

Representam acontecimentos.

Exemplo:

    SALE
    LOW_STOCK
    OUT_OF_STOCK
    PURCHASE_CREATED
    SUPPLIER_DELIVERY

## Tasks

Representam tarefas que precisam ser executadas.

Exemplo:

    REPLENISHMENT

## Decisions

Representam decisões tomadas pelos agentes.

Exemplo:

    REPLENISH

## Inventory Movements

Representam alterações no estoque.

Exemplo:

    SALE
    PURCHASE

Essa separação permite reconstruir o fluxo de uma operação.

---

# 🧩 Repository Layer

Arquivo principal:

    src/database/repositories.py

A camada de repositories centraliza operações de persistência utilizadas pelos diferentes componentes.

Entre os conceitos utilizados estão:

    register_event()
    register_decision()
    create_task()
    update_inventory()
    register_movement()
    clear_simulation_data()
    create_simulation_snapshot()

Isso evita espalhar toda a lógica de persistência diretamente pelas páginas do Streamlit ou pelos agentes.

---

# 🧪 Testes

O projeto possui:

    test_database.py

Esse arquivo pode ser utilizado para verificar a comunicação e o estado básico do banco de dados.

---

# 🛠️ Scripts auxiliares

## setup_project.py

Auxilia na preparação inicial do projeto.

## test_database.py

Utilizado para testes da conexão/estrutura do banco.

## run_simulation.py

Permite executar o motor de simulação fora da interface.

---

# 📌 Princípios do projeto

O projeto foi estruturado seguindo alguns princípios.

## Separação de responsabilidades

A interface não é responsável por realizar diretamente toda a lógica da operação.

A lógica está separada em:

    Dashboard
    Agents
    Analytics
    Database
    Simulation
    LLM

---

## SQL para operações estruturadas

O banco PostgreSQL é utilizado para armazenar e consultar os dados operacionais.

---

## Python para lógica

Python coordena:

- agentes;
- simulação;
- geração de vendas;
- geração de compras;
- análise;
- integração com LLM.

---

## LLM como camada de interpretação

O LLM não precisa receber toda a base de dados.

O sistema pode calcular os indicadores primeiro e enviar somente informações estruturadas para análise.

---

# 📈 O que o projeto demonstra

Este projeto demonstra conhecimentos em:

- Python;
- SQL;
- PostgreSQL;
- SQLAlchemy;
- pandas;
- Streamlit;
- arquitetura de software;
- sistemas de agentes;
- automação de processos;
- análise de dados;
- análise de demanda;
- forecasting;
- gerenciamento de estoque;
- simulação;
- integração com LLM;
- engenharia de dados;
- dashboards analíticos.

---

# 💼 Aplicação prática

Embora a simulação seja voltada para demonstração, a arquitetura representa problemas encontrados em operações reais.

Um sistema semelhante poderia ser utilizado para apoiar:

- varejo;
- e-commerce;
- distribuição;
- planejamento de estoque;
- compras;
- supply chain;
- monitoramento operacional.

A diferença principal é que, em um ambiente real, as fontes de vendas, estoque e fornecedores seriam conectadas aos sistemas operacionais da empresa.

---

# 🔬 Natureza do projeto

O Autonomous Inventory Agent é um projeto de portfólio e demonstração técnica.

Os dados históricos são utilizados como base para construir o cenário inicial.

As vendas, compras, eventos e entregas produzidos durante a execução da simulação são gerados pelo próprio sistema.

A simulação não representa transações reais.

---

# 👨‍💻 Autor

## Luis Henrique Turra Ramos

Cientista de Dados / Data Science

Interesses principais:

- Ciência de Dados
- Python
- SQL
- Machine Learning
- Analytics
- Inteligência Artificial
- Sistemas Autônomos

---

# 📄 Licença

Defina aqui a licença desejada para o projeto.

Exemplo:

    MIT License

---

# ⭐ Projeto

Autonomous Inventory Agent

Um sistema de estoque orientado por dados que combina:

    📊 Analytics
    🤖 Agentes Autônomos
    🗄️ PostgreSQL
    🔄 Simulação
    🛒 Vendas
    📦 Estoque
    🚚 Fornecedores
    🧠 LLM
    📈 Streamlit

O objetivo é transformar dados históricos em uma operação simulada capaz de monitorar, analisar, decidir e executar ações de forma autônoma.

## 🛠️ Technologies

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-336791?logo=postgresql&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)