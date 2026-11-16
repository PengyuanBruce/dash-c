# -*- coding: utf-8 -*-
"""大屏C · 六人作战看板 生成器

数据唯一来源：大屏A 的 build/data_cur.json（每人月/季信保实收与目标、优爆品完成与目标、
本季度3万客户数），以及 goods_sales 里的「上周新增」（上周五 − 上周日）。
不联网、不推断：任何一项缺就原样输出 null，页面显示 `--`。

用法：
    python gen_c.py                 # 读 A 的 data_cur.json，生成 index.html + c_data.json
    python gen_c.py --src <path>    # 指定别的 data_cur.json
"""
import argparse
import base64
import io
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = r"D:\AWB\公司数据管理大屏Agent\project\build\data_cur.json"
NAMES = ["汤子豪", "漆螯童", "李怡萍", "邓晓东", "牛群", "程碧瑶"]

TEMPLATE = os.path.join(BASE, "template_c.html")
LOGO = os.path.join(BASE, "logo-256.png")
OUT_HTML = os.path.join(BASE, "index.html")
OUT_DATA = os.path.join(BASE, "c_data.json")


def _num(v):
    try:
        if v is None or v == "":
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def _pct(a, b):
    a, b = _num(a), _num(b)
    if a is None or not b:
        return None
    return a / b * 100


def build(src):
    d = json.load(io.open(src, encoding="utf-8"))
    persons = {p["name"]: p for p in d.get("persons") or []}
    goods = {r["name"]: r for r in d.get("goods_sales") or []}
    ch = d.get("goods_challenge") or {}

    rows, missing = [], []
    for i, nm in enumerate(NAMES):
        p = persons.get(nm)
        g = goods.get(nm) or {}
        if p is None:
            missing.append(nm)
            rows.append({"name": nm, "role": "", "month_val": None, "month_target": None,
                         "month_pct": None, "quarter_val": None, "quarter_target": None,
                         "quarter_pct": None, "hit": None, "hit_target": None, "hit_pct": None,
                         "active": None, "active_target": None, "active_pct": None,
                         "week_add": _num(g.get("week_add"))})
            continue
        hit = _num(p.get("hit_products"))
        hit_t = _num(p.get("hit_target"))
        rows.append({
            "name": nm,
            "role": p.get("role") or "销售",
            "month_val": _num(p.get("month_val")),
            "month_target": _num(p.get("month_target")),
            "month_pct": _num(p.get("month_pct")),
            "quarter_val": _num(p.get("quarter_val")),
            "quarter_target": _num(p.get("quarter_target")),
            "quarter_pct": _num(p.get("quarter_pct")),
            "hit": hit,
            "hit_target": hit_t,
            "hit_pct": _num(p.get("hit_pct")) if p.get("hit_pct") is not None else _pct(hit, hit_t),
            # 3万客户数：完成 = 本季度3w客户数计数；目标 = 同比季度3w客户数计数（去年同期）
            "active": _num(p.get("active_clients")),
            "active_target": _num(p.get("active_clients_yoy")),
            "week_add": _num(g.get("week_add")),
        })

    tot_active = sum(r["active"] or 0 for r in rows) or None
    for r in rows:
        r["active_pct"] = _pct(r["active"], r["active_target"])
        r["active_share"] = (r["active"] / tot_active * 100) if (r["active"] is not None and tot_active) else None

    def _sum(k):
        vs = [r[k] for r in rows if r[k] is not None]
        return sum(vs) if vs else None

    s_month, s_month_t = _sum("month_val"), _sum("month_target")
    s_q, s_q_t = _sum("quarter_val"), _sum("quarter_target")
    s_hit, s_hit_t = _sum("hit"), _sum("hit_target")

    kpi = d.get("kpi") or {}
    goods_node = d.get("goods") or {}
    meta = {
        "data_ds": d.get("update_time", "")[:10] or "",
        "goods_ds": goods_node.get("date") or ch.get("data_ds") or "",
        "update_time": d.get("update_time") or "",
        "month": d.get("month") or "",
        "quarter": d.get("quarter") or "",
        "month_time": _num(d.get("month_time_pct")),
        "quarter_time": _num(d.get("quarter_time_pct")),
        # 优爆品是全季累计目标，时间进度用季度进度做参照
        "goods_time": _num(d.get("quarter_time_pct")),
        "week_end": ch.get("week_data_ds") or "",
        "week_base": ch.get("week_base_ds") or "",
        "missing": missing,
    }
    out = {
        "meta": meta,
        "summary": {
            "month_val": s_month, "month_pct": _pct(s_month, s_month_t),
            "quarter_val": s_q, "quarter_pct": _pct(s_q, s_q_t),
            "hit": s_hit, "hit_pct": _pct(s_hit, s_hit_t),
            "active": tot_active, "active_target": _sum("active_target"),
            "active_pct": _pct(tot_active, _sum("active_target")),
            "week_add": _sum("week_add"),
        },
        "persons": rows,
    }
    return out


def render(data):
    tpl = io.open(TEMPLATE, encoding="utf-8").read()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = tpl.replace("__DATA__", payload)
    # 队徽内联成 data URI：页面保持单文件可转发，不依赖额外请求
    if os.path.exists(LOGO):
        b64 = base64.b64encode(open(LOGO, "rb").read()).decode("ascii")
        html = html.replace("__LOGO__", "data:image/png;base64," + b64)
    else:
        html = html.replace("__LOGO__", "")
    io.open(OUT_HTML, "w", encoding="utf-8").write(html)
    io.open(OUT_DATA, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEFAULT_SRC)
    a = ap.parse_args()
    if not os.path.exists(a.src):
        raise SystemExit("找不到数据源：%s" % a.src)
    data = build(a.src)
    render(data)
    m, s = data["meta"], data["summary"]
    print("数据源 %s" % a.src)
    print("实收数据日 %s | 优爆品数据日 %s | 上周窗口 %s − %s"
          % (m["data_ds"], m["goods_ds"], m["week_end"], m["week_base"]))
    if m["missing"]:
        print("!! 数据里缺这些人的记录：%s" % "、".join(m["missing"]))
    print("六人：月 %s / 季 %s / 优爆品 %s / 3万户 %s / 上周增量 %s"
          % (round(s["month_val"] or 0, 2), round(s["quarter_val"] or 0, 2),
             s["hit"], s["active"], s["week_add"]))
    for p in data["persons"]:
        print("  %-5s 月 %7.2f%% 季 %7.2f%% 优 %6.2f%% 3w %s/%s %s 周增 %s"
              % (p["name"], p["month_pct"] or 0, p["quarter_pct"] or 0, p["hit_pct"] or 0,
                 p["active"], p["active_target"],
                 ("%.1f%%" % p["active_pct"]) if p["active_pct"] is not None else "--",
                 p["week_add"]))
    print("已生成 %s" % OUT_HTML)


if __name__ == "__main__":
    main()
