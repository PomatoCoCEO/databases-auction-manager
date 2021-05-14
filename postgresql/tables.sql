CREATE TABLE artigo (
	artigoid BIGINT,
	nome	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(artigoid)
);

CREATE TABLE utilizador (
	userid	 BIGINT UNIQUE NOT NULL,
	username VARCHAR(128) UNIQUE NOT NULL,
	email	 VARCHAR(256) UNIQUE NOT NULL,
	password BYTEA NOT NULL,
	PRIMARY KEY(userid)
);

CREATE TABLE token (
	authtoken	 NUMERIC(15) UNIQUE NOT NULL,
	expira_token	 TIMESTAMP NOT NULL,
	utilizador_userid BIGINT NOT NULL
);

CREATE TABLE leilao (
	leilaoid		 BIGINT,
	titulo		 VARCHAR(512) NOT NULL,
	descricao	 VARCHAR(512) NOT NULL,
	precominimo	 DOUBLE PRECISION NOT NULL DEFAULT 0,
	precoatual	 DOUBLE PRECISION NOT NULL,
	expira_leilao	 TIMESTAMP NOT NULL,
	dataabertura	 TIMESTAMP,
	utilizador_userid BIGINT NOT NULL,
	artigo_artigoid	 BIGINT NOT NULL,
	PRIMARY KEY(leilaoid)
);

CREATE TABLE mensagem_notificacao_msg (
	conteudo		 VARCHAR(512) NOT NULL,
	data		 TIMESTAMP NOT NULL,
	leilao_leilaoid	 BIGINT,
	utilizador_userid	 BIGINT,
	notificacao_id_notif BIGINT,
	PRIMARY KEY(notificacao_id_notif)
);

CREATE TABLE notificacao (
	id_notif BIGINT,
	assunto	 VARCHAR(512),
	conteudo VARCHAR(512) NOT NULL,
	data	 TIMESTAMP NOT NULL,
	lida	 BOOL,
	PRIMARY KEY(id_notif)
);

CREATE TABLE notificacao_licita_licita (
	licita_licitaid		 BIGINT UNIQUE NOT NULL,
	licita_valor		 DOUBLE PRECISION NOT NULL,
	licita_licita_hora	 TIMESTAMP NOT NULL,
	licita_leilao_leilaoid	 BIGINT UNIQUE NOT NULL,
	licita_utilizador_userid BIGINT UNIQUE NOT NULL,
	notificacao_id_notif	 BIGINT,
	PRIMARY KEY(notificacao_id_notif)
);

CREATE TABLE utilizador_notificacao (
	utilizador_userid	 BIGINT,
	notificacao_id_notif BIGINT,
	PRIMARY KEY(utilizador_userid,notificacao_id_notif)
);

-- on delete cascade

ALTER TABLE token ADD CONSTRAINT token_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk2 FOREIGN KEY (artigo_artigoid) REFERENCES artigo(artigoid);
ALTER TABLE mensagem_notificacao_msg ADD CONSTRAINT mensagem_notificacao_msg_fk1 FOREIGN KEY (notificacao_id_notif) REFERENCES notificacao(id_notif);
ALTER TABLE notificacao_licita_licita ADD CONSTRAINT notificacao_licita_licita_fk1 FOREIGN KEY (notificacao_id_notif) REFERENCES notificacao(id_notif);
ALTER TABLE utilizador_notificacao ADD CONSTRAINT utilizador_notificacao_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE utilizador_notificacao ADD CONSTRAINT utilizador_notificacao_fk2 FOREIGN KEY (notificacao_id_notif) REFERENCES notificacao(id_notif);
