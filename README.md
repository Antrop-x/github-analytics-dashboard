# 📊 GitHub Analytics Dashboard

> Análise crítica da distribuição de visibilidade no ecossistema de código aberto

## 🎥 Demonstração

[![Assista ao vídeo](https://img.youtube.com/vi/f3LHmchQ9II/0.jpg)](https://www.youtube.com/watch?v=f3LHmchQ9II)

## 🧠 Sobre o Projeto

Este projeto apresenta um dashboard interativo desenvolvido com Python e Streamlit para análise de dados da API do GitHub.
Diferente de abordagens tradicionais, o objetivo não é identificar "os melhores repositórios", mas investigar:

> **Como a visibilidade é distribuída no código aberto?**

A análise considera que métricas como *stars* funcionam como sinais sociais — frequentemente refletindo exposição acumulada, e não necessariamente qualidade técnica.

## ⚖️ Problema

- Visibilidade não é distribuída de forma equitativa
- Projetos populares acumulam mais atenção
- Projetos menores permanecem invisíveis

👉 Questão central:
> **Estamos medindo qualidade ou visibilidade?**

## 🎯 Objetivo

- Coletar dados da API do GitHub
- Processar métricas
- Construir visualizações interativas
- Permitir análise exploratória
- Estimular leitura crítica de dados

## 🏗️ Estrutura do Projeto

```bash
.
├── app.py                  # Ponto de entrada do app
├── core/                   # Lógica de negócio (métricas, cálculos)
├── services/               # Pipeline e processamento de dados
├── infrastructure/         # Integração com API do GitHub
├── config/                 # Configurações centralizadas
├── models/                 # Modelos de domínio (renomeado para domain.py)
├── ui/                     # Interface do usuário
├── tests/                  # Testes automatizados
├── data/                   # Dados locais (exemplo e histórico)
├── assets/                 # Imagens e recursos visuais
├── .github/workflows/      # CI/CD com GitHub Actions
├── requirements.txt        # Dependências
├── setup.py               # Configuração do pacote
├── pytest.ini             # Configuração de testes
├── Makefile               # Automação de tarefas
└── README.md
```

## 🔄 Arquitetura e Fluxo

### Fluxo de Dependências (Unidirecional)
```
ui → services → core → infrastructure
    ↓
 config (usado por todas as camadas)
```

### Pipeline de Dados
```
GitHub API → infrastructure → services → core → ui → Streamlit App
```

---

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.9+
- Git

### Instalação

```bash
# Clone o repositório
git clone https://github.com/your-org/github-analytics-dashboard.git
cd github-analytics-dashboard

# Instale as dependências
pip install -r requirements.txt

# Para desenvolvimento (opcional)
make install-dev
```

### Executar

```bash
# Via Makefile
make run

# Ou diretamente
streamlit run app.py
```

### Testes

```bash
# Executar todos os testes
make test

# Com cobertura
make test-coverage

# Com saída verbosa
make test-verbose
```

### Desenvolvimento

```bash
# Verificar qualidade do código
make check

# Formatar código
make format

# Verificar tipos (opcional)
make type-check
```

## ⚙️ Tecnologias

* **Python 3.9+**
* **Streamlit** - Interface web
* **Pandas** - Processamento de dados
* **Plotly** - Visualizações
* **Requests** - API HTTP
* **Pytest** - Testes
* **Black** - Formatação
* **Pylint** - Linting
* **MyPy** - Type checking

## ⚡ Funcionalidades

* 🔎 Filtro por linguagem de programação
* 📄 Paginação automática da API
* 📊 Métricas de desigualdade (Gini, concentração)
* 📈 Visualizações interativas
* 🔄 Pipeline de dados automatizado
* 🧪 Testes abrangentes
* 🚀 CI/CD com GitHub Actions

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código

- Use `black` para formatação
- Mantenha cobertura de testes > 80%
- Siga os princípios SOLID
- Documente funções complexas

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Contato

- Projeto: [GitHub Issues](https://github.com/your-org/github-analytics-dashboard/issues)
- Email: team@github-analytics.com