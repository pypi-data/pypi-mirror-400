# MLflow Tclake 插件

本插件将 [Tclake](https://cloud.tencent.com/product/tclake) 集成为 MLflow 的模型注册表存储后端，实现机器学习模型在腾讯云数据湖中的无缝存储与管理。

## 功能特性

- ✅ **模型注册表存储**：使用 Tclake 作为 MLflow 模型注册表的后端存储
- 🌐 **云服务集成**：原生支持腾讯云 SDK
- 🔒 **安全访问**：基于腾讯云认证机制的安全访问控制

## 安装方法

```bash
pip install mlflow-tclake-plugin
```

## 使用方法 

设置tclake作为registry_uri，模型元数据将自动注册到tclake

```bash
mlflow.set_registry_uri("tclake:region") # region需要替换为实际tclake开通地域，例如ap-beijing
```

## 系统要求

- Python 3.9+
- MLflow >= 3.1.4
- Tencent Cloud SDK >= 3.0.1478

## 开发指南

1. 安装开发依赖：
```bash
pip install -r requirements.txt
```

2. 运行测试：
```bash
pytest mlflow_tclake_plugin/test/
```