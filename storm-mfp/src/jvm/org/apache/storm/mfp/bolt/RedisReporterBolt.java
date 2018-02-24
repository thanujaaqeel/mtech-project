package org.apache.storm.mfp.bolt;

import org.apache.storm.task.OutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseRichBolt;
import org.apache.storm.tuple.Tuple;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import java.util.List;
import java.util.Map;

public class RedisReporterBolt extends BaseRichBolt {
  private static final Logger LOG = LoggerFactory.getLogger(RedisReporterBolt.class);

  private OutputCollector collector;
  private JedisPool pool;

  private String host;
  private int port;
  private String channel;

  public RedisReporterBolt(String host, int port, String channel){
    this.host = host;
    this.port = port;
    this.channel = channel;
  }

  @Override
  public void prepare(Map stormConf, TopologyContext context, OutputCollector collector) {
    this.collector = collector;
    pool = new JedisPool(new JedisPoolConfig(), host, port);
  }

  @Override
  public void execute(Tuple tuple) {
    report(tuple);
    collector.ack(tuple);
  }

  private void report(Tuple tuple){
    int transactionsSize = (int) tuple.getValue(0);
    String transactionsString = tuple.getString(1);
    String itemSetsString = tuple.getString(2);
    String reportString = transactionsSize + "\n" + transactionsString + "\n" + itemSetsString;
    publish(reportString);
  }

  private void publish(String message){
    Jedis jedis = pool.getResource();
    try {
      jedis.publish(channel, message);
    } finally {
      pool.returnResource(jedis);
    }
  }

  @Override
  public void cleanup(){
  }

  @Override
  public void declareOutputFields(OutputFieldsDeclarer ofd) {
  }
}
