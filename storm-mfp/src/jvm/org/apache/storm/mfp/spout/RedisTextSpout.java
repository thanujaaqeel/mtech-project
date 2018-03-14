/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.storm.mfp.spout;

import org.apache.storm.Config;
import org.apache.storm.topology.OutputFieldsDeclarer;
import java.util.Map;
import org.apache.storm.spout.SpoutOutputCollector;
import org.apache.storm.task.TopologyContext;
import org.apache.storm.topology.base.BaseRichSpout;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Values;
import org.apache.storm.utils.Utils;

import java.util.HashMap;
import java.util.Random;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;
import redis.clients.jedis.JedisPubSub;

import java.util.Map;
import java.util.concurrent.LinkedBlockingQueue;


public class RedisTextSpout extends BaseRichSpout {
  public static Logger LOG = LoggerFactory.getLogger(RedisTextSpout.class);
  boolean _isDistributed;
  SpoutOutputCollector _collector;

  LinkedBlockingQueue<String> queue;
  final int MAX_QUEUE_LENGTH = 100000;
  final int WAIT_FOR_NEXT_TUPLE = 1;

  JedisPool pool;

  String host;
  int port;
  String channel;

  int count;
  long startTime;
  
  public RedisTextSpout(String host, int port, String channel) {
    this(true);

    this.host = host;
    this.port = port;
    this.channel = channel;
    this.count = 0; 
    this.startTime = -1;
  }

  public RedisTextSpout(boolean isDistributed) {
    _isDistributed = isDistributed;
  }
  
  class ListenerThread extends Thread {
    LinkedBlockingQueue<String> queue;
    JedisPool pool;
    String channel;

    public ListenerThread(LinkedBlockingQueue<String> queue, JedisPool pool, String channel) {
      this.queue = queue;
      this.pool = pool;
      this.channel = channel;
    }

    public void run() {
      JedisPubSub listener = new JedisPubSub() {

        @Override
        public void onMessage(String _channel, String message) {
          // LOG.info("onMessage: "+ message.trim() );
          queue.offer(message.trim());
        }
      };
        
      Jedis jedis = pool.getResource();
      try {
        jedis.subscribe(listener, channel);
      } finally {
        pool.returnResource(jedis);
      }
    }
  };


  @Override
  public void open(Map conf, TopologyContext context, SpoutOutputCollector collector) {
    _collector = collector;
    
    queue = new LinkedBlockingQueue<String>(MAX_QUEUE_LENGTH);
    pool = new JedisPool(new JedisPoolConfig(), host, port);
    
    ListenerThread listener = new ListenerThread(queue, pool, channel);
    listener.start();

  }
  
  public void close() {
    pool.destroy();
  }
  
  @Override
  public void nextTuple() {
    String message = queue.poll();

    if( message == null){
      // LOG.info("Sleeping for next item");
      Utils.sleep(WAIT_FOR_NEXT_TUPLE);
      return;
    }

    _collector.emit(new Values(message));
    measure();
  }

  private void measure(){
    if(startTime == -1){
      startTime = System.currentTimeMillis();
    }
    count ++;

    long difference = (System.currentTimeMillis() - startTime)/1000;

    if(difference >= 1){
      // LOG.info("Total messages in 1 second: {}", count);
      count = 0; //reset
      startTime = -1;
    }
  }

  public void ack(Object msgId) {

  }

  public void fail(Object msgId) {
      
  }
  
  public void declareOutputFields(OutputFieldsDeclarer declarer) {
    declarer.declare(new Fields("text"));
  }

  @Override
  public Map<String, Object> getComponentConfiguration() {
    if(!_isDistributed) {
      Map<String, Object> ret = new HashMap<String, Object>();
      ret.put(Config.TOPOLOGY_MAX_TASK_PARALLELISM, 1);
      return ret;
    } else {
      return null;
    }
  }
}
