create table if not exists dictionary (
	id SERIAL primary key,
	enword varchar(80) unique not null,
	ruword varchar(80) unique not null
);

create table if not exists users (
	id SERIAL primary key,
	tg_user_id bigint unique not null
);

create table if not exists usersdict (
	id SERIAL primary key,
	userdictunit integer not null references dictionary(id),
	tg_user_id integer not null references users(id)
);