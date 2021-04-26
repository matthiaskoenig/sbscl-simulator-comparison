import org.sbml.jsbml.Model;
import org.sbml.jsbml.xml.stax.SBMLReader;
import org.simulator.math.odes.AdaptiveStepsizeIntegrator;
import org.simulator.math.odes.MultiTable;
import org.simulator.math.odes.RosenbrockSolver;
import org.simulator.sbml.SBMLinterpreter;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class Biomodels {

    public static String path = System.getProperty("user.dir");
    static StringBuilder str = new StringBuilder("model\tstatus\tload_time\tsimulate_time\trepeat\n");

    public static void testBiomodels(String file, int from, int to) throws IOException {
        AdaptiveStepsizeIntegrator solver = new RosenbrockSolver();
        solver.setAbsTol(1E-10);
        solver.setRelTol(1E-6);
        for (int modelnr = from; modelnr <= to; modelnr++) {
            for (int rep = 1; rep <= 5; rep++) {
                System.out.println("Biomodel " + modelnr);
                Model model = null;
                String modelName = "";
                try {
                    String modelFile = "";
                    if (modelnr < 10) {
                        modelFile = file + "BIOMD000000000" + modelnr + ".xml";
                        modelName = "BIOMD000000000" + modelnr;
                    } else if (modelnr < 100) {
                        modelFile = file + "BIOMD00000000" + modelnr + ".xml";
                        modelName = "BIOMD00000000" + modelnr;
                    } else if (modelnr < 1000) {
                        modelFile = file + "BIOMD0000000" + modelnr + ".xml";
                        modelName = "BIOMD0000000" + modelnr;
                    } else {
                        modelFile = file + "BIOMD000000" + modelnr + ".xml";
                        modelName = "BIOMD000000" + modelnr;
                    }
                    model = (new SBMLReader()).readSBML(modelFile).getModel();
                } catch (Exception e) {
                    model = null;
//                logger.warning("Exception while reading Biomodel " + modelnr);
                }
                if (model != null) {
                    solver.reset();
                    try {
                        double loadTime;
                        double simulateTime = 0d;
                        boolean status = true;
                        double time1 = System.nanoTime();
                        SBMLinterpreter interpreter = new SBMLinterpreter(model);
                        loadTime = (System.nanoTime() - time1);

                        MultiTable solution = null;
                        if ((solver != null) && (interpreter != null)) {
                            solver.setStepSize(1);
                            time1 = System.nanoTime();
                            solution = solver.solve(interpreter, interpreter.getInitialValues(), 0, 100);
                            simulateTime = (System.nanoTime() - time1);
                            if (solver.isUnstable()) {
                                status = false;
                            }
                        }

                        str.append(modelName).append("\t");
                        if (status) {
                            str.append("success\t");
                        } else {
                            str.append("failure\t");
                        }
                        str.append(loadTime / 1E9).append("\t");
                        str.append(simulateTime / 1E9).append("\t");
                        str.append(rep).append("\n");

                        File file1 = new File(path + "/results/ode/sbscl/" + modelName + ".tsv");
                        FileWriter fr = new FileWriter(file1);
                        StringBuilder s = getResultAsTSV(solution);
                        fr.write(s.toString());
                        fr.close();
                    } catch (Exception e) {
//                    logger.warning("Exception in Biomodel " + modelnr);
                    }
                }
            }
        }

        File file2 = new File(path + "/results/ode/biomodels_sbscl.tsv");
        FileWriter fr = new FileWriter(file2);
        fr.write(str.toString());
        fr.close();

    }

    public static void main(String[] args)
            throws IOException {
        testBiomodels(path + "/models/biomodels/", 1, 100);
    }

    private static StringBuilder getResultAsTSV(MultiTable result) {
        StringBuilder output = new StringBuilder("");

        for (int i = 0; i < result.getColumnCount() - 1; i++) {
            output.append(result.getColumnName(i)).append("\t");
        }
        output.append(result.getColumnName(result.getColumnCount() - 1)).append("\n");

        for (int i = 0; i < result.getRowCount(); i++) {
            for (int j = 0; j < result.getColumnCount() - 1; j++) {
                output.append(result.getValueAt(i, j)).append("\t");
            }
            output.append(result.getValueAt(i, result.getColumnCount() - 1)).append("\n");
        }

        return output;
    }
}
