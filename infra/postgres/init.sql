-- 這個腳本會由 docker-compose.yml 中定義的超級使用者 (例如 'postgres') 來執行。
-- 它的任務是為我們的 Flask 應用程式建立一個權限更受限的專用角色。

-- 檢查專用使用者 'my_app_user' 是否存在，如果不存在，則建立它並設定密碼。
-- 這樣可以確保即使資料庫已經存在，重新啟動容器也不會出錯。
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = '${POSTGRES_APP_USER}') THEN

      CREATE ROLE ${POSTGRES_APP_USER} WITH LOGIN PASSWORD '${POSTGRES_APP_PASSWORD}';
   END IF;
END
$do$;

-- 將由 POSTGRES_DB 環境變數所建立的資料庫的所有權限，授予給我們剛建立的應用程式專用使用者。
-- 'GRANT ALL PRIVILEGES' 允許我們的應用程式使用者進行連線、讀寫資料，
-- 以及最重要的，允許 Flask-Migrate (Alembic) 執行 CREATE/ALTER TABLE 等操作。
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_APP_DB} TO ${POSTGRES_APP_USER};

-- (可選但推薦) 為了讓專用使用者能在此資料庫中建立物件 (例如 Alembic 需要建立版本表)
-- 需要將資料庫的 public schema 權限也授予它。
GRANT USAGE, CREATE ON SCHEMA public TO ${POSTGRES_APP_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${POSTGRES_APP_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${POSTGRES_APP_USER};
