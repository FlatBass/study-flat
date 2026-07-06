package com.study.sillok.controller;

import com.study.sillok.service.SillokQueryService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class SillokQueryController {

    private final SillokQueryService sillokQueryService;

    @GetMapping("/sillok")
    public String search(@RequestParam String question) {
        return sillokQueryService.ask(question);
    }
}
