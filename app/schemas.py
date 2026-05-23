from pydantic import BaseModel
from typing import List, Optional

class ClienteBase(BaseModel):
    id: str
    nome: str
    nif: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    morada: Optional[str] = None
    limite_credito: float = 0.0
    divida: float = 0.0
    status: str = "Em Dia"
    total_faturas: int = 0
    ultima_fatura: Optional[str] = None

    class Config:
        from_attributes = True

class ClienteCreateUpdate(BaseModel):
    nome: str
    nif: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    morada: Optional[str] = None
    limite_credito: float = 0.0

class ProdutoBase(BaseModel):
    id: str
    nome: str
    categoria: str
    preco_unitario: float
    preco_historico_medio: float
    stock: int
    tendencia: str = "stable"

    class Config:
        from_attributes = True

class ProdutoCreateUpdate(BaseModel):
    nome: str
    categoria: str
    preco_unitario: float
    preco_historico_medio: float
    stock: int

class OperadorBase(BaseModel):
    id: str
    nome: str
    email: str
    avatar: Optional[str] = None
    ativo: bool = True
    role: str = "operador"

    class Config:
        from_attributes = True

class FaturaItemBase(BaseModel):
    id: str
    fatura_id: str
    produto_id: str
    produto_nome: str
    quantidade: int
    preco_unitario: float
    total: float

    class Config:
        from_attributes = True

class FaturaCreateItem(BaseModel):
    produto_id: str
    produto_nome: str
    quantidade: int
    preco_unitario: float

class FaturaCreate(BaseModel):
    cliente_id: str
    operador_id: str
    itens: List[FaturaCreateItem]
    status: str = "RASCUNHO"

class FaturaBase(BaseModel):
    id: str
    numero: str
    cliente_id: str
    operador_id: str
    data: str
    subtotal: float
    iva: float
    total: float
    status: str
    itens: List[FaturaItemBase] = []

    class Config:
        from_attributes = True

class VoiceCommandRequest(BaseModel):
    text: str

class VoiceCommandResponse(BaseModel):
    action: str
    client: Optional[dict] = None
    product: Optional[dict] = None
    product_id: Optional[str] = None
    quantidade: Optional[int] = None
    message: str

class AnomalyCheckRequest(BaseModel):
    subtotal: float
    cliente_id: str

class AnomalyCheckResponse(BaseModel):
    is_anomala: bool
    score_anomalia: float
    motivo: str

class DemandPredictionResponse(BaseModel):
    produto_nome: str
    stock_atual: int
    consumo_diario_medio: float
    previsao_demanda_30d: float
    dias_ate_esgotar: int
    confianca_modelo: str
    recomendacao: str

class BusinessInsightsResponse(BaseModel):
    previsao_faturacao_proximo_mes: float
    clientes_em_risco_churn: List[dict]
    produtos_criticos: List[dict]
    total_analisado_faturas: int
    total_analisado_clientes: int
    total_analisado_produtos: int
