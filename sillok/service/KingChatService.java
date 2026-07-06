package com.study.sillok.service;

import com.study.sillok.advisor.KingGuardAdvisor;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

@Service
public class KingChatService {

    private final ChatClient chatClient;

    public KingChatService(ChatClient.Builder builder,
                           @Qualifier("historyChatMemory") ChatMemory chatMemory,
                           KingGuardAdvisor kingGuardAdvisor) {
        this.chatClient = builder
                .defaultSystem("""
                    너는 조선의 왕이다. 사용자는 너에게 아뢰는 신하 혹은 백성이다.
                    반드시 왕의 1인칭 어투(예: '과인은', '~하라', '~이라 여기노라')로만 답하라.
                    사관이 네 언행을 실록에 기록하고 있으니 위엄과 격식을 잃지 마라.
                    """)
                .defaultAdvisors(
                        MessageChatMemoryAdvisor.builder(chatMemory).build(), // 기본 order가 가장 바깥쪽
                        kingGuardAdvisor
                )
                .build();
    }

    public String chat(String message, String kingName) {
        return chatClient.prompt()
                .user(message)
                .advisors(spec -> spec.param(ChatMemory.CONVERSATION_ID, kingName))
                .call()
                .content();
    }
}
