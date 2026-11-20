"""Transforma e cruza respostas JSON das APIs usando SQLite."""

import json # Biblioteca importada para converter dados python em JSON
import sqlite3 # Biblioteca para permitir consultas SQLite.
from typing import Any # importação do Any para variaveis aceitar qualquer tipo de dados.

# Função para transformat dados e retornar uma lista com varios dicionarios.
def transformar_dados(
    cep: str, endereco: dict[str, Any], clima: dict[str, Any]
) -> list[dict[str, Any]]:

   # criando o banco de dados
    conexao = sqlite3.connect(":memory:") # Cria um banco de dados temporario na memoria.
    conexao.row_factory = sqlite3.Row  # Tratamento para buscar coluna pelo nome em vez de apenas posição.

    # Executa o processamento.
    try:
        conexao.execute(
            "CREATE TABLE enderecos (cep TEXT PRIMARY KEY, dados_json TEXT NOT NULL)"
        )
        conexao.execute(
            "CREATE TABLE previsoes (cep TEXT NOT NULL, dados_json TEXT NOT NULL)"
        )

        # Inseção de dados e em caso de conflito com a PK ignora
        conexao.execute(
            "INSERT OR IGNORE INTO enderecos (cep, dados_json) VALUES (?, ?)",
            (cep, json.dumps(endereco, ensure_ascii=False)),
        )
        conexao.execute(
            "INSERT INTO previsoes (cep, dados_json) VALUES (?, ?)",
            (cep, json.dumps(clima, ensure_ascii=False)),
        )

        # Executa o comando SQL dentro do SQLite
        linhas = conexao.execute(
            """
            WITH endereco AS (
                SELECT
                    cep,
                    COALESCE(json_extract(dados_json, '$.localidade'), 'Não informado') AS cidade,
                    COALESCE(json_extract(dados_json, '$.uf'), 'Não informado') AS uf,
                    COALESCE(json_extract(dados_json, '$.bairro'), 'Não informado') AS bairro
                FROM enderecos
            ),
            previsao_aberta AS (
                SELECT
                    p.cep,
                    date(dia.value) AS data_iso,
                    CAST(json_extract(
                        p.dados_json,
                        '$.daily.temperature_2m_min[' || dia.key || ']'
                    ) AS REAL) AS temperatura_minima,
                    CAST(json_extract(
                        p.dados_json,
                        '$.daily.temperature_2m_max[' || dia.key || ']'
                    ) AS REAL) AS temperatura_maxima,
                    CAST(json_extract(
                        p.dados_json,
                        '$.daily.precipitation_sum[' || dia.key || ']'
                    ) AS REAL) AS precipitacao_mm
                FROM previsoes AS p,
                     json_each(json_extract(p.dados_json, '$.daily.time')) AS dia
            ),
            previsao_sem_duplicatas AS (
                SELECT *,
                     ROW_NUMBER() OVER (
                        PARTITION BY cep, data_iso ORDER BY data_iso
                    ) AS numero_linha
                FROM previsao_aberta
            )
            SELECT
                e.cep,
                e.cidade,
                e.uf,
                e.bairro,
                strftime('%d/%m/%Y', p.data_iso) AS data,
                p.temperatura_minima,
                p.temperatura_maxima,
                COALESCE(p.precipitacao_mm, 0.0) AS precipitacao_mm,
                ROUND(p.temperatura_maxima - p.temperatura_minima, 1) AS amplitude_termica,
                CASE
                    WHEN COALESCE(p.precipitacao_mm, 0.0) > 0 THEN 'com chuva'
                    ELSE 'sem chuva'
                END AS condicao_chuva
            FROM endereco AS e
            JOIN previsao_sem_duplicatas AS p ON p.cep = e.cep
            WHERE p.numero_linha = 1
            ORDER BY p.data_iso
            """
        ).fetchall()

        return [dict(linha) for linha in linhas]
    # Fecha a conexão 
    finally:
        conexao.close()
