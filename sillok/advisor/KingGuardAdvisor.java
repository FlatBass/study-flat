package com.study.sillok.advisor;

import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClientRequest;
import org.springframework.ai.chat.client.ChatClientResponse;
import org.springframework.ai.chat.client.advisor.api.CallAdvisor;
import org.springframework.ai.chat.client.advisor.api.CallAdvisorChain;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.model.Generation;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import java.util.regex.Pattern;

@Component
@Slf4j
public class KingGuardAdvisor implements CallAdvisor{

    // 필요에 맞게 계속 보강하세요. 완벽한 반말 탐지는 불가능합니다.
    private static final List<Pattern> RUDE_PATTERNS = List.of(
            Pattern.compile(".*(야|냐\\??|해라|하지마|닥쳐|꺼져|미친|새끼|병신|지랄|시발|씨발)\\s*$"),
            Pattern.compile(".*(뭐래|알아서\\s?해|그러던가)\\s*$")
    );

    // 왕이 '직접' 명령하는 1인칭 대사
    private static final List<String> PUNISHMENTS = List.of(
            "무엄하도다! 여봐라, 이 자를 당장 흑산도로 유배 보내라!",
            "감히 과인 앞에서 그런 말투를 쓰다니. 저잣거리 채소전으로 끌고 가 배추나 나르게 하라!",
            "이런 방자한 언사를 보았느냐! 저자의 녹봉을 삭감하고 근신을 명한다!",
            "무엄한 것! 당장 파직하고 남해로 부처(付處)하라!",
            "네 이놈, 목이 몇 개나 되느냐! 여봐라, 의금부로 압송하라!"
    );

    @Override
    public ChatClientResponse adviseCall(ChatClientRequest request, CallAdvisorChain chain) {
        String userText = request.prompt().getContents().trim();
        boolean isRude = RUDE_PATTERNS.stream().anyMatch(p -> p.matcher(userText).matches());

        if (isRude) {
            String punishment = PUNISHMENTS.get(ThreadLocalRandom.current().nextInt(PUNISHMENTS.size()));
            log.warn("[왕의 진노] 무엄한 언사 감지: {}", userText);

            return ChatClientResponse.builder()
                    .chatResponse(ChatResponse.builder()
                            .generations(List.of(new Generation(new AssistantMessage(punishment))))
                            .build())
                    .context(Map.copyOf(request.context()))
                    .build();
        }
        return chain.nextCall(request);
    }

    @Override
    public String getName() {
        return this.getClass().getSimpleName();
    }

    @Override
    public int getOrder() {
        return 0; // MessageChatMemoryAdvisor(기본값이 훨씬 앞단)보다는 안쪽에서 실행 → 이 응답도 실록에 저장됨
    }
}
