"""建历史用例库 —— 用 SQLite 模拟提问场景里的 MySQL。

真实场景：测试平台的历史用例存在 MySQL 里（用例名、描述、脚本）。
这里用标准库 sqlite3 建同构的表并灌入 14 条种子用例，零依赖跑通全流程。
换成真 MySQL 时只需把连接层换掉，表结构和后面两路召回的逻辑都不变。

用法：
    python3 setup_db.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "testcases.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS test_cases (
    id          INTEGER PRIMARY KEY,
    module      TEXT NOT NULL,      -- 所属模块：登录/订单/支付/用户/库存
    priority    TEXT NOT NULL,      -- P0/P1/P2
    name        TEXT NOT NULL,      -- 用例名
    description TEXT NOT NULL,      -- 用例描述
    script      TEXT NOT NULL       -- 对应的测试脚本
);
"""

CASES = [
    ("登录", "P0", "正确用户名密码登录成功",
     "输入已注册的用户名和正确密码，登录成功并返回 token。",
     '''def test_login_success():
    resp = login("alice", "correct-pass")
    assert resp.status == 200
    assert resp.json["token"]'''),

    ("登录", "P1", "密码连续错误五次锁定账户",
     "同一账户连续输错密码五次后，账户锁定 30 分钟，期间正确密码也无法登录。",
     '''def test_login_lock_after_5_failures():
    for _ in range(5):
        login("alice", "wrong-pass")
    resp = login("alice", "correct-pass")
    assert resp.status == 423  # Locked'''),

    ("登录", "P2", "验证码过期后登录失败",
     "短信验证码超过 5 分钟有效期后提交，登录失败并提示验证码已过期。",
     '''def test_login_expired_captcha():
    code = request_sms_code("13800138000")
    advance_time(minutes=6)
    resp = login_by_sms("13800138000", code)
    assert "过期" in resp.json["message"]'''),

    ("订单", "P0", "创建订单成功并扣减库存",
     "用户下单成功后，订单状态为待支付，对应 SKU 库存减少相应数量。",
     '''def test_create_order_deducts_stock():
    before = get_stock("SKU-1")
    order = create_order("alice", "SKU-1", qty=2)
    assert order.status == "PENDING_PAY"
    assert get_stock("SKU-1") == before - 2'''),

    ("订单", "P1", "取消订单后库存回滚",
     "用户取消待支付订单后，订单状态变为已取消，之前扣减的库存全部回滚。",
     '''def test_cancel_order_restores_stock():
    order = create_order("alice", "SKU-1", qty=2)
    before = get_stock("SKU-1")
    cancel_order(order.id)
    assert get_stock("SKU-1") == before + 2'''),

    ("订单", "P1", "退款申请审核通过后原路退回",
     "已支付订单发起退款，审核通过后金额原路退回支付账户，订单状态变为已退款。",
     '''def test_refund_returns_via_original_channel():
    order = create_paid_order("alice")
    req = apply_refund(order.id)
    approve_refund(req.id)
    assert order.reload().status == "REFUNDED"
    assert refund_channel(req.id) == order.pay_channel'''),

    ("订单", "P2", "订单超时未支付自动关闭",
     "待支付订单超过 30 分钟未支付，系统自动关闭订单并释放库存。",
     '''def test_order_auto_close_on_timeout():
    order = create_order("alice", "SKU-1", qty=1)
    advance_time(minutes=31)
    assert order.reload().status == "CLOSED"'''),

    ("支付", "P0", "支付回调幂等性校验",
     "同一笔支付的回调通知重复到达多次时，只入账一次，不产生重复流水。",
     '''def test_duplicate_callback_idempotent():
    order = create_paid_order("alice")
    notify_payment(order.pay_no)
    notify_payment(order.pay_no)  # 同一回调重复通知
    assert ledger_entries(order.id) == 1'''),

    ("支付", "P1", "余额不足支付失败提示",
     "账户余额小于订单金额时支付失败，提示余额不足，订单保持待支付状态。",
     '''def test_pay_insufficient_balance():
    set_balance("alice", 1)
    resp = pay_order(order_id, channel="balance")
    assert resp.status == 400
    assert "余额不足" in resp.json["message"]'''),

    ("支付", "P1", "支付超时后订单状态回滚",
     "支付渠道超时未返回结果时，主动查询确认失败后，订单回滚为待支付。",
     '''def test_pay_timeout_rollback():
    with mock_channel_timeout():
        pay_order(order_id)
    reconcile(order_id)
    assert get_order(order_id).status == "PENDING_PAY"'''),

    ("用户", "P1", "修改手机号需旧手机验证码",
     "用户修改绑定手机号时，必须先通过旧手机号验证码校验，才能绑定新号。",
     '''def test_change_phone_requires_old_code():
    resp = change_phone("alice", new="13900139000", old_code=None)
    assert resp.status == 403'''),

    ("用户", "P2", "注销账户后个人数据脱敏",
     "用户注销账户后，历史订单中的姓名、手机号等个人信息全部脱敏存储。",
     '''def test_deactivate_masks_personal_data():
    deactivate("alice")
    order = get_order_by_user("alice")
    assert order.phone.startswith("138****")'''),

    ("库存", "P0", "并发下单不超卖",
     "库存仅剩 1 件时，两个用户同时下单，只有一单成功，库存不出现负数。",
     '''def test_concurrent_order_no_oversell():
    set_stock("SKU-1", 1)
    r1, r2 = concurrent(create_order, ("alice", "SKU-1"), ("bob", "SKU-1"))
    assert [r1.ok, r2.ok].count(True) == 1
    assert get_stock("SKU-1") == 0'''),

    ("库存", "P2", "库存不足时下单失败",
     "下单数量大于剩余库存时，下单失败并提示库存不足，库存数量不变。",
     '''def test_order_fails_when_stock_short():
    set_stock("SKU-1", 1)
    resp = create_order("alice", "SKU-1", qty=2)
    assert resp.status == 400'''),

    ("支付", "P2", "0 元订单直接支付成功",
     "优惠券抵扣后实付金额为 0 的订单，跳过支付渠道直接标记支付成功。",
     '''def test_zero_amount_order_auto_paid():
    order = create_order_with_coupon("alice", full_discount=True)
    assert order.status == "PAID"
    assert order.pay_channel == "NONE"'''),
]


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.executemany(
        "INSERT INTO test_cases (module, priority, name, description, script) "
        "VALUES (?, ?, ?, ?, ?)", CASES)
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM test_cases").fetchone()[0]
    mods = [r[0] for r in conn.execute(
        "SELECT module || 'x' || COUNT(*) FROM test_cases GROUP BY module")]
    print(f"已建库 {DB_PATH.name}：{n} 条历史用例（{', '.join(mods)}）")
    conn.close()


if __name__ == "__main__":
    main()
