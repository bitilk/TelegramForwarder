from models.models import ForwardMode
import re
import logging
import asyncio
from handlers.message_handler import pre_handle
from utils.common import check_keywords

logger = logging.getLogger(__name__)

async def process_forward_rule(client, event, chat_id, rule):
    """处理转发规则（用户模式）"""
    should_forward = False
    message_text = event.message.text or ''
    # check_message_text = await pre_handle(message_text)
    # 添加日志
    logger.info(f'处理规则 ID: {rule.id}')
    logger.info(f'消息内容: {message_text}')
    logger.info(f'规则模式: {rule.forward_mode.value}')
    
    should_forward = await check_keywords(rule,message_text)
    
    logger.info(f'最终决定: {"转发" if should_forward else "不转发"}')
    
    if should_forward:
        target_chat = rule.target_chat
        target_chat_id = int(target_chat.telegram_chat_id)
        
        try:
            
            
            if event.message.grouped_id:
                # 等待一段时间以确保收到所有媒体组消息
                await asyncio.sleep(1)
                
                # 收集媒体组的所有消息
                messages = []
                async for message in client.iter_messages(
                    event.chat_id,
                    limit=20,  # 限制搜索范围
                    min_id=event.message.id - 10,
                    max_id=event.message.id + 10
                ):
                    if message.grouped_id == event.message.grouped_id:
                        messages.append(message.id)
                        logger.info(f'找到媒体组消息: ID={message.id}')
                
                # 按照ID排序，确保转发顺序正确
                messages.sort()
                
                # 一次性转发所有消息
                await client.forward_messages(
                    target_chat_id,
                    messages,
                    event.chat_id
                )
                logger.info(f'[用户] 已转发 {len(messages)} 条媒体组消息到: {target_chat.name} ({target_chat_id})')
                
            else:
                # 处理单条消息
                await client.forward_messages(
                    target_chat_id,
                    event.message.id,
                    event.chat_id
                )
                logger.info(f'[用户] 消息已转发到: {target_chat.name} ({target_chat_id})')
                
                
        except Exception as e:
            logger.error(f'转发消息时出错: {str(e)}')
            logger.exception(e) 