import re
from sqlalchemy.orm import Session
from app import models

def normalize_text(text: str) -> str:
    """Normaliza o texto de voz removendo acentos, pontuação e espaços extras."""
    if not text:
        return ""
    text = text.lower()
    # Substituições simples de acentuação
    replacements = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u',
        'ç': 'c'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return " ".join(text.split())

def parse_voice_command(db: Session, raw_text: str) -> dict:
    """
    Analisa a transcrição de voz e mapeia para uma ação estruturada no sistema,
    buscando correspondência real de produtos e clientes na base de dados PostgreSQL.
    """
    normalized = normalize_text(raw_text)
    
    if not normalized:
        return {"action": "UNKNOWN", "message": "Nenhum comando de voz detectado."}

    # 1. COMANDO: CONFIRMAR FATURA
    if any(k in normalized for k in ["confirmar", "salvar", "finalizar", "emitir"]):
        return {
            "action": "CONFIRM_INVOICE",
            "message": "Comando reconhecido: Confirmar e emitir fatura."
        }

    # 2. COMANDO: LIMPAR FATURA / RASCUNHO
    if any(k in normalized for k in ["limpar", "cancelar", "apagar tudo", "esvaziar"]):
        return {
            "action": "CLEAR_INVOICE",
            "message": "Comando reconhecido: Limpar rascunho de fatura."
        }

    # 3. COMANDO: DEFINIR CLIENTE
    # Ex: "faturar para joao manuel silva", "cliente maria"
    client_match = re.search(r'(?:cliente|faturar\spara|para\so\scliente|para\sa\scliente)\s+(.+)', normalized)
    if client_match:
        client_query = client_match.group(1).strip()
        # Buscar cliente correspondente por nome na base de dados
        clientes = db.query(models.Cliente).all()
        best_client = None
        best_score = 0
        
        for c in clientes:
            c_norm = normalize_text(c.nome)
            # Calcular overlap de palavras
            q_words = set(client_query.split())
            c_words = set(c_norm.split())
            overlap = len(q_words.intersection(c_words))
            if overlap > best_score:
                best_score = overlap
                best_client = c

        if best_client:
            return {
                "action": "SET_CLIENT",
                "client": {
                    "id": best_client.id,
                    "nome": best_client.nome,
                    "nif": best_client.nif
                },
                "message": f"Cliente selecionado por voz: {best_client.nome}"
            }
        else:
            return {
                "action": "ERROR",
                "message": f"Cliente '{client_query}' não foi encontrado na base de dados."
            }

    # 4. COMANDO: ADICIONAR PRODUTO
    # Ex: "adicionar 5 arroz branco", "adicionar arroz 10 unidades", "acrescentar óleo 2"
    add_match = any(k in normalized for k in ["adicionar", "acrescentar", "por", "colocar", "lanca"])
    if add_match:
        # Extrair quantidade (procurar por números no texto)
        numbers = re.findall(r'\b\d+\b', normalized)
        quantidade = int(numbers[0]) if numbers else 1
        
        # Limpar o comando para sobrar apenas o termo de busca do produto
        clean_prod_query = normalized
        for k in ["adicionar", "acrescentar", "por", "colocar", "lanca", "unidades", "unidade", "un", "unids"]:
            clean_prod_query = clean_prod_query.replace(k, "")
        clean_prod_query = re.sub(r'\b\d+\b', '', clean_prod_query) # remover o número
        clean_prod_query = " ".join(clean_prod_query.split()) # remover espaços
        
        if not clean_prod_query:
            return {"action": "UNKNOWN", "message": "Por favor, diga o nome do produto a adicionar."}

        # Buscar produto correspondente na base de dados
        produtos = db.query(models.Produto).all()
        best_product = None
        best_score = 0
        
        for p in produtos:
            p_norm = normalize_text(p.nome)
            q_words = set(clean_prod_query.split())
            p_words = set(p_norm.split())
            overlap = len(q_words.intersection(p_words))
            if overlap > best_score:
                best_score = overlap
                best_product = p

        if best_product:
            return {
                "action": "ADD_ITEM",
                "product": {
                    "id": best_product.id,
                    "nome": best_product.nome,
                    "preco_unitario": best_product.preco_unitario,
                    "categoria": best_product.categoria
                },
                "quantidade": quantidade,
                "message": f"Adicionado por voz: {quantidade}x {best_product.nome}"
            }
        else:
            return {
                "action": "ERROR",
                "message": f"Produto '{clean_prod_query}' não encontrado no catálogo."
            }

    # 5. COMANDO: REMOVER PRODUTO
    # Ex: "remover arroz", "tirar feijao"
    remove_match = any(k in normalized for k in ["remover", "tirar", "apagar", "eliminar"])
    if remove_match:
        clean_prod_query = normalized
        for k in ["remover", "tirar", "apagar", "eliminar"]:
            clean_prod_query = clean_prod_query.replace(k, "")
        clean_prod_query = " ".join(clean_prod_query.split())
        
        if not clean_prod_query:
            return {"action": "UNKNOWN", "message": "Diga o nome do produto que deseja remover da fatura."}

        # Buscar correspondência
        produtos = db.query(models.Produto).all()
        best_product = None
        best_score = 0
        
        for p in produtos:
            p_norm = normalize_text(p.nome)
            q_words = set(clean_prod_query.split())
            p_words = set(p_norm.split())
            overlap = len(q_words.intersection(p_words))
            if overlap > best_score:
                best_score = overlap
                best_product = p

        if best_product:
            return {
                "action": "REMOVE_ITEM",
                "product_id": best_product.id,
                "message": f"Removido por voz: {best_product.nome}"
            }
        else:
            return {
                "action": "ERROR",
                "message": f"Produto '{clean_prod_query}' não encontrado na fatura."
            }

    return {
        "action": "UNKNOWN",
        "message": f"Comando de voz não catalogado: '{raw_text}'. Tente: 'Adicionar 5 Arroz' ou 'Faturar para João'."
    }
