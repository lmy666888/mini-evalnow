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

```bash
pytest
```
