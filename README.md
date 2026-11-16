# 野狼队业绩看板（大屏C）

线上地址：https://pengyuanbruce.github.io/dash-c/

野狼队六个人（汤子豪、漆螯童、李怡萍、邓晓东、牛群、程碧瑶）一人一张卡，每张卡显示：

| 指标 | 内容 | 进度条 |
|---|---|---|
| 当月实收 | 完成 / 目标（USD） | 有，含时间进度竖线 |
| 当季实收 | 完成 / 目标（USD） | 有，含时间进度竖线 |
| 优爆品 | 完成 / 目标（个） | 有（目标是当季累计目标） |
| 3万客户数 | 本季度3万客户数计数 | 只给数值 + 六人内部占比（无目标） |
| 上周优爆品增量 | 上周五 − 上周日 | 数字，涨绿跌红 |

## 数据来源

全部读大屏A 的 `build/data_cur.json`，不单独采集：

- `persons[]`：`month_val/month_target/month_pct`、`quarter_val/quarter_target/quarter_pct`、`hit_products/hit_target/hit_pct`、`active_clients`
- `goods_sales[]`：`week_add`（商品成长口径，上周五 − 上周日，即上周一至周五净增）
- 顶层：`month`、`quarter`、`month_time_pct`、`quarter_time_pct`、`goods.date`、`goods_challenge.week_data_ds/week_base_ds`

任何一项缺失都输出 `null`，页面显示 `--`，**不拿 0 或上月值兜底**。

## 更新方式

```powershell
cd C:\Users\admin\Desktop\大屏C_六人看板
python gen_c.py     # 读 A 的 data_cur.json，重写 index.html + c_data.json
python push_c.py    # 只推有变化的文件到 GitHub Pages
```

- `logo-256.png` / `logo.png` 队徽（页头与 favicon，内联进 index.html）
- `template_c.html` 管样式与布局（深蓝科技风，桌面 3×2 / 平板 2 列 / 手机 1 列）
- `gen_c.py` 管数据装配（`--src` 可指定别的 data_cur.json）
- `push_c.py` 管发布（按 git blob sha 比对，内容没变不推）
