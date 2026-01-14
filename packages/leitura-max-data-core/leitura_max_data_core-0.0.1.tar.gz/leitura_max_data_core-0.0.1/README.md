# Maxlib

Biblioteca com funções aplicadas a rotina do cientista de dados na Maxpar

## Como usar

Instale com:

```
pip install maxlib
```

Use no seu código:

```
from maxlib import
```

## Como funciona?

Quando inicia-se um projeto, muitas das funções iniciais de pré-processamente e leitura são compartilhados em diversos projetos, para isso
os principais tratamentos serão simplificados em funções mais simples de serem chamadas a fim de dar aceleridade nos momentos iniciais dos projetos.

Importe a função `leitura_snowflake`

``` 
>>> from maxlib import leitura_snowflake
```

Por padrão leitura_snowflake retorna `Dataframe`

```
>>> base_atendimento = leitura_snowflake(consulta='SELECT * FROM report.max_atendimento.rep_custo_mao_obra', email='daniel.antunes@maxpar.com.br)
>>> type(base_atendimento)
Dataframe
``` 


## Licença

Maxpar

## Autores

Daniel Antunes Cordeiros