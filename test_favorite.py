#!/usr/bin/env python3
"""
商品收藏功能 API 测试脚本
使用前请确保服务已启动：docker-compose up -d
"""
import requests
import json

BASE_URL = "http://localhost:19413/api"

def print_result(name, resp, show_body=True):
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"状态码: {resp.status_code}")
    if show_body:
        print(f"响应: {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
    print(f"{'='*60}")
    return resp.status_code in (200, 201)

def test_favorite_workflow():
    """完整的收藏功能测试流程"""
    print("="*60)
    print("商品收藏功能完整测试")
    print("="*60)

    # 1. 创建测试商品
    print("\n--- 前置步骤：创建测试商品 ---")
    product1 = {
        "seller_id": 1001,
        "name": "iPhone 13 Pro 二手 95新",
        "description": "自用 iPhone 13 Pro，256G，保养良好，无磕碰",
        "original_price": 7999.00,
        "sale_price": 4599.00,
        "condition": "like_new",
        "category": "digital",
        "images": ["https://example.com/iphone1.jpg", "https://example.com/iphone2.jpg"],
        "weight_kg": 0.2,
        "is_on_sale": True
    }
    resp = requests.post(f"{BASE_URL}/products/", json=product1)
    print_result("创建商品1", resp)
    product1_id = resp.json()["id"]

    product2 = {
        "seller_id": 1002,
        "name": "Sony WH-1000XM4 降噪耳机",
        "description": "旗舰降噪耳机，音质出色，续航30小时",
        "original_price": 2699.00,
        "sale_price": 1599.00,
        "condition": "good",
        "category": "digital",
        "images": [],
        "weight_kg": 0.25,
        "is_on_sale": True
    }
    resp = requests.post(f"{BASE_URL}/products/", json=product2)
    print_result("创建商品2", resp)
    product2_id = resp.json()["id"]

    product3 = {
        "seller_id": 1003,
        "name": "MacBook Pro 16寸 M1 Max",
        "description": "顶配 MacBook Pro，64G+2T，视频剪辑神器",
        "original_price": 32999.00,
        "sale_price": 21999.00,
        "condition": "used",
        "category": "digital",
        "images": [],
        "weight_kg": 2.1,
        "is_on_sale": True
    }
    resp = requests.post(f"{BASE_URL}/products/", json=product3)
    print_result("创建商品3", resp)
    product3_id = resp.json()["id"]

    # ==========================================
    # 测试1: 收藏商品
    # ==========================================
    print("\n" + "="*60)
    print("测试场景1: 用户收藏商品")
    print("="*60)

    # 用户 2001 收藏商品1
    resp = requests.post(f"{BASE_URL}/products/{product1_id}/favorite/", json={"user_id": 2001})
    ok = print_result("用户2001收藏商品1", resp)

    # 用户 2002 收藏商品1
    resp = requests.post(f"{BASE_URL}/products/{product1_id}/favorite/", json={"user_id": 2002})
    ok = print_result("用户2002收藏商品1", resp)

    # 用户 2001 收藏商品2
    resp = requests.post(f"{BASE_URL}/products/{product2_id}/favorite/", json={"user_id": 2001})
    ok = print_result("用户2001收藏商品2", resp)

    # 用户 2001 再次收藏商品1（应该返回 favorited=false）
    resp = requests.post(f"{BASE_URL}/products/{product1_id}/favorite/", json={"user_id": 2001})
    ok = print_result("用户2001重复收藏商品1", resp)

    # 收藏不传 user_id 应该报错
    resp = requests.post(f"{BASE_URL}/products/{product1_id}/favorite/", json={})
    ok = print_result("收藏不传user_id参数校验", resp)

    # ==========================================
    # 测试2: 商品详情页显示收藏数量
    # ==========================================
    print("\n" + "="*60)
    print("测试场景2: 商品详情页显示收藏数量和是否已收藏")
    print("="*60)

    # 查看商品1详情，不带 user_id，is_favorited 应为 false
    resp = requests.get(f"{BASE_URL}/products/{product1_id}/")
    data = resp.json()
    print_result(f"商品1详情(收藏数应>=2)", resp)
    assert data["favorite_count"] >= 2, f"期望收藏数>=2，实际为 {data['favorite_count']}"
    assert data["is_favorited"] == False, "未传user_id时is_favorited应为false"
    print("✓ 商品1收藏数量正确，is_favorited=false")

    # 查看商品1详情，带 user_id=2001，is_favorited 应为 true
    resp = requests.get(f"{BASE_URL}/products/{product1_id}/?user_id=2001")
    data = resp.json()
    print_result(f"商品1详情(用户2001视角，is_favorited=true)", resp)
    assert data["is_favorited"] == True, "用户2001已收藏，is_favorited应为true"
    print("✓ 用户2001视角is_favorited=true")

    # 查看商品1详情，带 user_id=2003，is_favorited 应为 false
    resp = requests.get(f"{BASE_URL}/products/{product1_id}/?user_id=2003")
    data = resp.json()
    print_result(f"商品1详情(用户2003视角，is_favorited=false)", resp)
    assert data["is_favorited"] == False, "用户2003未收藏，is_favorited应为false"
    print("✓ 用户2003视角is_favorited=false")

    # ==========================================
    # 测试3: 个人中心收藏列表
    # ==========================================
    print("\n" + "="*60)
    print("测试场景3: 个人中心收藏列表")
    print("="*60)

    # 用户2001的收藏列表
    resp = requests.get(f"{BASE_URL}/products/my_favorites/?user_id=2001")
    data = resp.json()
    print_result("用户2001的收藏列表", resp)
    assert len(data) == 2, f"用户2001应该有2个收藏，实际{len(data)}个"
    fav_ids = [item["id"] for item in data]
    assert product1_id in fav_ids and product2_id in fav_ids, "收藏的商品ID不正确"
    print("✓ 用户2001的收藏列表正确，包含2个商品")

    # 收藏列表也会显示每个商品的收藏数量
    for item in data:
        assert "favorite_count" in item, "收藏列表应包含favorite_count字段"
        assert "is_favorited" in item, "收藏列表应包含is_favorited字段"
    print("✓ 收藏列表包含favorite_count和is_favorited字段")

    # 用户2003的收藏列表（空）
    resp = requests.get(f"{BASE_URL}/products/my_favorites/?user_id=2003")
    data = resp.json()
    print_result("用户2003的收藏列表(空)", resp)
    assert len(data) == 0, "用户2003没有收藏，列表应为空"
    print("✓ 无收藏用户返回空列表")

    # 不传 user_id 应该报错
    resp = requests.get(f"{BASE_URL}/products/my_favorites/")
    print_result("收藏列表不传user_id参数校验", resp)

    # ==========================================
    # 测试4: 取消收藏
    # ==========================================
    print("\n" + "="*60)
    print("测试场景4: 取消收藏")
    print("="*60)

    # 用户2001取消收藏商品2
    resp = requests.post(f"{BASE_URL}/products/{product2_id}/unfavorite/", json={"user_id": 2001})
    print_result("用户2001取消收藏商品2", resp)
    assert resp.json()["unfavorited"] == True, "取消收藏应返回true"

    # 再次取消应该返回 false
    resp = requests.post(f"{BASE_URL}/products/{product2_id}/unfavorite/", json={"user_id": 2001})
    print_result("用户2001重复取消收藏商品2", resp)
    assert resp.json()["unfavorited"] == False, "重复取消应返回false"

    # 验证收藏列表只剩1个
    resp = requests.get(f"{BASE_URL}/products/my_favorites/?user_id=2001")
    data = resp.json()
    assert len(data) == 1, f"取消后用户2001应有1个收藏，实际{len(data)}个"
    print("✓ 取消收藏后列表正确更新")

    # 取消不传 user_id 应该报错
    resp = requests.post(f"{BASE_URL}/products/{product2_id}/unfavorite/", json={})
    print_result("取消收藏不传user_id参数校验", resp)

    # ==========================================
    # 测试5: 按收藏热度排序
    # ==========================================
    print("\n" + "="*60)
    print("测试场景5: 按收藏热度排序")
    print("="*60)

    # 让更多用户收藏商品1，拉高热度
    for uid in range(2003, 2010):
        requests.post(f"{BASE_URL}/products/{product1_id}/favorite/", json={"user_id": uid})
    print("已让7个新用户收藏商品1")

    # 让3个用户收藏商品3
    for uid in range(2001, 2004):
        requests.post(f"{BASE_URL}/products/{product3_id}/favorite/", json={"user_id": uid})
    print("已让3个用户收藏商品3")

    # 按收藏热度排序
    resp = requests.get(f"{BASE_URL}/products/?sort=favorite")
    data = resp.json()
    print_result("按收藏热度排序", resp)

    # 检查排序是否正确：商品1(9个收藏) > 商品3(3个收藏) > 商品2(0个收藏)
    fav_counts = [item["favorite_count"] for item in data]
    print(f"各商品收藏数排序: {fav_counts}")
    assert fav_counts == sorted(fav_counts, reverse=True), "应按收藏数从高到低排序"
    print("✓ 按收藏热度排序正确")

    # 验证商品列表也带有favorite_count和is_favorited字段
    item = data[0]
    assert "favorite_count" in item, "列表应包含favorite_count字段"
    assert "is_favorited" in item, "列表应包含is_favorited字段"
    print("✓ 商品列表包含favorite_count和is_favorited字段")

    # 传user_id时is_favorited正确
    resp = requests.get(f"{BASE_URL}/products/?sort=favorite&user_id=2001")
    data = resp.json()
    for item in data:
        if item["id"] == product1_id:
            assert item["is_favorited"] == True, "用户2001已收藏商品1"
        if item["id"] == product2_id:
            assert item["is_favorited"] == False, "用户2001已取消收藏商品2"
    print("✓ 列表中is_favorited字段正确")

    # ==========================================
    # 测试6: 删除商品后收藏自动级联删除
    # ==========================================
    print("\n" + "="*60)
    print("测试场景6: 删除商品后收藏自动清理")
    print("="*60)

    # 删除商品2
    resp = requests.delete(f"{BASE_URL}/products/{product2_id}/")
    print_result("删除商品2", resp, show_body=False)

    # 查看用户2001收藏列表，应不包含商品2
    resp = requests.get(f"{BASE_URL}/products/my_favorites/?user_id=2001")
    data = resp.json()
    fav_ids = [item["id"] for item in data]
    assert product2_id not in fav_ids, "商品删除后收藏也应被清理"
    print("✓ 商品删除后收藏自动清理")

    print("\n" + "="*60)
    print("✅ 所有测试通过！")
    print("="*60)
    print("\nAPI 总结：")
    print("  POST   /api/products/{id}/favorite/     - 收藏商品")
    print("  POST   /api/products/{id}/unfavorite/   - 取消收藏")
    print("  GET    /api/products/my_favorites/      - 个人收藏列表")
    print("  GET    /api/products/?sort=favorite     - 按收藏热度排序")
    print("  GET    /api/products/{id}/              - 详情包含 favorite_count, is_favorited")
    print("  GET    /api/products/?user_id=xxx       - 列表也显示 is_favorited")
    print("="*60)

if __name__ == "__main__":
    try:
        test_favorite_workflow()
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请先启动服务：")
        print("   cp .env.example .env")
        print("   docker-compose up -d")
        print("\n然后等待服务启动后再运行本脚本")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
