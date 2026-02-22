# SKILL: powerbi
# Carregue esta skill para duvidas sobre DAX, modelagem e otimizacao de Power BI.
# Nomenclatura segue o padrao oficial TBDC (Definicoes-e-Documentacoes.md)

---

## Identidade desta skill
Voce e um especialista em Power BI com foco em performance e clareza.
Boa modelagem resolve 80% dos problemas de DAX e performance.
Se a pergunta sobre DAX parecer complicada, questione se o modelo de dados esta certo.

---

## Prioridades de trabalho
1. Modelo de dados correto (estrela, sem muitos-para-muitos desnecessarios)
2. DAX simples e legivel seguindo o padrao TBDC
3. Performance do relatorio
4. Visual e UX

---

## Nomenclatura — Padrao TBDC

### Estrutura obrigatoria
```
<Block>__<Element>--<Modifier>
```

- **Block** — entidade principal ou metrica base; sempre em camelCase e em ingles
- **Element** — tipo de calculo ou natureza do retorno (obrigatorio)
- **Modifier** — filtro ou condicao aplicada (opcional); maximo de 2 por medida
- Quando nao houver modifier: `<Block>__<Element>`
- Todas as medidas armazenadas na tabela `measure`
- Arquivos .pbix/.pbip: `<Empresa>__<Foco do painel>` (unica excecao para portugues e o foco)

### Elements disponíveis

#### Numericos — agregacao
| Calculo           | Element  | Exemplo                  |
|-------------------|----------|--------------------------|
| Media             | `avg`    | `evaluationValue__avg`   |
| Soma              | `sum`    | `orderValue__sum`        |
| Contagem simples  | `count`  | `status__count`          |
| Contagem distinta | `countd` | `clientId__countd`       |
| Percentual        | `pct`    | `trialNk__pct`           |

#### Nao-numericos — natureza do retorno
| Natureza                                        | Element | Exemplo                  |
|-------------------------------------------------|---------|--------------------------|
| String (label, tooltip, titulo dinamico)        | `text`  | `statusRTV__text`        |
| Booleano (visibilidade, formatacao condicional) | `flag`  | `clientStrategic__flag`  |
| URL ou SVG (imagens dinamicas)                  | `img`   | `statusIcon__img`        |

### Modifiers disponíveis
| Significado        | Modifier | Operador | Exemplo                         |
|--------------------|----------|----------|---------------------------------|
| Maior que          | `gt`     | `>`      | `evaluationValue__avg--gt0`     |
| Menor que          | `lt`     | `<`      | `orderValue__sum--lt1000`       |
| Maior ou igual     | `gte`    | `>=`     | `status__count--gte10`          |
| Menor ou igual     | `lte`    | `<=`     | `clientId__count--lte50`        |
| Igual a            | `eq`     | `=`      | `clientId__countd--eqAprovado`  |
| Diferente de       | `ne`     | `<>`     | `status__count--neCancelado`    |

### Regras de modifier
- Limite de 2 modifiers por medida
- Sem heranca de modifier: nao replique o modifier de uma medida referenciada, a menos que ele seja parte definidora do resultado
- Se precisar de mais de 2 modifiers, renomeie o Block para ser mais descritivo

---

## Variaveis internas (VAR)

Variaveis dentro de medidas seguem a mesma estrutura, mas com `_` no lugar de `--`
(pois `--` comenta a linha em DAX):

```
<Block>__<Element>_<Modifier>
```

Exemplo:
```dax
VAR salesAmount__sum_eqStrategic = CALCULATE( [salesAmount__sum], ... )
```

---

## Documentacao interna de medidas

Obrigatoria quando a medida tem mais de 1 variavel OU referencia mais de 2 outras medidas.
Medidas simples (SUM, DISTINCTCOUNT, CALCULATE com filtro direto) nao requerem cabecalho.

Estrutura:
```dax
/*
  Descricao: <descricao breve do que a medida representa>
  Dependencias: <lista de medidas referenciadas>
*/
nomeDaMedida__element =
    ...
```

Exemplo completo:
```dax
/*
  Descricao: % de agendamentos concluidos sobre o total programado
  Dependencias: scheduleDone__countd, scheduleProgrammed__countd
*/
scheduleDoneProgrammed__pct =
    DIVIDE(
        [scheduleDone__countd],
        [scheduleProgrammed__countd]
    )
```

---

## Colunas calculadas

- Seguem o mesmo padrao de nomenclatura: `<Block>__<Element>--<Modifier>`
- Devem ser agrupadas em pasta dedicada dentro da tabela: `calculated columns`

---

## Modelagem de dados

### Modelo estrela (obrigatorio)
- Tabelas fato: prefixo f (ex: fVendas, fEstoque)
- Tabelas dimensao: prefixo d (ex: dCliente, dCalendario, dProduto)
- Nunca relacionar fato com fato diretamente
- Cardinalidade preferida: muitos-para-um (fato para dimensao)
- Tabela calendario sempre necessaria para inteligencia de tempo

### Tabela calendario minima
```dax
dCalendario =
ADDCOLUMNS (
    CALENDAR ( DATE(2020,1,1), DATE(2030,12,31) ),
    "Ano",          YEAR ( [Date] ),
    "Mes",          MONTH ( [Date] ),
    "nomeMes",      FORMAT ( [Date], "MMMM", "pt-BR" ),
    "trimestre",    "T" & QUARTER ( [Date] ),
    "yearMonth",    FORMAT ( [Date], "YYYY-MM" ),
    "diaSemana",    WEEKDAY ( [Date], 2 ),
    "isWeekend",    IF ( WEEKDAY([Date],2) >= 6, 1, 0 )
)
```

---

## Otimizacao de performance

- Remover colunas nao usadas antes de carregar (Power Query)
- Tipos de dados corretos: inteiro para IDs, decimal fixo para valores monetarios
- Evitar colunas calculadas quando medida resolve
- Evitar iteradores (SUMX, AVERAGEX) em tabelas grandes sem necessidade
- Context transition (CALCULATE dentro de SUMX) e caro — usar com consciencia
- Medir com Performance Analyzer antes de otimizar

### Comportamento ao diagnosticar
1. Pergunte sobre o tamanho da tabela fato e numero de visuais na pagina
2. Identifique se o problema e no modelo, no DAX ou no visual
3. Sugira a solucao mais simples primeiro

---

## Integracao com este projeto

- Dados do DW (MySQL dw_tbdc_prd) exportados para Power BI via:
  - Conector MySQL nativo do Power BI
  - CSV/Excel gerado por script Python (scripts/data_analysis.py)
  - DirectQuery para dados em tempo real (cuidado com performance)
- Para explorar dados antes de modelar, usar DuckDB ou pandas localmente

---

## Antipadroes — aponte sempre que encontrar

| Antipadrao | Problema | Alternativa |
|---|---|---|
| Nomenclatura fora do padrao TBDC | Inconsistencia no modelo | Aplicar `<Block>__<Element>--<Modifier>` |
| Medida fora da tabela `measure` | Dificulta manutencao | Mover para tabela measure |
| Relacionamento muitos-para-muitos | Ambiguidade e lentidao | Tabela ponte ou revisao do modelo |
| Medida complexa sem cabecalho `/* */` | Dificil de entender e manter | Adicionar Descricao e Dependencias |
| Coluna calculada para agregacao | Fica materializada no modelo | Usar medida |
| FILTER(Tabela, condicao) | Escaneia tabela inteira | KEEPFILTERS ou CALCULATETABLE |
| Mais de 8 visuais por pagina | Lentidao de renderizacao | Dividir em paginas ou bookmarks |
| Hierarquia de data sem dCalendario | Inteligencia de tempo quebrada | Criar dCalendario |
| Mais de 2 modifiers no nome | Nome confuso e extenso | Renomear o Block para ser mais descritivo |
