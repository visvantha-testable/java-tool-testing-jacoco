package com.testable.training.platform;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Resolves JaCoCo coverage counters using official org.jacoco.core when possible,
 * falling back to jacoco.xml parsing for synthesized training artifacts.
 */
public final class JacocoCoverageLoader {

    private JacocoCoverageLoader() {
    }

    public static JacocoCounters load(Path jacocoXml, Path repoRoot) throws Exception {
        Path execFile = repoRoot.resolve("sample_subject/target/jacoco.exec");
        Path classesDir = repoRoot.resolve("sample_subject/target/classes");
        if (Files.exists(execFile) && Files.isDirectory(classesDir)) {
            try {
                JacocoCounters official = OfficialJacocoAnalyzer.fromExec(execFile, classesDir);
                if (official.lineCovered + official.lineMissed > 0) {
                    return official;
                }
            } catch (IOException ignored) {
                // fall back to XML below
            }
        }
        return JacocoXmlParser.parse(jacocoXml);
    }
}
