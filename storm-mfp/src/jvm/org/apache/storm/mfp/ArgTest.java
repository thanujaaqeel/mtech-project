package org.apache.storm.mfp;

import java.util.List;
import java.util.Map;
import java.util.HashMap;

public class ArgTest{
  // static methods
  private static Map<String, String> buildDefaultRunOptions(){
    HashMap<String, String> map = new HashMap();
    map.put("name", "mfp");
    map.put("workers", "2");
    map.put("host", "localhost");
    map.put("transaction", "1,1");
    map.put("mfp", "1,1");
    map.put("reporter", "1,1");
    map.put("windowSize", "20");
    map.put("slidingWindowSize", "5");
    map.put("mfpSupportLevel", "2");

    return map;
  }

  private static Map<String, String> buildRunOptions(String[] args){
    Map<String, String> runOptions = buildDefaultRunOptions();

    for(String arg : args){
      String[] parts = arg.split(":");
      String option = parts[0].trim();
      String value = parts[1].trim();
      runOptions.put(option, value);
    }
    return runOptions;
  }

  public static void main(String[] args){
    Map<String, String> runOptions = buildRunOptions(args);
    System.out.println("OPTIONS: \n" + runOptions.toString());
  }
}
