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
├── .gitignore           # Filtro para impedir o envio de arquivos locais (.venv, db.sqlite3, caches)
├── README.md            # Documentação principal do projeto
├── requirements.txt     # Dependências e bibliotecas do ecossistema Python utilizadas
├── .venv/               # Ambiente virtual isolado (ignorado pelo Git)
└── src/                 # Diretório raiz do código-fonte Django
    ├── manage.py        # Utilitário de linha de comando do Django
    ├── core/            # Módulo central de configurações do projeto (settings, urls)
    └── restaurante/     # App principal (Regras de negócio: mesas, categorias, produtos e pedidos)