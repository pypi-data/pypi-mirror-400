# NFSe Nacional - Python SDK

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

SDK Python para integração com a API de emissão de Notas Fiscais de Serviço (NFSe) da Nota Nacional. Este projeto facilita a emissão de NFSe seguindo o padrão nacional, incluindo construção do XML, assinatura digital e comunicação com a API oficial.

## 📋 Índice

- [Características](#-características)
- [Instalação](#-instalação)
- [Uso Rápido](#-uso-rápido)
- [Documentação](#-documentação)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Desenvolvimento](#-desenvolvimento)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)
- [Suporte](#-suporte)

## ✨ Características

- ✅ **Conformidade com XSD**: Geração de XML validado contra o schema oficial
- ✅ **Assinatura Digital**: Suporte a certificados A1 (.pfx) para assinatura XML
- ✅ **Autenticação Automática**: Autenticação via certificado digital (sem necessidade de API keys)
- ✅ **Validação Integrada**: Validação XSD antes do envio
- ✅ **Ambientes Separados**: Suporte para produção restrita e produção real
- ✅ **Testes Automatizados**: Suite completa de testes com validação XSD
- ✅ **Type Hints**: Código totalmente tipado para melhor experiência de desenvolvimento
- ✅ **Documentação Completa**: Exemplos e documentação detalhada

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Certificado digital A1 (.pfx) válido
- Arquivos XSD da especificação (disponíveis em `schemas/`)

### Instalação via pip

```bash
pip install -r requirements.txt
```

### Instalação para Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/mupisystems/nfse_nacional.git
cd nfse_nacional

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

## 💡 Uso Rápido

### Exemplo Básico

```python
from src.nfse.emissor import NFSeEmissor
from src.nfse.api_client import Ambiente
from src.nfse.models import DPS, Prestador, Tomador, Servico, Endereco, Tributo
from decimal import Decimal
from datetime import datetime

# 1. Configure o emissor
emissor = NFSeEmissor(
    pfx_path="caminho/para/certificado.pfx",
    pfx_password="senha_do_certificado",
    ambiente=Ambiente.PRODUCAO_RESTRITA  # ou Ambiente.PRODUCAO_REAL
)

# 2. Crie os dados do prestador
prestador = Prestador(
    cpf_cnpj="12345678000190",
    inscricao_municipal="123456",
    optante_simples_nacional=True,
    op_simp_nac=3,  # ME/EPP
    reg_apuracao_sn=1,
    p_tot_trib_sn=Decimal("15.00")
)

# 3. Crie os dados do tomador
tomador = Tomador(
    cpf_cnpj="98765432000100",
    razao_social="Cliente Exemplo Ltda"
)

# 4. Crie os dados do serviço
servico = Servico(
    codigo_servico="1401",
    descricao="Desenvolvimento de software",
    valor_servico=Decimal("1000.00"),
    codigo_municipio="3550308"  # Código IBGE
)

# 5. Crie o DPS
dps = DPS(
    prestador=prestador,
    tomador=tomador,
    servicos=[servico],
    numero_rps="100000000000001",
    serie_rps="00001",
    data_emissao=datetime.now(),
    c_loc_emi="3550308"  # Código IBGE do município emissor
)

# 6. Emita a nota fiscal
resultado = emissor.emitir_nota(dps, validate_xml=True)
print(f"Nota emitida: {resultado}")
```

### Exemplo Completo

Consulte o arquivo [`examples/exemplo_basico.py`](examples/exemplo_basico.py) para um exemplo completo e comentado com todos os campos disponíveis.

## 📚 Documentação

### Componentes Principais

#### NFSeEmissor
Classe principal que orquestra todo o fluxo de emissão:
- Construção do XML do DPS
- Assinatura digital com certificado A1
- Envio para a API da Nota Nacional

#### XMLBuilder
Constrói o XML do DPS conforme o schema XSD oficial:
```python
from src.nfse.xml_builder import XMLBuilder

builder = XMLBuilder(xsd_path="schemas/DPS_v1.00.xsd")
xml = builder.build_dps_xml(dps, validate=True)
```

#### Modelos de Dados
- `DPS`: Declaração de Prestação de Serviço
- `Prestador`: Dados do prestador (emissor)
- `Tomador`: Dados do tomador (cliente)
- `Servico`: Dados do serviço prestado
- `Tributo`: Informações de tributação
- `Endereco`: Dados de endereço

### Fluxo de Emissão

1. **Construção do XML**: Monta o XML da Declaração de Prestação de Serviço (DPS) com todos os dados necessários
2. **Assinatura Digital**: Assina o XML com certificado digital A1 (.pfx)
3. **Validação XSD**: Valida o XML assinado contra o schema oficial (opcional)
4. **Envio para API**: Envia o XML comprimido (gzip) e codificado (base64) para a API

## 📁 Estrutura do Projeto

```
nfse_nacional/
├── src/
│   └── nfse/              # Módulo principal
│       ├── __init__.py
│       ├── models.py      # Modelos de dados
│       ├── xml_builder.py # Construtor de XML
│       ├── signer.py      # Assinatura digital
│       ├── api_client.py  # Cliente HTTP
│       ├── emissor.py     # Classe principal
│       └── config.py      # Configurações
├── tests/                  # Testes automatizados
│   ├── test_xml_builder.py
│   ├── test_client.py
│   └── conftest.py
├── examples/              # Exemplos de uso
│   └── exemplo_basico.py
├── schemas/               # Arquivos XSD
│   ├── DPS_v1.00.xsd
│   └── tiposComplexos_v1.00.xsd
├── requirements.txt       # Dependências
├── pyproject.toml        # Configuração do projeto
└── README.md
```

## 🛠️ Desenvolvimento

### Executando os Testes

```bash
# Todos os testes
pytest tests/

# Com cobertura de código
pytest tests/ --cov=src --cov-report=html

# Apenas testes de validação XML
pytest tests/test_xml_builder.py -v

# Com output detalhado
pytest tests/ -v -s
```

### Validação XSD

Os testes validam automaticamente o XML gerado contra o schema XSD oficial:
- ✅ Estrutura do XML
- ✅ Elementos obrigatórios
- ✅ Tipos de dados
- ✅ Valores permitidos
- ✅ Geração correta do ID do DPS

### Formatação de Código

Usamos `ruff` para linting e formatação (substitui black e flake8):
```bash
# Instalar ruff
pip install ruff

# Formatar código
ruff format src/ tests/ examples/

# Verificar linting
ruff check src/ tests/ examples/

# Formatar e verificar linting
ruff check --fix src/ tests/ examples/
```

## 🤝 Contribuindo

Contribuições são muito bem-vindas! Este é um projeto open source e estamos abertos a melhorias, correções e novas funcionalidades.

**📖 Leia nosso [Guia de Contribuição](CONTRIBUTING.md) para detalhes completos.**

### Formas de Contribuir

- 🐛 **Reportar bugs**: Use o [template de bug report](https://github.com/mupisystems/nfse_nacional/issues/new?template=bug_report.md)
- 💡 **Sugerir funcionalidades**: Use o [template de feature request](https://github.com/mupisystems/nfse_nacional/issues/new?template=feature_request.md)
- 💻 **Contribuir com código**: Veja o [Guia de Contribuição](CONTRIBUTING.md)
- 📝 **Melhorar documentação**: Corrija erros ou adicione exemplos
- 🧪 **Adicionar testes**: Aumente a cobertura de testes
- 🔍 **Revisar código**: Ajude a revisar Pull Requests

### Processo Rápido

1. **Fork** o projeto
2. **Crie uma branch** (`git checkout -b feature/MinhaFeature`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. **Push** para a branch (`git push origin feature/MinhaFeature`)
5. **Abra um Pull Request**

### Áreas que Precisam de Contribuição

- 🔍 Melhorias na validação XSD
- 📝 Documentação adicional e exemplos
- 🧪 Mais casos de teste
- 🌐 Suporte a outros formatos/cenários
- 🐛 Correção de bugs
- ⚡ Otimizações de performance

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 💬 Suporte

- 📖 **Documentação**: Consulte os exemplos em `examples/`
- 🐛 **Bugs**: Reporte em [Issues](https://github.com/mupisystems/nfse_nacional/issues)
- 💡 **Sugestões**: Abra uma [Issue](https://github.com/mupisystems/nfse_nacional/issues) com a tag `enhancement`
- 📧 **Contato**: [Seu email ou link de contato]

## 🙏 Agradecimentos

Agradecemos a todos os contribuidores que ajudam a melhorar este projeto!

---

**Nota**: Este projeto não é oficialmente afiliado à Nota Nacional ou à Receita Federal. É uma implementação open source da comunidade para facilitar a integração com a API oficial.
