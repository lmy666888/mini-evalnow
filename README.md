# Mini EvalNow

学生与教师之间的双向反馈平台。目前包含最小 FastAPI 应用和健康检查测试。

以下命令均在项目根目录执行。

## 激活虚拟环境

如果尚未创建虚拟环境，先运行 `python3 -m venv .venv`。

```bash
source .venv/bin/activate
```

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 启动应用

```bash
uvicorn app.main:app --reload
```

- `http://127.0.0.1:8000/` 返回 `{"message": "Mini EvalNow API"}`。
- `http://127.0.0.1:8000/health` 返回 `{"status": "ok"}`。

## 运行测试

数据库测试需要本机 PostgreSQL 正在运行，且已创建数据库和应用用户。
在项目根目录的 `.env` 中设置 `DATABASE_URL`，使用
`postgresql+psycopg://<username>:<password>@localhost:5432/mini_evalnow` 格式。
请替换占位符，并对用户名和密码中的 URL 特殊字符进行百分号编码。
`.env` 已被 Git 忽略，不要提交数据库密码。
数据库测试通过 SQLAlchemy Session 执行 `SELECT 1`，不会创建表。

```bash
pytest
```

## 数据库迁移

Alembic 从 `.env` 读取 `DATABASE_URL`。创建新 migration 后应先检查生成内容，
再应用到数据库：

```bash
alembic upgrade head
```

查看数据库当前 revision：

```bash
alembic current
```

## JWT 配置

认证接口需要在 `.env` 中设置以下变量：

```dotenv
JWT_SECRET_KEY=<strong-random-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

`JWT_SECRET_KEY` 应使用独立的强随机值，不要提交到 Git。支持的算法为
`HS256`、`HS384` 和 `HS512`，密钥至少应分别为 32、48 和 64 bytes。
