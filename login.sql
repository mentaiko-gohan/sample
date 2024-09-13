- ユーザー管理用テーブル作成

create table user(
    email varchar(128) primary key,
    password varbinary(200)
);

insert into user (email, password) values ('udon@funa.com', aes_encrypt('udon', 'funa'));
insert into user (email, password) values ('maguro@funa.com', aes_encrypt('maguro', 'funa'));

#暗号化を解除した状態で登録内容を確認できる
select email, cast(aes_decrypt(password, 'funa') as char) as password from user;
#暗号化したまま登録内容を確認
select * from user;