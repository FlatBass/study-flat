package com.study.day02promptoutput.day2experience.service;

import com.study.day02promptoutput.day2experience.dto.ExperienceBreakdownResponse;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ExperienceService {

    private final ChatClient chatClient;

    public ExperienceService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public ExperienceBreakdownResponse breakdownExperience(
            String experience) {
        return chatClient.prompt()
                .user(u->u.text(
                        """
                        아래 경험을 취업 준비용 경험분해 표로 정리해줘.
                        
                                응답은 다음 Java record 구조에 맞게 작성해줘.
                                
                                                                최상위 객체:
                                                                - situation: 경험의 전체 상황, 목표, 배경
                                                                - problems: 문제 목록
                                
                                                                problems의 각 항목:
                                                                - problem: 겪었던 문제 또는 어려움
                                                                - actions: 행동 목록
                                
                                                                actions의 각 항목:
                                                                - actionTaken: 문제 해결을 위해 실제로 한 행동
                                                                - competency: 그 행동에서 드러난 역량
                                
                                                                조건:
                                                                - situation은 전체 경험을 대표하는 하나의 문장으로 작성
                                                                - problems는 2개에서 4개 정도로 작성
                                                                - 각 problem마다 actions를 1개에서 4개 작성
                                                                - 사용자가 입력한 경험을 바탕으로만 작성
                                                                - 과장하지 말고 구체적으로 작성
                                
                                                                사용자 경험:
                                                                {experience}
                        """
                )
                        .param("experience", experience))
                .call()
                .entity(ExperienceBreakdownResponse.class);
    }
}
