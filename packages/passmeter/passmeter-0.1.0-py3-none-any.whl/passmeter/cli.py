import argparse
import re
import csv # New 
from tabulate import tabulate
from collections import Counter
from colorama import Fore, Style, init
from zxcvbn import zxcvbn # New
import math

# Inicializar Colorama para exibição colorida no terminal
init(autoreset=True)

# Banner ASCII para exibir na execução do script
def exibir_banner():
    banner = """
 ▄▄▄· ▄▄▄· .▄▄ · .▄▄ · • ▌ ▄ ·. ▄▄▄ .▄▄▄▄▄▄▄▄ .▄▄▄  
▐█ ▄█▐█ ▀█ ▐█ ▀. ▐█ ▀. ·██ ▐███•▀▄.▀·•██  ▀▄.▀·▀▄ █·
 ██▀·▄█▀▀█ ▄▀▀▀█▄▄▀▀▀█▄▐█ ▌▐▌▐█·▐▀▀•▄ ▐█.\u00b7▐▀▀•▄▐▀▀▄ 
▐█•·▐█ ▪▐▌▐█▄▪▐█▐█▄▪▐███ ██▌▐█\u2022▐█▄▄▌ ▐█\u2022·▐█▄▄▌▐█•█▌
.▀    ▀  ▀  ▀▀▀▀  ▀▀▀▀ ▀▀  █\u2022▀▀▀ ▀▀▀  ▀▀▀  ▀▀▀ .▀  ▀
"""
    print(Fore.CYAN + banner)

# Função para calcular a forca de uma senha
def analisar_senha_zxcvbn(senha, user_inputs=[]):
    resultado = zxcvbn(senha, user_inputs=user_inputs)
    
    # Cria uma lista garantindo que 'warning' esteja dentro de colchetes
    feedback_list = [resultado['feedback']['warning']] + resultado['feedback']['suggestions']
    
    return {
        'senha': senha,
        'score': resultado['score'],
        'crack_time': resultado['crack_times_display']['offline_slow_hashing_1e4_per_second'],
        # Filtra strings vazias e junta com vírgula
        'feedback': ", ".join([f for f in feedback_list if f])
    }

# Função para avaliar a força da senha
def avaliar_forca_senha(senha):
    """
    Avalia a força da senha com base no tamanho e na diversidade de caracteres.
    """
    tamanho = len(senha)
    tipos_caracteres = 0

    # Verifica a presença de diferentes tipos de caracteres
    if re.search(r'[a-z]', senha):
        tipos_caracteres += 1
    if re.search(r'[A-Z]', senha):
        tipos_caracteres += 1
    if re.search(r'[0-9]', senha):
        tipos_caracteres += 1
    if re.search(r'[!@#$%^&*()_+\-=[\]{};\\:\"|,.<>\/?]', senha):
        tipos_caracteres += 1

    # Avalia a senha com base em seu comprimento e diversidade de caracteres
    if tamanho <= 6 or tipos_caracteres == 1:
        return "Muito Fraca"
    elif 7 <= tamanho <= 10 and tipos_caracteres >= 2:
        return "Fraca"
    elif 11 <= tamanho <= 16 and tipos_caracteres >= 2:
        return "Média"
    elif 17 <= tamanho <= 20 and tipos_caracteres >= 3:
        return "Forte"
    elif tamanho >= 21 and tipos_caracteres == 4:
        return "Muito Forte"
    else:
        return "Indeterminada"

# Função para verificar se a senha está na lista "rockyou"
def verificar_rockyou(senha, lista_rockyou):
    """
    Verifica se a senha está presente na lista de senhas populares "rockyou.txt".
    """
    return senha in lista_rockyou

# Função para carregar a lista de senhas populares (rockyou.txt)
def carregar_rockyou(arquivo_rockyou):
    try:
        with open(arquivo_rockyou ,'r', encoding = 'utf-8', errors='ignore') as file:
            return {linha.strip() for linha in file}
    except FileNotFoundError:
        return set

# Função para ler o arquivo de senhas e analisar cada senha
def analisar_senhas(arquivo_senhas, lista_rockyou):
    """
    Lê o arquivo de senhas e avalia cada senha.
    Para cada senha, calcula sua força, forca e verifica se está na lista de senhas populares.
    """
    senhas = []
    with open(arquivo_senhas, 'r') as file:
        for linha in file:
            senha = linha.strip()
            if senha:  # Verifica se a linha não está vazia
                senhas.append(senha)

    analise = []
    for senha in senhas:
        esta_na_rockyou = verificar_rockyou(senha, lista_rockyou)
        dados_zxcvbn = analisar_senha_zxcvbn(senha)

        analise.append({
            'senha': senha, 
            'forca': dados_zxcvbn['score'], # Agora é numérico (0-4)
            'tempo': dados_zxcvbn['crack_time'],
            'rockyou': esta_na_rockyou
        })
    return analise
# Função para gerar um sumário das senhas analisadas e exibir em tabelas
def gerar_sumario(analise):
    """
    Gera um sumário das senhas analisadas, incluindo detalhes como senhas mais curtas,
    mais longas, mais fortes, e senhas repetidas.
    """
    total_senhas = len(analise)
    senhas_repetidas = [item for item, count in Counter([a['senha'] for a in analise]).items() if count > 1]
    senha_mais_curta = min(analise, key=lambda x: len(x['senha']))
    senha_mais_longa = max(analise, key=lambda x: len(x['senha']))
    forca_media = sum(a['forca'] for a in analise) / total_senhas

    # Tabelas de resumo
    tabela_resumo = [
        ["Total de Senhas", total_senhas],
        ["forca Média das Senhas", f"{forca_media:.2f}"]
    ]

    tabela_detalhes = [
        ["Senha Mais Curta", senha_mais_curta['senha'], len(senha_mais_curta['senha'])],
        ["Senha Mais Longa", senha_mais_longa['senha'], len(senha_mais_longa['senha'])],
        ["Senha Menos Forte", min(analise, key=lambda x: x['forca'])['senha']],
        ["Senha Mais Forte", max(analise, key=lambda x: x['forca'])['senha']]
    ]

    # Exibir tabela de resumo
    print(Fore.CYAN + "\nResumo das Senhas:")
    print(tabulate(tabela_resumo, headers=["Descrição", "Valor"], tablefmt="grid"))

    # Exibir tabela de detalhes
    print(Fore.CYAN + "\nDetalhes das Senhas:")
    print(tabulate(tabela_detalhes, headers=["Descrição", "Senha", "Comprimento"], tablefmt="grid"))

    # Exibir tabela de senhas analisadas
    tabela_senhas = [
        [
            "*" * len(a['senha']), # Oculta a senha visualmente
            a['forca'], 
            a['tempo'], 
            "Sim" if a['rockyou'] else "Não"
        ] for a in analise
    ]
    print(Fore.CYAN + "\nDetalhes das Senhas Analisadas:")
    print(tabulate(tabela_senhas, headers=["Senha (Oculta)", "Score (0-4)", "Tempo Quebra", "RockYou"], tablefmt="grid"))

    # Exibir tabela de senhas repetidas
    if senhas_repetidas:
        print(Fore.YELLOW + "\nSenhas Repetidas:")
        tabela_repetidas = [[senha] for senha in senhas_repetidas]
        print(tabulate(tabela_repetidas, headers=[Fore.YELLOW + "Senha"], tablefmt="grid"))
    else:
        print(Fore.GREEN + "\nNenhuma senha repetida encontrada.")
def main():
    """
    Função principal que lida com os argumentos passados ao script e executa as análises
    de senhas e gera os relatórios.
    """
    parser = argparse.ArgumentParser(description="Analisador de Senhas")
    parser.add_argument("arquivo_senhas", help="Arquivo contendo as senhas a serem analisadas")
    parser.add_argument("arquivo_rockyou", help="Arquivo contendo a lista de senhas populares (rockyou.txt)")
    args = parser.parse_args()

    # Carregar a lista de senhas populares
    lista_rockyou = carregar_rockyou(args.arquivo_rockyou)

    # Analisar as senhas do arquivo fornecido
    analise = analisar_senhas(args.arquivo_senhas, lista_rockyou)

    # Gerar e exibir o sumário das senhas analisadas
    gerar_sumario(analise)

if __name__ == "__main__":
    exibir_banner()
    main()