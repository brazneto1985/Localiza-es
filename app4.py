from flask import Flask, render_template, request, redirect, flash, url_for
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Adicione uma chave secreta para usar flash messages

# Caminho relativo para o arquivo CSV com os dados
csv_path = os.path.join(os.path.dirname(__file__), 'endereços.csv')

# Tenta carregar o CSV com dados de instalação, medidor e coordenadas
try:
    df = pd.read_csv(csv_path)
    print("Colunas disponíveis:", df.columns)  # Verificar colunas do CSV
    # Convertendo colunas para string e removendo espaços extras
    df['instalação'] = df['instalação'].astype(str).str.strip()
    df['medidor'] = df['medidor'].astype(str).str.strip()
except FileNotFoundError:
    print("Erro: O arquivo endereços.csv não foi encontrado.")
    # Define colunas esperadas para evitar KeyError em outras partes do código
    df = pd.DataFrame(columns=['instalação', 'medidor', 'latitude', 'longitude'])
except KeyError:
    print("Erro: Colunas esperadas não foram encontradas no arquivo CSV.")
    # Define colunas esperadas para evitar KeyError
    df = pd.DataFrame(columns=['instalação', 'medidor', 'latitude', 'longitude'])

# Rota inicial que exibe o formulário de busca
@app.route("/")
def index():
    return render_template("index.html", mapa_url=None)

# Rota para processar a busca
@app.route("/buscar", methods=["POST"])
def buscar():
    entrada = request.form.get("entrada", "").strip().lower()
    if not entrada:
        flash("Por favor, insira uma instalação ou medidor.", "error")
        return redirect("/")

    # Verifica se as colunas necessárias estão presentes
    if 'instalação' not in df.columns or 'medidor' not in df.columns:
        flash("Colunas necessárias não encontradas no arquivo CSV.", "error")
        return redirect("/")

    # Busca no DataFrame
    resultado = df[
        df['instalação'].str.lower().str.contains(entrada) |
        df['medidor'].str.lower().str.contains(entrada)
    ]

    if not resultado.empty:
        latitude = resultado.iloc[0]['latitude']
        longitude = resultado.iloc[0]['longitude']
        mapa_url = f"https://www.google.com/maps?q={latitude},{longitude}"
        flash("Localização encontrada!", "success")
        return render_template("index.html", mapa_url=mapa_url)
    else:
        flash("Instalação ou Medidor não encontrados.", "error")
        return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

