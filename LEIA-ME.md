# Plaza Wallet

Painel local em Python para o dinheiro do **MILF's Plaza**, com interface escura, reposição automática e escolha de idioma ao abrir.

[English](README.md) · [Español](LEEME.md)

## Idiomas

Escolha **Português (Brasil)**, **English** ou **Español** na abertura. Sua última escolha fica pré-selecionada. Use **Idioma** na lateral para trocar sem reiniciar o jogo. Botões, instruções, estados, erros do aplicativo e números seguem o idioma escolhido. As janelas nativas de arquivos e os detalhes dos erros do sistema seguem o idioma do Windows. A tradução é do painel, não dos textos do jogo.

## Instalar e usar

A versão **EXE para Windows não precisa de Python instalado**. Extraia o ZIP Windows e abra **PlazaWallet.exe**. O conector e as traduções estão incluídos no executável. Deixe o EXE numa pasta com permissão de escrita para lembrar preferências.

Para executar o código-fonte, use Windows e **Python 3.10+ com Tkinter**, sem pacotes pip adicionais. As duas versões precisam de uma instalação Ren'Py que aceite scripts `.rpy` adicionais.

1. Extraia o download. Abra **PlazaWallet.exe**, ou **Iniciar.bat** / **Start.bat** na versão em código-fonte.
2. Escolha o idioma e clique em **Continuar**.
3. Clique em **Escolher pasta** e selecione a instalação que contém `game` e `renpy`.
4. Com o jogo fechado, clique em **Instalar conector**.
5. Abra o jogo, carregue uma partida e clique em **Ler jogo** no painel.
6. `money` é selecionada automaticamente. Escolha o saldo mínimo e clique em **Ativar reposição ∞**. Aguarde a confirmação do jogo.

O padrão é **3.000**, porque a versão **18b22** reduz saldos maiores a esse limite. O conector repõe o piso após blocos Python e nas interações, com verificações periódicas. A ativação e o saldo foram confirmados numa partida real de 18b22, Ren'Py 8.3.7. A reposição após gastos é coberta por testes com motor simulado. Outras versões não foram verificadas.

## Preferências e remoção

Idioma, pasta e saldo ficam em **settings.local.json**, junto do aplicativo. Esse arquivo é ignorado pelo Git. `settings.example.json` mostra o formato; não é necessário editá-lo. A pasta do app deve permitir escrita para lembrar preferências. Se for somente leitura, o painel continua funcionando e informa a falha ao salvar preferências.

**Desativar** interrompe a reposição e mantém o saldo. Fechar só o painel mantém a reposição até fechar o jogo. Ao reiniciar o jogo, ela começa desativada.

O painel não edita arquivos de save diretamente. Saves feitos pelo jogo após a ativação podem conter o dinheiro alterado; carregue um save anterior para voltar ao valor antigo. Para remover, feche o jogo e clique em **Remover**. O conector é movido para `plaza_wallet_backups`, fora de `game`. Os scripts originais não são substituídos.

## Diagnóstico

- Sem conexão: confira a pasta, instale o conector e reinicie completamente o jogo.
- Sem saldo: carregue uma partida e clique em **Ler jogo**. Somente `money` aparece.
- Erro de escrita: o conector precisa de permissão para gravar em `game/plaza_wallet`.
- Erro na abertura após instalar: feche o jogo e use **Remover**, ou mova `zz_plaza_wallet.rpy` e `zz_plaza_wallet.rpyc` para fora de `game`.
- Atualização do conector exige reiniciar o jogo. Atualização apenas das traduções exige reabrir só o painel.

## Desenvolvimento e GitHub

Execute `python plaza_wallet.py` para abrir. Na pasta do projeto, execute `python -m unittest discover -v` para rodar os testes. Os testes de interface exigem sessão gráfica com Tkinter.

As traduções estão em **i18n.py**. `ROWS` contém o original português e as traduções em inglês e espanhol. Preserve `{path}`, `{count}` e `{detail}`. Os testes verificam traduções, formatação, preferências, troca de idioma, estados e o conector.

Publique os arquivos do ZIP limpo. Não inclua `settings.local.json`, arquivos do jogo, saves, logs, `.rpyc` gerados ou backups. O `.gitignore` exclui os arquivos locais. O pacote não contém recursos do jogo.

Execute `python build_release.py` para gerar `dist/PlazaWallet.zip` a partir de uma lista explícita de arquivos. Preferências pessoais e arquivos gerados ficam fora do pacote automaticamente.

### Gerar o EXE

No Windows com Python instalado, execute `python -m pip install -r requirements-build.txt` e depois `python build_exe.py`. O resultado fica em `dist/PlazaWallet.exe`. O conector é incorporado como recurso; preferências pessoais e arquivos do jogo ficam fora do EXE. As pastas de compilação são ignoradas pelo Git.

Execute `PlazaWallet.exe --self-test report.json` para verificar as telas de idioma, as preferências e a instalação do conector numa pasta temporária isolada, sem acessar o jogo real.
