create or replace procedure warn_auct_winners()
language plpgsql
AS $$
declare
    cur_ended cursor FOR
        select leilaoid , precominimo, precoatual, utilizador_userid from leilao
            where expira_leilao <= now() and acabou = false;
    winner_licita licita%rowtype;
    notif_id notificacao.id_notif%type;
    leilao_row leilao%rowtype;
BEGIN
    for val in cur_ended
    loop

        SELECT coalesce(max(id_notif),0 )+1
            into notif_id
            from notificacao;
            
        if val.precominimo > val.precoatual THEN
                insert into notificacao
                values(notif_id, 
                    'Aviso: Ninguem licitou no seu leilao (nº'||val.leilaoid||')!',
                    'Lamentamos informar que não houve licitações no seu leilão n º '||val.leilaoid || ', que acabou de terminar.',
                    now());
            insert into utilizador_notificacao
                values (val.utilizador_userid, notif_id, false);
        end if;
        select *
            into winner_licita
            from licita
            where leilao_leilaoid = val.leilaoid and valor = (select max(valor) from licita where leilao_leilaoid = val.leilaoid);
        
        insert into notificacao
            values(notif_id, 
                'Aviso: venceu o leilao '||val.leilaoid||'!',
                'Venceu o leilao '||val.leilaoid||', pagando o valor '||winner_licita.valor||'!',
                now());
        insert into utilizador_notificacao
            values (winner_licita.utilizador_userid, notif_id, false);
    end loop;
end;
$$;