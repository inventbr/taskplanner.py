def calcular_cronograma(tarefas):
    # Validar IDs e durações
    ids = [t["id"] for t in tarefas]

    if len(ids) != len(set(ids)):
        raise ValueError("Existem IDs duplicados.")

    por_id = {t["id"]: t for t in tarefas}
    sucessoras = {i: [] for i in ids}
    grau = {i: 0 for i in ids}

    for t in tarefas:
        if t["duracao"] < 0:
            raise ValueError("Duração negativa.")

        for dep in t["dependencias"]:
            if dep not in por_id:
                raise ValueError(f"Dependência inválida: {dep}")
            if dep == t["id"]:
                raise ValueError("Dependência circular.")

            sucessoras[dep].append(t["id"])
            grau[t["id"]] += 1

    # Ordenação topológica
    fila = [i for i in ids if grau[i] == 0]
    ordem = []

    while fila:
        atual = fila.pop(0)
        ordem.append(atual)

        for prox in sucessoras[atual]:
            grau[prox] -= 1
            if grau[prox] == 0:
                fila.append(prox)

    if len(ordem) != len(ids):
        raise ValueError("Há dependências circulares.")

    # Início e término mais cedo
    inicio = {}
    fim = {}

    for i in ordem:
        deps = por_id[i]["dependencias"]
        inicio[i] = max((fim[d] for d in deps), default=0)
        fim[i] = inicio[i] + por_id[i]["duracao"]

    prazo = max(fim.values(), default=0)

    # Início e término mais tarde
    inicio_tarde = {}
    fim_tarde = {}

    for i in reversed(ordem):
        if sucessoras[i]:
            fim_tarde[i] = min(
                inicio_tarde[s] for s in sucessoras[i]
            )
        else:
            fim_tarde[i] = prazo

        inicio_tarde[i] = (
            fim_tarde[i] - por_id[i]["duracao"]
        )

    # Resultado
    resultado = []

    for i in ordem:
        folga = inicio_tarde[i] - inicio[i]

        resultado.append({
            "id": i,
            "tarefa": por_id[i]["nome"],
            "inicio": inicio[i],
            "fim": fim[i],
            "duracao": por_id[i]["duracao"],
            "folga": folga,
            "critica": folga == 0
        })

    return prazo, resultado


# ===================================
# CADASTRE SUAS TAREFAS AQUI
# ===================================

tarefas = [
    {
        "id": "A",
        "nome": "Desligar máquina",
        "duracao": 2,
        "dependencias": []
    },
    {
        "id": "B",
        "nome": "Trocar peça",
        "duracao": 3,
        "dependencias": ["A"]
    },
    {
        "id": "C",
        "nome": "Pintar estrutura",
        "duracao": 4,
        "dependencias": ["A"]
    },
    {
        "id": "D",
        "nome": "Testar e religar",
        "duracao": 1,
        "dependencias": ["B", "C"]
    }
]

# ===================================
# EXECUÇÃO
# ===================================

prazo, resultado = calcular_cronograma(tarefas)

print("\n===== RELATÓRIO DO PROJETO =====")
print(f"Prazo mínimo: {prazo} dias\n")

for r in resultado:
    status = "CRÍTICA" if r["critica"] else "Não crítica"

    print(f"Tarefa: {r['tarefa']}")
    print(f"Início: dia {r['inicio']}")
    print(f"Término: dia {r['fim']}")
    print(f"Duração: {r['duracao']} dias")
    print(f"Folga: {r['folga']} dias")
    print(f"Status: {status}")
    print("-" * 30)
