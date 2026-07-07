package com.study.gifanalze.controller;

import com.study.gifanalze.dto.GifAnalysisResponse;
import com.study.gifanalze.service.GifAnalysisService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
public class GifAnalysisController {

    private final GifAnalysisService gifAnalysisService;

    public GifAnalysisController(GifAnalysisService gifAnalysisService) {
        this.gifAnalysisService = gifAnalysisService;
    }

    /** GIF 파일을 프레임 단위로 분석해 애니메이션 내용을 설명한다. */
    @PostMapping("/api/gif-analysis")
    public GifAnalysisResponse analyzeGif(@RequestParam MultipartFile file) {
        String description = gifAnalysisService.analyzeGif(file);
        return new GifAnalysisResponse(description);
    }
}
