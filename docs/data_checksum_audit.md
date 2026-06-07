# Data checksum audit

`checksum-audit` records SHA-256 checksums for local public-data files and generated intermediate artifacts. This supports later Data Availability and Code Availability statements without committing restricted datasets or credentials.

## Command

```powershell
python -m nature_climate_ai.cli checksum-audit --root data --output data/checksums/data_checksum_audit.md --csv data/checksums/data_checksums.csv
```

## Outputs

- `data/checksums/data_checksum_audit.md`: human-readable audit report and current readiness status.
- `data/checksums/data_checksums.csv`: machine-readable file path, byte size, algorithm and checksum table.

## Interpretation

The command returns `NOT_READY` when no checksumable local data files exist. That is the expected state before ERA5/ERA5-Land, MODIS, FLUXNET or generated intermediate artifacts have been downloaded or produced.

It deliberately ignores `data/metadata/` and `data/checksums/` so that metadata templates and the checksum manifest itself are not mistaken for scientific data.

## 中文审阅说明

本命令为本地数据文件生成 SHA-256 校验值，用于支持后续数据可用性和复现说明。没有真实数据文件时应保持 `NOT_READY`；该命令不会验证账号权限、数据政策合规性或科学质量控制。
