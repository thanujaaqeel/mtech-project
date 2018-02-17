
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

import org.apache.storm.mfp.spout.RedisTextSpout;
import org.apache.storm.mfp.spout.RandomSentenceSpout;

import java.util.Map;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import org.apache.storm.mfp.bolt.MFPMinerBolt;

import static org.apache.storm.topology.base.BaseWindowedBolt.Count;

public class MaximalFrequentPatternTopology {

  private int TRANSACTION_WINDOW_SIZE = 50;
  private int MFP_MINIMUM_SUPPORT_LEVEL = 2;

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
    BaseRichSpout spout;

    boolean fromRedis = true;
    if(fromRedis){
      spout = redisSpout();
    }else{
      spout = new RandomSentenceSpout();
    }

    return buildTopologyFromSpout(spout);
  }


  private StormTopology buildTopologyFromSpout(BaseRichSpout spout){
    TopologyBuilder builder = new TopologyBuilder();

    builder.setSpout("transaction", spout, 1);
    builder.setBolt("mfp", minerBolt(), 3).shuffleGrouping("transaction");

    return builder.createTopology();
  }

  private MFPMinerBolt minerBolt(){
    return new MFPMinerBolt(MFP_MINIMUM_SUPPORT_LEVEL).withWindow(Count.of(TRANSACTION_WINDOW_SIZE));
  }

  private redisSpout(){
    return new RedisTextSpout("localhost", 6379, "MFP_STREAM");
  }

  public static void main(String[] args) throws Exception {
    MaximalFrequentPatternTopology mfpTopology = new MaximalFrequentPatternTopology();

    boolean simulateCluster = !(args != null && args.length > 0);

    if( simulateCluster ){
      mfpTopology.runOnLocalCluster();
    }else{
      mfpTopology.runOnCluster(args[0]);
    }
  }

}
