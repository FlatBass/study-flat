package com.study.day02promptoutput.day2experience.dto;

import java.util.List;

public record ExperienceBreakdownResponse(
        String situation,
        List<ProblemGroup> problems
) {
}
