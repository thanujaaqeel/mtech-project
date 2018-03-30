
package org.apache.storm.mfp;

import org.apache.storm.Config;
import org.apache.storm.LocalCluster;
import org.apache.storm.StormSubmitter;
import org.apache.storm.task.OutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.testing.TestWordSpout;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.TopologyBuilder;
import org.apache.storm.topology.base.BaseRichBolt;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Tuple;
import org.apache.storm.tuple.Values;
import org.apache.storm.utils.Utils;
import org.apache.storm.generated.StormTopology;
import org.apache.storm.topology.base.BaseRichSpout;
import org.apache.storm.generated.AlreadyAliveException;
import org.apache.storm.generated.InvalidTopologyException;
import org.apache.storm.generated.AuthorizationException;
import org.apache.storm.topology.IWindowedBolt;
import org.apache.storm.topology.IRichSpout;

import org.apache.storm.mfp.spout.RedisTextSpout;
import org.apache.storm.mfp.spout.FileTextSpout;

import org.apache.storm.mfp.bolt.MFPMinerBolt;
import org.apache.storm.mfp.bolt.RedisReporterBolt;

import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.TimeUnit;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import static org.apache.storm.topology.base.BaseWindowedBolt.Count;
import static org.apache.storm.topology.base.BaseWindowedBolt.Duration;

import org.apache.storm.mfp.metrics.HttpForwardingMetricsConsumer;

public class MaximalFrequentPatternTopology {

  private static final String TRANSACTION_WINDOW_SIZE = "20";
  private static final String TRANSACTION_SLIDING_WINDOW_SIZE = "5";
  private static final String MFP_MINIMUM_SUPPORT_LEVEL = "2";

  private Map<String, String> options;

  public MaximalFrequentPatternTopology(Map<String, String> options){
    this.options = options;
  }

  public void runOnCluster() throws AlreadyAliveException, InvalidTopologyException, AuthorizationException{
    Config conf = new Config();

    conf.registerMetricsConsumer(HttpForwardingMetricsConsumer.class, "http://" + getHost() + ":5000/metric", 1);
    conf.setNumWorkers(getWorkers());

    StormSubmitter.submitTopologyWithProgressBar(getName(), conf, buildTopology());
  }

  private String getName(){
    return options.get("name").trim();
  }

  private String getHost(){
    return options.get("host").trim();
  }

  private int getWorkers(){
    return Integer.parseInt(options.get("workers"));
  }

  private int getExecutors(String component){
    return Integer.parseInt(options.get(component).split(",")[0]);
  }

  private int getTasks(String component){
    return Integer.parseInt(options.get(component).split(",")[1]);
  }

  private int getWindowSize(){
    return Integer.parseInt(options.get("windowSize"));
  }

  private int getSlidingWindowSize(){
    return Integer.parseInt(options.get("slidingWindowSize"));
  }

  private int getMfpSupportLevel(){
    return Integer.parseInt(options.get("mfpSupportLevel"));
  }

  private StormTopology buildTopology(){
    TopologyBuilder builder = new TopologyBuilder();

    builder.setSpout("transaction",
                     transactionsSpout(getHost()),
                     getExecutors("transaction"))
            .setNumTasks(getTasks("transaction"));

    builder.setBolt("mfp",
                    minerBolt(),
                    getExecutors("mfp"))
           .setNumTasks(getTasks("mfp"))
           .shuffleGrouping("transaction");

    builder.setBolt("reporter",
                    reporterBolt(getHost()),
                    getExecutors("reporter"))
           .setNumTasks(getTasks("reporter"))
           .shuffleGrouping("mfp");

    return builder.createTopology();
  }

  private IWindowedBolt minerBolt(){
    MFPMinerBolt minerBolt = new MFPMinerBolt(getMfpSupportLevel());
    IWindowedBolt bolt = minerBolt.withWindow(Count.of(getWindowSize()), Count.of(getSlidingWindowSize()));
    // IWindowedBolt bolt = minerBolt.withTumblingWindow(new Duration(1, TimeUnit.SECONDS));
    return bolt;
  }

  private IRichSpout transactionsSpout(String redisHost){
    RedisTextSpout spout = new RedisTextSpout(redisHost, 6379, "MFP_STREAM");
    // FileTextSpout spout = new FileTextSpout("/Users/aqeel/mtech-project/twitter-input/tweets_1.txt");
    return spout;
  }

  private RedisReporterBolt reporterBolt(String redisHost){
    RedisReporterBolt bolt = new RedisReporterBolt(redisHost, 6379, "MFP_OUTPUT_STREAM");
    return bolt;
  }

  // static methods
  private static Map<String, String> buildDefaultRunOptions(){
    HashMap<String, String> map = new HashMap();
    map.put("name", "mfp");
    map.put("workers", "2");
    map.put("host", "localhost");
    map.put("transaction", "1,1");
    map.put("mfp", "1,1");
    map.put("reporter", "1,1");
    map.put("windowSize", TRANSACTION_WINDOW_SIZE);
    map.put("slidingWindowSize", TRANSACTION_SLIDING_WINDOW_SIZE);
    map.put("mfpSupportLevel", MFP_MINIMUM_SUPPORT_LEVEL);

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

  public static void main(String[] args) throws Exception {
    Map<String, String> runOptions = buildRunOptions(args);
    System.out.println(runOptions.toString());
    MaximalFrequentPatternTopology mfpTopology = new MaximalFrequentPatternTopology(runOptions);
    mfpTopology.runOnCluster();
    // storm rebalance mfp -e mfp=2
  }
}
