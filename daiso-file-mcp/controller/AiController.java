package com.study.day05_tool_mcp.controller;

import com.study.day05_tool_mcp.service.McpChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class AiController {

    private final McpChatService mcpChatService;

    @GetMapping("/api/mcp")
    public String mcpTool(@RequestParam String question) {
        return mcpChatService.chatFilesystem(question);
    }

    @GetMapping("/api/daiso")
    public String mcpDaiso(@RequestParam String question) {
        return mcpChatService.chatDaiso(question);
    }

    @GetMapping("/api/daiso-file")
    public String daisoToFile(@RequestParam String question) {
        return mcpChatService.chatDaisoAndSave(question);
    }

}
