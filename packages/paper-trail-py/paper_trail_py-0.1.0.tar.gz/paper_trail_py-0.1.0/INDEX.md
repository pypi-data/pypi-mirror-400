# 📑 PaperTrail-Py 项目索引

> 快速导航到项目的各个部分

## 🚀 快速开始

- [README.md](README.md) - 项目主页，快速了解和使用
- [QUICKSTART.md](QUICKSTART.md) - 5分钟快速入门
- [examples/complete_example.py](examples/complete_example.py) - 完整功能演示

## 📖 文档

### 核心文档
- [README.md](README.md) - 项目概览、功能介绍、API 文档
- [ARCHITECTURE.md](ARCHITECTURE.md) - 完整架构设计文档（必读）
- [QUICKSTART.md](QUICKSTART.md) - 快速入门指南
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目完成总结

### API 参考

按模块查看源码文档：

| 模块     | 功能                             | 文件                                                                 |
| -------- | -------------------------------- | -------------------------------------------------------------------- |
| 装饰器   | `@track_versions()`              | [src/paper_trail/decorators.py](src/paper_trail/decorators.py)       |
| 数据模型 | `Version` 类                     | [src/paper_trail/models.py](src/paper_trail/models.py)               |
| 查询     | `VersionQuery` API               | [src/paper_trail/query.py](src/paper_trail/query.py)                 |
| 恢复     | `reify_version()`                | [src/paper_trail/reify.py](src/paper_trail/reify.py)                 |
| 上下文   | `whodunnit`, `transaction_group` | [src/paper_trail/context.py](src/paper_trail/context.py)             |
| 序列化   | 自定义序列化器                   | [src/paper_trail/serializers.py](src/paper_trail/serializers.py)     |
| 配置     | `configure()`                    | [src/paper_trail/config.py](src/paper_trail/config.py)               |
| 异步     | 异步 API                         | [src/paper_trail/async_support.py](src/paper_trail/async_support.py) |
| 性能     | 批量操作                         | [src/paper_trail/performance.py](src/paper_trail/performance.py)     |

## 💻 源码

### 核心模块
```
src/paper_trail/
├── __init__.py          - 公共 API 导出
├── models.py            - Version 数据模型
├── decorators.py        - 装饰器实现
├── context.py           - 上下文管理
├── query.py             - 查询 API
├── reify.py             - 版本恢复
├── serializers.py       - 序列化器
├── config.py            - 配置管理
├── async_support.py     - 异步支持
└── performance.py       - 性能优化
```

### 测试
```
tests/
├── conftest.py          - Pytest 配置
├── test_decorators.py   - 装饰器测试
├── test_query.py        - 查询测试
├── test_reify.py        - 恢复测试
├── test_context.py      - 上下文测试
└── test_performance.py  - 性能测试
```

## 📝 示例代码

### 完整示例
- [examples/complete_example.py](examples/complete_example.py) - 包含所有功能的演示

### 代码片段

#### 基础使用
```python
from paper_trail import track_versions

@track_versions()
class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String)
```

#### 查询版本
```python
from paper_trail import VersionQuery

versions = (
    VersionQuery(session)
    .for_model(Article, 123)
    .order_by_time(ascending=False)
    .all()
)
```

#### 版本恢复
```python
from paper_trail import reify_version

restored = reify_version(session, version, Article, commit=True)
```

#### 上下文管理
```python
from paper_trail import whodunnit

with whodunnit('user@example.com'):
    article.title = 'Updated'
    session.commit()
```

## 🔧 配置文件

### 项目配置
- [pyproject.toml](pyproject.toml) - uv 项目配置、依赖声明
- [Makefile](Makefile) - 开发命令集合
- [.gitignore](.gitignore) - Git 忽略规则
- [.pre-commit-config.yaml](.pre-commit-config.yaml) - Pre-commit hooks

### CI/CD
- [.github/workflows/ci.yml](.github/workflows/ci.yml) - 持续集成
- [.github/workflows/publish.yml](.github/workflows/publish.yml) - PyPI 发布

## 🛠️ 开发工具

### 脚本
- [scripts/setup.sh](scripts/setup.sh) - 快速环境设置脚本

### 常用命令
```bash
# 安装
make dev-install

# 测试
make test
make test-cov

# 代码质量
make lint
make format
make type-check

# 构建
make build
make publish
```

## 📊 项目架构

### 设计文档
详见 [ARCHITECTURE.md](ARCHITECTURE.md)，包含：

1. 项目概述和理念
2. 完整技术栈
3. 详细项目结构
4. 10 大核心功能详解
5. 开发规范
6. CI/CD 配置
7. 成功标准

### 核心概念

#### 1. 版本追踪流程
```
模型变更 → SQLAlchemy 事件 → 创建 Version 记录 → 存储到数据库
```

#### 2. 数据结构
```
Version:
  - id: 主键
  - item_type: 模型表名
  - item_id: 记录 ID
  - event: create/update/destroy
  - whodunnit: 操作者
  - transaction_id: 事务分组
  - object: 完整快照（JSON）
  - object_changes: 变更增量（JSON）
  - created_at: 时间戳
```

#### 3. 查询模式
```
VersionQuery → 链式调用 → 过滤/排序 → 执行查询 → 返回结果
```

## 🎯 学习路径

### 初学者
1. 阅读 [README.md](README.md)
2. 跟随 [QUICKSTART.md](QUICKSTART.md)
3. 运行 [examples/complete_example.py](examples/complete_example.py)
4. 查看测试了解 API 用法

### 进阶开发者
1. 深入 [ARCHITECTURE.md](ARCHITECTURE.md)
2. 阅读源码（从 `__init__.py` 开始）
3. 研究测试用例
4. 参考 [CONTRIBUTING.md](CONTRIBUTING.md) 贡献代码

### 架构师
1. 研究设计决策（[ARCHITECTURE.md](ARCHITECTURE.md)）
2. 性能优化策略（[performance.py](src/paper_trail/performance.py)）
3. 扩展点分析（序列化器、配置）

## 📚 外部资源

### 依赖文档
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [uv 文档](https://github.com/astral-sh/uv)
- [pytest 文档](https://docs.pytest.org/)

### 参考项目
- [PaperTrail (Ruby)](https://github.com/paper-trail-gem/paper_trail)

### 相关标准
- [PEP 484](https://peps.python.org/pep-0484/) - Type Hints
- [PEP 621](https://peps.python.org/pep-0621/) - pyproject.toml
- [Semantic Versioning](https://semver.org/)

## 🤝 社区

### 贡献
- [CONTRIBUTING.md](CONTRIBUTING.md) - 详细贡献指南
- [Issues](https://github.com/yourusername/paper-trail-py/issues) - Bug 报告和功能请求
- [Discussions](https://github.com/yourusername/paper-trail-py/discussions) - 问答和讨论

### 支持
- 📧 Email: support@example.com
- 💬 Discussions
- 📖 Documentation

## 📄 许可证

本项目采用 [MIT License](LICENSE)

---

## 🔍 快速查找

### 想要...

| 目标         | 文档                                                         |
| ------------ | ------------------------------------------------------------ |
| 快速了解项目 | [README.md](README.md)                                       |
| 5分钟上手    | [QUICKSTART.md](QUICKSTART.md)                               |
| 查看完整示例 | [examples/complete_example.py](examples/complete_example.py) |
| 理解架构设计 | [ARCHITECTURE.md](ARCHITECTURE.md)                           |
| 贡献代码     | [CONTRIBUTING.md](CONTRIBUTING.md)                           |
| 查看项目总结 | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)                     |
| 安装依赖     | `make dev-install`                                           |
| 运行测试     | `make test`                                                  |
| 查看 API     | [src/paper_trail/](src/paper_trail/)                         |
| 学习用法     | [tests/](tests/) + [examples/](examples/)                    |

---

**最后更新**: 2026-01-07  
**项目版本**: 0.1.0  
**文档版本**: 1.0
