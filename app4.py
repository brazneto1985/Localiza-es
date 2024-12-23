from flask import Flask, render_template, request, redirect, flash, url_for, session
import pandas as pd
import os

app = Flask(__name__)
# Use uma chave de ambiente
app.secret_key = os.getenv('SECRET_KEY', 'default_secret')
app.config['VERSION'] = "1.0.3"  # Versão do aplicativo

# Usuários de exemplo para login (pode ser extraído de uma fonte segura)
users = {"leitura": os.getenv(
    "LEITURA_PASS", "din@2024"), "eletrica": os.getenv("ELETRICA_PASS", "din@2024")}

# Caminho relativo para o arquivo CSV com os dados
csv_path = os.path.join(os.path.dirname(__file__), 'endereços.csv')

# Tenta carregar o CSV com dados de instalação, medidor, MRU, endereço e coordenadas
try:
    df = pd.read_csv(csv_path)
    df['instalação'] = df['instalação'].astype(str).str.strip()
    df['medidor'] = df['medidor'].astype(str).str.strip()
    df['MRU'] = df['MRU'].astype(str).str.strip()
    df['endereço'] = df['endereço'].astype(str).str.strip()
except FileNotFoundError:
    df = pd.DataFrame(columns=['instalação', 'medidor',
                      'MRU', 'endereço', 'latitude', 'longitude'])
except KeyError:
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
            session['username'] = username
            flash("Login bem-sucedido!", "success")
            return redirect(url_for("index"))
        else:
            flash("Credenciais inválidas, tente novamente.", "error")
    return render_template("login.html")

# Rota para logout


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("login"))

# Rota inicial que exibe o formulário de busca


@app.route("/")
def index():
    if not session.get('logged_in'):
        return redirect(url_for("login"))
    return render_template("index.html", mapa_url=None, resultado=None, referencias=None, versao=app.config['VERSION'])

# Rota para processar a busca


@app.route("/buscar", methods=["POST"])
def buscar():
    if not session.get('logged_in'):
        return redirect(url_for("login"))

    entrada = request.form.get("entrada", "").strip().lower()
    if not entrada:
        flash("Por favor, insira uma instalação ou medidor.", "error")
        return redirect("/")

    if {'instalação', 'medidor', 'MRU', 'endereço'}.issubset(df.columns):
        resultado = df[
            df['instalação'].str.lower().str.contains(entrada) |
            df['medidor'].str.lower().str.contains(entrada)
        ]

        if not resultado.empty:
            index_resultado = resultado.index[0]
            dados = {
                "instalação": resultado.iloc[0]['instalação'],
                "MRU": resultado.iloc[0]['MRU'],
                "medidor": resultado.iloc[0]['medidor'],
                "endereço": resultado.iloc[0]['endereço']
            }
            latitude = resultado.iloc[0].get('latitude', None)
            longitude = resultado.iloc[0].get('longitude', None)
            mapa_url = f"https://www.google.com/maps?q={latitude},{longitude}" if latitude and longitude else None

            inicio = max(0, index_resultado - 5)
            fim = min(len(df), index_resultado + 6)
            referencias = df.iloc[inicio:fim][[
                'MRU', 'instalação', 'medidor', 'endereço']]

            flash("Localização encontrada!", "success")
            return render_template(
                "index.html",
                mapa_url=mapa_url,
                resultado=dados,
                referencias=referencias.to_dict('records'),
                versao=app.config['VERSION']
            )
        else:
            flash("Instalação ou Medidor não encontrados.", "error")
            return redirect("/")
    else:
        flash("Colunas necessárias não encontradas no arquivo CSV.", "error")
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)


