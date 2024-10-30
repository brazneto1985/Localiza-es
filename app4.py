from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import webbrowser
import os

# Carregar a planilha com os dados
try:
    df = pd.read_csv(os.path.join(
        'C:\\Users\\Brazn\\Desktop\\app_atualizado', 'endereços.csv'))
    df['instalação'] = df['instalação'].astype(str).str.strip()
    df['medidor'] = df['medidor'].astype(str).str.strip()
except FileNotFoundError:
    print("Erro: O arquivo endereços.csv não foi encontrado.")
    df = pd.DataFrame()  # cria um DataFrame vazio caso o arquivo não seja encontrado


app = Flask(__name__)
app.secret_key = 'chave_secreta'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/buscar', methods=['POST'])
def buscar():
    entrada = request.form['entrada'].strip()

    # Procurar o endereço ou instalação correspondente
    resultado = df[(df['instalação'].str.casefold() == entrada.casefold()) |
                   (df['medidor'].str.casefold() == entrada.casefold())]

    if not resultado.empty:
        latitude = resultado.iloc[0]['latitude']
        longitude = resultado.iloc[0]['longitude']

        # Construir e retornar a URL do Google Maps
        url = f"https://www.google.com/maps?q={latitude},{longitude}"
        flash(
            f"<a href='{url}' target='_blank'>Abrir Google Maps</a>", "success")
    else:
        flash("Instalação ou Medidor não encontrados na planilha.", "error")

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
