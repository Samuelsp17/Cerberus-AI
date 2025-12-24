# Cerberus AI

Cerberus AI é um projeto open source que atua como um assistente para pentesters e bug bounty hunters, utilizando múltiplos modelos de linguagem para analisar requisições de segurança e gerar respostas técnicas com foco em segurança ofensiva.

O sistema foi projetado para ser **modular e extensível**, permitindo a substituição ou adição de novos modelos conforme o projeto evolui e novas opções se tornam disponíveis.


## Visão Geral

O Cerberus AI utiliza uma abordagem baseada em **múltiplos LLMs trabalhando em paralelo**, onde cada modelo fornece uma resposta independente para a mesma requisição de bug bounty ou pentest.

Essas respostas são coletadas e utilizadas tanto para **análise comparativa** quanto como **base de dados para o treinamento de um modelo adicional**, cujo objetivo é aprender com os padrões e estratégias produzidos pelos modelos originais.

```md
### Requisitos

- Python 3.10 ou superior
- pip atualizado
pip install -r requirements.txt
```
Os modelos utilizados não são permanentes. O sistema foi projetado para permitir a integração futura de:

- Novos modelos mais avançados
- Modelos open source
- Modelos uncensored
- Modelos especializados em segurança

---
## Arquitetura
[ Security Request ]
 → [ LLM Plugin 1 | LLM Plugin 2 | LLM Plugin N ]
 → [ Orchestrator / Normalizer ]
 → [ Dataset Builder ]
 → [ Learner Model ] (Em desenvolvimento)



### Componentes principais

- **Camada de LLMs**  
  Conjunto de modelos independentes, intercambiáveis e configuráveis.

- **Camada de orquestração**  
  Responsável por enviar requisições, coletar respostas e padronizar os resultados.

- **Camada de dados**  
  Armazena as respostas para análise, avaliação e treinamento.

- **Modelo agregador**  
  Modelo em desenvolvimento que será treinado com base nas respostas dos demais LLMs, buscando gerar respostas mais consistentes e especializadas.

---

## Estado Atual do Projeto

- Integração funcional com múltiplos provedores de LLM
- Respostas paralelas para requisições de bug bounty
- Arquitetura preparada para troca e adição de modelos
- Pipeline inicial de coleta de dados

O projeto encontra-se em desenvolvimento ativo, com foco atual na consolidação da base de dados e no desenho do modelo agregador.

---

## Objetivos

- Reduzir a dependência de um único modelo de linguagem
- Explorar múltiplas abordagens ofensivas para o mesmo problema
- Criar um modelo especializado em bug bounty e pentest
- Facilitar a experimentação com diferentes LLMs
- Apoiar profissionais de segurança na análise técnica

---

## Extensibilidade

O Cerberus AI foi projetado para facilitar:

- Substituição de modelos existentes
- Integração de novos provedores
- Uso de modelos locais ou remotos
- Ajustes de prompts e estratégias por modelo

Nenhum modelo é tratado como definitivo.

---

## Open Source

Este projeto é open source e aceita contribuições da comunidade.

Contribuições podem incluir código, documentação, sugestões de arquitetura, testes ou novos conectores de modelos.

---

## Aviso Legal

Este projeto destina-se exclusivamente a fins educacionais e de pesquisa em segurança da informação.

O uso das informações ou ferramentas geradas para atividades ilegais é de responsabilidade exclusiva do usuário.




