from flask import Flask, request, render_template, make_response, jsonify, redirect, url_for, session, request
from flask_login import login_required, LoginManager, UserMixin, login_user
# import pdfkit
import calendar
from datetime import datetime, timedelta
# from weasyprint import HTML
import jaydebeapi


# Configurar os detalhes da conexão
driver = 'org.postgresql.Driver'
url = 'jdbc:postgresql://samu-sc-db.cvg42ka4w3up.sa-east-1.rds.amazonaws.com:5432/postgres'
username = 'samu_sc'
password = 'eoQGe1ioB3VJ2UYILCDV'

# Carregar o driver JDBC
jar_file = 'C:/Program Files/PostgreSQL/14/postgresql-42.7.3.jar'
jars = [jar_file]

# Estabelecer a conexão
conn = jaydebeapi.connect(driver, url, [username, password], jars=jars)

tipo_ocorrencia_dict = {}

app = Flask(__name__)
login_manager = LoginManager(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

meses_traduzidos = {
    'January': 'Janeiro',
    'February': 'Fevereiro',
    'March': 'Março',
    'April': 'Abril',
    'May': 'Maio',
    'June': 'Junho',
    'July': 'Julho',
    'August': 'Agosto',
    'September': 'Setembro',
    'October': 'Outubro',
    'November': 'Novembro',
    'December': 'Dezembro'
}

def traduzir_mes(mes):
    return meses_traduzidos.get(mes, mes)

def login_solicitado(route):
    def encapsular(*args, **kwargs):
        if "logado" in session:
            return route(*args, **kwargs)
        else:
            return redirect('/')
    return encapsular

def validacao_login(nome_usuario, senha_usuario):
    return nome_usuario == "admin" and senha_usuario == "admin123"

def obter_id_do_usuario(nome_usuario):
    if nome_usuario == "admin":
        return 1
    else:
        return None
    
@app.route('/')
def page_login():
    return render_template('login.html')

# @app.route('/pdf_gerado', methods=['GET', 'POST'])
# def gerar_pdf():
#     titulo = request.args.get('titulo')
#     renderizado = render_template('testepdf.html', titulo=titulo)
#     config = pdfkit.configuration(wkhtmltopdf='static/wkhtmltopdf/bin/wkhtmltopdf.exe')
#     pdf= pdfkit.from_string(renderizado, False, configuration=config)
#     # pdf = HTML(string=renderizado).write_pdf()
    
#     response = make_response(pdf)
#     response.headers['Content-Type'] = 'application/pdf'
#     nome_arquivo = f'{titulo}.pdf' if titulo else 'relatório_vazio.pdf'
#     response.headers['Content-Disposition'] = f'inline; filename={nome_arquivo}'
#     response.headers['nome_arquivo'] = nome_arquivo
#     return response

# @app.route('/testepdf', methods=['GET'])
# def pdf_pass():
#     return render_template('testepdf.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
        nome_usuario = request.form.get('usuario')
        senha_usuario = request.form.get('senha')

        if validacao_login(nome_usuario, senha_usuario):
            user_id = obter_id_do_usuario(nome_usuario)
            user = User(user_id)
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('page_login'))
        
@app.route('/logout')
def logout():
    session.pop('logado', None)
    session.clear()
    return redirect(url_for('page_login'))

@app.route('/sistema_rda')
@login_required
def index():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    veiculo = request.args.get('veiculo')
    return render_template('sistema_rda.html', data_inicio=data_inicio, data_fim=data_fim, veiculo=veiculo)

@app.route('/filtro_tipo_veiculo', methods=['GET'])
def filtro_tipo_veiculo():
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            public.dim_tipo_veiculo.nm_tipo_veiculo
        from public.dim_veiculo2
	    inner join public.dim_tipo_veiculo on (public.dim_veiculo2.sk_tipo_veiculo = public.dim_tipo_veiculo.sk_tipo_veiculo)
        WHERE
            public.dim_tipo_veiculo.sk_tipo_veiculo <> 0
        GROUP BY 
            public.dim_tipo_veiculo.nm_tipo_veiculo''')
    tipo_veiculos = [row[0] for row in cursor.fetchall()]
    return jsonify(tipo_veiculos)

@app.route('/filtro_veiculo', methods=['GET'])
def filtro_veiculos():
    tipo_veiculo = request.args.get('tipo_veiculo')
    cursor = conn.cursor()
    cursor.execute('''
        Select
	        public.dim_tipo_veiculo.nm_tipo_veiculo,
	        public.dim_veiculo2.ds_equipe
        from public.dim_veiculo2
	    inner join public.dim_tipo_veiculo on (public.dim_veiculo2.sk_tipo_veiculo = public.dim_tipo_veiculo.sk_tipo_veiculo)
        WHERE  
            public.dim_tipo_veiculo.nm_tipo_veiculo = ?
            AND public.dim_veiculo2.sk_veiculo not in (36, 78, 105, 120, 173, 247)
            AND public.dim_veiculo2.flg_ativo = '1'
            --AND public.dim_veiculo.cd_cnes is not null
        GROUP BY 
            public.dim_tipo_veiculo.nm_tipo_veiculo,
	        public.dim_veiculo2.ds_equipe
        ORDER BY
            public.dim_veiculo2.ds_equipe asc
        ''', (tipo_veiculo,))
    veiculos = [row[1] for row in cursor.fetchall()]
    return jsonify(veiculos)

@app.route('/dados_atendimento', methods=['POST'])
def dados_atendimentos():
    data_inicio =  request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    veiculo = request.form.get('veiculo')
    cursor = conn.cursor()
    data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
    # print(data_inicio)
    cursor.execute('''
        SELECT
            EXTRACT(YEAR from fo.data_abertura_ocorrencia) as ano,       
            EXTRACT(MONTH from fo.data_abertura_ocorrencia) as mes,
            SUM(1) as total_atendimentos,
            EXTRACT(EPOCH FROM AVG(fv.data_hora_saida_base - fv.data_hora_envio_veiculo)) AS tempo_medio_resposta_saida_base,
            EXTRACT(EPOCH FROM AVG(fv.data_hora_chegada_local - fo.data_abertura_ocorrencia)) AS tempo_medio_resposta_total
        FROM public.fato_veiculo as fv
        INNER JOIN public.fato_ocorrencia fo on fv.sk_ocorrencia = fo.sk_ocorrencia
        INNER JOIN public.dim_tipo_veiculo dtv on fv.sk_tipo_veiculo_enviado = dtv.sk_tipo_veiculo
        INNER JOIN public.dim_veiculo2 dv on fv.sk_veiculo_enviado = dv.sk_veiculo
        WHERE
             fo.data_abertura_ocorrencia >= TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND fo.data_abertura_ocorrencia < TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND dv.ds_equipe = ?
            --AND fo.sk_tipo_ocorrencia in (22, 42, 65, 88, 113, 136, 160, 184)
            AND fv.sk_tipo_motivo_cancelamento = 0
            AND fv.data_hora_chegada_local IS NOT NULL
            AND fo.data_encerramento_ocorrencia IS NOT NULL
        GROUP BY
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia)
        ORDER BY
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia)
       ''', (data_inicio, data_fim_ajustada.strftime('%Y-%m-%d %H:%M:%S'), veiculo))
    rows = cursor.fetchall()
    result = [{'mes': traduzir_mes(calendar.month_name[row[1]]), 
               'total_atendimentos': row[2], 
               'tempo_medio_resposta_saida_base': row[3], 
               'tempo_medio_resposta_total': row[4]} for row in rows
            ]
    return jsonify(result)

@app.route('/dados_atendimento_tipo_ocorrencia', methods=['POST'])
def dados_atendimentos_tipo_ocorrencia():
    data_inicio =  request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    veiculo = request.form.get('veiculo')
    cursor = conn.cursor()
    data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
    cursor.execute('''
        SELECT
            EXTRACT(YEAR from fo.data_abertura_ocorrencia) as ano,       
            EXTRACT(MONTH from fo.data_abertura_ocorrencia) as mes,
            CASE
                WHEN  dto.nm_tipo_ocorrencia in ('TRANSFERÊNCIA', 'Transferência CERINTER', 'Outros', 'Transferência inter-hospitalar') THEN 'Outros'
                when dto.nm_tipo_ocorrencia  is null then 'Outros'
                ELSE dto.nm_tipo_ocorrencia END  as nm_tipo_ocorrencia,
            
            SUM(1) as total_atendimentos
        FROM public.fato_veiculo as fv
        INNER JOIN public.fato_ocorrencia fo on fv.sk_ocorrencia = fo.sk_ocorrencia
        INNER JOIN public.dim_tipo_ocorrencia dto on fo.sk_tipo_ocorrencia = dto.sk_tipo_ocorrencia
        INNER JOIN public.dim_veiculo2 dv on fv.sk_veiculo_enviado = dv.sk_veiculo
        WHERE
            fo.data_abertura_ocorrencia >= TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND fo.data_abertura_ocorrencia < TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND dv.ds_equipe = ?
            AND fv.sk_tipo_motivo_cancelamento = 0
            AND fv.data_hora_chegada_local IS NOT NULL
            AND fo.data_encerramento_ocorrencia IS NOT NULL
        GROUP BY
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia),
            dto.nm_tipo_ocorrencia
        ORDER BY
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia)
        ''', (data_inicio, data_fim_ajustada.strftime('%Y-%m-%d %H:%M:%S'), veiculo))
    rows = cursor.fetchall()
    resultado_final = []
    for row in rows:
        ano, mes, nm_tipo_ocorrencia, total_atendimentos = row
        mes = traduzir_mes(calendar.month_name[mes])

        linha_tabela = {'nm_tipo_ocorrencia': nm_tipo_ocorrencia}
        linha_tabela['ano'] = ano
        linha_tabela['mes'] = mes
        linha_tabela['total_atendimentos'] = total_atendimentos

        resultado_final.append(linha_tabela)
    return jsonify(resultado_final)

@app.route('/dados_atendimento_por_genero', methods=['POST'])
def dados_atendimento_por_genero():
    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    veiculo = request.form.get('veiculo')
    cursor = conn.cursor()
    data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
    cursor.execute('''
        SELECT
            EXTRACT(YEAR from fo.data_abertura_ocorrencia) as ano,       
            EXTRACT(MONTH from fo.data_abertura_ocorrencia) as mes,
            CASE
                CAST
                   (fvt.sexo_vitima as integer)
                   WHEN 1 THEN 'Masculino'
                   WHEN 2 THEN 'Feminino'
                   ELSE 'Não Informado'
                END as sexo_vitima,
            SUM(1) as total_atendimentos
        FROM public.fato_veiculo as fv
        INNER JOIN public.fato_ocorrencia fo on fv.sk_ocorrencia = fo.sk_ocorrencia
        INNER JOIN public.fato_vitima fvt on fv.sk_vitima = fvt.sk_vitima
        INNER JOIN public.dim_veiculo2 dv on fv.sk_veiculo_enviado = dv.sk_veiculo
        WHERE
            fo.data_abertura_ocorrencia >= TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND fo.data_abertura_ocorrencia < TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND dv.ds_equipe = ?
            AND fv.sk_tipo_motivo_cancelamento = 0
            AND fv.data_hora_chegada_local IS NOT NULL
            AND fo.data_encerramento_ocorrencia IS NOT NULL
        GROUP BY
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia),
            sexo_vitima
        ORDER BY
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia)
    ''', (data_inicio, data_fim_ajustada.strftime('%Y-%m-%d %H:%M:%S'), veiculo))
    rows = cursor.fetchall()
    resultado_final = []
    for row in rows:
        ano, mes, sexo_vitima, total_atendimentos = row
        mes = traduzir_mes(calendar.month_name[mes])

        linha_tabela = {'sexo_vitima': sexo_vitima}
        linha_tabela['ano'] = ano
        linha_tabela['mes'] = mes
        linha_tabela['total_atendimentos'] = total_atendimentos

        resultado_final.append(linha_tabela)
    return jsonify(resultado_final)

@app.route('/dados_atendimento_por_fxEtaria', methods=['POST'])
def dados_atendimentos_por_fxEtaria():
    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    veiculo = request.form.get('veiculo')
    cursor = conn.cursor()
    data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
    cursor.execute('''
        SELECT
            EXTRACT(YEAR from fo.data_abertura_ocorrencia) as ano,       
            EXTRACT(MONTH from fo.data_abertura_ocorrencia) as mes,
            dfe.nm_faixa_etaria as nm_faixa_etaria,
            SUM(1) as total_atendimentos
        FROM public.fato_veiculo as fv
        INNER JOIN public.fato_ocorrencia fo on fv.sk_ocorrencia = fo.sk_ocorrencia
        INNER JOIN public.fato_vitima fvt on fv.sk_vitima = fvt.sk_vitima
        INNER JOIN public.dim_faixa_etaria dfe on fvt.sk_faixa_etaria = dfe.sk_faixa_etaria  
        INNER JOIN public.dim_veiculo2 dv on fv.sk_veiculo_enviado = dv.sk_veiculo
        WHERE
            fo.data_abertura_ocorrencia >= TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND fo.data_abertura_ocorrencia < TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND dv.ds_equipe = ?
            and fvt.sexo_vitima in ('1', '2')
            AND fv.sk_tipo_motivo_cancelamento = 0
            AND fv.data_hora_chegada_local IS NOT NULL
            AND fo.data_encerramento_ocorrencia IS NOT NULL
        GROUP by
            fo.cd_ocorrencia,
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia),
            nm_faixa_etaria
        ORDER BY
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia),
            nm_faixa_etaria
   ''', (data_inicio, data_fim_ajustada.strftime('%Y-%m-%d %H:%M:%S'), veiculo))
    rows = cursor.fetchall()
    resultado_final = []

    for row in rows:
        ano, mes, nm_faixa_etaria, total_atendimentos = row
        mes = traduzir_mes(calendar.month_name[mes])

        linha_tabela = {'nm_faixa_etaria': nm_faixa_etaria}
        linha_tabela['ano'] = ano
        linha_tabela['mes'] = mes
        linha_tabela['total_atendimentos'] = total_atendimentos

        resultado_final.append(linha_tabela)
    return jsonify(resultado_final)

@app.route('/dados_atendimento_por_municipio', methods=['POST'])
def dados_atendimentos_por_municipio():
    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    veiculo = request.form.get('veiculo')
    cursor = conn.cursor()
    data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
    cursor.execute('''
        SELECT
            EXTRACT(YEAR from fo.data_abertura_ocorrencia) as ano,       
            EXTRACT(MONTH from fo.data_abertura_ocorrencia) as mes,
            dm.nm_municipio as nm_municipio,
            SUM(1) as total_atendimentos
        FROM public.fato_veiculo as fv
        INNER JOIN public.fato_ocorrencia fo on fv.sk_ocorrencia = fo.sk_ocorrencia
        INNER JOIN public.dim_veiculo2 dv on fv.sk_veiculo_enviado = dv.sk_veiculo
        INNER JOIN public.dim_municipio dm on fo.sk_municipio_ocorrencia = dm.sk_municipio
        WHERE
            fo.data_abertura_ocorrencia >= TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND fo.data_abertura_ocorrencia < TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND dv.ds_equipe = ?
            AND fv.sk_tipo_motivo_cancelamento = 0
            AND fv.data_hora_chegada_local IS NOT NULL
            AND fo.data_encerramento_ocorrencia IS NOT NULL
        GROUP BY
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia),
            dm.nm_municipio
        ORDER BY
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia)
        ''', (data_inicio, data_fim_ajustada.strftime('%Y-%m-%d %H:%M:%S'), veiculo))
    rows = cursor.fetchall()
    resultado_final = []

    for row in rows:
        ano, mes, nm_municipio, total_atendimentos = row
        mes = traduzir_mes(calendar.month_name[mes])

        linha_tabela = {'nm_municipio': nm_municipio}
        linha_tabela['ano'] = ano
        linha_tabela['mes'] = mes
        linha_tabela['total_atendimentos'] = total_atendimentos

        resultado_final.append(linha_tabela)
    return jsonify(resultado_final)

@app.route('/dados_atendimento_por_unidade', methods=['POST'])
def dados_atendimentos_por_unidade():
    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    veiculo = request.form.get('veiculo')
    cursor = conn.cursor()
    data_fim_ajustada = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
    cursor.execute('''
        SELECT
            EXTRACT(YEAR from fo.data_abertura_ocorrencia) as ano,       
            EXTRACT(MONTH from fo.data_abertura_ocorrencia) as mes,
            CASE 
                WHEN dud.nm_unidade_destino is null then 'Outros' 
                ELSE dud.nm_unidade_destino
                   END as nm_unidade_destino,
            SUM(1) as total_atendimentos
        FROM public.fato_veiculo as fv
        INNER JOIN public.fato_ocorrencia fo on fv.sk_ocorrencia = fo.sk_ocorrencia
        INNER JOIN public.dim_veiculo2 dv on fv.sk_veiculo_enviado = dv.sk_veiculo
    	LEFT JOIN public.dim_unidade_destino dud on (fo.sk_unidade_destino = dud.sk_unidade_destino)
        WHERE
            fo.data_abertura_ocorrencia >= TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND fo.data_abertura_ocorrencia < TO_TIMESTAMP(?, 'YYYY-MM-DD HH24:MI:SS')
            AND dv.ds_equipe = ?
            AND fv.sk_tipo_motivo_cancelamento = 0
            AND fv.data_hora_chegada_local IS NOT NULL
            AND fo.data_encerramento_ocorrencia IS NOT NULL
        GROUP BY
            EXTRACT(YEAR from fo.data_abertura_ocorrencia),
            EXTRACT(MONTH from fo.data_abertura_ocorrencia),
            dud.nm_unidade_destino
        ''', (data_inicio, data_fim_ajustada.strftime('%Y-%m-%d %H:%M:%S'), veiculo))
    rows = cursor.fetchall()
    resultado_final = []

    for row in rows:
        ano, mes, nm_unidade_destino, total_atendimentos = row
        mes = traduzir_mes(calendar.month_name[mes])

        linha_tabela = {'nm_unidade_destino': nm_unidade_destino}
        linha_tabela['ano'] = ano
        linha_tabela['mes'] = mes
        linha_tabela['total_atendimentos'] = total_atendimentos

        resultado_final.append(linha_tabela)
    return jsonify(resultado_final)

if __name__ == '__main__':
    app.secret_key = 'admin123'
    app.run(debug=True)