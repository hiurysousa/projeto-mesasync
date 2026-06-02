# 🌊 MesaSync: Autoatendimento Inteligente via QR Code

> **Projeto desenvolvido para a Trilha de Formação Sebrae Supernova (Temporada 2026)**
> Sistema de gerenciamento de pedidos e cardápio digital focado na transformação e letramento digital de microempreendedores do setor de gastronomia praiana (barracas de praia e restaurantes de orla).

---

## 🎯 Proposta de Valor & Contexto

O **MesaSync** nasce para resolver o gargalo de atendimento físico enfrentado por estabelecimentos de alta rotatividade em regiões litorâneas (foco inicial: Aracati/CE). O sistema elimina a barreira do "atendimento demorado" e otimiza a logística de garçons por meio de uma experiência de autoatendimento fluida e inclusiva.

### 🚀 O Diferencial de UX: Zero Atrito
Diferente de sistemas tradicionais que exigem downloads pesados ou cadastros burocráticos, o MesaSync foca na agilidade:
1. O cliente aponta a câmera para o **QR Code** fixado na mesa.
2. A aplicação identifica automaticamente o **ID da mesa** e abre o cardápio interativo.
3. **Sem necessidade de Login:** O cliente monta seu carrinho de forma 100% anônima, informando apenas o seu nome no ato do fechamento do pedido. 
4. O pedido é processado e disparado diretamente para a cozinha/painel administrativo e via integração orquestrada para o WhatsApp do estabelecimento.

---

## 🛠️ Stack Tecnológica

O projeto foi estruturado utilizando uma arquitetura robusta, segura e escalável baseada no ecossistema Python:

* **Back-end & Lógica de Negócios:** [Django Framework](https://www.djangoproject.com/) (Arquitetura robusta com baterias inclusas).
* **Persistência de Dados:** ORM nativo do Django com Banco de Dados Relacional.
* **Segurança:** Mascaramento e proteção de credenciais administrativas via algoritmo criptográfico nativo do Django.
* **Front-end:** HTML5, CSS3, JavaScript estruturado (utilizando armazenamento temporário de sessão com `sessionStorage` para persistência do carrinho).

---

## 📂 Organização do Repositório

O repositório adota as boas práticas do ecossistema Django, separando o código-fonte de configurações locais de ambiente:

```text
📂 mesasync/                              # Diretório raiz do repositório
├── .gitignore                           # Filtro do Git para ignorar arquivos locais (.venv, db.sqlite3)
├── README.md                            # Documentação principal e guia de execução do projeto
├── requirements.txt                     # Lista de dependências do ecossistema Python (Django, Pillow, etc.)
├── .venv/                               # Ambiente virtual isolado com as bibliotecas instaladas
│
└── 📂 src/                              # Diretório raiz do código-fonte do projeto Django
    ├── manage.py                        # Utilitário de linha de comando para gerenciamento do Django
    │
    ├── 📂 core/                         # Módulo central de configurações globais do projeto
    │   ├── __init__.py
    │   ├── settings.py                  # Definições de segurança, apps instalados e caminhos de mídia
    │   ├── urls.py                      # Roteamento global (mapeia o admin e inclui o app restaurante)
    │   └── wsgi.py / asgi.py            # Interfaces de servidores web para implantação (deploy)
    │
    └── 📂 restaurante/                  # Aplicativo funcional (Regras de negócio do MesaSync)
        ├── 📂 migrations/               # Histórico de evolução e estruturação do banco de dados
        │
        ├── 📂 templates/                # Diretório de arquivos de visualização (Front-end)
        │   └── 📂 cliente/
        │       └── mesasync_cardapio.html # Interface mobile-first do cardápio digital do cliente
        │
        ├── admin.py                     # Registro das models para exibição no painel Django Admin
        ├── apps.py                      # Configurações estruturais do aplicativo restaurante
        ├── models.py                    # Esquema de banco de dados (Estabelecimento, Mesa, Categoria, Produto, Pedido)
        ├── tests.py                     # Scripts dedicados a testes automatizados unitários e de integração
        ├── urls.py                      # Rotas internas do app (Ex: tratamento do QR Code e envio de pedidos)
        └── views.py                     # Lógica de controle (Intermediação entre o banco de dados e o HTML)