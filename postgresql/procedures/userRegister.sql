create or replace function register_user(uname utilizador.username%type, pswd utilizador.password%type, eml utilizador.email%type) 
returns utilizador.userId%type
language plpgsql
as $$
declare
    uId integer;
begin
    select coalesce(max(userid)+1, 0) into uId from utilizador; 
    insert into utilizador (userId, username, password, email) 
    values(uId, uname, pswd, eml);
    return uId;

end;
$$;