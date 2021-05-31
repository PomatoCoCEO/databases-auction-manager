create or replace function insert_auction(u_id leilao.utilizador_userid%type, a_id leilao.artigo_artigoid%type, p_min leilao.precominimo%type, 
    title leilao.titulo%type, descr leilao.descricao%type, expire_date leilao.expira_leilao%type, item_name artigo.nome%type)
returns leilao.leilaoid%type
language plpgsql
as  $$
declare 
    l_id integer;
    art_row artigo%rowtype;
BEGIN
    SELECT * into art_row from artigo where a_id = artigoid;
    if art_row is null then
        insert into artigo values( a_id , item_name);
    elsif upper(art_row.nome) != upper(item_name) then
        return -1;
    end if;
    IF EXPIRE_DATE < NOW() THEN
        RETURN -2;
    END IF;

    select coalesce(max(leilaoid), 0)+1 into l_id from leilao;
    insert into leilao( leilaoid, titulo, descricao, precominimo, precoatual, expira_leilao,dataabertura,utilizador_userid,artigo_artigoid, versao_atual )
        values(l_id, title, descr, p_min, p_min-0.01, expire_date, now(), u_id, a_id, l_id);
    return l_id;
end;
$$;

create or replace function create_copy_to_update(l_id leilao.leilaoid%type, u_id utilizador.userid%type)
returns leilao.leilaoid%type
language plpgsql
as  $$
declare 
    l_id_novo integer;
    l_row leilao%rowtype;
    curs_users cursor FOR  
        select distinct utilizador_userid from mensagem where leilao_leilaoid = l_id
        union select distinct utilizador_userid from licita where leilao_leilaoid = l_id;
    aid_notif notificacao.id_notif%type;
BEGIN
    select coalesce(max(leilaoid),-1)+1 into l_id_novo from leilao;
    
    if not exists(select * from leilao where leilaoid = l_id) THEN
        return -3;
    end if;
    select * into l_row from leilao where leilaoid = l_id;
    if l_row.utilizador_userid != u_id THEN
        return -2;
    end if;
    if l_row.leilaoid != l_row.versao_atual then
        return -1;
    end if;
    l_row.leilaoId := l_id_novo;
    insert into leilao values (l_row.*);
    update leilao set versao_atual = l_id_novo where versao_atual = l_id or leilaoid=l_id;
    update mensagem set leilao_leilaoid = l_id_novo where leilao_leilaoid = l_id;
    update licita set leilao_leilaoid = l_id_novo where leilao_leilaoid = l_id;
    select coalesce(max(id_notif), 0)+1 into aid_notif from notificacao;
    insert into notificacao (id_notif, assunto, conteudo, data) values
            (aid_notif, 'Alteração de informação de leilão', 
            'O leilão '||l_id||' sofreu alterações na descrição. Agora é identificado pelo número '||l_id_novo||'.', 
            now());
    if not exists(select distinct utilizador_userid from mensagem where leilao_leilaoid = l_id
        union select distinct utilizador_userid from licita where leilao_leilaoid = l_id) THEN
        return l_id_novo;
    end if;
    for usr in curs_users
    loop
        insert into utilizador_notificacao values (usr.utilizador_userid, aid_notif, false);
    end loop;
    return l_id_novo;--l_id_novo;
end;
$$;
