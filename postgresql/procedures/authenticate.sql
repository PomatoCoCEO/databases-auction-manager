
create or replace function generate_token() returns token.authtoken%type
language plpgsql
as  $$
declare 
    tok token.authtoken%type;
    unico integer;
begin
    unico := -1;
    while unico != 0
    loop
        select floor(random() * 2000000) into tok;
        SELECT count(*) into unico
        from token
        where token.authtoken = tok;
    end loop;
    return tok;
end;
$$;

-- use index for username
create or replace function authenticate(uname utilizador.username%type, pswd utilizador.password%type) returns token.authtoken%type
language plpgsql
as  $$
declare 
    pass utilizador.password%type;
    tok token%rowtype;
begin
    select userId, password into tok.utilizador_userid , pass
    from utilizador u
    where u.username= uname;
    if pass= pswd THEN
        tok.authtoken := generate_token();
        insert into token
            values(tok.authToken, CURRENT_DATE+INTERVAL '1 hour',tok.utilizador_userId);
        -- return token
    else
        tok.authToken := -1;
        -- return invalid token
    end if;
    
    return tok.authToken;
end;
$$;

