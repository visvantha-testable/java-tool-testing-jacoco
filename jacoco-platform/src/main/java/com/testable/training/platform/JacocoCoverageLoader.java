package com.testable.training.platform;

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
            return OfficialJacocoAnalyzer.fromExec(execFile, classesDir);
        }
        return JacocoXmlParser.parse(jacocoXml);
    }
}
