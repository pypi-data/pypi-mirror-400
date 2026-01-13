# mtcli-vwap
  
Plugin do **mtcli** para cálculo da **VWAP (Volume Weighted Average Price)** a partir de dados intraday do **MetaTrader 5**.
  
O plugin foi projetado para uso em **linha de comando**, com saída textual simples e compatível com leitores de tela (NVDA, JAWS), seguindo uma arquitetura organizada em **MVC**.
  
---
  
## O que é VWAP?
  
A **VWAP (Volume Weighted Average Price)** é o preço médio ponderado pelo volume negociado.  
Ela é amplamente utilizada por traders institucionais como referência de preço justo intraday.
  
Fórmula:
  
```

VWAP = Σ(preço × volume) / Σ(volume)

````
  
---
  
## Funcionalidades
  
- Cálculo de VWAP intraday
- Suporte a múltiplos timeframes (M1 até H4)
- Integração direta com o MetaTrader 5
- Uso de contexto seguro de conexão (`mt5_conexao`)
- Saída textual simples (ideal para terminal)
- Arquitetura MVC (Model / Controller / View)
  
---
  
## 📦 Instalação
  
### Pré-requisitos
  
- Python 3.10+
- MetaTrader 5 instalado e configurado
- Conta e terminal abertos no MT5
- Biblioteca `MetaTrader5` funcionando
  
### Instalação via pip (modo desenvolvimento)
  
```bash
pip install -e .
````
  
Ou:
  
```bash
pip install mtcli-vwap
```
  
---
    
## Uso
  
Comando principal:
  
```bash
mtcli vwap
```
  
### Opções disponíveis
  
| Opção             | Descrição                              |
| ----------------- | -------------------------------------- |
| `-s`, `--symbol`  | Código do ativo (ex: WDOF26, WINF26)   |
| `-m`, `--minutes` | Timeframe em minutos                   |
| `-l`, `--limit`   | Número de barras utilizadas no cálculo |
  
### Exemplo
  
```bash
mtcli vwap --symbol WDOF26 --minutes 5 --limit 100
```
  
---
  
## Timeframes suportados
  
* M1, M2, M3, M4
* M5, M6, M10, M12, M15, M20, M30
* H1, H2, H3, H4
  
Caso um timeframe não seja informado corretamente, o padrão é **M1**.
  
---
  
## Arquitetura
  
```
mtcli_vwap/
├── cli.py         # Interface de linha de comando
├── controller.py  # Orquestração da lógica
├── model.py       # Cálculo da VWAP (dados + regra)
├── view.py        # Saída textual
├── conf.py        # Configurações padrão
```
  
---
  
## Observações importantes
  
* O cálculo usa **datetime em UTC**, conforme padrão do MetaTrader 5.
* A VWAP é calculada apenas com dados **intraday**.
* Caso o símbolo não esteja disponível no MT5, o comando retorna erro e não quebra a execução.
  
---
  
## Conexão com o MetaTrader 5
  
A conexão é gerenciada via:
  
```python
with mt5_conexao():
    ...
```
  
Isso garante:
  
* Inicialização segura
* Finalização correta
* Evita múltiplas conexões simultâneas
  
---
  
## Público-alvo
  
* Traders discricionários
* Scalpers e day traders
* Desenvolvedores de ferramentas CLI para trading
* Usuários que analisam VWAP, Market Profile e Volume Profile
  
---
  
## Licença
  
Este projeto é licenciado sob a **GNU General Public License v3.0 (GPL-3.0)**.
  
Você é livre para usar, modificar e redistribuir este software, desde que qualquer trabalho derivado também seja distribuído sob a mesma licença.
  
---
  
## Autor
  
**Valmir França**
📧 [vfranca3@gmail.com](mailto:vfranca3@gmail.com)
  
---
  
## Projetos relacionados
  
* `mtcli`
* `mtcli-market`
  
