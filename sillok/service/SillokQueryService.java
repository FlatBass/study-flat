package com.study.sillok.service;

import lombok.RequiredArgsConstructor;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class SillokQueryService {

    private final JdbcTemplate jdbcTemplate;
    private final ChatClient.Builder chatClientBuilder;

    public String ask(String question) {
        List<Map<String, Object>> rows = jdbcTemplate.queryForList("""
        SELECT conversation_id, content, type
        FROM SPRING_AI_CHAT_MEMORY
        ORDER BY conversation_id
        """);

        if (rows.isEmpty()) {
            return "아직 기록된 실록이 없사옵니다.";
        }

        StringBuilder sillok = new StringBuilder();
        for (Map<String, Object> row : rows) {
            String king = String.valueOf(row.get("conversation_id"));
            String type = String.valueOf(row.get("type"));
            String content = String.valueOf(row.get("content"));
            String speaker = "USER".equals(type) ? "신하" : "전하";
            sillok.append('[').append(king).append("] ")
                    .append(speaker).append(": ").append(content).append('\n');
        }

        ChatClient chatClient = chatClientBuilder
                .defaultSystem("""
                    너는 규장각의 사관이다. 아래 제공되는 실록 기록만을 근거로
                    사용자의 질문에 답하라. 실록에 근거가 없는 내용은 추측하지 말고
                    "해당 사료를 찾을 수 없사옵니다"라고 답하라.
                    """)
                .build();

        return chatClient.prompt()
                .user(u -> u.text("""
                        [실록 기록]
                        {sillok}

                        [질문]
                        {question}
                        """)
                        .param("sillok", sillok.toString())
                        .param("question", question))
                .call()
                .content();
    }
}
