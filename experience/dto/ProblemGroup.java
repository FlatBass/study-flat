package com.study.day02promptoutput.day2experience.dto;

import java.util.List;

public record ProblemGroup(
        String problem,
        List<ActionItem> actions
) {
}
