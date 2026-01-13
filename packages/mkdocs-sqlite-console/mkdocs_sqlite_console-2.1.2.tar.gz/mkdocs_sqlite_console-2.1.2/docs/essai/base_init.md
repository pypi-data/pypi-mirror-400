## Vérifie que l'utilisation des arguments base et init ensemble fonctionne

le code de init ajoute 3 entrées aux 3 venant de tests.db :

```sql
{{ sqlide(
    titre="base + init",
    base="bases/test.db",
    init="init_base.sql",
    sql="sql/code.sql"
)}}
```


{{ sqlide(
    titre="base + init",
    base="bases/test.db",
    init="init_base.sql",
    sql="sql/code.sql"
)}}