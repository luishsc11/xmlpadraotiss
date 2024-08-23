import os
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def save_xml(xml_data):
    file_path = 'x'
    new_file_path = os.path.join(os.path.dirname(file_path), 'processed_' + os.path.basename(file_path))
    with open(file_path, 'wb') as new_file:
        new_file.write(xml_data)

def process_xml(xml_data):
    save_xml(xml_data)
    namespaces = {'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'}
    root = ET.fromstring(xml_data)
    guias = []
    total_valor = 0

    guiasTISS = root.findall('.//ans:guiasTISS', namespaces)
    for guias_tiss in guiasTISS:
        guiasSP_SADT = guias_tiss.findall('.//ans:guiaSP-SADT', namespaces)
        guiasInternacao = guias_tiss.findall('.//ans:guiaResumoInternacao', namespaces)
        posicao = -1
        for guia_sadt in guiasSP_SADT:
            numero_guia_operador = guia_sadt.find('.//ans:dadosAutorizacao/ans:numeroGuiaOperadora', namespaces)
            if numero_guia_operador is not None:
                posicao += 1
                nome_beneficiario = guia_sadt.find('.//ans:dadosBeneficiario/ans:nomeBeneficiario', namespaces)
                valor_total = guia_sadt.find('.//ans:valorTotal/ans:valorTotalGeral', namespaces)
                valor_formatado = "{:.4f}".format(float(valor_total.text))
                
                xml_guia = ET.tostring(guia_sadt, encoding='unicode', method='xml')
                
                guia = {
                    'numeroGuia': numero_guia_operador.text,
                    'nome_beneficiario': nome_beneficiario.text,
                    'valor_total': valor_formatado,
                    'xml_guia': xml_guia,
                    'posicao': posicao
                }
                guias.append(guia)
                total_valor += float(valor_total.text)

        for guia_internacao in guiasInternacao:
            numero_guia_operador = guia_internacao.find('.//ans:dadosAutorizacao/ans:numeroGuiaOperadora', namespaces)
            if numero_guia_operador is not None:
                nome_beneficiario = guia_internacao.find('.//ans:dadosBeneficiario/ans:nomeBeneficiario', namespaces)
                valor_total = guia_internacao.find('.//ans:valorTotal/ans:valorTotalGeral', namespaces)
                valor_formatado = "{:.4f}".format(float(valor_total.text))
                
                xml_guia = ET.tostring(guia_internacao, encoding='unicode', method='xml')
                
                guia = {
                    'numeroGuia': numero_guia_operador.text,
                    'nome_beneficiario': nome_beneficiario.text,
                    'valor_total': valor_formatado,
                    'xml_guia': xml_guia
                }
                guias.append(guia)
                total_valor += float(valor_total.text)

    return guias, "{:.2f}".format(total_valor)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        numero_guia = request.form['numero_guia']
        return redirect(url_for('detalhes_guia', numero_guia=numero_guia))
    return render_template('index.html')

@app.route('/import_xml', methods=['POST'])
def import_xml():
    uploaded_file = request.files['xml_file']
    if uploaded_file.filename != '':
        xml_data = uploaded_file.read()
        guias, total_valor = process_xml(xml_data)
        return render_template('guias.html', guias=guias, total_valor=total_valor)
    else:
        return "Nenhum arquivo selecionado."

@app.route('/detalhes_guia/<int:posicao>', methods=['GET', 'POST'])
def detalhes_guia(posicao):
    guias, _ = process_xml(open('x', 'rb').read())
    xml_guia = guias[posicao]

    return render_template('detalhesguia.html', xml_guia=xml_guia)

if __name__ == '__main__':
    app.run(debug=True)
