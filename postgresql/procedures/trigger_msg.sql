create or replace function msg_update_notif()
returns trigger
language plpgsql
as $$
declare 
    curs_act_users cursor FOR
    select distinct utilizador_userid from mensagem m 
    where m.leilao_leilaoid = new.leilao_leilaoid 
        and m.utilizador_userid !=new.utilizador_userid;
    id_notif_msg notificacao.id_notif%type;
    user_author utilizador.username%type;
    owner_id utilizador.userid%type;
    owner_wrote boolean;
begin
    -- new=new;
    if not exists (select distinct utilizador_userid from mensagem m 
        where m.leilao_leilaoid = new.leilao_leilaoid 
            and m.utilizador_userid !=new.utilizador_userid) THEN return null;
    end if;
    select coalesce(max(id_notif),-1)+1 into id_notif_msg from notificacao;
    select username into user_author from utilizador where userid = new.utilizador_userid;
    insert into notificacao
        values (id_notif_msg, 'Nova mensagem no leilão '||new.leilao_leilaoid, 'O utilizador '|| user_author||' escreveu no mural do leilão '||new.leilao_leilaoid||':'||new.conteudo, now());
    insert into notificacao_msg values(new.msg_id, id_notif_msg);
    for usr in curs_act_users
    loop
        if usr.utilizador_userid = owner_id THEN
            owner_wrote = true;
        end if;
        insert into utilizador_notificacao
            values (usr.utilizador_userid, id_notif_msg, false);
    end loop;
    if owner_wrote = false then
        select utilizador_userid into owner_id from leilao where leilaoid = new.leilao_leilaoid;
        insert into utilizador_notificacao values (owner_id, id_notif_msg, false);
    end if;
    return new;
end;
$$;

create trigger tr_msg 
after insert on mensagem
for each ROW
execute procedure msg_update_notif();