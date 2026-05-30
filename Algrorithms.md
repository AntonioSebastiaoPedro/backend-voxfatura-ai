Viewed README.md:139-171
Viewed README_ML.md:1-201
Listed directory ai
Viewed voice_nlp.py:1-183
Viewed predictor.py:1-474

Aqui está a lista completa de todos os algoritmos, abordagens estatísticas e técnicas de Inteligência Artificial implementadas no backend do **VoxFatura AI** (`back/app/ai/`), organizados pelo tipo de problema, tipo de aprendizado e local exato de aplicação na aplicação:

---

### 1. Regressão (Estimativa de Valores Numéricos Contínuos)

#### **A. Random Forest Regressor** (`sklearn.ensemble.RandomForestRegressor`)
* **Tipo de Aprendizado:** Supervisionado (*Supervised Learning*).
* **Tipo de Algoritmo:** Conjunto de Árvores de Decisão (*Ensemble Method*).
* **Onde é usado:** No arquivo [`predictor.py:L9-L149`](file:///home/ansebast/Documents/voxfatura_ai/back/app/ai/predictor.py#L9-L149), especificamente na função `train_and_predict_demand`.
* **Como é aplicado:** É treinado dinamicamente na memória (*Just-in-Time*) para cada produto individual no PostgreSQL. Mapeia a sazonalidade e tendências cruzando 5 variáveis de entrada (*features*): dia da semana (`dia_semana`), dia do mês (`dia_mes`), mês do ano (`mes`), preço médio praticado (`preco`) e stock atual do produto (`stock_atual`) para projetar a quantidade diária de escoamento no período de 30 dias seguintes.

#### **B. Média Móvel Inteligente Ponderada (Weighted Moving Average - WMA)**
* **Tipo de Aprendizado:** Estatístico / Supervisionado com base em histórico temporal.
* **Tipo de Algoritmo:** Média Móvel Ponderada (*Weighted Moving Average*).
* **Onde é usado:** No arquivo [`predictor.py:L70-L85`](file:///home/ansebast/Documents/voxfatura_ai/back/app/ai/predictor.py#L70-L85), integrado na função `train_and_predict_demand`.
* **Como é aplicado:** Computa a velocidade média diária de vendas ponderando com maior relevância a atividade recente de curtíssimo prazo: aplica **70% de peso** à média de vendas dos últimos 7 dias de calendário e **30% de peso** aos últimos 30 dias de calendário. É fundido com as previsões do Random Forest num modelo híbrido para estimar os dias exatos restantes até à rotura física de stock de cada item.

#### **C. Regressão Linear** (`sklearn.linear_model.LinearRegression`)
* **Tipo de Aprendizado:** Supervisionado (*Supervised Learning*).
* **Tipo de Algoritmo:** Modelo de Regressão Linear Simples.
* **Onde é usado:** No arquivo [`predictor.py:L228-L246`](file:///home/ansebast/Documents/voxfatura_ai/back/app/ai/predictor.py#L228-L246) e [`L413-L430`](file:///home/ansebast/Documents/voxfatura_ai/back/app/ai/predictor.py#L413-L430), nas funções `get_business_insights` e `get_complete_ai_dashboard`.
* **Como é aplicado:** Consolida o faturamento total mensal da empresa armazenado no PostgreSQL e cria um índice temporal consecutivo dos meses. O modelo traça a reta de tendência matemática e projeta a estimativa provável de faturamento global do negócio para os próximos 4 meses subsequentes exibidos no Dashboard corporativo.

---

### 2. Deteção de Anomalias (Identificação de Outliers e Auditoria)

#### **A. Isolation Forest** (`sklearn.ensemble.IsolationForest`)
* **Tipo de Aprendizado:** Não Supervisionado (*Unsupervised Learning*).
* **Tipo de Algoritmo:** Algoritmo de Isolamento Baseado em Particionamento de Árvores de Decisão (*Anomaly Detection*).
* **Onde é usado:** No arquivo [`predictor.py:L150-L182`](file:///home/ansebast/Documents/voxfatura_ai/back/app/ai/predictor.py#L150-L182), na função `detect_invoice_anomaly`.
* **Como é aplicado:** Utilizado em tempo real para auditoria de faturamento no endpoint `/api/ai/check-anomaly`. Ele avalia a distribuição de subtotais de todas as faturas confirmadas no banco de dados e tenta isolar a transação atual. Transações com valores suspeitos ou discrepantes em relação à rotina do sistema exigem poucos cortes na árvore de decisão para serem isoladas, sendo então classificadas como anomalias usando uma taxa de contaminação de **5%**.

#### **B. Limiar de Confiança Estatística baseada em Desvio Padrão**
* **Tipo de Aprendizado:** Estatístico / Não Supervisionado.
* **Tipo de Algoritmo:** Análise Multivariada de Desvio Padrão (*Outlier Filtering*).
* **Onde é usado:** No arquivo [`predictor.py:L186-L205`](file:///home/ansebast/Documents/voxfatura_ai/back/app/ai/predictor.py#L186-L205), integrado na função `detect_invoice_anomaly`.
* **Como é aplicado:** Complementa o Isolation Forest analisando o perfil específico do cliente. Calcula a média histórica e desvio padrão das faturas passadas do cliente em questão. O sistema delimita a barreira de confiança saudável por:
  $$\text{Limite Superior} = \text{Média Histórica} + (2 \times \text{Desvio Padrão})$$
  Se o subtotal da nova fatura exceder este limite superior, for $3\times$ superior ao consumo habitual do cliente, ou $3.5\times$ superior à média geral (em caso de novo cliente), a transação é sinalizada no Dashboard de auditoria com o motivo explícito.

---

### 3. Processamento de Linguagem Natural (NLP e Mapeamento Semântico)

#### **A. Normalização Léxica e Correspondência Semântica por Word-Overlap (Abordagem de Jaccard)**
* **Tipo de Aprendizado:** Baseado em Regras e Análise Semântica (*Rule-based NLP / Vector Overlap*).
* **Tipo de Algoritmo:** Tokenização lexical com pontuação de intersecção de conjuntos de palavras (*Jaccard-like Word-Overlap Scoring*).
* **Onde é usado:** No arquivo [`voice_nlp.py`](file:///home/ansebast/Documents/voxfatura_ai/back/app/ai/voice_nlp.py#L1-L183) de forma integral, no endpoint `/api/ai/voice-command`.
* **Como é aplicado:** 
  1. **Normalização:** Remove toda a acentuação gráfica típica da fala ou escrita em português angolano (Ex: "óleo" torna-se "oleo"), reduz para minúsculas e remove caracteres especiais através de Regex para homogeneização textual.
  2. **Identificação de Intenções:** Analisa a presença de termos gatilho (como "confirmar", "emitir", "limpar").
  3. **Reconhecimento de Entidades (Clientes e Produtos):** Extrai a quantidade associada com expressões regulares. Em seguida, obtém a lista de nomes da base de dados e calcula a intersecção de palavras do comando vocalizado contra o catálogo. A entidade que obtém o maior overlap semântico é selecionada de forma automática (permitindo que o operador fale livremente expressões como "adiciona 5 arroz branco de luanda" e o sistema localize o produto correto "Arroz Branco 25kg" e a quantidade "5").

---

### 4. Classificação de Risco (Risco de Inadimplência e Churn)

#### **A. Modelo de Score de Confiança e Probabilidade de Churn**
* **Tipo de Aprendizado:** Supervisionado baseado em Regras Heurísticas e Regressão de Períodos.
* **Tipo de Problema:** Classificação de Risco.
* **Onde é usado:** No arquivo [`predictor.py:L248-L261`](file:///home/ansebast/Documents/voxfatura_ai/back/app/ai/predictor.py#L248-L261) e [`L298-L324`](file:///home/ansebast/Documents/voxfatura_ai/back/app/ai/predictor.py#L298-L324), nas funções `get_business_insights` e `get_complete_ai_dashboard`.
* **Como é aplicado:** Calcula a probabilidade de perda de cliente (*churn*) ou risco financeiro associado de 10 a 100. Analisa de forma contínua o rácio de dívida ativa contra o limite de crédito contratado, e deduz pontos com base no número de dias de inatividade operacional desde a última fatura registada no PostgreSQL.