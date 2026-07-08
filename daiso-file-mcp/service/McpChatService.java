package com.study.day05_tool_mcp.service;

import com.study.day05_tool_mcp.mcp.McpToolCatalog;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.stereotype.Service;

@Service
public class McpChatService {

    private final ChatClient chatClient;
    private final McpToolCatalog catalog;


    public McpChatService(ChatClient.Builder builder,
                          McpToolCatalog catalog) {
        this.chatClient = builder.build();
        this.catalog = catalog;
    }

    public String chatFilesystem(String question) {
        return ask(question, catalog.filesystemTools());
    }

    public String chatDaiso(String question) {
        return ask(question, catalog.daisoTools());
    }

    // 다이소 검색 + 파일 저장을 한 번에
    public String chatDaisoAndSave(String question) {

        String systemPrompt = """
                너는 다이소 상품/매장 정보를 조회하고, 그 결과를 로컬 파일로 저장하는 에이전트야.
                다음 절차를 반드시 따라라:
                1. 사용자 질문에 필요한 다이소 관련 도구(daiso_ 접두사)를 사용해 정보를 검색한다.
                2. 검색 결과를 사용자가 요청한 형식(txt 또는 json)에 맞게 정리한다.
                   - json이면 유효한 JSON 배열/객체로, 들여쓰기 포함해서 만든다.
                   - txt면 사람이 읽기 편한 줄글/목록 형태로 만든다.
                3. filesystem 도구(write_file 등)를 사용해 결과를 파일로 저장한다.
                   파일 경로는 반드시 서버에 허용된 루트 디렉토리(mcp-sandbox) 하위에 상대 경로로 지정한다.
                   파일명은 질문 내용을 유추해 알기 쉽게 짓는다 (예: daiso_storage_box_inventory.json).
                4. 마지막에 어떤 파일에 무엇을 저장했는지 사용자에게 간단히 요약해서 알려준다.
                """;

        return chatClient.prompt()
                .system(systemPrompt)
                .user(question)
                .tools((Object[]) catalog.allTools())
                .call()
                .content();
    }

    private String ask(String question, ToolCallback[] tools) {
        return chatClient.prompt()
                .user(question)
                .tools((Object[]) tools)
                .call()
                .content();
    }

}
