import os
import sys
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app import models

def db_init(drop_first=True):
    print("Inicializando tabelas na base de dados PostgreSQL...")
    # Cria todas as tabelas no PostgreSQL
    if drop_first:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")

    db: Session = SessionLocal()
    try:
        # ════════════════════════════════════════════════════════════
        #  OPERADORES
        # ════════════════════════════════════════════════════════════
        operadores = [
            models.Operador(id="op-001", nome="Ana Beatriz Lopes", email="ana.lopes@voxfatura.ao", avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=AnaBeatriz", ativo=True, role="operador"),
            models.Operador(id="op-002", nome="Ricardo Nunes", email="ricardo.nunes@voxfatura.ao", avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=RicardoN", ativo=True, role="operador"),
            models.Operador(id="op-003", nome="Carla Mendes", email="carla.mendes@voxfatura.ao", avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=CarlaM", ativo=True, role="operador"),
            models.Operador(id="admin", nome="Administrador Sistema", email="utilizador@voxfatura.ao", avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Admin", ativo=True, role="admin"),
            models.Operador(id="supervisor", nome="Supervisor Geral", email="supervisor@voxfatura.ao", avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Supervisor", ativo=True, role="supervisor"),
            models.Operador(id="auditor", nome="Auditor Geral", email="auditor@voxfatura.ao", avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Auditor", ativo=True, role="auditor"),
        ]
        db.add_all(operadores)
        print(f"Inseridos {len(operadores)} operadores.")

        # ════════════════════════════════════════════════════════════
        #  CLIENTES
        # ════════════════════════════════════════════════════════════
        clientes_raw = [
            ("cli-001", "João Manuel Silva", "5417283901", "+244 923 456 789", "joao.silva@email.ao", "Rua da Missão, Luanda", 500000.0, 0.0, "Em Dia", 38, "2026-05-10"),
            ("cli-002", "Maria Fernanda Costa", "5417283902", "+244 924 567 890", "maria.costa@email.ao", "Av. 4 de Fevereiro, Luanda", 300000.0, 45000.0, "Com Dívida", 22, "2026-04-25"),
            ("cli-003", "António José Pereira", "5417283903", "+244 925 678 901", "antonio@email.ao", "Bairro Maculusso, Luanda", 400000.0, 0.0, "Em Dia", 45, "2026-05-11"),
            ("cli-004", "Isabel Rodrigues Santos", "5417283904", "+244 926 789 012", "isabel.santos@email.ao", "Rua Rainha Ginga, Luanda", 250000.0, 0.0, "Em Dia", 20, "2026-05-08"),
            ("cli-005", "Carlos Alberto Mendes", "5417283905", "+244 927 890 123", "carlos.mendes@email.ao", "Bairro Alvalade, Luanda", 600000.0, 120000.0, "Com Dívida", 55, "2026-04-15"),
            ("cli-006", "Ana Paula Ferreira", "5417283906", "+244 928 901 234", "ana.ferreira@email.ao", "Rua Direita, Luanda", 350000.0, 0.0, "Em Dia", 28, "2026-05-09"),
            ("cli-007", "Pedro Miguel Alves", "5417283907", "+244 929 012 345", "pedro.alves@email.ao", "Av. Lenine, Luanda", 450000.0, 0.0, "Em Dia", 33, "2026-05-11"),
            ("cli-008", "Luísa Margarida Sousa", "5417283908", "+244 930 123 456", "luisa.sousa@email.ao", "Bairro Maianga, Luanda", 200000.0, 28000.0, "Com Dívida", 14, "2026-04-20"),
            ("cli-009", "Francisco Neto Baptista", "5417283909", "+244 931 234 567", "f.baptista@email.ao", "Sambizanga, Luanda", 700000.0, 0.0, "Em Dia", 70, "2026-05-10"),
            ("cli-010", "Rosa Conceição Lima", "5417283910", "+244 932 345 678", "rosa.lima@email.ao", "Rangel, Luanda", 180000.0, 67000.0, "Com Dívida", 11, "2026-03-28"),
            ("cli-011", "Sérgio Domingos Castro", "5417283911", "+244 933 456 789", "sergio.castro@email.ao", "Cacuaco, Luanda", 520000.0, 0.0, "Em Dia", 50, "2026-05-07"),
            ("cli-012", "Beatriz Helena Vargas", "5417283912", "+244 934 567 890", "beatriz.vargas@email.ao", "Viana, Luanda", 290000.0, 0.0, "Em Dia", 24, "2026-05-06"),
            ("cli-013", "Manuel Eduardo Gomes", "5417283913", "+244 935 678 901", "manuel.gomes@email.ao", "Kilamba, Luanda", 800000.0, 250000.0, "Com Dívida", 78, "2026-05-01"),
            ("cli-014", "Teresa Filomena Nunes", "5417283914", "+244 936 789 012", "teresa.nunes@email.ao", "Talatona, Luanda", 420000.0, 0.0, "Em Dia", 30, "2026-05-09"),
            ("cli-015", "Augusto Ribeiro Lopes", "5417283915", "+244 937 890 123", "augusto.lopes@email.ao", "Benfica, Luanda", 340000.0, 0.0, "Em Dia", 42, "2026-05-11"),
            ("cli-016", "Constança Pires Teixeira", "5417283916", "+244 938 901 234", "constanca@email.ao", "Cazenga, Luanda", 160000.0, 38000.0, "Com Dívida", 12, "2026-04-10"),
            ("cli-017", "Diogo Mário Figueiredo", "5417283917", "+244 939 012 345", "diogo.fig@email.ao", "Samba, Luanda", 480000.0, 0.0, "Em Dia", 58, "2026-05-08"),
            ("cli-018", "Esperança Graça Monteiro", "5417283918", "+244 940 123 456", "esperanca@email.ao", "Golfe 2, Luanda", 230000.0, 0.0, "Em Dia", 18, "2026-05-05"),
            ("cli-019", "Hugo Celestino Barros", "5417283919", "+244 941 234 567", "hugo.barros@email.ao", "Ingombota, Luanda", 560000.0, 95000.0, "Com Dívida", 36, "2026-04-30"),
            ("cli-020", "Inês Marlene Correia", "5417283920", "+244 942 345 678", "ines.correia@email.ao", "Patriota, Luanda", 310000.0, 0.0, "Em Dia", 25, "2026-05-10"),
            ("cli-021", "Joaquim Baptista Neto", "5417283921", "+244 943 456 789", "joaquim.neto@email.ao", "Rocha Pinto, Luanda", 390000.0, 0.0, "Em Dia", 29, "2026-05-04"),
            ("cli-022", "Felicidade Andrade Cruz", "5417283922", "+244 944 567 890", "felicidade@email.ao", "Bairro Operário, Luanda", 270000.0, 55000.0, "Com Dívida", 16, "2026-04-22"),
            ("cli-023", "Rui Alexandre Tavares", "5417283923", "+244 945 678 901", "rui.tavares@email.ao", "Bairro 28 de Agosto, Luanda", 430000.0, 0.0, "Em Dia", 47, "2026-05-07"),
            ("cli-024", "Glória Marta Sequeira", "5417283924", "+244 946 789 012", "gloria.seq@email.ao", "Praia do Bispo, Luanda", 195000.0, 0.0, "Em Dia", 10, "2026-05-02"),
            ("cli-025", "Arnaldo Pinto Pacheco", "5417283925", "+244 947 890 123", "arnaldo.pacheco@email.ao", "Belas, Luanda", 510000.0, 0.0, "Em Dia", 62, "2026-05-09"),
            ("cli-026", "Natália Ferraz Oliveira", "5417283926", "+244 948 901 234", "natalia.oliveira@email.ao", "Viana Sul, Luanda", 220000.0, 42000.0, "Com Dívida", 13, "2026-04-18"),
            ("cli-027", "Valter Simão Rodrigues", "5417283927", "+244 949 012 345", "valter.sim@email.ao", "Zango 2, Luanda", 380000.0, 0.0, "Em Dia", 34, "2026-05-06"),
            ("cli-028", "Celeste Marina Afonso", "5417283928", "+244 950 123 456", "celeste.afonso@email.ao", "Morro Bento, Luanda", 145000.0, 0.0, "Em Dia", 8, "2026-05-03"),
            ("cli-029", "Hélio Américo Dias", "5417283929", "+244 951 234 567", "helio.dias@email.ao", "Cidade Alta, Luanda", 640000.0, 180000.0, "Com Dívida", 44, "2026-04-28"),
            ("cli-030", "Suzana Brites Leal", "5417283930", "+244 952 345 678", "suzana.leal@email.ao", "Futungo de Belas, Luanda", 260000.0, 0.0, "Em Dia", 19, "2026-05-08")
        ]
        
        clientes = []
        for c in clientes_raw:
            clientes.append(models.Cliente(
                id=c[0], nome=c[1], nif=c[2], telefone=c[3], email=c[4], 
                morada=c[5], limite_credito=c[6], divida=c[7], status=c[8],
                total_faturas=c[9], ultima_fatura=c[10]
            ))
        db.add_all(clientes)
        print(f"Inseridos {len(clientes)} clientes.")

        # ════════════════════════════════════════════════════════════
        #  PRODUTOS
        # ════════════════════════════════════════════════════════════
        produtos_raw = [
            ("prod-001", "Arroz Branco 25kg", "Cereais", 8000.0, 7500.0, 150, "up"),
            ("prod-002", "Feijão Preto 10kg", "Leguminosas", 6500.0, 6800.0, 200, "down"),
            ("prod-003", "Óleo Alimentar 5L", "Óleos", 12000.0, 11500.0, 80, "up"),
            ("prod-004", "Farinha de Trigo 25kg", "Cereais", 5500.0, 5500.0, 120, "stable"),
            ("prod-005", "Açúcar Refinado 25kg", "Açúcares", 4000.0, 4200.0, 180, "down"),
            ("prod-006", "Sal Marinho 5kg", "Condimentos", 1500.0, 1500.0, 250, "stable"),
            ("prod-007", "Refrigerante Cola 24un", "Bebidas", 3500.0, 3200.0, 300, "up"),
            ("prod-008", "Água Mineral 12L", "Bebidas", 1200.0, 1200.0, 400, "stable"),
            ("prod-009", "Leite em Pó 1kg", "Laticínios", 9500.0, 9000.0, 60, "up"),
            ("prod-010", "Massa Alimentícia 5kg", "Cereais", 3000.0, 3000.0, 220, "stable"),
            ("prod-011", "Café Torrado 500g", "Bebidas", 7000.0, 7200.0, 90, "down"),
            ("prod-012", "Sabão em Pó 3kg", "Limpeza", 4500.0, 4500.0, 140, "stable"),
            ("prod-013", "Detergente Líquido 1L", "Limpeza", 2800.0, 2800.0, 190, "stable"),
            ("prod-014", "Tomate Pelado 400g", "Conservas", 950.0, 900.0, 320, "up"),
            ("prod-015", "Sardinha em Lata 250g", "Conservas", 1800.0, 1750.0, 280, "up"),
            ("prod-016", "Cerveja Nacional 24un", "Bebidas", 5200.0, 5000.0, 180, "up"),
            ("prod-017", "Papel Higiénico 12un", "Higiene", 3200.0, 3100.0, 220, "up"),
            ("prod-018", "Frango Inteiro kg", "Carnes", 2200.0, 2100.0, 50, "up"),
            ("prod-019", "Azeite Extra Virgem 1L", "Óleos", 14500.0, 14000.0, 40, "up"),
            ("prod-020", "Biscoito Sortido 400g", "Snacks", 2100.0, 2000.0, 260, "up"),
            ("prod-021", "Manteiga 500g", "Laticínios", 6800.0, 6500.0, 75, "up"),
            ("prod-022", "Queijo Gouda 500g", "Laticínios", 11000.0, 10500.0, 45, "up"),
            ("prod-023", "Pão de Forma 500g", "Panificação", 1800.0, 1700.0, 100, "up"),
            ("prod-024", "Batata Frita 200g", "Snacks", 1400.0, 1350.0, 310, "up"),
            ("prod-025", "Iogurte Natural 4un", "Laticínios", 2500.0, 2400.0, 120, "stable"),
            ("prod-026", "Sumo de Laranja 1L", "Bebidas", 2200.0, 2100.0, 185, "up"),
            ("prod-027", "Vinagre Branco 750ml", "Condimentos", 1100.0, 1100.0, 200, "stable"),
            ("prod-028", "Milho em Grão 5kg", "Cereais", 3800.0, 3600.0, 160, "up"),
            ("prod-029", "Champô 400ml", "Higiene", 3500.0, 3400.0, 140, "stable"),
            ("prod-030", "Creme Dental 150g", "Higiene", 1600.0, 1550.0, 230, "up")
        ]
        
        produtos = []
        for p in produtos_raw:
            produtos.append(models.Produto(
                id=p[0], nome=p[1], categoria=p[2], preco_unitario=p[3],
                preco_historico_medio=p[4], stock=p[5], tendencia=p[6]
            ))
        db.add_all(produtos)
        print(f"Inseridos {len(produtos)} produtos.")

        # ════════════════════════════════════════════════════════════
        #  HISTÓRICO DE PREÇOS
        # ════════════════════════════════════════════════════════════
        hist_precos_raw = [
            ("prod-001", "2024-01-01", 6200.0), ("prod-001", "2024-04-01", 6400.0), ("prod-001", "2024-07-01", 6500.0), ("prod-001", "2024-10-01", 6800.0),
            ("prod-001", "2025-01-01", 6800.0), ("prod-001", "2025-04-01", 7000.0), ("prod-001", "2025-07-01", 7200.0), ("prod-001", "2025-10-01", 7500.0),
            ("prod-001", "2026-01-01", 7500.0), ("prod-001", "2026-03-01", 7800.0), ("prod-001", "2026-05-01", 8000.0),
            
            ("prod-003", "2024-01-01", 9200.0), ("prod-003", "2024-04-01", 9500.0), ("prod-003", "2024-07-01", 10000.0),("prod-003", "2024-10-01", 10500.0),
            ("prod-003", "2025-01-01", 10500.0),("prod-003", "2025-04-01", 11000.0),("prod-003", "2025-07-01", 11200.0),("prod-003", "2025-10-01", 11500.0),
            ("prod-003", "2026-01-01", 11500.0),("prod-003", "2026-03-01", 11800.0),("prod-003", "2026-05-01", 12000.0),

            ("prod-002", "2024-01-01", 7200.0), ("prod-002", "2024-07-01", 7000.0), ("prod-002", "2025-01-01", 6900.0), ("prod-002", "2025-07-01", 6700.0),
            ("prod-002", "2026-01-01", 6600.0), ("prod-002", "2026-05-01", 6500.0),

            ("prod-005", "2024-01-01", 4600.0), ("prod-005", "2024-07-01", 4600.0), ("prod-005", "2025-01-01", 4500.0), ("prod-005", "2025-07-01", 4200.0),
            ("prod-005", "2026-01-01", 4200.0), ("prod-005", "2026-05-01", 4000.0),

            ("prod-016", "2024-01-01", 4300.0), ("prod-016", "2024-07-01", 4500.0), ("prod-016", "2025-01-01", 4600.0), ("prod-016", "2025-07-01", 4800.0),
            ("prod-016", "2026-01-01", 5000.0), ("prod-016", "2026-05-01", 5200.0),

            ("prod-019", "2024-01-01", 11500.0),("prod-019", "2024-07-01", 12000.0),("prod-019", "2025-01-01", 12500.0),("prod-019", "2025-07-01", 13500.0),
            ("prod-019", "2026-01-01", 14000.0),("prod-019", "2026-05-01", 14500.0),

            ("prod-009", "2024-01-01", 8000.0), ("prod-009", "2024-07-01", 8200.0), ("prod-009", "2025-01-01", 8500.0), ("prod-009", "2025-07-01", 8800.0),
            ("prod-009", "2026-01-01", 9000.0), ("prod-009", "2026-05-01", 9500.0),

            ("prod-018", "2024-01-01", 1850.0), ("prod-018", "2024-07-01", 1900.0), ("prod-018", "2025-01-01", 1950.0), ("prod-018", "2025-07-01", 2000.0),
            ("prod-018", "2026-01-01", 2100.0), ("prod-018", "2026-05-01", 2200.0),

            ("prod-007", "2024-01-01", 2900.0), ("prod-007", "2024-07-01", 3000.0), ("prod-007", "2025-01-01", 3100.0), ("prod-007", "2025-07-01", 3200.0),
            ("prod-007", "2026-01-01", 3300.0), ("prod-007", "2026-05-01", 3500.0),

            ("prod-021", "2024-01-01", 5800.0), ("prod-021", "2024-07-01", 6000.0), ("prod-021", "2025-01-01", 6200.0), ("prod-021", "2025-07-01", 6500.0),
            ("prod-021", "2026-01-01", 6500.0), ("prod-021", "2026-05-01", 6800.0),

            ("prod-022", "2024-01-01", 9500.0), ("prod-022", "2024-07-01", 9800.0), ("prod-022", "2025-01-01", 10000.0),("prod-022", "2025-07-01", 10200.0),
            ("prod-022", "2026-01-01", 10500.0),("prod-022", "2026-05-01", 11000.0),

            ("prod-028", "2024-01-01", 3200.0), ("prod-028", "2024-07-01", 3300.0), ("prod-028", "2025-01-01", 3400.0), ("prod-028", "2025-07-01", 3600.0),
            ("prod-028", "2026-01-01", 3600.0), ("prod-028", "2026-05-01", 3800.0)
        ]
        
        hist_precos = []
        for h in hist_precos_raw:
            hist_precos.append(models.HistoricoPreco(produto_id=h[0], data=h[1], preco=h[2]))
        db.add_all(hist_precos)
        print(f"Inseridos {len(hist_precos)} históricos de preços.")

        # ════════════════════════════════════════════════════════════
        #  FATURAS (15 faturas principais de teste com itens reais)
        # ════════════════════════════════════════════════════════════
        faturas_raw = [
            ("fat-001", "FAT-2026-001", "cli-001", "op-001", "2026-05-11T09:15:00.000Z", 64000.0, 8960.0, 72960.0, "CONFIRMADA", [
                ("i001a", "prod-001", "Arroz Branco 25kg", 5, 8000.0, 40000.0),
                ("i001b", "prod-003", "Óleo Alimentar 5L", 2, 12000.0, 24000.0)
            ]),
            ("fat-002", "FAT-2026-002", "cli-003", "op-002", "2026-05-11T10:30:00.000Z", 56500.0, 7910.0, 64410.0, "CONFIRMADA", [
                ("i002a", "prod-002", "Feijão Preto 10kg", 3, 6500.0, 19500.0),
                ("i002b", "prod-005", "Açúcar Refinado 25kg", 4, 4000.0, 16000.0),
                ("i002c", "prod-007", "Refrigerante Cola 24un", 6, 3500.0, 21000.0)
            ]),
            ("fat-003", "FAT-2026-003", "cli-007", "op-001", "2026-05-11T11:45:00.000Z", 53000.0, 7420.0, 60420.0, "CONFIRMADA", [
                ("i003a", "prod-009", "Leite em Pó 1kg", 4, 9500.0, 38000.0),
                ("i003b", "prod-010", "Massa Alimentícia 5kg", 5, 3000.0, 15000.0)
            ]),
            ("fat-004", "FAT-2026-004", "cli-009", "op-003", "2026-05-10T14:20:00.000Z", 59600.0, 8344.0, 67944.0, "CONFIRMADA", [
                ("i004a", "prod-016", "Cerveja Nacional 24un", 8, 5200.0, 41600.0),
                ("i004b", "prod-015", "Sardinha em Lata 250g", 10, 1800.0, 18000.0)
            ]),
            ("fat-005", "FAT-2026-005", "cli-015", "op-002", "2026-05-09T15:05:00.000Z", 65500.0, 9170.0, 74670.0, "CONFIRMADA", [
                ("i005a", "prod-019", "Azeite Extra Virgem 1L", 3, 14500.0, 43500.0),
                ("i005b", "prod-018", "Frango Inteiro kg", 10, 2200.0, 22000.0)
            ]),
            ("fat-006", "FAT-2026-006", "cli-004", "op-001", "2026-05-10T09:00:00.000Z", 44000.0, 6160.0, 50160.0, "CONFIRMADA", [
                ("i006a", "prod-004", "Farinha de Trigo 25kg", 8, 5500.0, 44000.0)
            ]),
            ("fat-007", "FAT-2026-007", "cli-006", "op-003", "2026-05-10T10:15:00.000Z", 51200.0, 7168.0, 58368.0, "CONFIRMADA", [
                ("i007a", "prod-017", "Papel Higiénico 12un", 6, 3200.0, 19200.0),
                ("i007b", "prod-012", "Sabão em Pó 3kg", 4, 4500.0, 18000.0),
                ("i007c", "prod-013", "Detergente Líquido 1L", 5, 2800.0, 14000.0)
            ]),
            ("fat-008", "FAT-2026-008", "cli-011", "op-002", "2026-05-10T11:30:00.000Z", 160000.0, 22400.0, 182400.0, "CONFIRMADA", [
                ("i008a", "prod-001", "Arroz Branco 25kg", 10, 8000.0, 80000.0),
                ("i008b", "prod-003", "Óleo Alimentar 5L", 5, 12000.0, 60000.0),
                ("i008c", "prod-005", "Açúcar Refinado 25kg", 5, 4000.0, 20000.0)
            ]),
            ("fat-009", "FAT-2026-009", "cli-014", "op-001", "2026-05-09T09:45:00.000Z", 34800.0, 4872.0, 39672.0, "CONFIRMADA", [
                ("i009a", "prod-020", "Biscoito Sortido 400g", 12, 2100.0, 25200.0),
                ("i009b", "prod-008", "Água Mineral 12L", 8, 1200.0, 9600.0)
            ]),
            ("fat-010", "FAT-2026-010", "cli-017", "op-003", "2026-05-09T14:00:00.000Z", 56250.0, 7875.0, 64125.0, "CONFIRMADA", [
                ("i010a", "prod-011", "Café Torrado 500g", 6, 7000.0, 42000.0),
                ("i010b", "prod-014", "Tomate Pelado 400g", 15, 950.0, 14250.0)
            ]),
            ("fat-999", "FAT-2026-151", "cli-001", "op-001", "2026-05-11T16:00:00.000Z", 18000.0, 2520.0, 20520.0, "RASCUNHO", [
                ("i999a", "prod-006", "Sal Marinho 5kg", 12, 1500.0, 18000.0)
            ])
        ]

        for f_raw in faturas_raw:
            fatura = models.Fatura(
                id=f_raw[0], numero=f_raw[1], cliente_id=f_raw[2], operador_id=f_raw[3],
                data=f_raw[4], subtotal=f_raw[5], iva=f_raw[6], total=f_raw[7], status=f_raw[8]
            )
            db.add(fatura)
            db.flush() # Associa o ID antes de inserir itens
            
            for item_raw in f_raw[9]:
                fatura_item = models.FaturaItem(
                    id=item_raw[0], fatura_id=fatura.id, produto_id=item_raw[1],
                    produto_nome=item_raw[2], quantidade=item_raw[3],
                    preco_unitario=item_raw[4], total=item_raw[5]
                )
                db.add(fatura_item)
                
        print(f"Inseridas {len(faturas_raw)} faturas e seus itens correspondentes.")
        
        db.commit()
        print("Base de dados local populada com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"Erro ao popular base de dados: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    if "--if-empty" in sys.argv:
        db = SessionLocal()
        try:
            Base.metadata.create_all(bind=engine)
            count = db.query(models.Operador).count()
            if count > 0:
                print("Base de dados PostgreSQL já contém dados. Ignorando seeding inicial.")
                sys.exit(0)
            print("Base de dados vazia. A proceder à inicialização de demonstração...")
        except Exception as e:
            print(f"Erro ao verificar base de dados: {e}")
        finally:
            db.close()
        db_init(drop_first=False)
    else:
        db_init(drop_first=True)
