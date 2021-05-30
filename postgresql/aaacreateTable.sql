CREATE TABLE artigo (
	artigoid BIGINT,
	nome	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(artigoid)
);

CREATE TABLE utilizador (
	userid	 BIGINT UNIQUE NOT NULL,
	username VARCHAR(128) UNIQUE NOT NULL,
	email	 VARCHAR(256) UNIQUE NOT NULL,
	password  VARCHAR(256) NOT NULL,
	PRIMARY KEY(userid)
);

CREATE TABLE licita (
	licitaid		 BIGINT,
	valor		 DOUBLE PRECISION NOT NULL,
	licita_hora	 TIMESTAMP WITH TIME ZONE NOT NULL,
	leilao_leilaoid	 BIGINT NOT NULL,
	utilizador_userid BIGINT NOT NULL,
	PRIMARY KEY(licitaid)
);

CREATE TABLE token (
	authtoken	 VARCHAR(128) UNIQUE NOT NULL,
	expira_token	 TIMESTAMP WITH TIME ZONE NOT NULL,
	utilizador_userid BIGINT NOT NULL
);

CREATE TABLE leilao (
	leilaoid		 BIGINT,
	titulo		 VARCHAR(512) NOT NULL,
	descricao	 VARCHAR(512) NOT NULL,
	precominimo	 DOUBLE PRECISION NOT NULL DEFAULT 0,
	precoatual	 DOUBLE PRECISION NOT NULL,
	expira_leilao	 TIMESTAMP WITH TIME ZONE NOT NULL,
	dataabertura	 TIMESTAMP WITH TIME ZONE,
	versao_atual	 BIGINT NOT NULL,
	utilizador_userid BIGINT NOT NULL,
	artigo_artigoid	 BIGINT NOT NULL,
	PRIMARY KEY(leilaoid)
);

CREATE TABLE mensagem (
	msg_id		 BIGINT,
	conteudo		 VARCHAR(512) NOT NULL,
	data		 TIMESTAMP WITH TIME ZONE NOT NULL,
	utilizador_userid BIGINT NOT NULL,
	leilao_leilaoid	 BIGINT NOT NULL,
	PRIMARY KEY(msg_id)
);

CREATE TABLE notificacao (
	id_notif BIGINT,
	assunto	 VARCHAR(512),
	conteudo VARCHAR(512) NOT NULL,
	data	 TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY(id_notif)
);

CREATE TABLE notificacao_msg (
	mensagem_msg_id	 BIGINT NOT NULL,
	notificacao_id_notif BIGINT,
	PRIMARY KEY(notificacao_id_notif)
);

CREATE TABLE notificacao_licita (
	licita_licitaid	 BIGINT NOT NULL,
	notificacao_id_notif BIGINT,
	PRIMARY KEY(notificacao_id_notif)
);

CREATE TABLE utilizador_notificacao (
	utilizador_userid	 BIGINT,
	notificacao_id_notif BIGINT,
	lida boolean,
	PRIMARY KEY(utilizador_userid,notificacao_id_notif)
);


ALTER TABLE licita ADD CONSTRAINT licita_fk1 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE licita ADD CONSTRAINT licita_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE token ADD CONSTRAINT token_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk2 FOREIGN KEY (artigo_artigoid) REFERENCES artigo(artigoid);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk2 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE notificacao_msg ADD CONSTRAINT notificacao_msg_fk1 FOREIGN KEY (mensagem_msg_id) REFERENCES mensagem(msg_id);
ALTER TABLE notificacao_msg ADD CONSTRAINT notificacao_msg_fk2 FOREIGN KEY (notificacao_id_notif) REFERENCES notificacao(id_notif);
ALTER TABLE notificacao_licita ADD CONSTRAINT notificacao_licita_fk1 FOREIGN KEY (licita_licitaid) REFERENCES licita(licitaid);
ALTER TABLE notificacao_licita ADD CONSTRAINT notificacao_licita_fk2 FOREIGN KEY (notificacao_id_notif) REFERENCES notificacao(id_notif);
ALTER TABLE utilizador_notificacao ADD CONSTRAINT utilizador_notificacao_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE utilizador_notificacao ADD CONSTRAINT utilizador_notificacao_fk2 FOREIGN KEY (notificacao_id_notif) REFERENCES notificacao(id_notif);
