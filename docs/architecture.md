# Arquitetura - GitHub Analytics Dashboard

## Visão Geral

O GitHub Analytics Dashboard é uma aplicação web para análise da produção simbólica e material no ecossistema GitHub, implementada com arquitetura em camadas para separação clara de responsabilidades.

## Princípios Arquiteturais

### 🎯 Separação de Responsabilidades
- **UI (Apresentação)**: Renderização pura, sem lógica de negócio
- **Serviços (Domínio)**: Lógica de negócio isolada
- **Infraestrutura (Técnico)**: Comunicação externa e persistência
- **Core (Compartilhado)**: Utilitários e métricas

### 📋 Contratos Entre Camadas
```python
@dataclass
class AnalysisResult:
    """Contrato principal entre camadas"""
    metrics: Dict[str, Any]      # Métricas calculadas
    interpretation: Dict[str, Any]  # Interpretação estruturada
    confidence: float            # Confiança da análise
    metadata: Dict[str, Any]     # Metadados
```

### 🧹 UI Puramente Renderizadora
- **NÃO faz**: interpretação, cálculo, inferência
- **SOMENTE faz**: renderização baseada em contratos
- **Recebe**: `AnalysisResult` como fonte única de verdade

## Estrutura de Diretórios

```
├── main.py                 # 🚀 Entrypoint único
├── app.py                  # 📱 UI Streamlit (legacy)
├── config/
│   └── settings.py         # ⚙️ Configurações centralizadas
├── core/
│   ├── __init__.py
│   └── metrics.py          # 📊 Algoritmos de métricas
├── infrastructure/
│   ├── __init__.py
│   ├── base_api.py         # 🔌 Contratos de API
│   └── github_api.py       # 🌐 Cliente GitHub
├── models/
│   └── models.py           # 📋 Schemas de dados
├── services/
│   ├── __init__.py
│   ├── pipeline_service.py     # 🔄 Orquestração de dados
│   ├── interpretation_service.py # 🧠 Lógica interpretativa
│   └── storage_service.py      # 💾 Abstração de armazenamento
├── ui/
│   └── ui.py               # 🎨 Componentes de renderização
├── data/                   # 📁 Dados externos (não versionados)
├── tests/                  # ✅ Testes automatizados
└── docs/                   # 📚 Documentação
```

## Fluxo de Dados

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   main.py   │───▶│ PipelineService │───▶│InterpretationSvc│
│             │    │                 │    │                 │
│  Inicializa │    │ Coleta dados    │    │ Interpreta      │
│  dependências│    │ brutos          │    │ dados          │
└─────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────┐    ┌─────────────────┐                   │
│ GitHub      │◀───│  GitHubApi     │◀──────────────────┘
│ Analytics   │    │  Client        │
│ UI          │    │                 │
│             │    │ Comunicação     │
│ Renderiza   │    │ HTTP + Auth     │
└─────────────┘    └─────────────────┘
```

## Componentes Principais

### main.py - Entrypoint Único
```python
def main():
    settings = Settings()
    pipeline_service = PipelineService(settings)
    interpretation_service = InterpretationService()
    ui = GitHubAnalyticsUI(pipeline_service, interpretation_service, settings)
    ui.run()
```

### PipelineService
- **Responsabilidade**: Orquestração de coleta de dados
- **Isola**: Lógica de cache, rate limiting, validação
- **Retorna**: Dados brutos + metadados

### InterpretationService
- **Responsabilidade**: Toda lógica interpretativa
- **Isola**: Classificações, heurísticas, síntese narrativa
- **Retorna**: `AnalysisResult` estruturado

### GitHubAnalyticsUI
- **Responsabilidade**: Renderização pura
- **Recebe**: `AnalysisResult` como contrato
- **Não faz**: Cálculos, interpretações, inferências

### StorageService
- **Responsabilidade**: Abstração de armazenamento de dados
- **Backends**: Arquivos locais, mock data, futuro DB/API
- **Estratégia**: Primário → Fallback → Mock
- **Isola**: Persistência de dados da aplicação

## Padrões de Design

### Injeção de Dependências
```python
# main.py injeta dependências
ui = GitHubAnalyticsUI(
    pipeline_service=pipeline_service,
    interpretation_service=interpretation_service,
    settings=settings
)
```

### Contratos Explícitos
```python
@dataclass
class AnalysisResult:
    """Fonte única de verdade para UI"""
    metrics: Dict[str, Any]
    interpretation: Dict[str, Any]
    confidence: float
    metadata: Dict[str, Any]
```

### Separação Vertical
- Cada serviço tem responsabilidade única
- Comunicação via contratos bem definidos
- Testabilidade independente

## Qualidade e Manutenibilidade

### ✅ Testes Automatizados
- Cobertura completa de serviços
- Testes de integração entre camadas
- CI/CD com pytest + linting

### 📏 Padrões de Código
- Type hints obrigatórios
- Black para formatação
- Pylint para qualidade

### 🔒 Segurança
- Bearer token authentication
- Validação de entrada
- Rate limiting

### Por que Storage Layer?
- **Externalização**: Dados fora do repositório
- **Flexibilidade**: Múltiplos backends (arquivo, DB, API)
- **Testabilidade**: Mock data para desenvolvimento
- **Escalabilidade**: Preparado para diferentes necessidades

## Decisões Arquiteturais

### Por que Separação UI/Serviços?
- **Manutenibilidade**: Lógica de negócio isolada da apresentação
- **Testabilidade**: Serviços testáveis independentemente da UI
- **Reutilização**: Serviços podem ser usados por diferentes UIs

### Por que Contratos Estruturados?
- **Type Safety**: Dataclasses com type hints
- **Clareza**: Interface explícita entre camadas
- **Evolução**: Mudanças controladas via contratos

### Por que Entrypoint Único?
- **Simplicidade**: Um ponto de entrada claro
- **Configuração**: Inicialização centralizada
- **Debugging**: Fluxo de inicialização rastreável

### Por que Storage Abstração?
- **Independência**: Aplicação não conhece detalhes de persistência
- **Flexibilidade**: Fácil troca entre backends
- **Desenvolvimento**: Mock data acelera desenvolvimento/testes

## Métricas de Qualidade

- **Cobertura de Testes**: >90%
- **Complexidade Ciclomática**: <10 por função
- **Tempo de Build**: <2 minutos
- **Taxa de Sucesso de Testes**: 100%

## Roadmap Evolutivo

### ✅ Concluído
- **Storage Layer**: Abstração completa com backends múltiplos
- **EntryPoint Único**: `main.py` como ponto de entrada principal
- **Interpretação Isolada**: `interpretation_service.py` com lógica separada
- **Contratos Estruturados**: `AnalysisResult` entre camadas
- **UI Purificada**: Renderização pura baseada em contratos

### Próximas Etapas
1. **CI/CD Expansion**: pytest automático, lint, coverage obrigatório
2. **API REST**: Exposição de serviços via HTTP
3. **Database Backend**: PostgreSQL/MySQL para storage
4. **Microserviços**: Separação física de componentes
5. **Event Streaming**: Processamento assíncrono

### Débitos Técnicos Identificados
- Dados em `data/` devem ser externalizados
- Cache limitado a memória (poderia usar Redis)
- UI acoplada ao Streamlit (poderia ser genérica)

---

*Documentação gerada automaticamente - Manter atualizada com mudanças arquiteturais*</content>
<parameter name="filePath">c:\Users\JHON\github-analytics-dashboard\docs\architecture.md