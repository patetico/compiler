Compilador usado na matéria de Compiladores na UFMT.

---

Este projeto foi feito usando python 3.9. Seu funcionamento é exemplificado em `main.py`.  

Autômato do tokenizador:

![tokenizador](/dados/tokenizer.png)

Os estados são mapeados aos seguintes tipos:

| Estado | Tipo       |
|:------:|------------|
| s1     | INTEGER    |
| s3     | REAL       |
| s4     | IDENTIFIER |
| s5     | SYMBOL     |
| s8     | WHITESPACE |
