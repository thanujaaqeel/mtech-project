
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

  private final int TRANSACTION_WINDOW_SIZE = 20;
  private final int TRANSACTION_SLIDING_WINDOW_SIZE = 5;
  private final int MFP_MINIMUM_SUPPORT_LEVEL = 2;

  public void runOnCluster(String[] args) throws AlreadyAliveException, InvalidTopologyException, AuthorizationException{
    Config conf = new Config();

    String name = args[0];
    int mfpParallelismHint = 1;
    int mfpNumTasks = 4;
    int numWorkers = 1;
    String redisHost = "localhost";

    if (args.length >= 2){
      mfpParallelismHint = Integer.parseInt(args[1]);
    }
    if (args.length >= 3){
      mfpNumTasks = Integer.parseInt(args[2]);
    }

    if (args.length >= 4){
      numWorkers = Integer.parseInt(args[3]);
    }

    if (args.length >= 5){
      redisHost = args[4];
    }

    conf.registerMetricsConsumer(HttpForwardingMetricsConsumer.class, "http://localhost:5000/metric", 1);
    conf.setNumWorkers(numWorkers);

    StormSubmitter.submitTopologyWithProgressBar(name, conf, buildTopology(mfpParallelismHint, mfpNumTasks, redisHost));
  }

  private StormTopology buildTopology(int mfpParallelismHint, int mfpNumTasks, String redisHost){
    TopologyBuilder builder = new TopologyBuilder();

    builder.setSpout("transaction", transactionsSpout(redisHost), 1);

    builder.setBolt("mfp", minerBolt(), mfpParallelismHint)
           .setNumTasks(mfpNumTasks)
           .shuffleGrouping("transaction");

    builder.setBolt("reporter", reporterBolt(redisHost), 1)
           .shuffleGrouping("mfp");
    return builder.createTopology();
  }

  private IWindowedBolt minerBolt(){
    MFPMinerBolt minerBolt = new MFPMinerBolt(MFP_MINIMUM_SUPPORT_LEVEL);
    IWindowedBolt bolt = minerBolt.withWindow(Count.of(TRANSACTION_WINDOW_SIZE), Count.of(TRANSACTION_SLIDING_WINDOW_SIZE));
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

  public static void main(String[] args) throws Exception {
    MaximalFrequentPatternTopology mfpTopology = new MaximalFrequentPatternTopology();
    mfpTopology.runOnCluster(args);
    // storm rebalance mfp -e mfp=2
  }
}
