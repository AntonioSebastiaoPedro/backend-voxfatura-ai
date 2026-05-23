from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    nif = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    morada = Column(String, nullable=True)
    limite_credito = Column(Float, default=0.0)
    divida = Column(Float, default=0.0)
    status = Column(String, default="Em Dia")
    total_faturas = Column(Integer, default=0)
    ultima_fatura = Column(String, nullable=True)

    faturas = relationship("Fatura", back_populates="cliente")

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    preco_historico_medio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    tendencia = Column(String, default="stable")

class Operador(Base):
    __tablename__ = "operadores"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    avatar = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    role = Column(String, default="operador")

    faturas = relationship("Fatura", back_populates="operador")

class Fatura(Base):
    __tablename__ = "faturas"

    id = Column(String, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True, nullable=False)
    cliente_id = Column(String, ForeignKey("clientes.id"), nullable=False)
    operador_id = Column(String, ForeignKey("operadores.id"), nullable=False)
    data = Column(String, nullable=False)
    subtotal = Column(Float, nullable=False)
    iva = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="RASCUNHO")  # RASCUNHO, CONFIRMADA, CANCELADA

    cliente = relationship("Cliente", back_populates="faturas")
    operador = relationship("Operador", back_populates="faturas")
    itens = relationship("FaturaItem", back_populates="fatura", cascade="all, delete-orphan", lazy="joined")

class FaturaItem(Base):
    __tablename__ = "fatura_itens"

    id = Column(String, primary_key=True, index=True)
    fatura_id = Column(String, ForeignKey("faturas.id"), nullable=False)
    produto_id = Column(String, ForeignKey("produtos.id"), nullable=False)
    produto_nome = Column(String, nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    fatura = relationship("Fatura", back_populates="itens")
    produto = relationship("Produto")

class HistoricoPreco(Base):
    __tablename__ = "historico_precos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    produto_id = Column(String, ForeignKey("produtos.id"), nullable=False)
    data = Column(String, nullable=False)
    preco = Column(Float, nullable=False)

    produto = relationship("Produto")
