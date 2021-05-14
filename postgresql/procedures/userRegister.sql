create or replace function registerUser(uname utilizador.username%type, pswd utilizador.password%type, eml utilizador.email%type) 
returns utilizador.userId%type
language plpgsql
as $$
declare
    userRet utilizador.userId%type;
    uId integer;
begin
    userRet := -1;
    select count(*) into uId from utilizador; 
    insert into utilizador (userId, username, password, email) 
    values(uId, uname, pswd, eml);
    select userId  
        into userRet  
        from utilizador u   
        where u.username = uname;
    return userRet;
end;
$$;