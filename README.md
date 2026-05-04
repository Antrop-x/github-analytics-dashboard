# 📊 Observatório do Trabalho Digital

> Análise crítica da distribuição de visibilidade no ecossistema de código aberto

Interface de leitura da infraestrutura do GitHub como sistema de produção simbólica e material.

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

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas clara com separação de responsabilidades:

```
Infrastructure → Services → UI
```

### Camadas

- **Infrastructure**: APIs, storage, configurações
- **Services**: Lógica de negócio, processamento de dados
- **UI**: Interface puramente renderizadora (Pure Rendering Pattern)

## 📦 Estrutura do Projeto

```
├── app.py                      # Ponto de entrada principal
├── config/
│   └── settings.py            # Configurações da aplicação
├── core/
│   └── metrics.py             # Métricas e cálculos
├── data/                      # Dados persistidos
├── infrastructure/
│   ├── base_api.py           # API base
│   └── github_api.py         # API do GitHub
├── models/
│   └── ui_models.py          # Dataclasses para UI
├── services/
│   ├── analysis_service.py   # Serviço de análise
│   ├── interpretation_service.py # Serviço de interpretação
│   ├── pipeline_service.py   # Pipeline de ingestão
│   ├── storage_inspection_service.py # Inspeção de storage
│   └── storage_service.py    # Serviço de storage
├── ui/
│   ├── __init__.py           # Pacote UI
│   ├── components.py         # Componentes reutilizáveis
│   ├── layout.py             # Layout principal
│   ├── sections.py           # Seções da interface
│   ├── theme.py              # Tema visual
│   └── ui.py                 # Funções de compatibilidade
└── tests/                    # Testes automatizados
```

## 🚀 Funcionalidades

### Análise de Repositórios
- Ingestão de dados do GitHub API
- Métricas de desigualdade (Gini, concentração)
- Análise de hegemonia computada
- Interpretações automatizadas

### Storage Inteligente
- Backend primário: Arquivos locais
- Fallback automático para dados mock
- Inspeção de disponibilidade
- Métricas de saúde do storage

### Interface Moderna
- Tema GitHub Dark consistente
- Componentes reutilizáveis
- Layout responsivo
- Pure Rendering Pattern

## 🛠️ Tecnologias

- **Python 3.14+**
- **Streamlit**: Framework web
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações
- **Pytest**: Testes automatizados
- **Requests**: HTTP client

## 📊 Métricas Implementadas

### Desigualdade
- **Coeficiente de Gini**: Mede distribuição de stars
- **Concentração Top 10%**: Participação dos repositórios mais populares
- **Índice de Dominação**: Mede poder de mercado

### Hegemonia
- **Índice de Hegemonia**: Combinação de stars + forks
- **Análise de Segmentos**: Low/Mid/Top performers
- **Interpretações Contextuais**: Alta/Média/Baixa hegemonia

## 🎨 Design System

### Tema Visual
- **Cores**: GitHub Dark palette
- **Tipografia**: Monospace para código, sans-serif para texto
- **Componentes**: Cards padronizados, badges, métricas
- **Responsividade**: Layout adaptável

### Componentes
- `MetricCard`: Métricas formatadas
- `InfoCard`: Informações contextuais
- `StatusBadge`: Estados booleanos
- `ProgressBar`: Barras com labels customizados

## 🧪 Testes

```bash
# Executar todos os testes
python -m pytest tests/ -v

# Executar testes específicos
python -m pytest tests/test_ui_models.py -v
python -m pytest tests/test_storage_inspection.py -v
```

### Cobertura de Testes
- ✅ Modelos de UI (dataclasses)
- ✅ Serviços de inspeção
- ✅ Componentes visuais
- ✅ Integração entre camadas
- ✅ Tratamento de erros

## 🚀 Como Executar

1. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

2. **Configurar ambiente**:
```bash
# Configurar token do GitHub (opcional)
export GITHUB_TOKEN=your_token_here
```

3. **Executar aplicação**:
```bash
streamlit run app.py
```

## 📌 Relatório Geral

Este repositório foi atualizado para consolidar a arquitetura, fortalecer a manutenção e tornar a interface mais robusta.

### Estado Atual do Projeto
- **Arquitetura modular**: separação clara entre `infrastructure`, `services` e `ui`
- **UI desacoplada**: a camada de interface recebe apenas dados prontos para renderização
- **Tipos fortes**: dataclasses em `models/ui_models.py` substituem `Dict[str, Any]`
- **Componentização**: cards e indicadores reutilizáveis garantem consistência visual
- **Testes completos**: 62 testes passando com pytest
- **Ferramentas de qualidade**: suporte para Black, isort, flake8, mypy e pre-commit

### Principais Conquistas
- Refatoração da lógica de storage e inspeção para evitar acoplamento direto na UI
- Correção do bug de referência da variável `heg`
- Implementação correta de barra de progresso com label e estado visual
- Remoção de `st.caption` inválido ou mal utilizado
- Construção de um tema visual consistente baseado em GitHub Dark
- Criação de `dev.py` para tarefas de desenvolvimento e testes

### Resultados Validados
- **62/62 testes passaram**
- **Integração entre camadas comprovada**
- **Importações e objetos principais testados em runtime**
- **Layout e componentes prontos para nova evolução**

## 🔧 Melhorias Recentes

### ✅ Arquitetura Refatorada
- **Separação de Camadas**: Infrastructure → Services → UI
- **Pure Rendering Pattern**: UI completamente passiva
- **Dataclasses Tipadas**: Substituição de `Dict[str, Any]` por estruturas fortes
- **Serviços Intermediários**: Inspeção de storage desacoplada da UI

### ✅ Componentes Reutilizáveis
- **MetricCard**: Métricas formatadas com ícones
- **InfoCard**: Informações contextuais padronizadas
- **ProgressBar Customizada**: Barras com labels e cores dinâmicas
- **StatusBadge**: Estados booleanos consistentes

### ✅ Qualidade de Código
- **62 testes automatizados** cobrindo todas as funcionalidades
- **Linting e formatação**: Black, isort, flake8, mypy
- **Pre-commit hooks**: Validação automática antes de commits
- **Script de desenvolvimento**: `dev.py` para tarefas comuns

### ✅ Tema Visual Consistente
- **GitHub Dark Theme**: Paleta completa e consistente
- **CSS Variables**: Configuração centralizada de cores
- **Componentes Padronizados**: Identidade visual forte
- **Responsividade**: Layout adaptável a diferentes telas

### ✅ Correções de Bugs
- **Variável heg**: Corrigida referência incorreta
- **Barra de progresso**: Implementação correta com labels
- **st.caption inválido**: Removido uso incorreto
- **Acoplamento UI**: Desacoplada dos serviços diretos

## 📈 Desenvolvimento

### Adicionando Novos Componentes

1. **Criar dataclass em `models/ui_models.py`**:
```python
@dataclass
class NewComponent:
    title: str
    data: Any
    # ... propriedades
```

2. **Implementar função em `ui/components.py`**:
```python
def render_new_component(component: NewComponent):
    # Lógica de renderização
    pass
```

3. **Adicionar à seção apropriada em `ui/sections.py`**:
```python
def render_new_section(data):
    render_new_component(data)
```

### Adicionando Novos Testes

1. **Criar arquivo em `tests/test_new_feature.py`**:
```python
class TestNewFeature:
    def test_feature(self):
        # Teste
        pass
```

2. **Executar testes**:
```bash
python -m pytest tests/test_new_feature.py -v
```

### Script de Desenvolvimento

O projeto inclui um script `dev.py` para facilitar tarefas comuns:

```bash
# Configurar ambiente de desenvolvimento
python dev.py setup

# Executar testes
python dev.py test
python dev.py test --coverage

# Verificar qualidade do código
python dev.py lint --all

# Formatar código
python dev.py format

# Executar aplicação
python dev.py run
python dev.py run --port 8502
```

### Comandos Disponíveis
- `setup`: Instalar dependências e configurar pre-commit
- `test`: Executar testes com opções de cobertura
- `lint`: Verificar código com múltiplas ferramentas
- `format`: Formatar código automaticamente
- `run`: Executar aplicação Streamlit
- `install`: Instalar dependências do projeto

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código

- Use `black` para formatação
- Mantenha cobertura de testes alta
- Siga princípios de código limpo e type hints
- Documente funções complexas

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Contato

- Projeto: [GitHub Issues](https://github.com/your-org/github-analytics-dashboard/issues)
- Email: team@github-analytics.com | jhonmaxr017@gmail.com 