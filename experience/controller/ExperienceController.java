package com.study.day02promptoutput.day2experience.controller;

import com.study.day02promptoutput.day2experience.dto.ExperienceBreakdownResponse;
import com.study.day02promptoutput.day2experience.dto.ResumeResponse;
import com.study.day02promptoutput.day2experience.service.ExperienceService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;

@Controller
@RequiredArgsConstructor
public class ExperienceController {

    private final ExperienceService experienceService;

    @GetMapping("/experience")
    public String experienceForm() {
        return "experience/experience-form";
    }

    @PostMapping("/experience")
    public String analyzeExperience(@RequestParam String experience,
                                    Model model) {
        ExperienceBreakdownResponse  breakdown =
                experienceService.breakdownExperience(experience);

        model.addAttribute("experience", experience);
        model.addAttribute("breakdown", breakdown);

        return "experience/experience-result";
    }
}
