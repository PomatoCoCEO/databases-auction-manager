##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2020/2021 ===============
## =============================================
## =================== Demo ====================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors: 
##   Nuno Antunes <nmsa@dei.uc.pt>
##   BD 2021 Team - https://dei.uc.pt/lei/
##   University of Coimbra

 
from flask import Flask, jsonify, request
import logging, psycopg2, time
import hashlib
import threading,time
from encrypter import dec_file


usr=""
pswd=""
hst=""
dbase=""


app = Flask(__name__) 


def return_user_id(token, cur):
    statement = """
                  SELECT confirm_token(%s)"""
    try:
        cur.execute(statement, (token,))
        res= cur.fetchone()
        res=res[0]
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        res=-1
    if res is None: 
        return -1
    return res

# !not used rn
def formatter_db_update(dic, id ):
    return 'update leiloes set ('+(len(dic)-1)*'%s,'+'%s) values ('+'('+(len(dic)-1)*'%s,'+'%s) where leilaoid='+id+';' # dic.keys()+ dic.values())


def warn_winning_bidders(): # fazer uma thread com esta funcao
    # ver quais os leilões que acabaram
    conn = db_connection()
    cur = conn.cursor()
    while True:
        try:
            print("checking auctions")
            cur.execute('call clean_tokens();')
            cur.execute('call warn_auct_winners();')
            cur.execute('commit')
            time.sleep(5*60) #sleeps 5 minutes before each action
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error('In supporting thread...')
            logger.error(error)
            cur.execute('rollback')

    # avisar os respetivos utilizadores

#very basic email regex checking: [a-zA-Z0-9\.\_]+@[a-zA-Z0-9\.\_]+\.[a-zA-Z0-9\.\_]+

# user login
@app.route("/dbproj/user/", methods=['POST']) # insercao de artigo
def add_user():
    logger.info("###              INSERTION OF USERS            ###");   
    payload = request.get_json()

    if "username" not in payload or "password" not in payload or "email" not in payload :
        return 'username , email and password are required to create a new username!'

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new user  ----")
    logger.debug(f'payload: {payload}')

    # parameterized queries, good for security and performance
    statement = """
                  SELECT register_user(%s, %s, %s);"""
    
    val_pass = hashlib.sha256(payload["password"].encode()).hexdigest()
    #logger.info(payload["username"])
    logger.info(val_pass)  # ? is this what you mean?

    values = (payload["username"], val_pass, payload["email"])

    try:
        cur.execute(statement, values)
        cur.execute('commit')
        result = 'User registered!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute('rollback')
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
            
    return jsonify(result)


# user login
@app.route("/dbproj/message/<leilaoid>", methods=['POST']) # insercao de artigo
def send_message(leilaoid):
    logger.info("###              INSERTION OF USERS            ###");   
    payload = request.get_json()

    if "message" not in payload or "authToken" not in payload:
        return 'message and authToken are required to send message!'

    conn = db_connection()
    cur = conn.cursor()
    userId = return_user_id(payload["authToken"], cur)
    if userId == -1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'

    logger.info("---- new user  ----")
    logger.debug(f'payload: {payload}')

    # parameterized queries, good for security and performance
    statement = """
                    
                  INSERT INTO mensagem values ((select coalesce(max(msg_id),0)+1 from mensagem), %s, now(), %s, %s);
                """

    values = (payload["message"], userId, leilaoid)

    try:
        cur.execute(statement, values)
        cur.execute('commit')
        result = 'Message delivered!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute('rollback')
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


# user login
@app.route("/dbproj/notif/<all>", methods=['GET']) # insercao de artigo
def open_notif_box(all):
    logger.info("###              NOTIFICATION CHECK            ###");   
    payload = request.get_json()
    
    if "authToken" not in payload:
        return 'authToken is required to check notif box!'

    conn = db_connection()
    cur = conn.cursor()
    userId = return_user_id(payload["authToken"], cur)
    if userId == -1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'

    logger.info("---- checking notifs  ----")
    logger.debug(f'payload: {payload}')

    # parameterized queries, good for security and performance
    if all:
        statement1 = """      
                    select assunto, conteudo, data from notificacao where id_notif in 
                        (select notificacao_id_notif from utilizador_notificacao 
                            where utilizador_userid = %s)
                            order by id_notif desc;
                    """
    else:
        statement1 = """      
                    select assunto, conteudo, data from notificacao where id_notif in 
                        (select notificacao_id_notif from utilizador_notificacao 
                            where utilizador_userid = %s and lida = false)
                            order by id_notif desc;
                    """

    statement2 = """      
                update utilizador_notificacao set lida = true where 
                    utilizador_userid =%s 
                """

    values = ( userId,)
    result =[]
    try:
        cur.execute(statement1, values)
        rows = cur.fetchall()
        if rows == []:
            result= 'No new notifications'
        else:
            for row in rows:
                print(row)
                result.append({'assunto': row[0], 'data': row[2], 'conteudo': row[1]})
            cur.execute(statement2, values)
            cur.execute('commit')
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute('rollback')
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)




@app.route("/dbproj/user/", methods=['PUT'])
def authenticate_user():
    logger.info("###              AUTHENTICATION OF USERS              ###");   
    content = request.get_json()

    if "userId" not in content or "password" not in content:
        return 'user and password are required to login!'

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- update user  ----")
    logger.info(f'content: {content}')

    # parameterized queries, good for security and performance
    statement ="""
                SELECT authenticate(%s, %s, interval '03:00:00')
                """

    val_pass = hashlib.sha256(content["password"].encode()).hexdigest()
    values = (content["userId"], val_pass)
    logger.info(f'SELECT authenticate({values[0]}, {values[1]})')
    try:
        cur.execute(statement, values)
        res=cur.fetchone()
        logger.info(f'{res}')
        result={"authToken": res[0]}
        cur.execute('commit')
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute('rollback')
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)

@app.route('/') 
def hello(): 
    return """

    Benvindo ao gestor de leilões!  <br/>
    <br/>
    Efetue o seu login ou registe-se para continuar!<br/>
    <br/>
    AP Team<br/>
    <br/>
    """

##
##      Demo GET
##
## Obtain all departments, in JSON format
##
## To use it, access: 
## 
##   http://localhost:8080/departments/
##

## GET http://localhost:8080/dbproj/leiloes
'''
def terminate_auctions():

    while True:
        return 1

'''

@app.route("/dbproj/leiloes", methods=['GET'], strict_slashes=True)
def get_all_auctions():
    logger.info("###              DEMO: GET /leiloes             ###");   
    payload = request.get_json()

    if "authToken" not in payload:
        return 'authToken is required to list all auctions!'

    conn = db_connection()
    cur = conn.cursor()


    if return_user_id(payload["authToken"], cur) == -1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'
    
    cur.execute("SELECT leilaoid, descricao FROM leilao where leilaoid = versao_atual")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- leiloes  ----")
    for row in rows:
        logger.debug(row)
        content = {'leilaoId': int(row[0]), 'descricao': row[1]}
        payload.append(content) # appending to the payload to be returned

    conn.close()
    return jsonify(payload)

@app.route("/dbproj/leiloes/<keyword>", methods=['GET'], strict_slashes=True)
def get_auction_by_keyword(keyword): #check
    logger.info("###              DEMO: GET /leiloes             ###");   
    payload = request.get_json()

    if "authToken" not in payload:
        return 'authToken is required to list auctions with that keyword!'

    conn = db_connection()
    cur = conn.cursor()

    if return_user_id(payload["authToken"], cur) == -1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'

    keyword1='%'+ keyword + '%'

    statement1= """
        select leilaoid, descricao from leilao
            where leilaoid in 
            (SELECT distinct versao_atual FROM leilao
                    WHERE (artigo_artigoid = %s 
                     or descricao like %s ) ) 
        """
    statement2= """
        select leilaoid, descricao from leilao
            where leilaoid in 
            (SELECT distinct versao_atual FROM leilao
                    WHERE descricao like %s  ) 
        """

    try:
        art_id= int(keyword)
        cur.execute(statement1, (str(art_id), keyword1))
    except ValueError:
        cur.execute(statement2, (keyword1,))

    rows = cur.fetchall()

    payload = []
    logger.debug("---- leiloes  ----")
    
    for row in rows:
        logger.debug(row)
        content = {'leilaoId': int(row[0]), 'descricao': row[1]}
        payload.append(content) # appending to the payload to be returned

    if payload==[]:
        payload= 'No auction matches your search!'
    conn.close()
    return jsonify(payload)

@app.route("/dbproj/leilao/", methods=['POST']) # insercao de artigo
def add_auction():
    logger.info("###              DEMO: POST /leilao         ###");   
    payload = request.get_json()
    if "authToken" not in payload or "artigoId" not in payload or "precoMinimo" not in payload or "titulo" not in payload or "descricao" not in payload or "expira_leilao" not in payload or "nome" not in payload:
        return 'authToken, artigoId, precoMinimo, titulo, descricao, expira_leilao and nome are required to add an auction!'

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new leilao  ----")
    logger.debug(f'payload: {payload}')

    user_id= return_user_id(payload["authToken"], cur)
    if user_id==-1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'

    # parameterized queries, good for security and performance
    statement = """SELECT insert_auction(%s, %s, %s,%s, %s, %s, %s)"""

    values = (user_id, payload["artigoId"], payload["precoMinimo"], payload["titulo"], payload["descricao"], payload["expira_leilao"], payload["nome"])

    try:
        cur.execute(statement, values)
        l_id=cur.fetchone()
        if l_id[0]==-1:
            result= 'Name does not correspond to its id'
            cur.execute('rollback')
            return result
        elif l_id[0] ==-2:
            result= 'expire date is in the past...'
            cur.execute('rollback')
            return result
        else:    
            result= {"leilaoId": int (l_id[0])}
        cur.execute('commit')
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute('rollback')
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

@app.route("/dbproj/leilao/<leilaoId>", methods=['PUT']) # insercao de artigo
def update_auction(leilaoId):
    logger.info("###              DEMO: PUT /leilao/id         ###");   
    payload = request.get_json()

    if "authToken" not in payload or ("titulo" not in payload and "descricao" not in payload):
        return 'authToken, titulo and/or descricao  are required to update an auction!'

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- update leilao  ----")
    logger.debug(f'payload: {payload}')

    user_id= return_user_id(payload["authToken"], cur)
    if user_id==-1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'

    # parameterized queries, good for security and performance
    statement = """SELECT create_copy_to_update(%s, %s)"""

    values = (leilaoId, user_id)

    try:
        cur.execute(statement, values)
        l_row= cur.fetchone()
        logger.info(str(l_row))
        if l_row[0] == -1:
            result = 'Error: Can\'t edit an old version of an auction'
        elif l_row[0]==-2:
            result = 'Error: Can\'t edit an auction you didn\'t open'
        elif l_row[0]==-3:
            result = 'The auction you are trying to edit does not exist!'
        else:
            statement2 = """
                select * from leilao where leilaoid = %s
            """
            value2 = (l_row[0],)
            cur.execute(statement2, value2)
            row_to_update= cur.fetchone()

            descricao = row_to_update[2]
            if "descricao" in payload:
                # cur.execute("update leilao set descricao = %s where leilaoid = %s", (payload["descricao"],l_id[0]))
                descricao = payload["descricao"]
            titulo = row_to_update[1]
            if "titulo" in payload:
                # cur.execute("update leilao set titulo = %s where leilaoid = %s", (payload["titulo"],l_id[0]))
                titulo = payload["titulo"]
            cur.execute("update leilao set titulo = %s, descricao= %s where leilaoid = %s", (titulo, descricao, row_to_update[0]))
            
            logger.info("after update")
            cur.execute('commit')
            #cur.execute("select leilaoid, titulo, descricao, artigo_artigoid, expira_leilao from leilao where leilaoid= %s",(l_row[0],))
            #res=cur.fetchone()
            result={'leilaoId': int(row_to_update[0]),'titulo' : titulo, 'descricao': descricao, 'artigoid': row_to_update[3], 'expire_date': row_to_update[4] }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute('rollback')
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

@app.route("/dbproj/leilao/<leilaoId>", methods=['GET']) # consulta completa de leilao
def details_auction(leilaoId):
    logger.info("###              DEMO: GET /leilao/id         ###");   
    payload = request.get_json()

    if "authToken" not in payload:
        return 'authToken is required to consult auction\'s details!'

    conn = db_connection()
    cur = conn.cursor()

    authToken = payload["authToken"]

    logger.debug(f'authToken: {authToken}')
    user_id= return_user_id(authToken, cur)
    if user_id==-1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'
    
    # parameterized queries, good for security and performance
    statement1 = """
        SELECT titulo, descricao, precoatual, expira_leilao , utilizador_userid
        from leilao ll where
        ll.leilaoId = %s and ll.leilaoId = ll.versao_atual
    """

    statement2 = """
    select * from artigo where artigoid = (select artigo_artigoid from leilao where leilaoId = %s);
    """

    statement3 = """
        select m.conteudo, m.data, u.username
        from mensagem m, utilizador u
        where leilao_leilaoid = %s
        and u.userid = m.utilizador_userid;
    """
    
    statement4 = """
        select l.licitaid, l.valor, l.licita_hora, u.username 
        from licita l , utilizador u
        where leilao_leilaoid = %s
        and u.userid = l.utilizador_userid;
    """

    values = (leilaoId,)

    try:
        payload = []
        cur.execute(statement1, values)
        row=cur.fetchone()
        if row != []:
            payload.append("General info on auction %s:" % leilaoId)
            content = [{'titulo': row[0], 'descricao': row[1], 'precoatual':row[2], 'expira_leilao':row[3]}]

            owner_id = row[4]
            cur.execute ("select nome from utilizador where userid = %s", (owner_id, ))
            owner_username = cur.fetchone()
            content["organizador"]= owner_username[0]

            payload.append(content) # appending to the payload to be returned 
            payload.append("Item info")
            cur.execute(statement2, values)
            row=cur.fetchone()
            content = [{'artigoId':row[0], 'nome':row[1]}]
            # content = [row]
            payload.append(content)

            payload.append("Mensagens:")
            cur.execute(statement3, values)
            content = []
            rows= cur.fetchall()
            for row in rows:
                content.append({'conteudo': row[0],'data': row[1], 'username':row[2]})
            payload.append(content)

            payload.append("Licitacoes:")

            cur.execute(statement4, values)
            content = []
            rows= cur.fetchall()
            for row in rows:
                content.append({'licitaid': row[0],'valor': row[1], 'licita_hora': row[2], 'username':row[3]})
            payload.append(content)

        
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = 'Error obtaining the info you asked for :(!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(payload)

@app.route("/dbproj/leilao/<leilaoId>/<licitacao>", methods=['PUT']) # insercao de artigo
def bid_leilao(leilaoId, licitacao):
    logger.info("###              DEMO: PUT /leilao/id         ###");   
    payload = request.get_json()

    if "authToken" not in payload:
        return 'authToken is needed to make a bid'

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'leilaoId: {leilaoId}; licitacao: {licitacao}')

    user_id= return_user_id(payload["authToken"], cur)
    if user_id==-1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'
    

    value_licita = float(licitacao)
    # parameterized queries, good for security and performance
    statement = """
    begin transaction isolation level serializable;
    SELECT licitacao(%s, %s, %s)
    """

    values = (user_id, leilaoId, licitacao)

    try:
        cur.execute(statement, values)
        res=cur.fetchone()
        res= res[0]
        logger.info(f'{res}')
        if res== -1:
            result = 'You need to bid higher than the last bid'
            cur.execute('rollback')
        elif res==-2:
            result = 'This auction has already ended!'
            cur.execute('rollback')
        elif res== -3:
            result = 'You cannot bid in your own auction!'
            cur.execute('rollback')
        else:
            cur.execute('commit')
            result = 'Your bid has been registered!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Error while processing your bid!'
        cur.execute('rollback')
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

@app.route("/dbproj/lookup/", methods=['GET']) # insercao de artigo
def related_auctions():
    logger.info("###              DEMO: PUT /leilao/id         ###");   
    payload = request.get_json()

    if "authToken" not in payload:
        return 'authToken is needed to list related auctions'

    authToken= payload["authToken"]

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'authToken: {authToken}')
    authToken = payload["authToken"]
    user_id= return_user_id(authToken, cur)
    if user_id==-1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'
    
    # parameterized queries, good for security and performance
    statement = """
        SELECT leilaoid, titulo, descricao, precoatual, expira_leilao 
        from leilao ll where
        ll.utilizador_userid = %s and ll.leilaoid = ll.versao_atual
        or exists (select licita_utilizador_utilizadorid 
                    from notificacao_licita_licita n
                     where n.utilizador_userid = %s and n.licita_licitaid =ll.leilaoid )
        """

    values = (user_id, user_id)

    try:
        payload = []
        cur.execute(statement, values)
        rows=cur.fetchall()
        for row in rows:
            logger.debug(row)
            content = {'leilaoId': row[0],'titulo': row[1], 'descricao': row[2], 'precoatual':row[3], 'data_expira':row[4]}
            payload.append(content) # appending to the payload to be returned 
        
        
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        payload = 'Error obtaining the info you asked for :(!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(payload)

##      Demo GET
##
## Obtain department with ndep <ndep>
##
## To use it, access: 
## 
##   http://localhost:8080/departments/10
##

@app.route("/dbproj/artigo/<artigoId>", methods=['GET'])
def get_item(artigoId):
    logger.info("###              DEMO: GET /artigos/<artigoId>              ###");   
    payload = request.get_json()

    if "authToken" not in payload:
        return 'authToken is needed to consult an item'

    conn = db_connection()
    cur = conn.cursor()

    authToken = payload["authToken"]
    if return_user_id(authToken, cur)==-1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'
    
    logger.debug(f'artigoId: {artigoId}')
    
    cur.execute("SELECT artigoId, nome FROM artigo where artigoid = %s", (artigoId,) )
    rows = cur.fetchall()
    if rows is None:
        return 'No matches for your search!'
    row = rows[0]
    logger.debug("---- selected item  ----")
    logger.debug(row)
    content = {'artigoId': int(row[0]), 'nome': row[1] }
    conn.close ()
    return jsonify(content)

##
##      Demo POST
##
## Add a new department in a JSON payload
##
## To use it, you need to use postman or curl: 
##
##   curl -X POST http://localhost:8080/departments/ -H "Content-Type: application/json" -d '{"localidade": "Polo II", "ndep": 69, "nome": "Seguranca"}'
##


@app.route("/dbproj/artigo/", methods=['POST']) # insercao de artigo
def insert_item():
    logger.info("###              DEMO: POST /artigo            ###");   
    payload = request.get_json()

    if "authToken" not in payload:
        return 'authToken is needed to add an item'

    conn = db_connection()
    cur = conn.cursor()

    authToken = payload["authToken"]
    if return_user_id(authToken, cur)==-1:
        if conn is not None:
            conn.close()
        return 'Invalid token: check it or login again'

    logger.info("---- new artigo ----")
    logger.debug(f'payload: {payload}')

    # parameterized queries, good for security and performance
    statement = """
                  INSERT INTO artigo (artigoId, nome) 
                          VALUES ( %s,   %s  )"""

    values = (payload["artigoId"], payload["nome"])

    try:
        cur.execute(statement, values)
        cur.execute('commit')
        result = 'Inserted!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute('rollback')
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(user = usr,
                            password = pswd,
                            host = hst,
                            port = "5432",
                            database = dbase)
    db.set_session(autocommit=False)
    return db


##########################################################
## MAIN
##########################################################
if __name__ == "__main__":

    ret = dec_file('.creds_crypto')
    print(ret)
    ar = ret.split(',')
    print('User: %s' % ar[0])
    usr= ar[0]
    print('Password: %s' % ar[1])
    pswd= ar[1]
    print('Host: %s' % ar[2])
    hst= ar[2]
    print('Database: %s' % ar[3])
    dbase= ar[3]


    x = threading.Thread(target=warn_winning_bidders, args=())
    x.start()
    print('Boo1')
    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    print('Boo2')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    print('Boo3')
    # create formatt
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                              '%H:%M:%S')
                              # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    print('Boo4')

    time.sleep(1) # just to let the DB start before this print :-)


    logger.info("\n---------------------------------------------------------------\n" + 
                  "API v1.0 online: http://localhost:8080/departments/\n\n")

    app.run(host="0.0.0.0", debug=True, threaded=True)
