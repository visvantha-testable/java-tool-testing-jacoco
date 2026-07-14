package com.testable.training.platform;

import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.IBundleCoverage;
import org.jacoco.core.analysis.ICounter;
import org.jacoco.core.analysis.ISourceNode;
import org.jacoco.core.tools.ExecFileLoader;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Loads coverage using the official JaCoCo Core API from
 * <a href="https://github.com/jacoco/jacoco">jacoco/jacoco</a>.
 * Pattern based on org.jacoco.examples.ReportGenerator and CoreTutorial.
 */
public final class OfficialJacocoAnalyzer {

    private OfficialJacocoAnalyzer() {
    }

    public static JacocoCounters fromExec(Path execFile, Path classesDirectory) throws IOException {
        if (!Files.exists(execFile)) {
            throw new IOException("Missing JaCoCo exec file: " + execFile);
        }
        if (!Files.isDirectory(classesDirectory)) {
            throw new IOException("Missing compiled classes directory: " + classesDirectory);
        }

        ExecFileLoader loader = new ExecFileLoader();
        loader.load(execFile.toFile());

        CoverageBuilder builder = new CoverageBuilder();
        Analyzer analyzer = new Analyzer(loader.getExecutionDataStore(), builder);
        analyzer.analyzeAll(classesDirectory.toFile());

        IBundleCoverage bundle = builder.getBundle("sample_subject");
        JacocoCounters counters = fromBundle(bundle);
        if (!loader.getSessionInfoStore().getInfos().isEmpty()) {
            counters.sessionId = loader.getSessionInfoStore().getInfos().get(0).getId();
        }
        return counters;
    }

    public static JacocoCounters fromBundle(IBundleCoverage bundle) {
        JacocoCounters counters = new JacocoCounters();
        applyCounter(bundle.getLineCounter(), counters, CounterKind.LINE);
        applyCounter(bundle.getBranchCounter(), counters, CounterKind.BRANCH);
        applyCounter(bundle.getInstructionCounter(), counters, CounterKind.INSTRUCTION);

        bundle.getPackages().forEach(pkg -> pkg.getClasses().forEach(clazz -> {
            for (int line = clazz.getFirstLine(); line <= clazz.getLastLine(); line++) {
                ILine lineInfo = clazz.getLine(line);
                int status = lineInfo.getStatus();
                if ((status & ISourceNode.EMPTY) != 0) {
                    continue;
                }
                if (status == ISourceNode.NOT_COVERED) {
                    counters.ghostLines++;
                }
                ICounter branch = lineInfo.getBranchCounter();
                if (branch.getTotalCount() > 0
                        && branch.getCoveredCount() > 0
                        && branch.getMissedCount() > 0) {
                    counters.partialBranchLines++;
                }
            }
        }));
        return counters;
    }

    private enum CounterKind { LINE, BRANCH, INSTRUCTION }

    private static void applyCounter(ICounter counter, JacocoCounters counters, CounterKind kind) {
        switch (kind) {
            case LINE -> {
                counters.lineMissed = counter.getMissedCount();
                counters.lineCovered = counter.getCoveredCount();
            }
            case BRANCH -> {
                counters.branchMissed = counter.getMissedCount();
                counters.branchCovered = counter.getCoveredCount();
            }
            case INSTRUCTION -> {
                counters.instructionMissed = counter.getMissedCount();
                counters.instructionCovered = counter.getCoveredCount();
            }
        }
    }
}
