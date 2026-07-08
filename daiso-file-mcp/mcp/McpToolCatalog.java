package com.study.day05_tool_mcp.mcp;

import io.modelcontextprotocol.client.McpSyncClient;
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.function.Predicate;

@Component
public class McpToolCatalog {

    // @modelcontextprotocol/server-filesystem 이 노출하는 고정 도구 이름들
    private final Set<String> FILESYSTEM_TOOL_NAMES = Set.of(
            "read_file", "read_multiple_files", "write_file", "edit_file",
            "create_directory", "list_directory", "list_directory_with_sizes",
            "directory_tree", "move_file", "search_files", "get_file_info",
            "list_allowed_directories"
    );
    private final ToolCallback[] allTools;

    // 생성자 빌드 대신 Spring AI가 mcp 설정(stdio + streamable-http 전부)을 모아 자동으로 만들어주는 빈을 그대로 주입
    public McpToolCatalog(ToolCallbackProvider mcpToolCallbackProvider) {
        this.allTools = mcpToolCallbackProvider.getToolCallbacks();
    }

    // 등록된 모든 MCP 도구 (filesystem + daiso 등)
    public ToolCallback[] allTools(){
        return allTools;
    }

    /** 도구 이름 조건으로 필터링해서 서브셋을 뽑고 싶을 때 사용 */
    public ToolCallback[] toolsMatching(Predicate<String> nameFilter) {
        return Arrays.stream(allTools)
                .filter(tool -> nameFilter.test(tool.getToolDefinition().name()))
                .toArray(ToolCallback[]::new);
    }

    public ToolCallback[] filesystemTools() {
        return toolsMatching(FILESYSTEM_TOOL_NAMES::contains);
    }

    public ToolCallback[] daisoTools() {
        // filesystem 도구가 아니면 전부 daiso 계열(daiso_, cu_, cgv_ 등)로 간주
        return toolsMatching(name -> !FILESYSTEM_TOOL_NAMES.contains(name));
    }
}
