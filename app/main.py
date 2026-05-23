from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from .database import engine, Base, get_db
from . import models, schemas
from .ai import predictor, voice_nlp

app = FastAPI(
    title="VoxFatura AI API",
    description="Backend inteligente em Python com PostgreSQL local e Machine Learning integrado.",
    version="1.0"
)

# Configurar CORS para permitir comunicação segura com o Frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ════════════════════════════════════════════════════════════
#  ENDPOINTS: CLIENTES
# ════════════════════════════════════════════════════════════

@app.get("/api/clientes", response_model=List[schemas.ClienteBase])
def read_clientes(db: Session = Depends(get_db)):
    return db.query(models.Cliente).all()

@app.get("/api/clientes/{id}", response_model=schemas.ClienteBase)
def read_cliente(id: str, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@app.post("/api/clientes", response_model=schemas.ClienteBase)
def create_cliente(cliente_in: schemas.ClienteCreateUpdate, db: Session = Depends(get_db)):
    count = db.query(models.Cliente).count()
    new_id = f"cli-{str(count + 1).zfill(3)}"
    while db.query(models.Cliente).filter(models.Cliente.id == new_id).first():
        count += 1
        new_id = f"cli-{str(count + 1).zfill(3)}"
        
    db_cliente = models.Cliente(
        id=new_id,
        nome=cliente_in.nome,
        nif=cliente_in.nif,
        telefone=cliente_in.telefone,
        email=cliente_in.email,
        morada=cliente_in.morada,
        limite_credito=cliente_in.limite_credito,
        divida=0.0,
        status="Em Dia",
        total_faturas=0,
        ultima_fatura=None
    )
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.put("/api/clientes/{id}", response_model=schemas.ClienteBase)
def update_cliente(id: str, cliente_in: schemas.ClienteCreateUpdate, db: Session = Depends(get_db)):
    db_cliente = db.query(models.Cliente).filter(models.Cliente.id == id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db_cliente.nome = cliente_in.nome
    db_cliente.nif = cliente_in.nif
    db_cliente.telefone = cliente_in.telefone
    db_cliente.email = cliente_in.email
    db_cliente.morada = cliente_in.morada
    db_cliente.limite_credito = cliente_in.limite_credito
    if db_cliente.divida > 0:
        db_cliente.status = "Com Dívida"
    else:
        db_cliente.status = "Em Dia"
        
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

# ════════════════════════════════════════════════════════════
#  ENDPOINTS: PRODUTOS
# ════════════════════════════════════════════════════════════

@app.get("/api/produtos", response_model=List[schemas.ProdutoBase])
def read_produtos(db: Session = Depends(get_db)):
    return db.query(models.Produto).all()

@app.get("/api/produtos/{id}", response_model=schemas.ProdutoBase)
def read_produto(id: str, db: Session = Depends(get_db)):
    produto = db.query(models.Produto).filter(models.Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@app.post("/api/produtos", response_model=schemas.ProdutoBase)
def create_produto(produto_in: schemas.ProdutoCreateUpdate, db: Session = Depends(get_db)):
    count = db.query(models.Produto).count()
    new_id = f"prod-{str(count + 1).zfill(3)}"
    while db.query(models.Produto).filter(models.Produto.id == new_id).first():
        count += 1
        new_id = f"prod-{str(count + 1).zfill(3)}"
        
    tendencia = "stable"
    diff = produto_in.preco_unitario - produto_in.preco_historico_medio
    if abs(diff) > produto_in.preco_historico_medio * 0.05:
        tendencia = "up" if diff > 0 else "down"

    db_produto = models.Produto(
        id=new_id,
        nome=produto_in.nome,
        categoria=produto_in.categoria,
        preco_unitario=produto_in.preco_unitario,
        preco_historico_medio=produto_in.preco_historico_medio,
        stock=produto_in.stock,
        tendencia=tendencia
    )
    db.add(db_produto)
    
    db_hist = models.HistoricoPreco(
        produto_id=new_id,
        data=datetime.now().strftime("%Y-%m-%d"),
        preco=produto_in.preco_unitario
    )
    db.add(db_hist)
    
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.put("/api/produtos/{id}", response_model=schemas.ProdutoBase)
def update_produto(id: str, produto_in: schemas.ProdutoCreateUpdate, db: Session = Depends(get_db)):
    db_produto = db.query(models.Produto).filter(models.Produto.id == id).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    preco_antigo = db_produto.preco_unitario
    
    db_produto.nome = produto_in.nome
    db_produto.categoria = produto_in.categoria
    db_produto.preco_unitario = produto_in.preco_unitario
    db_produto.preco_historico_medio = produto_in.preco_historico_medio
    db_produto.stock = produto_in.stock
    
    diff = produto_in.preco_unitario - produto_in.preco_historico_medio
    if abs(diff) > produto_in.preco_historico_medio * 0.05:
        db_produto.tendencia = "up" if diff > 0 else "down"
    else:
        db_produto.tendencia = "stable"
        
    if preco_antigo != produto_in.preco_unitario:
        db_hist = models.HistoricoPreco(
            produto_id=id,
            data=datetime.now().strftime("%Y-%m-%d"),
            preco=produto_in.preco_unitario
        )
        db.add(db_hist)
        
    db.commit()
    db.refresh(db_produto)
    return db_produto

# ════════════════════════════════════════════════════════════
#  ENDPOINTS: OPERADORES / UTILIZADORES
# ════════════════════════════════════════════════════════════

@app.get("/api/operadores", response_model=List[schemas.OperadorBase])
def read_operadores(db: Session = Depends(get_db)):
    return db.query(models.Operador).all()

# ════════════════════════════════════════════════════════════
#  ENDPOINTS: FATURAS & MOVIMENTAÇÕES DE STOCK
# ════════════════════════════════════════════════════════════

@app.get("/api/faturas", response_model=List[schemas.FaturaBase])
def read_faturas(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Fatura)
    if status:
        query = query.filter(models.Fatura.status == status)
    return query.order_by(models.Fatura.data.desc()).all()

@app.get("/api/faturas/{id}", response_model=schemas.FaturaBase)
def read_fatura(id: str, db: Session = Depends(get_db)):
    fatura = db.query(models.Fatura).filter(models.Fatura.id == id).first()
    if not fatura:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return fatura

@app.post("/api/faturas", response_model=schemas.FaturaBase)
def create_fatura(fatura_in: schemas.FaturaCreate, db: Session = Depends(get_db)):
    # 1. Validar Cliente e Operador
    cliente = db.query(models.Cliente).filter(models.Cliente.id == fatura_in.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    operador = db.query(models.Operador).filter(models.Operador.id == fatura_in.operador_id).first()
    if not operador:
        raise HTTPException(status_code=404, detail="Operador não encontrado")

    # 2. Gerar número de fatura sequencial dinâmico
    ano = datetime.now().year
    count = db.query(models.Fatura).filter(models.Fatura.numero.like(f"FAT-{ano}-%")).count()
    num_fatura = f"FAT-{ano}-{str(count + 1).zfill(3)}"

    # 3. Calcular subtotais baseados em itens
    subtotal = 0.0
    itens_para_criar = []
    
    fatura_id = str(uuid.uuid4())

    for idx, item in enumerate(fatura_in.itens):
        produto = db.query(models.Produto).filter(models.Produto.id == item.produto_id).first()
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_nome} não encontrado.")
        
        # Validar stock disponível se for confirmada diretamente
        if fatura_in.status == "CONFIRMADA" and produto.stock < item.quantidade:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {produto.nome} (Disponível: {produto.stock}).")

        item_total = item.quantidade * item.preco_unitario
        subtotal += item_total

        # Estruturar item da fatura
        itens_para_criar.append(models.FaturaItem(
            id=f"i-{fatura_id[-8:]}-{idx}",
            fatura_id=fatura_id,
            produto_id=item.produto_id,
            produto_nome=item.produto_nome,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
            total=item_total
        ))

        # Reduzir stock se a fatura já estiver CONFIRMADA
        if fatura_in.status == "CONFIRMADA":
            produto.stock -= item.quantidade

    iva = subtotal * 0.14  # IVA 14% padrão em Angola
    total = subtotal + iva

    # 4. Criar Fatura
    nova_fatura = models.Fatura(
        id=fatura_id,
        numero=num_fatura,
        cliente_id=fatura_in.cliente_id,
        operador_id=fatura_in.operador_id,
        data=datetime.now().isoformat() + "Z",
        subtotal=subtotal,
        iva=iva,
        total=total,
        status=fatura_in.status
    )
    
    db.add(nova_fatura)
    db.add_all(itens_para_criar)

    # 5. Atualizar perfil do cliente se confirmada
    if fatura_in.status == "CONFIRMADA":
        cliente.total_faturas += 1
        cliente.ultima_fatura = datetime.now().strftime("%Y-%m-%d")
        # Simular aumento de dívida se cliente for associado a crédito
        if cliente.limite_credito > 0:
            cliente.divida += total
            if cliente.divida > 0:
                cliente.status = "Com Dívida"

    try:
        db.commit()
        db.refresh(nova_fatura)
        return nova_fatura
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar fatura: {e}")

@app.put("/api/faturas/{id}/status", response_model=schemas.FaturaBase)
def update_fatura_status(id: str, status: str = Query(...), db: Session = Depends(get_db)):
    fatura = db.query(models.Fatura).filter(models.Fatura.id == id).first()
    if not fatura:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")

    if fatura.status == status:
        return fatura

    # Se a fatura estava como rascunho e agora é CONFIRMADA
    if fatura.status == "RASCUNHO" and status == "CONFIRMADA":
        for item in fatura.itens:
            produto = db.query(models.Produto).filter(models.Produto.id == item.produto_id).first()
            if produto:
                if produto.stock < item.quantidade:
                    raise HTTPException(status_code=400, detail=f"Stock insuficiente para {produto.nome} (Disponível: {produto.stock}).")
                produto.stock -= item.quantidade
        
        cliente = fatura.cliente
        cliente.total_faturas += 1
        cliente.ultima_fatura = datetime.now().strftime("%Y-%m-%d")

    # Se a fatura é cancelada e já estava confirmada (devolver stock)
    elif fatura.status == "CONFIRMADA" and status == "CANCELADA":
        for item in fatura.itens:
            produto = db.query(models.Produto).filter(models.Produto.id == item.produto_id).first()
            if produto:
                produto.stock += item.quantidade
                
        cliente = fatura.cliente
        cliente.total_faturas = max(0, cliente.total_faturas - 1)

    fatura.status = status
    db.commit()
    db.refresh(fatura)
    return fatura

@app.delete("/api/faturas/{id}")
def delete_fatura(id: str, db: Session = Depends(get_db)):
    fatura = db.query(models.Fatura).filter(models.Fatura.id == id).first()
    if not fatura:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    
    # Se estava confirmada, devolver stock e ajustar balanço do cliente antes de apagar
    if fatura.status == "CONFIRMADA":
        for item in fatura.itens:
            produto = db.query(models.Produto).filter(models.Produto.id == item.produto_id).first()
            if produto:
                produto.stock += item.quantidade
        
        cliente = fatura.cliente
        if cliente:
            cliente.total_faturas = max(0, cliente.total_faturas - 1)
            if cliente.limite_credito > 0:
                cliente.divida = max(0.0, cliente.divida - fatura.total)
                if cliente.divida == 0:
                    cliente.status = "Em Dia"

    db.delete(fatura)
    db.commit()
    return {"message": "Fatura eliminada com sucesso"}

# ════════════════════════════════════════════════════════════
#  ENDPOINTS: HISTÓRICO DE PREÇOS
# ════════════════════════════════════════════════════════════

@app.get("/api/historico_precos")
def read_historico_precos(db: Session = Depends(get_db)):
    precos = db.query(models.HistoricoPreco).all()
    return [{"produtoId": p.produto_id, "data": p.data, "preco": p.preco} for p in precos]

# ════════════════════════════════════════════════════════════
#  ENDPOINTS: INTELIGÊNCIA ARTIFICIAL (IA) & ML LOCAL
# ════════════════════════════════════════════════════════════

@app.post("/api/ai/voice-command", response_model=schemas.VoiceCommandResponse)
def process_voice(req: schemas.VoiceCommandRequest, db: Session = Depends(get_db)):
    """Recebe transcrição de voz e processa ações no backend relacional."""
    result = voice_nlp.parse_voice_command(db, req.text)
    return result

@app.get("/api/ai/prediction/demand/{product_id}", response_model=schemas.DemandPredictionResponse)
def predict_demand(product_id: str, db: Session = Depends(get_db)):
    """Previsão de demanda e rotura de stock usando regressão linear local."""
    result = predictor.train_and_predict_demand(db, product_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.post("/api/ai/check-anomaly", response_model=schemas.AnomalyCheckResponse)
def check_invoice_anomaly(req: schemas.AnomalyCheckRequest, db: Session = Depends(get_db)):
    """Deteta anomalias ou fraudes em subtotais de fatura usando Isolation Forest local."""
    result = predictor.detect_invoice_anomaly(db, req.subtotal, req.cliente_id)
    return result

@app.get("/api/ai/business-insights", response_model=schemas.BusinessInsightsResponse)
def get_insights(db: Session = Depends(get_db)):
    """Insights corporativos globais com ML (previsão financeira, risco de churn e rotura)."""
    return predictor.get_business_insights(db)
