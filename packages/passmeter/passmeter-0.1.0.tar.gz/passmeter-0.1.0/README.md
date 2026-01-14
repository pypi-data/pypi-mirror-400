# Avaliador de Força de Senhas (PassMeter)

Ferramenta de auditoria de senhas que utiliza a biblioteca `zxcvbn` para análise heurística, estimativa de tempo de quebra e feedback de segurança. Suporta verificação contra wordlists populares.

## Funcionalidades

- **Análise Heurística (zxcvbn)**: Classificação de força (Score 0-4) e estimativa de tempo para quebra offline.
- **Feedback de Segurança**: Sugestões e avisos sobre vulnerabilidades específicas encontradas na senha.
- **Verificação em Wordlist**: Checagem opcional em listas como `rockyou.txt`.
- **OpSec (Privacidade)**: As senhas são exibidas mascaradas (`******`) no terminal por padrão.
- **Exportação de Dados**: Gera relatórios detalhados em formato CSV.

## Instalação

Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```
Uso
Análise Básica

Executa apenas a análise heurística do zxcvbn:

```bash
python passmeter.py senhas.txt
```
Com Wordlist e Exportação CSV

Verifica contra o RockYou e salva o resultado em arquivo:
```bash

python passmeter.py senhas.txt --rockyou rockyou.txt --csv relatorio.csv
```
Exibir Senhas 

Força a exibição das senhas em texto claro no terminal (use com cautela):
```bash

python passmeter.py senhas.txt --show
```
Argumentos

    arquivo_senhas: Caminho do arquivo contendo as senhas (uma por linha).

    --rockyou [ARQUIVO]: (Opcional) Caminho para a wordlist de senhas vazadas.

    --csv [ARQUIVO]: (Opcional) Caminho para salvar a saída em formato CSV.

    --show: (Opcional) Desativa o mascaramento de senhas no terminal.

