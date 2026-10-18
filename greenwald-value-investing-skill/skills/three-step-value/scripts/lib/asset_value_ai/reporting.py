"""Chinese Markdown presentation of the final ledger and its arithmetic."""

from __future__ import annotations


def _text(value) -> str:
    return str(value if value is not None else "未提供").replace("|", "\\|").replace("\n", "<br>")


def _amount(value) -> str:
    if value is None:
        return "未计量"
    return f"{value:,.2f}"


_LABELS = {
    "name": "项目", "id": "标识", "decision": "处理决定", "items": "涉及项目",
    "reason": "理由", "result": "结果或主张", "conclusion": "结论",
    "book_value": "账面金额", "value": "估计金额", "low": "较低金额", "high": "较高金额",
    "text_path": "全文文件", "path": "原文文件", "coverage": "实际阅读范围", "limitation": "资料局限",
    "source": "来源", "sources": "来源", "currency": "币种", "period_end": "报告期",
    "valuation_date": "资产估值基准日", "effective_date": "资产估值基准日",
    "description": "说明", "basis": "采用口径",
    "operating_assets_example_value": "经营资产合并算例金额",
    "operating_cash": "经营现金", "receivables": "应收款项", "inventory": "存货",
    "plant_equipment_land_example_value": "厂房、设备及土地合并算例金额",
    "operating_intangible_resources": "经营无形资源", "excess_cash": "超额现金",
    "nonoperating_assets": "非经营资产", "operating_liabilities": "经营负债",
    "interest_bearing_debt": "有息债务", "other_obligations": "其他义务",
    "equipment_standalone_book_value": "设备独立账面金额",
    "plant_equipment_land_book_value": "厂房、设备及土地合并账面金额",
    "ordinary_shares": "普通股股数", "nci": "少数权益", "preferred": "优先权益",
    "change_from_2025": "较2025年变化", "equipment_estimate": "设备估计",
    "aggregation": "汇总核对", "net_values": "净额处理", "cash_and_intangibles": "现金及无形资源",
    "obligations": "义务处理", "equity_and_shares": "权益与股数", "calculation": "计算核对",
    "warnings": "提示说明", "scope": "研究范围", "method": "方法", "quantity": "数量",
    "unit_cost": "单位成本", "base": "计算基数", "factor": "调整系数", "gross": "总额",
    "deduction": "扣减金额", "net_value": "净价值", "share": "持有份额",
    "rate": "折现率", "cashflows": "现金流", "amount": "金额", "years": "年数",
    "item_values": "替换项目金额", "item_values_range": "项目金额范围",
    "shares": "普通股分母", "treatment": "处理方式",
}


def _scalar(value) -> str:
    if value is None:
        return "未提供"
    if isinstance(value, bool):
        return "是" if value else "否"
    if isinstance(value, (int, float)):
        return f"{value:,}"
    return str(value)


def _label(key) -> str:
    return _LABELS.get(str(key), str(key).replace("_", " "))


def _structure(value, depth=0) -> list[str]:
    """Render arbitrary research explanations without Python object syntax."""
    indent = "  " * depth
    lines = []
    entries = value.items() if isinstance(value, dict) else enumerate(value, 1)
    for key, entry in entries:
        label = _label(key) if isinstance(value, dict) else f"第{key}项"
        if isinstance(entry, (dict, list, tuple)):
            if not entry:
                lines.append(f"{indent}- **{label}：** 未列项目")
            else:
                lines += [f"{indent}- **{label}**", ""] + _structure(entry, depth + 1)
        elif isinstance(value, dict):
            text = _scalar(entry).replace("\n", "\n" + indent + "  ")
            if key in ("text_path", "path") and isinstance(entry, str) and entry.startswith("/"):
                text = f"[材料文件](<{entry}>)"
            lines.append(f"{indent}- **{label}：** {text}")
        else:
            lines.append(f"{indent}- {_scalar(entry).replace(chr(10), chr(10) + indent + '  ')}")
    return lines


def _paragraph(value) -> str:
    if isinstance(value, (dict, list, tuple)):
        return "\n".join(_structure(value))
    return _scalar(value) if value is not None else "未单列；以逐项理由为准。"


def _inline(value) -> str:
    if isinstance(value, dict):
        return "；".join(f"{_label(key)}：{_inline(entry)}" for key, entry in value.items())
    if isinstance(value, (list, tuple)):
        return "、".join(_inline(entry) for entry in value)
    return _scalar(value)


def _market_comparison(valuation: dict, calculation: dict) -> list[str]:
    comparison = valuation.get("market_comparison")
    if not comparison:
        return []
    quotes = comparison.get("quotes", [])
    lines = ["## 可选市场比较", "", "各类证券使用其实际发行在外股数和各自报价，换至估值币种后相加；资产参数来自前述研究。", "",
             "| 类别 | 股数 | 股价 | 报价币种 | 报价日 | 换算率及日期 | 换算市值 |",
             "| --- | ---: | ---: | --- | --- | --- | ---: |"]
    total = 0.0
    complete = bool(quotes)
    for quote in quotes:
        shares, price = quote.get("shares"), quote.get("price")
        fx = quote.get("fx_to_valuation")
        if quote.get("currency") == calculation.get("currency"):
            fx = 1
        market_value = None
        if shares is not None and price is not None and fx is not None:
            market_value = float(shares) * float(price) * float(fx)
            total += market_value
        else:
            complete = False
        lines.append(f"| {_text(quote.get('label', '普通股'))} | {_amount(shares)} | {_amount(price)} | {_text(quote.get('currency'))} | {_text(quote.get('quote_date'))} | {_text(fx)} / {_text(quote.get('fx_date'))} | {_amount(market_value)} |")
    expected_shares = calculation.get("shares")
    quoted_shares = sum(float(quote.get("shares") or 0) for quote in quotes)
    if expected_shares is None or abs(quoted_shares - expected_shares) > max(1e-6, abs(expected_shares) * 1e-9):
        complete = False
        lines += ["", "报价类别股数尚未覆盖同口径普通股总数，以上仅为所列类别市值，未计算集团折溢价。"]
    if complete:
        lines += ["", f"集团普通股市值：**{_amount(total)} {calculation.get('currency', '')}**。"]
        if total > 0 and calculation.get("equity_value") is not None:
            ratio = calculation["equity_value"] / total - 1
            lines += [f"基准资产价值相对市值差额：**{ratio:+.1%}**。该差额不是承诺收益。"]
    lines += ["", _paragraph(comparison.get("note", "汇率和报价日期单列，报价更新不代表资产已重估。"))]
    return lines


def _render_details(input_data: dict, valuation: dict, calculation: dict) -> str:
    issuer = input_data.get("issuer", {})
    currency = calculation.get("currency") or valuation.get("currency") or "计价币种未提供"
    premise = valuation.get("premise")
    premise_dates = premise if isinstance(premise, dict) else {}
    valuation_date = (valuation.get("valuation_date") or valuation.get("effective_date")
                      or premise_dates.get("valuation_date") or premise_dates.get("effective_date"))
    date_description = (f"资产估值基准日：{_text(valuation_date)}。" if valuation_date else
                        "资产估值基准日：未单列；各项采用的报表期间及更新条件见后文。")
    lines = [f"# {_text(issuer.get('name') or issuer.get('code') or '企业')}资产价值研究", "",
             f"**基准归母普通股资产价值：{_amount(calculation['equity_value'])} {currency}。**",
             "", "估值前提：", "", _paragraph(premise), "",
             f"金额单位：{currency} 基本货币单位。", date_description,
             f"研究截止日：{_text(input_data.get('as_of'))}；证据截止日：{_text(input_data.get('evidence_cutoff', input_data.get('as_of')))}。", "",
             "| 口径 | 基准金额 |", "| --- | ---: |",
             f"| 经营资产再生产成本总额 | {_amount(calculation['operating_assets'])} |",
             f"| 经营净资产再生产价值 | {_amount(calculation['operating_net_assets'])} |",
             f"| 归母普通股资产价值 | {_amount(calculation['equity_value'])} |",
             f"| 普通股发行在外股数 | {_amount(calculation.get('shares'))} |",
             f"| 每股资产价值（{currency}/股） | {_amount(calculation.get('per_share'))} |", "",
             "基准值包含台账中的合理估计，估计范围不代表置信区间或保证价值。"]
    missing = calculation.get("missing_items", [])
    unmeasured_obligations = any(item.get("kind") in ("liability", "nci", "preferred") and
                                (item.get("material") or item.get("basis") != "omitted") for item in missing)
    material_omissions = any(item.get("kind") in ("liability", "nci", "preferred") and
                             item.get("material") and item.get("basis") == "omitted"
                             for item in calculation.get("items", []))
    if valuation.get("unmeasured"):
        lines += ["", "**存在单列未明事项：以上总值采用前述金额和假设，具体金额或构成、权利条件的局限见后文；不能据此称为完整资产底线或已验证下限。**"]
    elif unmeasured_obligations or material_omissions:
        lines += ["", "**尚有未扣除的义务或其他权利人权益：以上为已计量范围的有条件估值，不能称为完整资产底线或已验证下限。**"]
    research = valuation.get("research", {})
    if input_data.get("simulation") or valuation.get("simulation") or research.get("mode") == "simulated":
        lines += ["", "**本报告使用模拟数据，仅用于验证计算和流程，不是企业真实估值。**"]
    if research:
        mode = {"live": "真实模型研究", "simulated": "离线模拟"}.get(research.get("mode"), research.get("mode", "未记录"))
        lines += ["", f"研究模式：{_text(mode)}；模型：{_text(research.get('model'))}；推理强度：{_text(research.get('effort'))}；实际调用数：{_text(research.get('calls_used'))}。"]
    lines += ["", "## 主代理结论与推理", "", _paragraph(valuation.get("summary")), ""]
    if valuation.get("reasoning"):
        lines += [_paragraph(valuation["reasoning"]), ""]
    if valuation.get("adoptions"):
        lines += ["采纳、替换与分歧处理：", "", _paragraph(valuation["adoptions"]), ""]
    if valuation.get("review"):
        lines += ["最终复核说明：", "", _paragraph(valuation["review"]), ""]
    lines += ["## 逐项事实、估计与处理", "",
              "| 项目 | 类别 | 账面金额 | 采用金额 | 依据性质 | 是否计入 | 方法、理由及来源 |",
              "| --- | --- | ---: | ---: | --- | --- | --- |"]
    basis_names = {"fact": "事实直接采用", "estimate": "模型估计", "book": "沿用账面", "omitted": "明确略去"}
    kind_names = {"asset": "资产", "liability": "负债", "nci": "少数权益", "preferred": "优先权益"}
    for item in calculation.get("items", []):
        included = item.get("included", item.get("include", True)) and item.get("value") is not None
        sources = item.get("sources") or []
        if isinstance(sources, str):
            sources = [sources]
        detail = item.get("reason", "")
        if item.get("formula"):
            detail += f"；计算：{_inline(item['formula'])}"
        if sources:
            detail += "；来源：" + "；".join(str(source) for source in sources)
        lines.append(f"| {_text(item.get('name', item['id']))} | {kind_names.get(item['kind'], item['kind'])} | {_amount(item.get('book_value'))} | {_amount(item.get('value'))} | {basis_names.get(item.get('effective_basis', item.get('basis')), '未标明')} | {'是' if included else '否'} | {_text(detail)} |")
    lines += ["", "## 计算与权益分配", "",
              f"全部资产 {_amount(calculation['total_assets'])} − 全部负债 {_amount(calculation['total_liabilities'])} − 少数权益 {_amount(calculation['minority_interests'])} − 未包含在负债中的优先权益 {_amount(calculation['preferred_interests'])} = **{_amount(calculation['equity_value'])} {currency}**。",
              "经营净资产只是分类展示；全部资产路径未再加一次净现金，也未重复扣经营负债。"]
    bridge = calculation.get("book_bridge")
    if bridge:
        lines += ["", f"账面桥（{bridge['scope']}）：账面普通股权益 {_amount(bridge['book_equity'])} + 资产调整 {_amount(bridge['asset_adjustment'])} − 负债调整 {_amount(bridge['liability_adjustment'])} − 少数权益调整 {_amount(bridge['nci_adjustment'])} − 优先权益调整 {_amount(bridge['preferred_adjustment'])} = {_amount(bridge['equity_value'])}；与总额路径差异 {_amount(bridge['difference'])}。这只核对算术，不证明估计依据。"]
    scenarios = calculation.get("scenarios", {})
    if scenarios:
        lines += ["", "## 重要估计的敏感性", "", "各项未提供边界时沿用基准；权益较低端采用资产较低金额和扣减项较高金额，较高端反向。这些独立极值组合仅表示金额敏感性范围，不代表相互一致的经营情景。", "",
                  "| 情景 | 归母普通股价值 | 每股价值 |", "| --- | ---: | ---: |"]
        for name, label in (("low", "权益较低"), ("high", "权益较高")):
            if name in scenarios:
                lines.append(f"| {label} | {_amount(scenarios[name]['equity_value'])} | {_amount(scenarios[name]['per_share'])} |")
    if calculation.get("joint_scenarios"):
        lines += ["", "## 主模型联合情景：实际执行与参数", "",
                  f"每项从同一基准独立重算，金额以 {currency} 基本货币单位表示，不改变基准；未执行的部分不提供伪造总值。"]
        for scenario in calculation["joint_scenarios"]:
            lines += ["", "### " + _text(scenario["name"]), _paragraph(scenario.get("parameters"))]
            result = scenario.get("calculation")
            if scenario["status"] == "calculated" and result:
                lines += [f"已重算：归母普通股价值 {_amount(result['equity_value'])}；每股 {_amount(result['per_share'])}；普通股数 {_amount(result['shares'])}。",
                          "完整情景逐项结果见 valuation.json 的 calculation.joint_scenarios。"]
                lines += ["- " + warning for warning in result.get("warnings", [])]
            else:
                lines += ["未计算总值：" + str(scenario.get("note") or scenario.get("reason") or "讨论性情景")]
    elif valuation.get("scenarios"):
        lines += ["", "## 主模型单列情景参数", "",
                  "当前提供的计算对象未包含联合情景结果，以下仅为参数说明，尚未自动重算为情景权益及每股结果。", "",
                  _paragraph(valuation["scenarios"])]
    lines += ["", "## 资料覆盖与两个年度比较", "",
              "材料准备状态：" + ("已准备。" if input_data.get("materials_ready") else "尚未准备齐全；不将单份年报比较列当作两年完整报告。"), "",
              "| 报告期 | 类型 | 原文/来源 |", "| --- | --- | --- |"]
    for report in input_data.get("reports", []):
        location = report.get("path") or report.get("url") or report.get("text_path")
        source = _text(location)
        if isinstance(location, str) and (location.startswith("/") or location.startswith(("https://", "http://"))):
            source = f"[原文](<{location}>)"
        lines.append(f"| {_text(report.get('period_end'))} | {_text(report.get('report_type'))} | {source} |")
    lines += ["", _paragraph(valuation.get("annual_comparison") or valuation.get("period_comparison") or input_data.get("annual_comparison") or input_data.get("period_comparison") or "两个年度比较尚未在汇总中提供；报告清单不替代实际比较。")]
    if valuation.get("materials_read"):
        lines += ["", "实际材料阅读记录：", "", _paragraph(valuation["materials_read"])]
    if valuation.get('reproduction_context'):
        lines += ['', '## 资源复制依据（供后续研究复用）', '', _paragraph(valuation['reproduction_context'])]
    lines += ["", "## 关键假设、条件与未计量处理", "", _paragraph(valuation.get("conditions") or valuation.get("assumptions"))]
    if valuation.get("unmeasured"):
        lines += ["", "单列未明事项及其影响：", "", _paragraph(valuation["unmeasured"])]
    warnings = list(input_data.get("warnings", [])) + list(calculation.get("warnings", [])) + list(research.get("warnings", []))
    if warnings:
        lines += ["", "处理说明：", ""] + [f"- {warning}" for warning in warnings]
    if valuation.get("sources"):
        lines += ["", "补充来源：", "", _paragraph(valuation["sources"])]
    lines += [""] + _market_comparison(valuation, calculation)
    return "\n".join(lines).rstrip() + "\n"


def render_report(input_data: dict, valuation: dict, calculation: dict) -> str:
    from .report_reader import compose_report
    return compose_report(input_data, valuation, calculation,
                          _render_details(input_data, valuation, calculation), method='asset')
