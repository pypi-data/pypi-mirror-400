# 📖 PaperTrail 架构设计文档

## 🎯 项目概述

PaperTrail-Py 是一个现代化的 Python 库，为 SQLAlchemy 模型提供自动版本追踪和审计日志功能。

### 核心理念

1. **零侵入性** - 通过装饰器启用，无需修改现有模型逻辑
2. **类型安全** - 完整的类型提示，配合 mypy 使用
3. **性能优先** - 批量操作、异步支持、索引优化
4. **开发者友好** - 简洁的 API，丰富的查询方法
5. **生产就绪** - 全面测试、CI/CD、文档完善

## 🏗️ 技术栈

### 核心依赖

| 工具       | 版本   | 用途       |
| ---------- | ------ | ---------- |
| Python     | 3.10+  | 语言运行时 |
| SQLAlchemy | 2.0+   | ORM 框架   |
| uv         | latest | 包管理器   |
| pytest     | 7.4+   | 测试框架   |
| mypy       | 1.5+   | 类型检查   |
| ruff       | 0.1+   | Linter     |
| black      | 23.9+  | 代码格式化 |

### 可选依赖

- **async**: SQLAlchemy[asyncio] - 异步数据库操作
- **postgresql**: psycopg2-binary - PostgreSQL 驱动
- **mysql**: pymysql - MySQL 驱动

## 📁 项目结构（src layout）

```
paper-trail-py/
├── src/paper_trail/              # 核心源码
│   ├── __init__.py               # 公共 API 导出
│   ├── models.py                 # Version 数据模型
│   ├── decorators.py             # @track_versions 装饰器
│   ├── context.py                # 上下文管理（whodunnit、事务分组）
│   ├── query.py                  # 版本查询 API
│   ├── reify.py                  # 版本恢复
│   ├── serializers.py            # 对象序列化器
│   ├── config.py                 # 全局配置
│   ├── async_support.py          # 异步支持
│   └── performance.py            # 性能优化工具
│
├── tests/                        # 测试套件
│   ├── conftest.py               # Pytest 配置和 fixtures
│   ├── test_decorators.py        # 装饰器测试
│   ├── test_query.py             # 查询 API 测试
│   ├── test_reify.py             # 版本恢复测试
│   ├── test_context.py           # 上下文管理测试
│   └── test_performance.py       # 性能测试
│
├── .github/workflows/            # CI/CD
│   ├── ci.yml                    # 持续集成
│   └── publish.yml               # PyPI 发布
│
├── pyproject.toml                # uv 项目配置
├── Makefile                      # 开发命令
├── .gitignore                    # Git 忽略规则
├── .pre-commit-config.yaml       # Pre-commit hooks
└── README.md                     # 项目文档
```

## 🔧 10 大核心功能详解

### 1️⃣ 版本追踪装饰器

**文件**: `decorators.py`

**功能**：为 SQLAlchemy 模型启用自动版本追踪

**API 设计**：
```python
@track_versions(
    only: Optional[Set[str]] = None,       # 仅追踪这些字段
    ignore: Optional[Set[str]] = None,     # 忽略这些字段
    serializer: Optional[Serializer] = None,  # 自定义序列化器
)
```

**实现要点**：
- 使用 SQLAlchemy 事件监听器 (`after_insert`, `after_update`, `after_delete`)
- 配置存储在类属性 `__paper_trail_config__`
- 支持字段过滤（only/ignore）
- 使用 connection.execute 在同一事务中插入版本记录

**示例**：
```python
@track_versions(ignore={'updated_at'})
class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
```

---

### 2️⃣ Version 数据模型

**文件**: `models.py`

**功能**：存储所有模型变更的核心数据结构

**字段设计**：
```python
class Version(Base):
    id: int                          # 主键
    item_type: str                   # 模型表名
    item_id: str                     # 记录 ID
    event: str                       # create/update/destroy
    whodunnit: str | None            # 操作者
    transaction_id: str | None       # 事务分组 ID
    object: dict | None              # 完整快照（JSON）
    object_changes: dict | None      # 变更增量（JSON）
    created_at: datetime             # 时间戳
```

**索引策略**：
```python
# 复合索引
Index('idx_item_lookup', 'item_type', 'item_id')
Index('idx_transaction_lookup', 'transaction_id', 'created_at')
Index('idx_whodunnit_lookup', 'whodunnit', 'created_at')

# 单列索引
Index on 'event'
Index on 'created_at'
```

**方法**：
- `to_dict()` - 序列化为字典
- `changeset` - 获取变更集（属性）
- `reify()` - 获取对象状态快照

---

### 3️⃣ 版本查询 API

**文件**: `query.py`

**功能**：提供流畅的查询接口

**API 设计**：
```python
VersionQuery(session)
    .for_model(Article, 123)         # 按模型实例
    .for_model_type(Article)         # 按模型类型
    .by_user('user@example.com')     # 按操作者
    .by_transaction('uuid-xxx')      # 按事务 ID
    .by_event('update')              # 按事件类型
    .between(start, end)             # 时间范围
    .after(timestamp)                # 之后
    .before(timestamp)               # 之前
    .order_by_time(ascending=False)  # 排序
    .limit(10)                       # 限制数量
    .all()                           # 执行并返回所有
    .first()                         # 返回第一个
    .count()                         # 计数
```

**实现要点**：
- 链式调用（Builder Pattern）
- 延迟执行（`.all()`, `.first()` 时才查询）
- 使用 SQLAlchemy 2.0 风格（`select()` 而非 `query()`）

---

### 4️⃣ 版本恢复 (Reify)

**文件**: `reify.py`

**功能**：从版本记录重建对象状态

**API 设计**：
```python
# 恢复到指定版本
reify_version(
    session: Session,
    version: Version,
    model_class: Type,
    commit: bool = False,
) -> Any

# 恢复到指定时间点
reify_to_time(
    session: Session,
    model_class: Type,
    model_id: Any,
    timestamp: datetime,
) -> Optional[Any]

# 比较两个版本的差异
get_changeset_diff(
    version_a: Version,
    version_b: Version,
) -> Dict[str, tuple]
```

**实现要点**：
- 从 `object` JSON 字段恢复所有字段
- 支持恢复已删除的记录（创建新实例）
- 可选立即提交或延迟提交

---

### 5️⃣ 上下文管理 (Whodunnit)

**文件**: `context.py`

**功能**：管理操作者信息和事务分组

**API 设计**：
```python
# 全局设置
set_whodunnit('user@example.com')
get_whodunnit() -> Optional[str]

# 上下文管理器
with whodunnit('admin@example.com'):
    article.title = 'Updated'
    session.commit()

# 事务分组
with transaction_group() as tx_id:
    article1.update()
    article2.update()
    session.commit()
```

**实现要点**：
- 使用 `contextvars.ContextVar` 实现线程安全
- 支持异步上下文
- 自动生成 UUID 作为 transaction_id

---

### 6️⃣ 事务分组

**文件**: `context.py`

**功能**：将多个变更关联到一个事务

**使用场景**：
- 批量更新操作
- 复杂业务逻辑（多表关联修改）
- 回滚整组变更

**示例**：
```python
with transaction_group() as tx_id:
    # 所有变更会有相同的 transaction_id
    article.title = 'New Title'
    session.commit()
    
    article.content = 'New Content'
    session.commit()

# 查询事务内的所有变更
versions = VersionQuery(session).by_transaction(tx_id).all()
```

---

### 7️⃣ 自定义序列化

**文件**: `serializers.py`

**功能**：控制对象如何序列化为 JSON

**接口设计**：
```python
class Serializer(Protocol):
    def serialize(obj, config) -> Dict[str, Any]:
        """序列化对象"""
        
    def get_changes(obj, config) -> Optional[Dict[str, tuple]]:
        """获取变更"""
```

**内置实现**：

1. **DefaultSerializer** - 默认序列化器
   - 处理基本类型（str, int, float, bool）
   - 自动转换 datetime、date、Decimal、Enum
   - 应用 only/ignore 过滤

2. **CustomFieldSerializer** - 自定义字段序列化
   ```python
   serializer = CustomFieldSerializer({
       'price': lambda v: f"${v:.2f}",
       'tags': lambda v: ','.join(v),
   })
   
   @track_versions(serializer=serializer)
   class Product(Base):
       # ...
   ```

---

### 8️⃣ 配置管理

**文件**: `config.py`

**功能**：全局配置选项

**配置项**：
```python
configure(
    enabled=True,                     # 全局开关
    version_table_name='versions',    # 表名
    default_ignore_fields={           # 默认忽略字段
        'updated_at',
        'modified_at',
        'last_modified',
    },
    store_object_snapshot=True,       # 存储完整快照
    store_object_changes=True,        # 存储变更增量
    batch_insert_threshold=100,       # 批量插入阈值
    async_enabled=False,              # 异步支持
)
```

**实现**：
- 使用 dataclass 管理配置
- 单例模式（全局 `_config` 实例）
- 提供 `get_config()` 和 `reset_config()`

---

### 9️⃣ 异步支持

**文件**: `async_support.py`

**功能**：为 SQLAlchemy 异步 API 提供版本追踪

**API 设计**：
```python
# 异步查询
async def get_versions_async(
    session: AsyncSession,
    model_class: Type,
    model_id: Any,
    limit: Optional[int] = None,
) -> List[Version]

# 异步恢复
async def reify_version_async(
    session: AsyncSession,
    version: Version,
    model_class: Type,
    commit: bool = False,
) -> Any

# 异步查询构建器
AsyncVersionQuery(session)
    .for_model(Article, 123)
    .order_by_time()
    .limit(10)
    .all()  # 返回 awaitable
```

**实现要点**：
- 使用 `AsyncSession`
- 所有查询方法返回 `awaitable`
- 兼容 SQLAlchemy 2.0 异步 API

---

### 🔟 性能优化

**文件**: `performance.py`

**功能**：批量操作和性能增强

**API 设计**：

1. **批量追踪**：
   ```python
   bulk_track_changes(
       session: Session,
       items: List,
       model_class: Type,
       event: str = 'update',
       whodunnit: str = None,
   ) -> int
   ```

2. **批量版本创建器**：
   ```python
   with BatchVersionCreator(session, batch_size=100) as batch:
       for item in items:
           batch.add_version(version_data)
       # 自动在 __exit__ 时 flush
   ```

3. **清理旧版本**：
   ```python
   cleanup_old_versions(
       session: Session,
       days: int = 90,
       model_class: Type = None,
   ) -> int
   ```

**性能策略**：
- 批量插入（`insert().values([...])`）
- 延迟提交（缓冲区）
- 分区归档（按时间清理）
- 索引优化

---

## 📋 开发规范

### 代码风格

- **格式化**: Black (line-length=88)
- **Linter**: Ruff
- **导入排序**: isort (profile=black)
- **类型检查**: mypy (strict mode)

### 测试要求

- **覆盖率**: > 95%
- **测试框架**: pytest
- **异步测试**: pytest-asyncio
- **数据库**: SQLite (测试), PostgreSQL (CI)

### Git 工作流

1. **分支策略**:
   - `main` - 稳定版本
   - `develop` - 开发分支
   - `feature/*` - 功能分支
   - `fix/*` - 修复分支

2. **Commit 规范**:
   ```
   <type>(<scope>): <subject>
   
   types: feat, fix, docs, style, refactor, test, chore
   ```

3. **Pre-commit Hooks**:
   - trailing-whitespace
   - end-of-file-fixer
   - black
   - isort
   - ruff
   - mypy

---

## 🚀 CI/CD 配置

### GitHub Actions 工作流

#### 1. CI 工作流 (`.github/workflows/ci.yml`)

**触发条件**:
- Push to `main`, `develop`
- Pull Request to `main`, `develop`

**Jobs**:

1. **test** - 多版本 Python 测试
   - Matrix: Python 3.10, 3.11, 3.12
   - PostgreSQL 服务容器
   - 运行 pytest + coverage
   - 上传到 Codecov

2. **lint** - 代码质量检查
   - ruff
   - black
   - isort

3. **type-check** - 类型检查
   - mypy

#### 2. Publish 工作流 (`.github/workflows/publish.yml`)

**触发条件**:
- GitHub Release 发布

**步骤**:
1. 使用 uv 构建包
2. 发布到 PyPI (使用 Trusted Publishing)

---

## 📝 配置模板

### pyproject.toml

```toml
[project]
name = "paper-trail-py"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["sqlalchemy>=2.0.0"]

[project.optional-dependencies]
dev = ["pytest>=7.4.0", "mypy>=1.5.0", "ruff>=0.1.0"]
async = ["sqlalchemy[asyncio]>=2.0.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--cov=paper_trail", "--cov-report=term-missing"]

[tool.mypy]
python_version = "3.10"
strict = true

[tool.ruff]
target-version = "py310"
line-length = 88

[tool.black]
line-length = 88
```

### Makefile

```makefile
install:
    uv pip install -e .

dev-install:
    uv pip install -e ".[dev,async]"

test:
    uv run pytest

lint:
    uv run ruff check src/ tests/
    uv run black --check src/ tests/

format:
    uv run black src/ tests/
    uv run isort src/ tests/

type-check:
    uv run mypy src/paper_trail
```

---

## 🎯 开发步骤

### Phase 1: 基础架构 ✅
- [x] 项目结构搭建
- [x] 配置文件（pyproject.toml, Makefile）
- [x] CI/CD 工作流

### Phase 2: 核心功能 ✅
- [x] Version 模型
- [x] @track_versions 装饰器
- [x] 事件监听器
- [x] 序列化器

### Phase 3: 查询和恢复 ✅
- [x] VersionQuery API
- [x] reify_version
- [x] 上下文管理

### Phase 4: 高级功能 ✅
- [x] 异步支持
- [x] 性能优化
- [x] 批量操作

### Phase 5: 测试和文档 ✅
- [x] 单元测试
- [x] 集成测试
- [x] README 文档
- [x] API 文档

### Phase 6: 发布 🚀
- [ ] 版本 0.1.0 发布到 PyPI
- [ ] 文档托管（Read the Docs）
- [ ] 社区推广

---

## ✅ 成功标准

### 功能完整性
- ✅ 10 大核心功能全部实现
- ✅ 同步 + 异步 API
- ✅ 完整的类型提示

### 代码质量
- ✅ 测试覆盖率 > 95%
- ✅ Mypy strict mode 通过
- ✅ Ruff + Black 零警告
- ✅ Pre-commit hooks 配置

### 性能
- ⏱️ 单次版本插入 < 10ms
- ⏱️ 批量插入 100 条 < 50ms
- ⏱️ 查询 1000 条版本 < 100ms

### 文档
- ✅ README 完整
- ✅ API 文档
- ✅ 使用示例
- ✅ 架构设计文档

### 工程化
- ✅ GitHub Actions CI/CD
- ✅ 自动化测试
- ✅ 自动发布到 PyPI
- ✅ 版本管理

---

## 🔮 未来计划

### v0.2.0
- [ ] Django ORM 支持
- [ ] 版本对比 UI 组件
- [ ] 审计日志导出（CSV/JSON）

### v0.3.0
- [ ] 版本压缩（只存储变更）
- [ ] 分区表支持
- [ ] 审计报告生成

### v1.0.0
- [ ] 生产级性能优化
- [ ] 完整的 API 稳定性保证
- [ ] 企业级功能（RBAC、加密）

---

**文档版本**: 1.0  
**最后更新**: 2026-01-07  
**维护者**: PaperTrail Team
