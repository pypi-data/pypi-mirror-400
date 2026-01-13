# Contribuindo

Este documento descreve as convenções de commits e como habilitar validação localmente.

1. Mensagens de commit

- Todas as mensagens de commit devem ser escritas em Português Brasileiro (pt-BR).
- Use prefixos semânticos no cabeçalho do commit: `feat`, `fix`, `test`, `chore`, `docs`, `refactor`, `perf`, `ci`, `build`, `revert`.
- Formato recomendado do cabeçalho:
  - `<tipo>(escopo-opcional): descrição curta em pt-BR`
  - Exemplo: `fix(cli): corrigir parsing de argumentos`

2. Habilitar hooks locais

Para validar automaticamente a mensagem de commit, recomendamos ativar os hooks do Git definidos em `.githooks`:

```powershell
git config core.hooksPath .githooks
```

Depois de habilitar, o hook `commit-msg` irá validar o formato do cabeçalho do commit

3. Modelo de commit

Você pode usar o template `.gitmessage` fornecido neste repositório como guia ao escrever mensagens de commit.
