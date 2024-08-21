BEGIN TRANSACTION;
DROP TABLE IF EXISTS "migration_history";
CREATE TABLE IF NOT EXISTS "migration_history" (
	"version"	TEXT NOT NULL,
	"created_ts"	BIGINT NOT NULL DEFAULT (strftime('%s', 'now')),
	PRIMARY KEY("version")
);
DROP TABLE IF EXISTS "system_setting";
CREATE TABLE IF NOT EXISTS "system_setting" (
	"name"	TEXT NOT NULL,
	"value"	TEXT NOT NULL,
	"description"	TEXT NOT NULL DEFAULT '',
	UNIQUE("name")
);
DROP TABLE IF EXISTS "user";
CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER,
	"created_ts"	BIGINT NOT NULL DEFAULT (strftime('%s', 'now')),
	"updated_ts"	BIGINT NOT NULL DEFAULT (strftime('%s', 'now')),
	"row_status"	TEXT NOT NULL DEFAULT 'NORMAL' CHECK("row_status" IN ('NORMAL', 'ARCHIVED')),
	"username"	TEXT NOT NULL UNIQUE,
	"role"	TEXT NOT NULL DEFAULT 'USER' CHECK("role" IN ('HOST', 'ADMIN', 'USER')),
	"email"	TEXT NOT NULL DEFAULT '',
	"nickname"	TEXT NOT NULL DEFAULT '',
	"password_hash"	TEXT NOT NULL,
	"avatar_url"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "user_setting";
CREATE TABLE IF NOT EXISTS "user_setting" (
	"user_id"	INTEGER NOT NULL,
	"key"	TEXT NOT NULL,
	"value"	TEXT NOT NULL,
	UNIQUE("user_id","key")
);
DROP TABLE IF EXISTS "memo";
CREATE TABLE IF NOT EXISTS "memo" (
	"id"	INTEGER,
	"creator_id"	INTEGER NOT NULL,
	"created_ts"	BIGINT NOT NULL DEFAULT (strftime('%s', 'now')),
	"updated_ts"	BIGINT NOT NULL DEFAULT (strftime('%s', 'now')),
	"row_status"	TEXT NOT NULL DEFAULT 'NORMAL' CHECK("row_status" IN ('NORMAL', 'ARCHIVED')),
	"content"	TEXT NOT NULL DEFAULT '',
	"visibility"	TEXT NOT NULL DEFAULT 'PRIVATE' CHECK("visibility" IN ('PUBLIC', 'PROTECTED', 'PRIVATE')),
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "memo_organizer";
CREATE TABLE IF NOT EXISTS "memo_organizer" (
	"memo_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"pinned"	INTEGER NOT NULL DEFAULT 0 CHECK("pinned" IN (0, 1)),
	UNIQUE("memo_id","user_id")
);
DROP TABLE IF EXISTS "memo_relation";
CREATE TABLE IF NOT EXISTS "memo_relation" (
	"memo_id"	INTEGER NOT NULL,
	"related_memo_id"	INTEGER NOT NULL,
	"type"	TEXT NOT NULL,
	UNIQUE("memo_id","related_memo_id","type")
);
DROP TABLE IF EXISTS "resource";
CREATE TABLE IF NOT EXISTS "resource" (
	"id"	INTEGER,
	"creator_id"	INTEGER NOT NULL,
	"created_ts"	BIGINT NOT NULL DEFAULT (strftime('%s', 'now')),
	"updated_ts"	BIGINT NOT NULL DEFAULT (strftime('%s', 'now')),
	"filename"	TEXT NOT NULL DEFAULT '',
	"blob"	BLOB DEFAULT NULL,
	"external_link"	TEXT NOT NULL DEFAULT '',
	"type"	TEXT NOT NULL DEFAULT '',
	"size"	INTEGER NOT NULL DEFAULT 0,
	"internal_path"	TEXT NOT NULL DEFAULT '',
	"memo_id"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "tag";
CREATE TABLE IF NOT EXISTS "tag" (
	"name"	TEXT NOT NULL,
	"creator_id"	INTEGER NOT NULL,
	UNIQUE("name","creator_id")
);
DROP TABLE IF EXISTS "activity";
CREATE TABLE IF NOT EXISTS "activity" (
	"id"	INTEGER,
	"creator_id"	INTEGER NOT NULL,
	"created_ts"	BIGINT NOT NULL DEFAULT (strftime('%s', 'now')),
	"type"	TEXT NOT NULL DEFAULT '',
	"level"	TEXT NOT NULL DEFAULT 'INFO' CHECK("level" IN ('INFO', 'WARN', 'ERROR')),
	"payload"	TEXT NOT NULL DEFAULT '{}',
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "storage";
CREATE TABLE IF NOT EXISTS "storage" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"type"	TEXT NOT NULL,
	"config"	TEXT NOT NULL DEFAULT '{}',
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "idp";
CREATE TABLE IF NOT EXISTS "idp" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"type"	TEXT NOT NULL,
	"identifier_filter"	TEXT NOT NULL DEFAULT '',
	"config"	TEXT NOT NULL DEFAULT '{}',
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "inbox";
CREATE TABLE IF NOT EXISTS "inbox" (
	"id"	INTEGER,
	"created_ts"	BIGINT NOT NULL DEFAULT (strftime('%s', 'now')),
	"sender_id"	INTEGER NOT NULL,
	"receiver_id"	INTEGER NOT NULL,
	"status"	TEXT NOT NULL,
	"message"	TEXT NOT NULL DEFAULT '{}',
	PRIMARY KEY("id" AUTOINCREMENT)
);