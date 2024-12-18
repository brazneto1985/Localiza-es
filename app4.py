from flask import Flask, render_template, request, redirect, flash, url_for, session
import pandas as pd
import os

app = Flask(__name__)
# Use uma chave de ambiente
app.secret_key = os.getenv('SECRET_KEY', 'default_secret')
app.config['VERSION'] = "1.0.2"  # Versão do aplicativo

# Usuários de exemplo para login (pode ser extraído de uma fonte segura)
users = {"leitura": os.getenv(
    "LEITURA_PASS", "din@2024"), "eletrica": os.getenv("ELETRICA_PASS", "din@2024")}

# Caminho relativo para o arquivo CSV com os dados
csv_path = os.path.join(os.path.dirname(__file__), 'endereços.csv')

# Tenta carregar o CSV com dados de instalação, medidor, MRU, endereço e coordenadas
try:
    df = pd.read_csv(csv_path)
    print("Colunas disponíveis:", df.columns)
    # Convertendo colunas para string e removendo espaços extras
    df['instalação'] = df['instalação'].astype(str).str.strip()
    df['medidor'] = df['medidor'].astype(str).str.strip()
    df['MRU'] = df['MRU'].astype(str).str.strip()
    df['endereço'] = df['endereço'].astype(str).str.strip()
except FileNotFoundError:
    print("Erro: O arquivo endereços.csv não foi encontrado.")
    df = pd.DataFrame(columns=['instalação', 'medidor',
                      'MRU', 'endereço', 'latitude', 'longitude'])
except KeyError:
    print("Erro: Colunas esperadas não foram encontradas no arquivo CSV.")
    df = pd.DataFrame(columns=['instalação', 'medidor',
                      'MRU', 'endereço', 'latitude', 'longitude'])

# Rota de login


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if users.get(username) == password:
            session['logged_in'] = True
            # Adiciona o nome do usuário na sessão
            session['username'] = username
            flash("Login bem-sucedido!", "success")
            return redirect(url_for("index"))
        else:
            flash("Credenciais inválidas, tente novamente.", "error")
    return render_template("login.html")

# Rota para logout


@app.route("/logout")
def logout():
    session.clear()  # Limpa todas as informações da sessão para maior segurança
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("login"))

# Rota inicial que exibe o formulário de busca


@app.route("/")
def index():
    if not session.get('logged_in'):
        return redirect(url_for("login"))
    return render_template("index.html", mapa_url=None, resultado=None, versao=app.config['VERSION'])

# Rota para processar a busca


@app.route("/buscar", methods=["POST"])
def buscar():
    if not session.get('logged_in'):
        return redirect(url_for("login"))

    entrada = request.form.get("entrada", "").strip().lower()
    if not entrada:
        flash("Por favor, insira uma instalação ou medidor.", "error")
        return redirect("/")

    # Verifica se as colunas necessárias estão presentes
    if {'instalação', 'medidor', 'MRU', 'endereço'}.issubset(df.columns):
        # Convertendo todas as colunas de interesse para string, para evitar problemas com valores não string
        df['instalação'] = df['instalação'].astype(str).str.strip()
        df['medidor'] = df['medidor'].astype(str).str.strip()

        # Busca no DataFrame, ignorando maiúsculas/minúsculas
        resultado = df[
            df['instalação'].str.contains(entrada, case=False, na=False) |
            df['medidor'].str.contains(entrada, case=False, na=False)
        ]

        if not resultado.empty:
            dados = {
                "instalação": resultado.iloc[0]['instalação'],
                "MRU": resultado.iloc[0]['MRU'],
                "medidor": resultado.iloc[0]['medidor'],
                "endereço": resultado.iloc[0]['endereço']
            }
            latitude = resultado.iloc[0]['latitude']
            longitude = resultado.iloc[0]['longitude']
            mapa_url = f"https://www.google.com/maps?q={latitude},{longitude}"
            flash("Localização encontrada!", "success")
            return render_template("index.html", mapa_url=mapa_url, resultado=dados, versao=app.config['VERSION'])
        else:
            flash("Instalação ou Medidor não encontrados.", "error")
            return redirect("/")
    else:
        flash("Colunas necessárias não encontradas no arquivo CSV.", "error")
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)


