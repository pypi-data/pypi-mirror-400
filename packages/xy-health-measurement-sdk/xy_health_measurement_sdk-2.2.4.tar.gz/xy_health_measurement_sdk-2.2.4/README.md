# 小阳心健康测量SDK

- [使用手册](https://measurement.xymind.cn/docs/sdk/python.html)

- [示例程序](https://github.com/xiaoyang-tech/measurement-python-client)

## 运行环境说明

自SDK >=2.2 版本起引入了部分C++库，这些库对OS环境和其自身依赖包可能存在较为严格的版本要求。

### 本地运行

如需本体环境调试，推荐版本如下：

- 运行平台
  - OS: Ubuntu 22.04 +
  - CPU: x86_64
- 依赖包
  - google protobuf 3.19.6
  - opencv 4.5.4

### Docker运行

当前SDK运行环境也提供了Docker镜像，具体用法可以参考[示例程序](https://github.com/xiaoyang-tech/measurement-python-client)。
