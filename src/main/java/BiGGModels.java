import org.sbml.jsbml.SBMLDocument;
import org.sbml.jsbml.SBMLReader;
import org.simulator.fba.FluxBalanceAnalysis;

import java.io.*;
import java.util.Objects;
import java.util.zip.GZIPInputStream;

public class BiGGModels {

    public static String basePath = System.getProperty("user.dir");
    static StringBuilder str = new StringBuilder("model\tobjective_value\tload_time\tsimulate_time\trepeat\n");

    public static void testFBA(File dir) throws Exception {

        for (File file : Objects.requireNonNull(dir.listFiles())) {
            String file_name = file.getName();
            String model_name = file.getName().substring(0, file_name.length() - 7);
            String completePath = file.getAbsolutePath();

            for (int rep = 1; rep <= 5; rep++) {
                InputStream stream = new GZIPInputStream(new FileInputStream(completePath));
                double loadTime;
                double simulateTime;

                double startTime = System.nanoTime();
                SBMLDocument doc = SBMLReader.read(stream);
                FluxBalanceAnalysis solver = new FluxBalanceAnalysis(doc);
                loadTime = (System.nanoTime() - startTime);

                startTime = System.nanoTime();
                solver.solve();
                simulateTime = (System.nanoTime() - startTime);

                str.append(model_name).append("\t");
                str.append(solver.getObjectiveValue()).append("\t");
                str.append(loadTime / 1E9).append("\t");
                str.append(simulateTime / 1E9).append("\t");
                str.append(rep).append("\n");
            }
        }

        File file2 = new File(basePath + "/results/fba/bigg_sbscl.tsv");
        FileWriter fr = new FileWriter(file2);
        fr.write(str.toString());
        fr.close();

    }

    public static void main(String[] args) throws Exception {
        String path = basePath + "/models/bigg-v1.6";
        testFBA(new File(path));
    }
}
