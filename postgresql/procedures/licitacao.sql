create or REPLACE function licitacao(u_id utilizador.userId%type, l_id licita.licitaid%type, val licita.valor%type)
returns licita.licitaid%type
language plpgsql
AS
$$
declare
    aid_notif notificacao.id_notif%type;
    curr_leilao leilao%rowtype;
    curs_act_users cursor FOR
        select distinct utilizador_userid from licita l where
            l.leilao_leilaoid = l_id and l.utilizador_userid != u_id;
    no_users_act integer;
    no_licit integer;
    bidder_username utilizador.username%type;
BEGIN
    select * into curr_leilao from leilao where leilaoid = l_id for update; -- locking this row of the table...
    if curr_leilao.precoatual >= val THEN
        return -1;
    elsif curr_leilao.expira_leilao < NOW() then
        return -2;
    elsif u_id = curr_leilao.utilizador_userid then
        return -3;
    end if;
    select coalesce(max(licitaid),0)+1 into no_licit from licita;
    insert into licita values(no_licit, val, now(), l_id, u_id); 
    update leilao set precoatual = val where leilaoid = l_id;

    select count(distinct utilizador_userid) into no_users_act 
    from licita l 
    where l.leilao_leilaoid = l_id and l.utilizador_userid != u_id;
    select coalesce(max(id_notif),0)+1 into aid_notif from notificacao;
    select username into bidder_username from utilizador where userid = u_id;
    if no_users_act >= 1 then -- isto poderia ser feito com um trigger
        insert into notificacao values (aid_notif, 'Notificação de licitação ultrapassada', 'A sua licitação foi ultrapassada no leilão ' || l_id, now());
        for usr in curs_act_users
        loop
            insert into utilizador_notificacao values (usr.utilizador_userid, aid_notif, false);
        end loop;
        insert into notificacao_licita values (no_licit, aid_notif); -- notificar utilizadores que licitaram neste leilao
        aid_notif := aid_notif +1;
    end if;

    -- notificar organizador do leilao
    insert into notificacao values (aid_notif, 'Nova licitação no seu leilão', 'Desenvolvimento no leilão ' || l_id || ': utilizador  '||bidder_username ||' licitou '||' '||val||'.', now());
    insert into notificacao_licita values(no_licit, aid_notif); -- isto tb poderia ser feito com um trigger...
    insert into utilizador_notificacao values (curr_leilao.utilizador_userid, aid_notif,false);
    return 0;
end;
$$;