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
