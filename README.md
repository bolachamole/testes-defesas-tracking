# Testes de defesas contra Web Tracking stateful e conteúdo de rastreamento

## Considerações iniciais
Este repositório utiliza uma modifição do [adblockparser](https://github.com/scrapinghub/adblockparser) que funciona com a biblioteca [google-re2](https://pypi.org/project/google-re2), assim como dependências que podem ser instaladas via pip:

```
pip install -r requirements.txt
```

Assume-se que um ambiente virtual python está sendo utilizado.

## Modo de uso
Após baixar as dependências, deve-se rodar o mitmproxy com a opção ```--set confdir=configs``` para baixar o certificado, como descrito [nessa página](https://docs.mitmproxy.org/dev/concepts/certificates/).

Testes devem ser iniciados por meio do comando:

```
python3 main.py --navegador=<nome do navegador> --nivel=<nível das configurações sendo testadas> --path-pefil=<caminho do perfil guardando as configurações do navegador a serem utilizadas> --path-navegador=<caminho do executável do navegador>
```

A opção ```path-perfil``` é recomendada, mas não obrigatória. Não é necessária ao testar o Safari.

A opção ```path-navegador``` é obrigatória ao testar os navegadores Opera e Brave, devido ao uso do WebDriver do Chrome.

Os seguintes valores são válidos para a opção ```navegador```: ```chrome```, ```firefox```, ```edge```, ```opera```, ```brave``` e ```safari```.

Os seguintes valores são válidos para a opção ```nivel```: ```normal```e ```rigoroso```. Ela serve apenas para diferenciar o nome das tabelas no banco de dados.
