package com.study.sillok.controller;

import com.study.sillok.service.KingChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RequestMapping("/api")
@RestController
@RequiredArgsConstructor
public class WangChatController {

    private final KingChatService kingChatService;

    @GetMapping("/wang-chat")
    public String chat(@RequestParam String message, @RequestParam String king) {
        return kingChatService.chat(message, king);
    }
}
