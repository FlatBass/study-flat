package com.study.gifanalze.service;

import com.study.gifanalze.GifFrameExtractor;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.content.Media;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.util.MimeTypeUtils;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.util.List;

/**
 * Gemini는 image/gif를 직접 지원하지 않으므로, GIF를 프레임 단위 PNG로 쪼갠 뒤
 * "시간 순서대로 나열된 애니메이션 프레임들"이라고 명시한 프롬프트와 함께
 * 여러 장의 이미지로 한 번에 전달한다.
 */
@Service
public class GifAnalysisService {

    private static final int MAX_FRAMES = 6;

    private final ChatClient chatClient;

    public GifAnalysisService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public String analyzeGif(MultipartFile file) {
        validateGif(file);

        byte[] gifBytes;
        try {
            gifBytes = file.getBytes();
        } catch (IOException e) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "GIF 파일을 읽는 중 오류가 발생했습니다.");
        }

        List<byte[]> frames = GifFrameExtractor.extractFramesAsPng(gifBytes, MAX_FRAMES);
        if (frames.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY,
                    "GIF에서 분석할 프레임을 추출하지 못했습니다.");
        }

        List<Media> mediaList = frames.stream()
                .map(png -> Media.builder()
                        .mimeType(MimeTypeUtils.IMAGE_PNG)
                        .data(new ByteArrayResource(png))
                        .build())
                .toList();

        String prompt = "첨부한 이미지들은 하나의 GIF 애니메이션에서 시간 순서대로 추출한 프레임들입니다. "
                + "프레임 순서를 바탕으로 애니메이션에서 어떤 동작·변화가 일어나는지, "
                + "그리고 전체적으로 무엇을 표현하는 GIF인지 설명해주세요.";

        UserMessage userMessage = UserMessage.builder()
                .text(prompt)
                .media(mediaList)
                .build();

        return chatClient.prompt(new Prompt(userMessage))
                .call()
                .content();
    }

    private void validateGif(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "GIF 파일을 업로드해주세요.");
        }
        String contentType = file.getContentType();
        if (contentType == null || !contentType.equals("image/gif")) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "GIF 파일만 지원합니다. 받은 타입: " + contentType);
        }
    }
}