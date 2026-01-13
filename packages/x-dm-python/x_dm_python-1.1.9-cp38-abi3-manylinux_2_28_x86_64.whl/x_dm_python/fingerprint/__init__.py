"""
Fingerprint (浏览器指纹) 模块

提供浏览器指纹管理功能，支持随机 User-Agent 和 Sec-Ch-Ua 头部。

Example:
    ```python
    from x_dm_python import fingerprint

    # 获取随机指纹
    fp = fingerprint.get_random_fingerprint()
    print(fp.user_agent)
    print(fp.sec_ch_ua)

    # 禁用随机化
    fingerprint.disable_randomization()

    # 自定义配置
    config = fingerprint.FingerprintConfig(
        enabled=True,
        browsers=["chrome"],
        platforms=["windows", "macos"],
    )
    fingerprint.configure(config)
    ```
"""

from ..x_dm_python import fingerprint as _fingerprint

FingerprintConfig = _fingerprint.FingerprintConfig
BrowserFingerprint = _fingerprint.BrowserFingerprint
configure = _fingerprint.configure
disable_randomization = _fingerprint.disable_randomization
enable_randomization = _fingerprint.enable_randomization
is_randomization_enabled = _fingerprint.is_randomization_enabled
get_random_fingerprint = _fingerprint.get_random_fingerprint
get_pool_size = _fingerprint.get_pool_size

__all__ = [
    "FingerprintConfig",
    "BrowserFingerprint",
    "configure",
    "disable_randomization",
    "enable_randomization",
    "is_randomization_enabled",
    "get_random_fingerprint",
    "get_pool_size",
]
