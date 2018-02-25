
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

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import static org.apache.storm.topology.base.BaseWindowedBolt.Count;

public class MaximalFrequentPatternTopology {

  private final int TRANSACTION_WINDOW_SIZE = 10;
  private final int TRANSACTION_SLIDING_WINDOW_SIZE = 5;
  private final int MFP_MINIMUM_SUPPORT_LEVEL = 2;

  public void runOnCluster(String name) throws AlreadyAliveException, InvalidTopologyException, AuthorizationException{
    Config conf = new Config();
    conf.setDebug(true);
    conf.setNumWorkers(3);

    StormSubmitter.submitTopologyWithProgressBar(name, conf, buildTopology());
  }

  public void runOnLocalCluster(){
    Config conf = new Config();
    conf.setDebug(true);

    LocalCluster cluster = new LocalCluster();
    cluster.submitTopology("test", conf, buildTopology());

    Utils.sleep(10000);

    cluster.killTopology("test");
    cluster.shutdown();
  }

  private StormTopology buildTopology(){
    TopologyBuilder builder = new TopologyBuilder();

    builder.setSpout("transaction", transactionsSpout(), 1);
    builder.setBolt("mfp", minerBolt(), 3).shuffleGrouping("transaction");
    builder.setBolt("reporter", reporterBolt(), 1).shuffleGrouping("mfp");
    return builder.createTopology();
  }

  private IWindowedBolt minerBolt(){
    MFPMinerBolt minerBolt = new MFPMinerBolt(MFP_MINIMUM_SUPPORT_LEVEL);
    IWindowedBolt bolt = minerBolt.withWindow(Count.of(TRANSACTION_WINDOW_SIZE), Count.of(TRANSACTION_SLIDING_WINDOW_SIZE));
    return bolt;
  }

  private IRichSpout transactionsSpout(){
    // RedisTextSpout spout = new RedisTextSpout("localhost", 6379, "MFP_STREAM");
    FileTextSpout spout = new FileTextSpout("/Users/thanuja/mtech-project/twitter-input/tweets_1.txt");
    return spout;
  }

  private RedisReporterBolt reporterBolt(){
    RedisReporterBolt bolt = new RedisReporterBolt("localhost", 6379, "MFP_OUTPUT_STREAM");
    return bolt;
  }

  public static void main(String[] args) throws Exception {
    MaximalFrequentPatternTopology mfpTopology = new MaximalFrequentPatternTopology();

    boolean simulateLocalCluster = !(args != null && args.length > 0);

    if( simulateLocalCluster ){
      mfpTopology.runOnLocalCluster();
    }else{
      mfpTopology.runOnCluster(args[0]);
    }
  }

}
