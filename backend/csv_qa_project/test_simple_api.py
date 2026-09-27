"""
测试无状态API - 演示如何使用单一问答接口
每次请求都需要上传CSV文件
"""
import logging
logger = logging.getLogger(__name__)
import requests
import json
import glob
import os

API_URL = "http://localhost:8000"
DATA_DIR = "./data/NL2SQL_temp/csv_qa_project/data"


def load_csv_files():
    """
    加载所有CSV文件
    返回: [(field_name, (filename, file_object, content_type)), ...]
    """
    csv_files = []
    csv_paths = glob.glob(f"{DATA_DIR}/*.csv")
    
    if not csv_paths:
        logger.warning(f"⚠️  警告: 在 {DATA_DIR} 目录下没有找到CSV文件")
        return []
    
    for filepath in csv_paths:
        filename = os.path.basename(filepath)
        csv_files.append(
            ('csv_files', (filename, open(filepath, 'rb'), 'text/csv'))
        )
    
    logger.info(f"📁 已加载 {len(csv_files)} 个CSV文件: {', '.join([f[1][0] for f in csv_files])}")
    return csv_files


def close_csv_files(csv_files):
    """关闭所有打开的文件"""
    for _, file_tuple in csv_files:
        file_tuple[1].close()


def ask_question(question, history=None):
    """
    发送问题到API
    
    Args:
        question: 问题文本
        history: 历史对话列表（可选）
    
    Returns:
        API响应的JSON结果
    """
    csv_files = load_csv_files()
    if not csv_files:
        return {"success": False, "error": "没有可用的CSV文件"}
    
    try:
        data = {"question": question}
        if history:
            data["history"] = json.dumps(history, ensure_ascii=False)
        
        response = requests.post(f"{API_URL}/ask", data=data, files=csv_files)
        return response.json()
    
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "无法连接到API服务器"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    finally:
        close_csv_files(csv_files)


def test_basic_question():
    """测试1: 基础问答"""
    logger.info("\n" + "="*70)
    logger.info("📋 测试1: 基础问答")
    logger.info("="*70)
    
    question = "有哪些数据集可用？"
    logger.info(f"❓ 问题: {question}")
    
    result = ask_question(question)
    
    if result['success']:
        logger.info(f"✅ 成功")
        logger.info(f"� 答案: {result['answer']}")
        logger.info(f"🆔 会话ID: {result['session_id']}")
        logger.info(f"⏱️  耗时: {result['execution_time']:.2f}秒")
        return True
    else:
        logger.error(f"❌ 失败: {result.get('error', '未知错误')}")
        return False


def test_with_history():
    """测试2: 带历史对话的问答"""
    logger.info("\n" + "="*70)
    logger.info("📋 测试2: 带历史对话的问答")
    logger.info("="*70)
    
    # 模拟历史对话
    history = [
        {"role": "user", "content": "有哪些数据集？"},
        {"role": "assistant", "content": "有产品目录、销售订单、员工信息、客户信息等数据集。"}
    ]
    
    logger.info("💭 历史对话:")
    for msg in history:
        role_name = "用户" if msg['role'] == 'user' else "AI"
        logger.info(f"   {role_name}: {msg['content']}")
    
    question = "统计每个产品类别的总销售额"
    logger.info(f"\n❓ 当前问题: {question}")
    
    result = ask_question(question, history)
    
    if result['success']:
        logger.info(f"✅ 成功")
        answer = result['answer']
        if len(answer) > 200:
            logger.info(f"💬 答案: {answer[:200]}...")
        else:
            logger.info(f"� 答案: {answer}")
        logger.info(f"⏱️  耗时: {result['execution_time']:.2f}秒")
        return True
    else:
        logger.error(f"❌ 失败: {result.get('error', '未知错误')}")
        return False


def test_complex_query():
    """测试3: 复杂查询（多表关联）"""
    logger.info("\n" + "="*70)
    logger.info("📋 测试3: 复杂查询（多表关联）")
    logger.info("="*70)
    
    question = "价格最高的5个产品是什么？"
    logger.info(f"❓ 问题: {question}")
    
    result = ask_question(question)
    
    if result['success']:
        logger.info(f"✅ 成功")
        answer = result['answer']
        if len(answer) > 300:
            logger.info(f"💬 答案: {answer[:300]}...")
        else:
            logger.info(f"💬 答案: {answer}")
        logger.info(f"⏱️  耗时: {result['execution_time']:.2f}秒")
        return True
    else:
        logger.error(f"❌ 失败: {result.get('error', '未知错误')}")
        return False


def test_multi_turn_conversation():
    """测试4: 多轮对话（保持上下文）"""
    logger.info("\n" + "="*70)
    logger.info("📋 测试4: 多轮对话（保持上下文）")
    logger.info("="*70)
    logger.info("💡 说明: 每次请求都重新上传CSV文件，通过history参数保持对话上下文")
    
    history = []
    
    questions = [
        "员工信息表有多少行数据？",
        "其中技术部有多少人？",
        "他们的平均薪资是多少？"
    ]
    
    success_count = 0
    
    for i, question in enumerate(questions, 1):
        logger.info(f"\n{'─'*70}")
        logger.info(f"� 第 {i}/{len(questions)} 轮")
        logger.info(f"❓ 问题: {question}")
        
        result = ask_question(question, history if history else None)
        
        if result['success']:
            answer = result['answer']
            
            # 显示答案（截断过长内容）
            if len(answer) > 150:
                logger.info(f"💬 答案: {answer[:150]}...")
            else:
                logger.info(f"💬 答案: {answer}")
            
            logger.info(f"⏱️  耗时: {result['execution_time']:.2f}秒")
            
            # 更新历史
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": answer})
            
            success_count += 1
        else:
            logger.error(f"❌ 失败: {result.get('error', '未知错误')}")
            break
    
    logger.info(f"\n{'─'*70}")
    logger.info(f"✅ 多轮对话完成: {success_count}/{len(questions)} 轮成功")
    
    return success_count == len(questions)


def main():
    """主测试流程"""
    logger.info("\n" + "="*70)
    logger.info("🧪 测试简化版API - 单一问答接口")
    logger.info("="*70)
    logger.info("\n确保API服务器正在运行: python api_server.py")
    logger.info("或者: uvicorn api_server:app --reload")
    
    try:
        # 测试服务器是否运行
        response = requests.get(f"{API_URL}/")
        logger.info(f"\n✅ API服务器运行正常: {response.json()['message']}")
    except requests.exceptions.ConnectionError:
        logger.info("\n❌ 无法连接到API服务器，请先启动服务器")
        return
    
    try:
        # # 测试1: 基础问答
        # test_basic_question()
        
        # # 测试2: 带历史对话
        # test_with_history()
        
        # 测试3: 复杂查询
        test_complex_query()
        
        # # 测试4: 多轮对话
        # test_multi_turn_conversation()
        
        logger.info("\n" + "="*70)
        logger.info("🎉 所有测试完成！")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
