import numpy as np
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from app import models

def train_and_predict_demand(db: Session, product_id: str) -> dict:
    """
    Treina dinamicamente modelos locais de previsão de demanda para estimar o consumo
    diário médio, previsão para 30 dias e data de esgotamento do stock de um determinado produto.
    Utiliza uma abordagem híbrida:
    - Média Móvel Inteligente (WMA) ponderada (70% peso nos últimos 7 dias, 30% nos últimos 30 dias).
    - Random Forest Regressor treinado com features avançadas (dia da semana, dia do mês, mês, preço, stock).
    - Correção estatística de lacunas temporais (reindexação contínua de calendário com preenchimento a zero).
    """
    # Buscar produto e histórico de vendas
    produto = db.query(models.Produto).filter(models.Produto.id == product_id).first()
    if not produto:
        return {"error": "Produto não encontrado"}

    itens = db.query(models.FaturaItem).join(models.Fatura).filter(
        models.FaturaItem.produto_id == product_id,
        models.Fatura.status == "CONFIRMADA"
    ).all()

    if len(itens) < 3:
        # Sem dados históricos suficientes para ML avançado, usar estimativa estatística simples
        return {
            "produto_nome": produto.nome,
            "stock_atual": produto.stock,
            "consumo_diario_medio": 0.5,
            "previsao_demanda_30d": 15.0, # Estimativa padrão
            "dias_ate_esgotar": round(produto.stock / 0.5) if produto.stock > 0 else 0,
            "confianca_modelo": "Baixa (Dados Insuficientes)",
            "recomendacao": "Aguarde mais vendas para calibração do modelo de IA."
        }

    # 1. Converter vendas em série temporal e agrupar por data (incluindo preço unitário)
    data_list = []
    for item in itens:
        dt_str = item.fatura.data.split("T")[0]
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        data_list.append({"data": dt, "quantidade": item.quantidade, "preco": item.preco_unitario})
    
    df = pd.DataFrame(data_list)
    df = df.groupby("data").agg({"quantidade": "sum", "preco": "mean"}).reset_index()
    df = df.sort_values("data")

    # 2. Correção Estatística de Lacunas (Time-Series Reindexing)
    # Garante que dias sem venda sejam considerados como consumo 0, evitando inflacionar a média diária
    first_date = df["data"].min()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    last_date = max(df["data"].max(), today)
    
    # Criar intervalo contínuo de calendário
    all_dates = pd.date_range(start=first_date, end=last_date, freq="D")
    df_full = pd.DataFrame({"data": all_dates})
    
    # Mesclar com os dados reais de venda
    df_full = df_full.merge(df, on="data", how="left")
    df_full["quantidade"] = df_full["quantidade"].fillna(0.0)
    # Preencher lacunas de preço com o último conhecido, ou o preço de cadastro do produto
    df_full["preco"] = df_full["preco"].ffill().bfill().fillna(produto.preco_unitario)
    df_full["stock_atual"] = produto.stock

    total_days = len(df_full)

    # 3. Opção 3 — Média Móvel Inteligente (Weighted Moving Average)
    # Calcula consumo focado no curto prazo (7 dias) com suporte histórico (30 dias)
    df_full = df_full.sort_values("data").reset_index(drop=True)
    
    mean_7 = float(df_full.tail(7)["quantidade"].mean())
    mean_30 = float(df_full.tail(30)["quantidade"].mean())
    
    if total_days < 7:
        consumo_wma = float(df_full["quantidade"].mean())
    elif total_days < 30:
        consumo_wma = 0.7 * mean_7 + 0.3 * float(df_full["quantidade"].mean())
    else:
        consumo_wma = 0.7 * mean_7 + 0.3 * mean_30
        
    consumo_wma = max(0.01, consumo_wma) # Evitar taxa nula absoluta

    # 4. Opções 1 e 2 — Random Forest Regressor com Engenharia de Features
    # Engenharia de atributos temporais e mercadológicos locais
    df_full["dia_semana"] = df_full["data"].dt.dayofweek
    df_full["dia_mes"] = df_full["data"].dt.day
    df_full["mes"] = df_full["data"].dt.month
    
    features = ["dia_semana", "dia_mes", "mes", "preco", "stock_atual"]
    X = df_full[features].values
    y = df_full["quantidade"].values

    # Treinar Random Forest Regressor local super leve (50 estimadores)
    rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
    rf_model.fit(X, y)

    # Gerar predição roll-forward passo-a-passo para os próximos 30 dias
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30, freq="D")
    df_future = pd.DataFrame({"data": future_dates})
    df_future["dia_semana"] = df_future["data"].dt.dayofweek
    df_future["dia_mes"] = df_future["data"].dt.day
    df_future["mes"] = df_future["data"].dt.month
    df_future["preco"] = produto.preco_unitario
    df_future["stock_atual"] = produto.stock
    
    X_future = df_future[features].values
    y_pred_rf = rf_model.predict(X_future)
    y_pred_rf = np.clip(y_pred_rf, 0, None)
    previsao_rf_30d = float(np.sum(y_pred_rf))

    # 5. Combinação Híbrida Inteligente
    previsao_wma_30d = consumo_wma * 30

    if total_days < 15:
        # Menos de 15 dias de histórico: focar 100% na Média Móvel Inteligente para estabilidade absoluta
        previsao_demanda_30d = previsao_wma_30d
        consumo_diario_estimado = consumo_wma
        confianca_modelo = "Média (Média Móvel Inteligente)"
    else:
        # Histórico robusto: mesclar os modelos para capturar sazonalidade (Random Forest) e consistência (WMA)
        previsao_demanda_30d = 0.5 * previsao_wma_30d + 0.5 * previsao_rf_30d
        consumo_diario_estimado = previsao_demanda_30d / 30.0
        confianca_modelo = "Alta (WMA + Random Forest)"

    dias_ate_esgotar = round(produto.stock / consumo_diario_estimado) if produto.stock > 0 else 0
    
    # Calcular recomendação analítica
    if dias_ate_esgotar == 0:
        recomendacao = "⚠️ Crítico: Sem stock! Efetuar encomenda urgente ao fornecedor."
    elif dias_ate_esgotar < 7:
        recomendacao = "🔴 Urgente: Stock a esgotar rapidamente. Recomenda-se repor stock nos próximos 2 dias."
    elif dias_ate_esgotar < 20:
        recomendacao = "🟡 Atenção: Stock moderado. Programar nova compra de reposição."
    else:
        recomendacao = "🟢 Seguro: Nível de stock saudável para a demanda prevista."

    return {
        "produto_nome": produto.nome,
        "stock_atual": produto.stock,
        "consumo_diario_medio": round(consumo_diario_estimado, 2),
        "previsao_demanda_30d": round(previsao_demanda_30d, 1),
        "dias_ate_esgotar": dias_ate_esgotar,
        "confianca_modelo": confianca_modelo,
        "recomendacao": recomendacao
    }

def detect_invoice_anomaly(db: Session, subtotal: float, cliente_id: str) -> dict:
    """
    Treina um modelo local de Isolation Forest/Estatístico para detetar anomalias nas faturas.
    Aprende os padrões normais de faturação do cliente e deteta desvios suspeitos.
    """
    faturas = db.query(models.Fatura).filter(
        models.Fatura.status == "CONFIRMADA"
    ).all()

    if len(faturas) < 5:
        return {
            "is_anomala": False,
            "score_anomalia": 0.0,
            "motivo": "Histórico insuficiente de faturas no sistema para calibrar o modelo de anomalias."
        }

    # Coletar subtotais de todas as faturas para treinar o Isolation Forest local
    subtotais = np.array([f.subtotal for f in faturas]).reshape(-1, 1)
    
    # Treinar Isolation Forest local dinâmico
    clf = IsolationForest(contamination=0.05, random_state=42)
    clf.fit(subtotais)
    
    # Prever anomalia para a fatura atual
    prediction = clf.predict([[subtotal]])[0] # -1 para anomalia, 1 para normal
    
    # Detalhar desvio estatístico do cliente
    faturas_cliente = db.query(models.Fatura).filter(
        models.Fatura.cliente_id == cliente_id,
        models.Fatura.status == "CONFIRMADA"
    ).all()
    
    is_anomala = bool(prediction == -1)
    score = 0.0
    motivo = "Os valores desta fatura estão alinhados com o padrão do sistema."

    if len(faturas_cliente) > 0:
        media_cliente = np.mean([f.subtotal for f in faturas_cliente])
        desvio_padrao = np.std([f.subtotal for f in faturas_cliente]) or 1.0
        limite_superior = media_cliente + 2 * desvio_padrao
        
        score = min(99.0, max(5.0, ((subtotal - media_cliente) / desvio_padrao) * 20))
        if subtotal > limite_superior:
            is_anomala = True
            motivo = f"Fatura {round(subtotal / media_cliente, 1)}x superior à média habitual deste cliente (Média: {round(media_cliente)} Kz)."
        elif subtotal > media_cliente * 3:
            is_anomala = True
            motivo = f"A fatura excede consideravelmente o histórico de consumo normal do cliente (Fatura: {subtotal} Kz vs Média: {round(media_cliente)} Kz)."
    else:
        # Se for cliente novo, comparar com a média geral do sistema
        media_geral = np.mean([f.subtotal for f in faturas])
        score = 50.0 if subtotal > media_geral * 2 else 10.0
        if subtotal > media_geral * 3.5:
            is_anomala = True
            motivo = f"Valor invulgarmente elevado em relação à média de transações de todo o sistema (Média: {round(media_geral)} Kz)."

    return {
        "is_anomala": is_anomala,
        "score_anomalia": round(score, 1) if is_anomala else 0.0,
        "motivo": motivo if is_anomala else "Fatura dentro dos limites operacionais normais."
    }

def get_business_insights(db: Session) -> dict:
    """
    Gera insights globais de IA corporativa analisando toda a base de dados relacional.
    Previsão de faturação do próximo mês, análise de risco de churn de clientes e rotura de stock.
    """
    faturas = db.query(models.Fatura).filter(models.Fatura.status == "CONFIRMADA").all()
    produtos = db.query(models.Produto).all()
    clientes = db.query(models.Cliente).all()

    if len(faturas) < 5:
        return {
            "previsao_faturacao_proximo_mes": 0.0,
            "clientes_em_risco_churn": [],
            "produtos_criticos": []
        }

    # 1. Previsão de Faturação usando regressão linear agregada mensal
    dados_mensais = {}
    for f in faturas:
        dt_str = f.data.split("T")[0]
        mes_ano = dt_str[:7] # YYYY-MM
        dados_mensais[mes_ano] = dados_mensais.get(mes_ano, 0.0) + f.total
        
    df_m = pd.DataFrame(list(dados_mensais.items()), columns=["mes", "total"])
    df_m = df_m.sort_values("mes").reset_index()
    df_m["index_num"] = df_m.index

    if len(df_m) >= 2:
        model = LinearRegression()
        model.fit(df_m[["index_num"]].values, df_m["total"].values)
        prox_mes_index = len(df_m)
        previsao_faturamento = float(model.predict([[prox_mes_index]])[0])
    else:
        previsao_faturamento = sum(df_m["total"].values) * 1.05 # Estimativa conservadora de +5%

    # 2. Clientes em risco de Churn (clientes que compraram muito no passado, mas não compram há mais de 30 dias)
    hoje = datetime.now()
    clientes_churn = []
    for c in clientes:
        if c.ultima_fatura:
            dt_ultima = datetime.strptime(c.ultima_fatura, "%Y-%m-%d")
            dias_inativo = (hoje - dt_ultima).days
            if dias_inativo > 20 and c.total_faturas > 15:
                clientes_churn.append({
                    "id": c.id,
                    "nome": c.nome,
                    "dias_inativo": dias_inativo,
                    "risco": "Elevado" if dias_inativo > 40 else "Moderado",
                    "motivo": f"Inativo há {dias_inativo} dias com histórico de alta fidelidade ({c.total_faturas} faturas)."
                })

    # 3. Produtos em rotura iminente de stock (previsto esgotar em menos de 10 dias)
    produtos_criticos = []
    for p in produtos:
        prediction = train_and_predict_demand(db, p.id)
        if "error" not in prediction and prediction["dias_ate_esgotar"] <= 10:
            produtos_criticos.append({
                "id": p.id,
                "nome": p.nome,
                "stock": p.stock,
                "dias_restantes": prediction["dias_ate_esgotar"],
                "recomendacao": prediction["recomendacao"]
            })

    return {
        "previsao_faturacao_proximo_mes": round(max(0, previsao_faturamento), 2),
        "clientes_em_risco_churn": clientes_churn[:5],
        "produtos_criticos": produtos_criticos[:5],
        "total_analisado_faturas": len(faturas),
        "total_analisado_clientes": len(clientes),
        "total_analisado_produtos": len(produtos)
    }
