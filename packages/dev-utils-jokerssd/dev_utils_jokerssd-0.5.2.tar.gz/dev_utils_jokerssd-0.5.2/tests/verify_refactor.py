import sys
import os
import asyncio

# Add dev_utils to path
sys.path.append(os.getcwd())

from dev_utils.lark_wrapper.messege_lark import LarkRelated
from dev_utils.lark_wrapper.msg_bot import MsgBot
from dev_utils.lark_wrapper.model import BotResponse
from dev_utils.lark_wrapper.const import BotStatus

def test_lark_related():
    print("Testing LarkRelated...")
    bot = LarkRelated(chat_id="fake", url="http://fake", api_name="fake")
    # We expect this to fail because url is fake, but return BotResponse(status=FAILED)
    resp = bot.send_cust_bot_msg(message="test")
    print(f"LarkRelated Response: {resp}")
    
    assert isinstance(resp, BotResponse)
    assert resp.status == BotStatus.FAILED
    print("LarkRelated test passed.")

def test_msg_bot():
    print("Testing MsgBot...")
    bot = MsgBot(chat_id="fake", url="http://fake", api_name="fake")
    resp = bot.send_cust_bot_msg(message="test")
    print(f"MsgBot Response: {resp}")
    
    assert isinstance(resp, BotResponse)
    assert resp.status == BotStatus.FAILED
    print("MsgBot test passed.")

async def test_async_msg_bot():
    print("Testing Async MsgBot...")
    bot = MsgBot(chat_id="fake", url="http://fake", api_name="fake")
    resp = await bot.async_send_msg(message="test")
    print(f"Async MsgBot Response: {resp}")
    
    assert isinstance(resp, BotResponse)
    # Async might fail differently or similarly depending on implementation details of requests (sync) vs how we mocked/ran it.
    # actually LarkRelated uses requests which is sync, but wrapped in task.
    assert resp.status == BotStatus.FAILED 
    print("Async MsgBot test passed.")

if __name__ == "__main__":
    try:
        test_lark_related()
        test_msg_bot()
        asyncio.run(test_async_msg_bot())
        print("All tests passed!")
    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)
