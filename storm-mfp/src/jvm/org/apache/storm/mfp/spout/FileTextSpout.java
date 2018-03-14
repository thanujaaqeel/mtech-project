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

import java.io.*;

public class FileTextSpout extends BaseRichSpout {
  public static Logger LOG = LoggerFactory.getLogger(FileTextSpout.class);
  boolean _isDistributed;
  SpoutOutputCollector _collector;

  final int RATE = 10;

  BufferedReader reader;
  
  String filename;

  int count;
  long startTime;
  
  public FileTextSpout(String filename) {
    this(true);
    this.filename = filename;
    this.count = 0; 
    this.startTime = -1;
  }

  public FileTextSpout(boolean isDistributed) {
    _isDistributed = isDistributed;
  }

  @Override
  public void open(Map conf, TopologyContext context, SpoutOutputCollector collector) {
    _collector = collector;
    reader = getReader();

  }
  
  public void close() {
    
  }
  
  @Override
  public void nextTuple() {
    String message;

    try{
      message = reader.readLine();
    }catch(IOException e){
      return;
    }

    if( reader == null || message == null){
      reader = getReader();
      return;
    }

    _collector.emit(new Values(message));

    measure();

    Utils.sleep(1000 / RATE);
    
  }
  
  private BufferedReader getReader(){
    try{
      return new BufferedReader(new FileReader(filename));
    }catch(IOException e){
      return null;
    }
  }

  private void measure(){
    if(startTime == -1){
      startTime = System.currentTimeMillis();
    }
    count ++;
    
    long difference = (System.currentTimeMillis() - startTime)/1000;

    if(difference >= 1){
      LOG.info("Total messages in 1 second: {}", count);
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
