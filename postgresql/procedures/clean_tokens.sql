create or replace procedure clean_tokens()
language plpgsql
as $$
BEGIN
    delete from token
        WHERE expira_token < now();
end
$$;