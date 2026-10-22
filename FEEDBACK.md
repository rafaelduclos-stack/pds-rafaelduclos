# Feedback das Aulas 01 e 02

A Aula 01 ainda está incompleta e a Aula 02 não pode ser conferida até corrigir as rotas. A rota de busca de pet está escrita como `/pets/<int:pet.id>`, mas o parâmetro precisa ser um nome, por exemplo `pet_id`; assim como está, o app não sobe. Depois disso, faltam o filtro por dono, POST, PUT e DELETE de pets. Confere tudo pelo `requisicoes.http` e mantém as respostas do contrato.
