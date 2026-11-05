from collections import defaultdict, deque
import json


def calcular_projeto(tarefas):
    """
    Calcula duração mínima, cronograma e caminho crítico.
    Cada tarefa contém:
    id, nome, duracao e dependencias.
    """

    por_id = {t["id"]: t for t in tarefas}

    if len(por_id) != len(tarefas):
        raise ValueError("Existem IDs de tarefas duplicados.")

    for tarefa in tarefas:
        if tarefa["duracao"] < 0:
            raise ValueError("A duração não pode ser negativa.")

        for dependencia in tarefa["dependencias"]:
            if dependencia not in por_id:
                raise ValueError(
                    f"Dependência inexistente: {dependencia}"
                )

            if dependencia == tarefa["id"]:
                raise ValueError("Uma tarefa não pode depender de si mesma.")

    # Montar grafo de dependências
    proximas = defaultdict(list)
    grau = {id: 0 for id in por_id}

    for tarefa in tarefas:
        for dep in tarefa["dependencias"]:
            proximas[dep].append(tarefa["id"])
            grau[tarefa["id"]] += 1

    # Ordenação topológica
    fila = deque(
        id for id in por_id if grau[id] == 0
    )
    ordem = []

    while fila:
        atual = fila.popleft()
        ordem.append(atual)

        for proxima in proximas[atual]:
            grau[proxima] -= 1
            if grau[proxima] == 0:
                fila.append(proxima)

    if len(ordem) != len(tarefas):
        raise ValueError("Dependências circulares detectadas.")

    # Cálculo dos tempos mais cedo
    inicio = {}
    fim = {}
    predecessor = {}

    for id in ordem:
        tarefa = por_id[id]
        deps = tarefa["dependencias"]

        if deps:
            melhor = max(deps, key=lambda d: fim[d])
            inicio[id] = fim[melhor]
            predecessor[id] = melhor
        else:
            inicio[id] = 0
            predecessor[id] = None

        fim[id] = inicio[id] + tarefa["duracao"]

    prazo = max(fim.values(), default=0)

    # Cálculo dos tempos mais tarde
    fim_tarde = {}
    inicio_tarde = {}

    for id in reversed(ordem):
        sucessoras = proximas[id]

        if sucessoras:
            fim_tarde[id] = min(
                inicio_tarde[s] for s in sucessoras
            )
        else:
            fim_tarde[id] = prazo

        inicio_tarde[id] = (
            fim_tarde[id] - por_id[id]["duracao"]
        )

    # Folgas
    folgas = {
        id: inicio_tarde[id] - inicio[id]
        for id in por_id
    }

    # Um caminho crítico
    finais = [
        id for id in por_id
        if not proximas[id] and folgas[id] == 0
        and fim[id] == prazo
    ]

    caminho = []

    if finais:
        atual = finais[0]
        while atual is not None:
            caminho.append(atual)
            atual = predecessor[atual]

        caminho.reverse()

    return prazo, inicio, fim, folgas, caminho


def exibir_resultado(tarefas):
    prazo, inicio, fim, folgas, caminho = (
        calcular_projeto(tarefas)
    )

    print("\n========== TASKPLANNER ==========")
    print(f"Prazo mínimo: {prazo} dias\n")

    print("CRONOGRAMA:")

    for tarefa in tarefas:
        id = tarefa["id"]
        print(
            f"{id} - {tarefa['nome']}: "
            f"Dia {inicio[id]} até {fim[id]} | "
            f"Duração: {tarefa['duracao']} dias | "
            f"Folga: {folgas[id]} dias"
        )

    print("\nCAMINHO CRÍTICO:")
    print(" -> ".join(caminho))

    print("\n=================================")


if __name__ == "__main__":

    # Exemplo: manutenção de uma máquina
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

    exibir_resultado(tarefas)
