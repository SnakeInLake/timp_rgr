--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: set_log_alert_flag(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.set_log_alert_flag() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    log_level_name VARCHAR;
BEGIN
    SELECT name INTO log_level_name
    FROM log_levels
    WHERE id = NEW.log_level_id;

    IF log_level_name IN ('ERROR', 'CRITICAL') THEN
        NEW.is_alert = TRUE;

    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.set_log_alert_flag() OWNER TO postgres;

--
-- Name: trigger_set_timestamp(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trigger_set_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.trigger_set_timestamp() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: atm_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atm_logs (
    id bigint NOT NULL,
    atm_id integer NOT NULL,
    event_timestamp timestamp with time zone NOT NULL,
    log_level_id integer NOT NULL,
    event_type_id integer,
    message text NOT NULL,
    payload jsonb,
    is_alert boolean DEFAULT false,
    acknowledged_by_user_id integer,
    acknowledged_at timestamp with time zone,
    recorded_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.atm_logs OWNER TO postgres;

--
-- Name: atm_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.atm_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.atm_logs_id_seq OWNER TO postgres;

--
-- Name: atm_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.atm_logs_id_seq OWNED BY public.atm_logs.id;


--
-- Name: atm_statuses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atm_statuses (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text
);


ALTER TABLE public.atm_statuses OWNER TO postgres;

--
-- Name: atm_statuses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.atm_statuses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.atm_statuses_id_seq OWNER TO postgres;

--
-- Name: atm_statuses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.atm_statuses_id_seq OWNED BY public.atm_statuses.id;


--
-- Name: atms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.atms (
    id integer NOT NULL,
    atm_uid character varying(100) NOT NULL,
    location_description text,
    ip_address character varying(45),
    status_id integer NOT NULL,
    added_by_user_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.atms OWNER TO postgres;

--
-- Name: atms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.atms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.atms_id_seq OWNER TO postgres;

--
-- Name: atms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.atms_id_seq OWNED BY public.atms.id;


--
-- Name: event_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_types (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    category character varying(50),
    description text
);


ALTER TABLE public.event_types OWNER TO postgres;

--
-- Name: event_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.event_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_types_id_seq OWNER TO postgres;

--
-- Name: event_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.event_types_id_seq OWNED BY public.event_types.id;


--
-- Name: log_levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.log_levels (
    id integer NOT NULL,
    name character varying(20) NOT NULL,
    severity_order integer
);


ALTER TABLE public.log_levels OWNER TO postgres;

--
-- Name: log_levels_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.log_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.log_levels_id_seq OWNER TO postgres;

--
-- Name: log_levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.log_levels_id_seq OWNED BY public.log_levels.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(20) DEFAULT 'operator'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: atm_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atm_logs ALTER COLUMN id SET DEFAULT nextval('public.atm_logs_id_seq'::regclass);


--
-- Name: atm_statuses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atm_statuses ALTER COLUMN id SET DEFAULT nextval('public.atm_statuses_id_seq'::regclass);


--
-- Name: atms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atms ALTER COLUMN id SET DEFAULT nextval('public.atms_id_seq'::regclass);


--
-- Name: event_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_types ALTER COLUMN id SET DEFAULT nextval('public.event_types_id_seq'::regclass);


--
-- Name: log_levels id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.log_levels ALTER COLUMN id SET DEFAULT nextval('public.log_levels_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: atm_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.atm_logs (id, atm_id, event_timestamp, log_level_id, event_type_id, message, payload, is_alert, acknowledged_by_user_id, acknowledged_at, recorded_at) FROM stdin;
2	1	2025-05-11 20:13:02.643+07	1	1	string	{"additionalProp1": {}}	f	\N	\N	2025-05-11 20:13:22.890067+07
3	1	2025-05-11 20:13:02.643+07	4	1	string	{"additionalProp1": {}}	t	\N	\N	2025-05-11 20:13:49.946035+07
\.


--
-- Data for Name: atm_statuses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.atm_statuses (id, name, description) FROM stdin;
1	active	Банкомат в рабочем состоянии
2	maintenance	Банкомат на техническом обслуживании
3	offline	Банкомат не в сети
4	error	В банкомате зафиксирована ошибка
\.


--
-- Data for Name: atms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.atms (id, atm_uid, location_description, ip_address, status_id, added_by_user_id, created_at, updated_at) FROM stdin;
1	1242141333	aaaaaa	\N	1	35	2025-05-10 22:19:45.258681+07	2025-05-10 22:28:23.763687+07
2	12421411	aaaaaa	\N	2	35	2025-05-10 22:20:11.159345+07	2025-05-16 22:30:29.732793+07
3	1241241	\N	\N	1	37	2025-05-15 01:41:50.177278+07	2025-05-16 22:30:29.732793+07
\.


--
-- Data for Name: event_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_types (id, name, category, description) FROM stdin;
1	CASH_WITHDRAWAL	TRANSACTION	Снятие наличных
2	DEPOSIT	TRANSACTION	Внесение наличных
3	BALANCE_INQUIRY	TRANSACTION	Запрос баланса
4	PAYMENT	TRANSACTION	Осуществление платежа
5	SYSTEM_BOOT	SYSTEM_HEALTH	Загрузка системы банкомата
6	SYSTEM_SHUTDOWN	SYSTEM_HEALTH	Выключение системы банкомата
7	COMPONENT_FAILURE	SYSTEM_HEALTH	Сбой компонента (принтер, кард-ридер и т.д.)
8	LOW_CASH_LEVEL	SYSTEM_HEALTH	Низкий уровень наличных в кассете
9	TAMPER_DETECTED	SECURITY	Обнаружена попытка взлома или физического воздействия
10	INVALID_PIN_ATTEMPT	SECURITY	Попытка ввода неверного ПИН-кода
11	CARD_JAMMED	OPERATIONAL_ISSUE	Застревание карты
12	PRINTER_ERROR	OPERATIONAL_ISSUE	Ошибка принтера
13	COMMUNICATION_ERROR	CONNECTIVITY	Ошибка связи с процессинговым центром
\.


--
-- Data for Name: log_levels; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.log_levels (id, name, severity_order) FROM stdin;
1	DEBUG	1
2	INFO	2
3	WARN	3
4	ERROR	4
5	CRITICAL	5
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, role, created_at, updated_at) FROM stdin;
35	superuser	bipka@example.com	$2b$12$TCZpHwkEcMRcIFFWAagKduEdfsu.SsH2qfpvVrm34u.UkBH1VS0N6	superadmin	2025-05-08 18:21:28.716171+07	2025-05-08 18:27:42.79872+07
36	aboba	aaaaaaaaaaaa@aaaaa.com	$2b$12$QMc0eXduXIhOtqkt.QGgcOrS7VpOe94nsB3mtr/xWFu27Gl9YuY3S	operator	2025-05-09 00:08:07.964365+07	2025-05-09 00:08:07.964365+07
2	operator	user@example.com	$2b$12$YncoCqknEaROcH8Ewpt6nOi1G9Fb4zsYoLJGlFmT.y.pYzngO1Hga	operator	2025-05-08 18:14:50.660558+07	2025-05-10 22:27:51.828176+07
37	testuser2	aaaaaaa22aaa@aaaaa.com	$2b$12$6AOLNNpI9qAcnf343aeX6uhUZ3.YYsn9NibxG5Y4IzNsgQz9yFzNW	admin	2025-05-10 15:56:57.747157+07	2025-05-10 22:27:55.786523+07
1	testuser	test@example.com	$2b$12$DDAa6U5a0UWOkI7hAfMUN.4/W4zHhvqnKVkdd5YpqkyE39ASh3F0e	admin	2025-05-08 16:25:19.270218+07	2025-05-10 22:27:57.437798+07
\.


--
-- Name: atm_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.atm_logs_id_seq', 3, true);


--
-- Name: atm_statuses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.atm_statuses_id_seq', 4, true);


--
-- Name: atms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.atms_id_seq', 10, true);


--
-- Name: event_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_types_id_seq', 13, true);


--
-- Name: log_levels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.log_levels_id_seq', 5, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 37, true);


--
-- Name: atm_logs atm_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atm_logs
    ADD CONSTRAINT atm_logs_pkey PRIMARY KEY (id);


--
-- Name: atm_statuses atm_statuses_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atm_statuses
    ADD CONSTRAINT atm_statuses_name_key UNIQUE (name);


--
-- Name: atm_statuses atm_statuses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atm_statuses
    ADD CONSTRAINT atm_statuses_pkey PRIMARY KEY (id);


--
-- Name: atms atms_atm_uid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atms
    ADD CONSTRAINT atms_atm_uid_key UNIQUE (atm_uid);


--
-- Name: atms atms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atms
    ADD CONSTRAINT atms_pkey PRIMARY KEY (id);


--
-- Name: event_types event_types_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_types
    ADD CONSTRAINT event_types_name_key UNIQUE (name);


--
-- Name: event_types event_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_types
    ADD CONSTRAINT event_types_pkey PRIMARY KEY (id);


--
-- Name: log_levels log_levels_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.log_levels
    ADD CONSTRAINT log_levels_name_key UNIQUE (name);


--
-- Name: log_levels log_levels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.log_levels
    ADD CONSTRAINT log_levels_pkey PRIMARY KEY (id);


--
-- Name: log_levels log_levels_severity_order_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.log_levels
    ADD CONSTRAINT log_levels_severity_order_key UNIQUE (severity_order);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_role_check2; Type: CHECK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE public.users
    ADD CONSTRAINT users_role_check2 CHECK (((role)::text = ANY (ARRAY[('operator'::character varying)::text, ('admin'::character varying)::text, ('superadmin'::character varying)::text]))) NOT VALID;


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: atms set_timestamp_atms; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER set_timestamp_atms BEFORE UPDATE ON public.atms FOR EACH ROW EXECUTE FUNCTION public.trigger_set_timestamp();


--
-- Name: users set_timestamp_users; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER set_timestamp_users BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.trigger_set_timestamp();


--
-- Name: atm_logs trigger_set_log_alert; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_set_log_alert BEFORE INSERT ON public.atm_logs FOR EACH ROW EXECUTE FUNCTION public.set_log_alert_flag();


--
-- Name: atm_logs fk_acknowledged_by_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atm_logs
    ADD CONSTRAINT fk_acknowledged_by_user FOREIGN KEY (acknowledged_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: atms fk_added_by_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atms
    ADD CONSTRAINT fk_added_by_user FOREIGN KEY (added_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: atm_logs fk_atm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atm_logs
    ADD CONSTRAINT fk_atm FOREIGN KEY (atm_id) REFERENCES public.atms(id) ON DELETE CASCADE;


--
-- Name: atm_logs fk_event_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atm_logs
    ADD CONSTRAINT fk_event_type FOREIGN KEY (event_type_id) REFERENCES public.event_types(id);


--
-- Name: atm_logs fk_log_level; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atm_logs
    ADD CONSTRAINT fk_log_level FOREIGN KEY (log_level_id) REFERENCES public.log_levels(id);


--
-- Name: atms fk_status; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.atms
    ADD CONSTRAINT fk_status FOREIGN KEY (status_id) REFERENCES public.atm_statuses(id);


--
-- PostgreSQL database dump complete
--

