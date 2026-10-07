# 🎯 Simulacetam - Orquestrador de Testes Simulados

O **Simulacetam** é um orquestrador interativo de simulados para terminal Linux/Ubuntu, voltado para preparação em concursos públicos e conhecimentos gerais. O sistema adota a metodologia clássica da banca **Cebraspe/Cespe** (onde uma questão errada anula uma certa), incluindo recursos modernos como revisão pedagógica de erros, placares criptografados contra adulteração e sistema de progressão de experiência (XP).

---

## ✨ Principais Funcionalidades

- **📚 Detecção Automática de Conteúdo**:
  - Reconhece e lista automaticamente todos os arquivos `.csv` presentes no diretório raiz como temas selecionáveis (ex: `gta5.csv`, `pln.csv`).
  - Permite adicionar novos temas a qualquer momento apenas inserindo novos arquivos `.csv`.

- **🎲 Sorteio Inteligente sem Repetição**:
  - Seleciona aleatoriamente a quantidade de questões definida na configuração, garantindo que não haja perguntas repetidas na mesma rodada.

- **⚖️ Regra de Pontuação (Estilo Cebraspe)**:
  - **Acerto**: `+1` ponto
  - **Erro**: `-1` ponto
  - **Pulo**: `0` pontos (nem ganha nem perde)

- **📝 Revisão Pedagógica Pós-Simulado**:
  - Mostra ao final um resumo estatístico detalhado.
  - Lista separadamente todas as questões que o usuário **errou** (mostrando a afirmação, a resposta assinalada e o gabarito oficial).
  - Lista separadamente todas as questões que o usuário **pulou** (com o gabarito oficial).

- **🔒 Placar Seguro Anti-Fraude (`.dat`)**:
  - Cada tema possui seu próprio arquivo de ranking (`<tema>_ranking.dat`).
  - Utiliza assinatura digital **HMAC-SHA256** combinada com compressão binária. Caso o usuário tente editar sua pontuação diretamente no arquivo com um editor de texto, o programa detecta a violação e rejeita o arquivo adulterado.

- **⭐ Sistema de Gamificação (XP Acumulado)**:
  - Controle individual de experiência por usuário (`<tema>_xp.dat`).
  - Acumula os pontos líquidos conquistados em cada simulado finalizado para cada nickname.

- **⚙️ Configuração Flexível (`simulado.cfg`)**:
  - Define o número padrão de questões por simulado.
  - Pode ser modificado tanto manualmente no arquivo quanto diretamente pelo menu interativo.

---

## 🕹️ Teclas de Controle Durante o Simulado

Ao responder cada pergunta no terminal, utilize as seguintes opções:

| Tecla | Ação |
| :---: | :--- |
| `V` ou `v` | Marcar sentença como **Verdadeira** |
| `F` ou `f` | Marcar sentença como **Falsa** |
| `P` ou `p` | **Pular** questão (não pontua nem desconta) |
| `0` | **Cancelar** o teste imediatamente e voltar ao menu principal |

---

## 💻 Requisitos do Sistema

- **Python**: versão `3.8` ou superior (testado e compatível até Python `3.14`).
- **Sistema Operacional**: Linux (Ubuntu, Debian, Fedora, Arch, etc.), macOS ou Windows (via WSL/Terminal).
- **Dependências Externas**: **Nenhuma!** O projeto foi desenvolvido utilizando 100% dos recursos nativos da biblioteca padrão do Python (`json`, `hmac`, `hashlib`, `zlib`, `random`, `glob`, etc.).

---

## 🚀 Como Executar

Clone o repositório ou navegue até a pasta do projeto e utilize uma das opções:

```bash
# Opção 1: Executando diretamente pelo interpretador Python
python3 simulado.py

# Opção 2: Executando como script executável
chmod +x simulado.py
./simulado.py

# Opção 3: Utilizando o wrapper Shell Script
chmod +x simulado.sh
./simulado.sh
```

---

## 📖 Como Adicionar Novos Temas de Estudo

Para criar uma nova área de conhecimento, basta criar um novo arquivo `.csv` na mesma pasta do programa.

### Estrutura do CSV:
- **Separador**: Ponto e vírgula (`;`)
- **Colunas**: `afirmação; RESPOSTA`
- **Respostas aceitas**: `V` para verdadeiro ou `F` para falso.

#### Exemplo (`direito_constitucional.csv`):
```csv
A República Federativa do Brasil rege-se nas suas relações internacionais pela prevalência dos direitos humanos; V
É permitido aos municípios a criação de distinções entre brasileiros ou preferências entre si; F
Todos são iguais perante a lei, sem distinção de qualquer natureza; V
```

Ao iniciar o programa, o tema **DIREITO_CONSTITUCIONAL** aparecerá automaticamente na lista de opções!

---

## 🗂️ Estrutura de Arquivos do Projeto

```text
├── simulado.py         # Código-fonte principal (orquestrador, menus e lógica segura)
├── simulado.sh         # Script wrapper em Bash para execução rápida
├── simulado.cfg        # Arquivo de configuração (número de questões por rodada)
├── requirements.txt    # Declaração de dependências (informativo)
├── README.md           # Documentação completa do projeto
├── .gitignore          # Arquivos e diretórios ignorados pelo Git
├── gta5.csv            # Banco de questões sobre GTA V
├── pln-env.csv         # Banco de questões sobre PLN e Ambientes Virtuais
└── pln.csv             # Banco de questões sobre Processamento de Linguagem Natural
```

---

## 🛡️ Mecanismo de Proteção dos Placares (`.dat`)

Diferente de formatos de texto plano que permitem alteração manual de pontuação, o **Simulacetam**:
1. Serializa os registros em formato estruturado.
2. Comprime os dados binários (`zlib`).
3. Gera uma assinatura criptográfica **HMAC-SHA256** combinando uma chave secreta interna com o nome do arquivo.
4. Ao carregar o ranking, recalcula a assinatura. Se houver qualquer discrepância (edição de um único byte), exibe alerta de violação de segurança e bloqueia a leitura de dados adulterados.
