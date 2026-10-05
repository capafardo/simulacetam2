#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SIMULACETAM - Orquestrador de Testes Simulados
Sistema de simulados para concursos públicos e conhecimentos gerais com
perguntas no estilo Certo/Errado (Cebraspe/Cespe), placar seguro e sistema de XP.
"""

import os
import sys
import glob
import json
import zlib
import hmac
import hashlib
import random
from datetime import datetime

CONFIG_FILE = "simulado.cfg"
DEFAULT_QUESTIONS_COUNT = 20
HMAC_SECRET = b"simulacetam_secure_storage_key_2026_@#!"

# Cores ANSI para formatação elegante no terminal
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def pause():
    input(f"\n{Color.CYAN}Pressione [ENTER] para continuar...{Color.RESET}")

# ==============================================================================
# 1. GERENCIAMENTO DE CONFIGURAÇÃO (simulado.cfg)
# ==============================================================================

def load_config():
    """Lê o número de questões da primeira linha de simulado.cfg."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_QUESTIONS_COUNT)
        return DEFAULT_QUESTIONS_COUNT
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            num = int(first_line)
            if num <= 0:
                raise ValueError("Número de questões deve ser maior que zero.")
            return num
    except Exception:
        # Se houver erro de leitura ou valor inválido, restaura padrão
        save_config(DEFAULT_QUESTIONS_COUNT)
        return DEFAULT_QUESTIONS_COUNT

def save_config(num_questions):
    """Grava o número de questões na primeira linha de simulado.cfg."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(f"{num_questions}\n")

# ==============================================================================
# 2. ARMAZENAMENTO SEGURO (.dat) COM PROTEÇÃO CONTRA ADULTERAÇÃO
# ==============================================================================

MAGIC_HEADER = b"SIMULADAT\x01"

def _compute_hmac(data_bytes, filename):
    # Assinatura baseada no conteúdo, segredo e nome do arquivo (evita trocar arquivos entre si)
    key = HMAC_SECRET + filename.encode("utf-8")
    return hmac.new(key, data_bytes, hashlib.sha256).digest()

def save_secure_dat(filepath, payload_obj):
    """Salva dados em formato binário comprimido e assinado criptograficamente."""
    data_json = json.dumps(payload_obj, ensure_ascii=False).encode("utf-8")
    compressed = zlib.compress(data_json, level=9)
    signature = _compute_hmac(compressed, os.path.basename(filepath))
    
    with open(filepath, "wb") as f:
        f.write(MAGIC_HEADER)
        f.write(signature)  # 32 bytes SHA-256
        f.write(compressed)

def load_secure_dat(filepath, default_value):
    """Carrega dados e verifica a integridade. Rejeita alterações manuais."""
    if not os.path.exists(filepath):
        return default_value
    
    try:
        with open(filepath, "rb") as f:
            header = f.read(len(MAGIC_HEADER))
            if header != MAGIC_HEADER:
                print(f"{Color.RED}[ERRO DE SEGURANÇA] Arquivo '{filepath}' foi adulterado ou possui formato inválido!{Color.RESET}")
                return default_value
            
            saved_sig = f.read(32)
            compressed = f.read()
            
            expected_sig = _compute_hmac(compressed, os.path.basename(filepath))
            if not hmac.compare_digest(saved_sig, expected_sig):
                print(f"{Color.RED}[VIOLAÇÃO DETECTADA] O arquivo '{filepath}' foi editado manualmente ou corrompido!{Color.RESET}")
                print(f"{Color.RED}A assinatura criptográfica não confere. Dados bloqueados.{Color.RESET}")
                return default_value
            
            data_json = zlib.decompress(compressed).decode("utf-8")
            return json.loads(data_json)
    except Exception as e:
        print(f"{Color.RED}[ERRO] Falha ao processar arquivo seguro '{filepath}': {e}{Color.RESET}")
        return default_value

def get_theme_base(csv_filename):
    """Retorna o nome base do tema (ex: 'gta5' para 'gta5.csv')."""
    return os.path.splitext(os.path.basename(csv_filename))[0]

def get_ranking_file(theme_base):
    return f"{theme_base}_ranking.dat"

def get_xp_file(theme_base):
    return f"{theme_base}_xp.dat"

# ==============================================================================
# 3. LEITURA E VALIDAÇÃO DE QUESTÕES
# ==============================================================================

def list_available_themes():
    """Localiza todos os arquivos .csv disponíveis na pasta."""
    csv_files = sorted(glob.glob("*.csv"))
    return csv_files

def load_questions_from_csv(csv_path):
    """
    Carrega as perguntas do arquivo CSV.
    Estrutura esperada: afirmação; SENTENÇA (V/F)
    """
    questions = []
    if not os.path.exists(csv_path):
        return questions
    
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.rsplit(";", 1)
            if len(parts) != 2:
                continue
            
            statement = parts[0].strip()
            answer = parts[1].strip().upper()
            
            if answer in ("V", "F"):
                questions.append({
                    "id": line_num,
                    "statement": statement,
                    "answer": answer
                })
    return questions

# ==============================================================================
# 4. EXECUÇÃO DO SIMULADO
# ==============================================================================

def run_simulation(theme_file, num_questions_config):
    questions_pool = load_questions_from_csv(theme_file)
    theme_base = get_theme_base(theme_file)
    
    if not questions_pool:
        clear_screen()
        print(f"{Color.RED}Não foi possível encontrar questões válidas no arquivo '{theme_file}'.{Color.RESET}")
        pause()
        return
    
    total_available = len(questions_pool)
    num_to_ask = min(num_questions_config, total_available)
    
    # Sorteio aleatório sem repetição dentro da mesma rodada
    selected_questions = random.sample(questions_pool, num_to_ask)
    
    acertos = 0
    erros = 0
    puladas = 0
    
    erros_detalhes = []
    puladas_detalhes = []
    
    for idx, q in enumerate(selected_questions, 1):
        while True:
            clear_screen()
            print(f"{Color.CYAN}{'=' * 65}{Color.RESET}")
            print(f"{Color.BOLD}SIMULADO: {theme_base.upper()}{Color.RESET} (Questão {idx} de {num_to_ask})")
            print(f"{Color.CYAN}{'=' * 65}{Color.RESET}\n")
            
            print(f"{Color.WHITE}{q['statement']}{Color.RESET}\n")
            print(f"{Color.CYAN}{'-' * 65}{Color.RESET}")
            print(f"Opções: [{Color.GREEN}V{Color.RESET}]erdadeiro | [{Color.RED}F{Color.RESET}]also | [{Color.YELLOW}P{Color.RESET}]ular | [{Color.MAGENTA}0{Color.RESET}] Sair e cancelar")
            
            user_input = input(f"{Color.BOLD}Sua resposta: {Color.RESET}").strip().upper()
            
            if user_input == "0":
                clear_screen()
                print(f"{Color.YELLOW}Teste cancelado pelo usuário.{Color.RESET}")
                print("Nenhuma pontuação ou progresso foi computado.")
                pause()
                return
            
            if user_input in ("V", "F"):
                if user_input == q["answer"]:
                    acertos += 1
                else:
                    erros += 1
                    erros_detalhes.append({
                        "num": idx,
                        "statement": q["statement"],
                        "user_answer": user_input,
                        "correct_answer": q["answer"]
                    })
                break
            elif user_input == "P":
                puladas += 1
                puladas_detalhes.append({
                    "num": idx,
                    "statement": q["statement"],
                    "correct_answer": q["answer"]
                })
                break
            else:
                # Entrada inválida, repete a questão
                continue
    
    # Cálculo da pontuação líquida
    pontos_liquidos = acertos - erros
    
    # Tela de Resultados
    clear_screen()
    print(f"{Color.CYAN}{'=' * 65}{Color.RESET}")
    print(f"{Color.BOLD}{Color.WHITE}          RESULTADO DO SIMULADO: {theme_base.upper()}{Color.RESET}")
    print(f"{Color.CYAN}{'=' * 65}{Color.RESET}\n")
    print(f"Total de questões respondidas: {num_to_ask}")
    print(f"{Color.GREEN}Acertos : {acertos}  (+{acertos} pts){Color.RESET}")
    print(f"{Color.RED}Erros   : {erros}  (-{erros} pts){Color.RESET}")
    print(f"{Color.YELLOW}Puladas : {puladas}  (0 pts){Color.RESET}")
    print(f"{Color.CYAN}{'-' * 65}{Color.RESET}")
    
    cor_pontos = Color.GREEN if pontos_liquidos > 0 else (Color.RED if pontos_liquidos < 0 else Color.YELLOW)
    print(f"{Color.BOLD}Pontuação Final: {cor_pontos}{pontos_liquidos} ponto(s){Color.RESET}\n")
    
    # Exibir questões que errou
    if erros_detalhes:
        print(f"\n{Color.RED}{Color.BOLD}--- QUESTÕES QUE VOCÊ ERROU ({len(erros_detalhes)}) ---{Color.RESET}")
        for item in erros_detalhes:
            print(f"\n{Color.BOLD}[Q{item['num']}]{Color.RESET} {item['statement']}")
            print(f"   Sua resposta: {Color.RED}{item['user_answer']}{Color.RESET} | Gabarito oficial: {Color.GREEN}{item['correct_answer']}{Color.RESET}")
    else:
        print(f"\n{Color.GREEN}Parabéns! Você não errou nenhuma questão.{Color.RESET}")
    
    # Exibir questões que pulou
    if puladas_detalhes:
        print(f"\n{Color.YELLOW}{Color.BOLD}--- QUESTÕES QUE VOCÊ PULOU ({len(puladas_detalhes)}) ---{Color.RESET}")
        for item in puladas_detalhes:
            print(f"\n{Color.BOLD}[Q{item['num']}]{Color.RESET} {item['statement']}")
            print(f"   Gabarito oficial: {Color.GREEN}{item['correct_answer']}{Color.RESET}")
    
    print(f"\n{Color.CYAN}{'=' * 65}{Color.RESET}")
    
    # Pergunta para salvar no placar
    while True:
        salvar = input("\nDeseja salvar o resultado no placar? (S/N): ").strip().upper()
        if salvar in ("S", "SIM"):
            nickname = ""
            while not nickname:
                nickname = input("Digite seu Nickname para o ranking: ").strip()
                if not nickname:
                    print(f"{Color.RED}O nickname não pode ser vazio.{Color.RESET}")
            
            # Salvar no Ranking
            ranking_file = get_ranking_file(theme_base)
            ranking_data = load_secure_dat(ranking_file, default_value=[])
            
            registro = {
                "nickname": nickname,
                "pontos": pontos_liquidos,
                "acertos": acertos,
                "erros": erros,
                "puladas": puladas,
                "total": num_to_ask,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            ranking_data.append(registro)
            save_secure_dat(ranking_file, ranking_data)
            
            # Atualizar XP do Jogador (Item 13)
            # O XP acumula o número de pontos conquistados em cada tentativa
            xp_file = get_xp_file(theme_base)
            xp_data = load_secure_dat(xp_file, default_value={})
            xp_atual = xp_data.get(nickname, 0)
            novo_xp = xp_atual + pontos_liquidos
            xp_data[nickname] = novo_xp
            save_secure_dat(xp_file, xp_data)
            
            print(f"\n{Color.GREEN}Resultado gravado com sucesso no ranking protegido!{Color.RESET}")
            print(f"Nickname: {Color.BOLD}{nickname}{Color.RESET} | XP nesta partida: {pontos_liquidos} | XP Total acumulado: {Color.BOLD}{novo_xp}{Color.RESET}")
            pause()
            break
        elif salvar in ("N", "NAO", "NÃO"):
            print(f"\n{Color.YELLOW}Resultado não salvo.{Color.RESET}")
            pause()
            break

# ==============================================================================
# 5. VISUALIZAÇÃO DE RANKING E XP
# ==============================================================================

def select_theme_menu(prompt_title):
    """Submenu para escolha de tema."""
    themes = list_available_themes()
    if not themes:
        clear_screen()
        print(f"{Color.RED}Nenhum arquivo CSV encontrado na pasta corrente!{Color.RESET}")
        pause()
        return None
    
    while True:
        clear_screen()
        print(f"{Color.CYAN}{'=' * 65}{Color.RESET}")
        print(f"{Color.BOLD}{prompt_title}{Color.RESET}")
        print(f"{Color.CYAN}{'=' * 65}{Color.RESET}\n")
        
        for idx, t in enumerate(themes, 1):
            base = get_theme_base(t)
            print(f"[{Color.GREEN}{idx}{Color.RESET}] {base.upper()} ({t})")
        print(f"\n[{Color.MAGENTA}0{Color.RESET}] Voltar ao menu principal")
        print(f"{Color.CYAN}{'=' * 65}{Color.RESET}")
        
        choice = input(f"{Color.BOLD}Selecione uma opção: {Color.RESET}").strip()
        if choice == "0":
            return None
        
        try:
            val = int(choice)
            if 1 <= val <= len(themes):
                return themes[val - 1]
        except ValueError:
            pass

def view_ranking():
    theme = select_theme_menu("VISUALIZAR PLACAR / RANKING DE PONTUAÇÃO")
    if not theme:
        return
    
    theme_base = get_theme_base(theme)
    ranking_file = get_ranking_file(theme_base)
    ranking = load_secure_dat(ranking_file, default_value=[])
    
    clear_screen()
    print(f"{Color.CYAN}{'=' * 75}{Color.RESET}")
    print(f"{Color.BOLD}             RANKING DE PONTUAÇÕES: {theme_base.upper()}{Color.RESET}")
    print(f"{Color.CYAN}{'=' * 75}{Color.RESET}")
    
    if not ranking:
        print(f"\n{Color.YELLOW}Nenhum registro encontrado no placar deste tema.{Color.RESET}\n")
    else:
        # Ordena por pontos decrescente
        sorted_ranking = sorted(ranking, key=lambda x: (x.get("pontos", 0), x.get("acertos", 0)), reverse=True)
        
        print(f"{Color.BOLD}{'POS':<4} {'NICKNAME':<18} {'PONTOS':<8} {'ACERTOS':<8} {'ERROS':<7} {'DATA/HORA'}{Color.RESET}")
        print("-" * 75)
        for pos, item in enumerate(sorted_ranking[:20], 1):
            cor = Color.GREEN if pos == 1 else (Color.YELLOW if pos in (2, 3) else Color.WHITE)
            print(f"{cor}{pos:<4} {item.get('nickname', 'Anônimo'):<18} {item.get('pontos', 0):<8} {item.get('acertos', 0):<8} {item.get('erros', 0):<7} {item.get('data', '-')}{Color.RESET}")
        print("-" * 75)
        print(f"Arquivo seguro: {ranking_file}")
    
    pause()

def view_xp_board():
    theme = select_theme_menu("VISUALIZAR QUADRO DE EXPERIÊNCIA (XP)")
    if not theme:
        return
    
    theme_base = get_theme_base(theme)
    xp_file = get_xp_file(theme_base)
    xp_data = load_secure_dat(xp_file, default_value={})
    
    clear_screen()
    print(f"{Color.CYAN}{'=' * 55}{Color.RESET}")
    print(f"{Color.BOLD}       QUADRO DE EXPERIÊNCIA (XP): {theme_base.upper()}{Color.RESET}")
    print(f"{Color.CYAN}{'=' * 55}{Color.RESET}")
    
    if not xp_data:
        print(f"\n{Color.YELLOW}Nenhum registro de XP encontrado neste tema.{Color.RESET}\n")
    else:
        sorted_xp = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)
        print(f"{Color.BOLD}{'POS':<4} {'NICKNAME':<25} {'XP TOTAL'}{Color.RESET}")
        print("-" * 55)
        for pos, (nick, total_xp) in enumerate(sorted_xp[:20], 1):
            cor = Color.GREEN if pos == 1 else (Color.YELLOW if pos in (2, 3) else Color.WHITE)
            print(f"{cor}{pos:<4} {nick:<25} {total_xp} XP{Color.RESET}")
        print("-" * 55)
        print(f"Arquivo seguro: {xp_file}")
    
    pause()

# ==============================================================================
# 6. CONFIGURAÇÃO DE QUANTIDADE DE QUESTÕES
# ==============================================================================

def configure_questions_count():
    current = load_config()
    while True:
        clear_screen()
        print(f"{Color.CYAN}{'=' * 65}{Color.RESET}")
        print(f"{Color.BOLD}CONFIGURAÇÃO: QUANTIDADE DE QUESTÕES POR SIMULADO{Color.RESET}")
        print(f"{Color.CYAN}{'=' * 65}{Color.RESET}\n")
        print(f"Quantidade configurada atualmente: {Color.BOLD}{current}{Color.RESET}")
        print(f"Arquivo de configuração: {Color.CYAN}{CONFIG_FILE}{Color.RESET}\n")
        print(f"Digite a nova quantidade (ex: 10, 20, 30) ou [{Color.MAGENTA}0{Color.RESET}] para voltar:")
        
        user_input = input(f"{Color.BOLD}> {Color.RESET}").strip()
        if user_input == "0":
            return
        
        try:
            val = int(user_input)
            if val > 0:
                save_config(val)
                clear_screen()
                print(f"{Color.GREEN}Configuração atualizada com sucesso para {val} questões!{Color.RESET}")
                pause()
                return
            else:
                print(f"{Color.RED}Informe um valor numérico positivo.{Color.RESET}")
                pause()
        except ValueError:
            print(f"{Color.RED}Valor inválido! Digite apenas números inteiros.{Color.RESET}")
            pause()

# ==============================================================================
# 7. MENU PRINCIPAL
# ==============================================================================

def main_menu():
    while True:
        clear_screen()
        current_num_questions = load_config()
        
        print(f"{Color.CYAN}{'=' * 65}{Color.RESET}")
        print(f"{Color.BOLD}{Color.WHITE}          SIMULACETAM - ORQUESTRADOR DE SIMULADOS{Color.RESET}")
        print(f"{Color.CYAN}{'=' * 65}{Color.RESET}")
        print(f"Configuração ativa: {Color.YELLOW}{current_num_questions} questões por simulado{Color.RESET}")
        print(f"{Color.CYAN}{'-' * 65}{Color.RESET}")
        print(f"[{Color.GREEN}1{Color.RESET}] Iniciar Simulado")
        print(f"[{Color.GREEN}2{Color.RESET}] Visualizar Placar / Ranking")
        print(f"[{Color.GREEN}3{Color.RESET}] Visualizar Quadro de Experiência (XP)")
        print(f"[{Color.GREEN}4{Color.RESET}] Alterar quantidade de questões por simulado")
        print(f"[{Color.MAGENTA}0{Color.RESET}] Sair")
        print(f"{Color.CYAN}{'=' * 65}{Color.RESET}")
        
        choice = input(f"{Color.BOLD}Opção desejada: {Color.RESET}").strip()
        
        if choice == "1":
            selected_theme = select_theme_menu("INICIAR SIMULADO - ESCOLHA O TEMA")
            if selected_theme:
                run_simulation(selected_theme, current_num_questions)
        elif choice == "2":
            view_ranking()
        elif choice == "3":
            view_xp_board()
        elif choice == "4":
            configure_questions_count()
        elif choice == "0":
            clear_screen()
            print(f"{Color.GREEN}Obrigado por utilizar o Simulacetam. Bons estudos!{Color.RESET}\n")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}Execução interrompida pelo usuário.{Color.RESET}\n")
        sys.exit(0)
