create or replace procedure warn_auct_winners()
language plpgsql
AS $$
declare
    cur_ended cursor FOR
        select leilaoid from leilao
            where expira_leilao <= now();
    winner_licita licita%rowtype;
    notif_id notificacao.id_notif%type;
BEGIN
    for val in cur_ended
    loop
        select *
            into winner_licita
            from licita
            where leilao_leilaoid = val and licita_valor = (select max(licita_valor) from licita where leilao_leilaoid = val);
        SELECT coalesce(max(id_notif),0 )+1
            into notif_id
            from notificacao;
        insert into notificacao
            values(notif_id, 
                'Aviso: venceu o leilao '||val||'!',
                'Venceu o leilao '||val||', pagando o valor '||winner_licita.licita_valor||'!',
                current_time, 
                false);
        insert into utilizador_notificacao
            values (winner_licita.utilizador_userid, notif_id, false);
        insert into notificacao_licita
            values (winner_licita.licitaid, notif_id);
    end loop;

end;
$$;