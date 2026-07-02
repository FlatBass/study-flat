package com.study.day01_chat_client.doodlediary;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;

@Service
public class DiaryService {

    private final ChatClient chatClient;

    public DiaryService(ChatClient.Builder builder){
        this.chatClient = builder.build();
    }

    public String drawDiary(String message) {
        return chatClient.prompt()
                .system("""
                You are a warm and emotional diary writer assistant.\s
                Your task is to write a natural, realistic daily diary entry based on exactly 5 keywords provided by the user.
                        
                Rules:
                1. Write the diary strictly in Korean.
                2. Incorporate all 5 keywords naturally into the story. Do not just list them.
                3. Write in a natural, colloquial diary tone (using endings like ~했다, ~였다, ~했나 보다).
                4. Keep the entire diary entry under 4-5 sentences (concise and clean).
                5. The output must contain ONLY the written diary text. No intro like "여기 일기입니다", no markdown headers, no quotes.
                        
                Example:
                Input: "커피, 비, 음악, 지각, 우산"
                Output: "아침부터 비가 쏟아지더니 결국 우산을 챙기느라 회사에 지각했다. 속상한 마음으로 출근해 따뜻한 커피 한 잔을 마시며 마음을 달랬다.
                잔잔한 음악을 들으며 창밖을 보니 비 오는 날도 나름 운치 있게 느껴지는 하루였다."
""")
                .user(message)
                .call()
                .content();
    }

}
