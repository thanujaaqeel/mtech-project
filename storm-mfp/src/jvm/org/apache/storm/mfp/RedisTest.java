package org.apache.storm.mfp;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import java.util.List;
import java.util.Map;

public class RedisTest{
  public static void main(String[] args) {
    String host = "localhost";
    int port = 6379;
    JedisPool pool = new JedisPool(new JedisPoolConfig(), host, port);
    Jedis jedis = pool.getResource();
    String value = args[0];
    if( args.length > 1 ){
      host = args[1];
    }

    System.out.println("Hostname " + host);

    try {
      jedis.set("test_key", value);
    } catch (Exception e){
      System.out.println("Error " + e.getMessage());
    }
    finally {
      pool.returnResource(jedis);
    }
  }
}
