package com.study.gifanalze;

import javax.imageio.ImageIO;
import javax.imageio.ImageReader;
import javax.imageio.metadata.IIOMetadata;
import javax.imageio.metadata.IIOMetadataNode;
import javax.imageio.stream.ImageInputStream;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;

/**
 * Gemini는 image/gif를 지원하지 않는다 (전송 시 400 "Unsupported MIME type: image/gif").
 * 그래서 GIF를 프레임 단위 PNG 이미지들로 변환해 모델에 "여러 장의 스틸컷"으로 전달한다.
 *
 * 주의: Java 내장 GIF 리더(ImageReader#read)는 프레임을 있는 그대로만 디코딩하며,
 * 최적화된(optimized) GIF는 프레임마다 "달라진 영역"만 담고 있어 그대로 PNG로 저장하면
 * 그림이 깨져 보인다. 그래서 GraphicControlExtension의 disposalMethod와
 * ImageDescriptor의 좌표를 직접 읽어 캔버스에 합성(compositing)한 뒤 PNG로 저장한다.
 */
public final class GifFrameExtractor {

    private GifFrameExtractor() {
    }

    public static List<byte[]> extractFramesAsPng(byte[] gifBytes, int maxFrames) {
        try (ImageInputStream iis = ImageIO.createImageInputStream(new ByteArrayInputStream(gifBytes))) {
            ImageReader reader = findGifReader();
            reader.setInput(iis, false);

            int totalFrames = reader.getNumImages(true);
            if (totalFrames <= 0) {
                throw new IllegalStateException("GIF에서 프레임을 읽을 수 없습니다.");
            }

            List<BufferedImage> composited = compositeAllFrames(reader, totalFrames);
            List<Integer> sampledIndexes = sampleIndexes(composited.size(), maxFrames);

            List<byte[]> pngFrames = new ArrayList<>();
            for (int index : sampledIndexes) {
                pngFrames.add(toPngBytes(composited.get(index)));
            }
            reader.dispose();
            return pngFrames;
        } catch (IOException e) {
            throw new IllegalStateException("GIF 프레임 추출 중 오류가 발생했습니다.", e);
        }
    }

    private static ImageReader findGifReader() {
        Iterator<ImageReader> readers = ImageIO.getImageReadersByFormatName("gif");
        if (!readers.hasNext()) {
            throw new NoSuchElementException("GIF 리더를 찾을 수 없습니다.");
        }
        return readers.next();
    }

    /**
     * 모든 프레임을 논리 화면 크기 캔버스에 순서대로 합성해 "완성된 그림" 리스트로 반환한다.
     */
    private static List<BufferedImage> compositeAllFrames(ImageReader reader, int totalFrames) throws IOException {
        int canvasWidth = reader.getWidth(0);
        int canvasHeight = reader.getHeight(0);
        BufferedImage canvas = new BufferedImage(canvasWidth, canvasHeight, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g2d = canvas.createGraphics();

        List<BufferedImage> result = new ArrayList<>();
        BufferedImage previousSnapshot = null;
        String previousDisposal = "none";

        for (int i = 0; i < totalFrames; i++) {
            BufferedImage frame = reader.read(i);
            IIOMetadata metadata = reader.getImageMetadata(i);
            FrameInfo info = readFrameInfo(metadata);

            if ("restoreToBackgroundColor".equals(previousDisposal)) {
                g2d.clearRect(0, 0, canvasWidth, canvasHeight);
            } else if ("restoreToPrevious".equals(previousDisposal) && previousSnapshot != null) {
                g2d.drawImage(previousSnapshot, 0, 0, null);
            }

            if ("restoreToPrevious".equals(info.disposalMethod())) {
                previousSnapshot = deepCopy(canvas);
            }

            g2d.drawImage(frame, info.left(), info.top(), null);
            result.add(deepCopy(canvas));

            previousDisposal = info.disposalMethod();
        }

        g2d.dispose();
        return result;
    }

    private record FrameInfo(int left, int top, String disposalMethod) {
    }

    private static FrameInfo readFrameInfo(IIOMetadata metadata) {
        int left = 0;
        int top = 0;
        String disposal = "none";

        IIOMetadataNode root = (IIOMetadataNode) metadata.getAsTree("javax_imageio_gif_image_1.0");

        IIOMetadataNode imageDescriptor = firstChild(root, "ImageDescriptor");
        if (imageDescriptor != null) {
            left = parseIntSafe(imageDescriptor.getAttribute("imageLeftPosition"));
            top = parseIntSafe(imageDescriptor.getAttribute("imageTopPosition"));
        }

        IIOMetadataNode graphicControl = firstChild(root, "GraphicControlExtension");
        if (graphicControl != null) {
            String value = graphicControl.getAttribute("disposalMethod");
            if (value != null && !value.isBlank()) {
                disposal = value;
            }
        }

        return new FrameInfo(left, top, disposal);
    }

    private static IIOMetadataNode firstChild(IIOMetadataNode parent, String name) {
        var nodes = parent.getElementsByTagName(name);
        return nodes.getLength() > 0 ? (IIOMetadataNode) nodes.item(0) : null;
    }

    private static int parseIntSafe(String value) {
        try {
            return (value == null || value.isBlank()) ? 0 : Integer.parseInt(value);
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    private static BufferedImage deepCopy(BufferedImage source) {
        BufferedImage copy = new BufferedImage(source.getWidth(), source.getHeight(), BufferedImage.TYPE_INT_ARGB);
        Graphics2D g = copy.createGraphics();
        g.drawImage(source, 0, 0, null);
        g.dispose();
        return copy;
    }

    private static List<Integer> sampleIndexes(int total, int maxFrames) {
        List<Integer> indexes = new ArrayList<>();
        if (total <= maxFrames) {
            for (int i = 0; i < total; i++) {
                indexes.add(i);
            }
            return indexes;
        }
        double step = (double) total / maxFrames;
        for (int i = 0; i < maxFrames; i++) {
            indexes.add((int) Math.floor(i * step));
        }
        return indexes;
    }

    private static byte[] toPngBytes(BufferedImage image) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        ImageIO.write(image, "png", out);
        return out.toByteArray();
    }
}
