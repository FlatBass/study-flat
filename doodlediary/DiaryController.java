package com.study.day01_chat_client.doodlediary;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class DiaryController {

    private final DiaryService diaryService;

    public DiaryController(DiaryService diaryService){
        this.diaryService = diaryService;
    }

    @GetMapping("/diary-page")
    public String diaryPage() {
        return "diary"; // templates/diary.html 파일을 찾아갑니다.
    }

    @GetMapping("/diary")
    @ResponseBody
    public String diary(@RequestParam String text) {
        return diaryService.drawDiary(text);
    }

}
