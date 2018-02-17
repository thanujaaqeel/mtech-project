package org.apache.storm.mfp.bolt;

import org.apache.storm.task.OutputCollector;
import org.apache.storm.task.TopologyContext;

import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseRichBolt;
import org.apache.storm.tuple.Tuple;

import com.github.chen0040.fpm.AssocRuleMiner;
import com.github.chen0040.fpm.apriori.Apriori;
import com.github.chen0040.fpm.data.MetaData;
import com.github.chen0040.fpm.data.ItemSets;
import com.github.chen0040.fpm.data.ItemSet;

import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

public class MFPBolt extends BaseRichBolt {

  private OutputCollector collector;

  @Override
  public void prepare(Map stormConf, TopologyContext context, OutputCollector collector) {
    this.collector = collector;

  }

  @Override
  public void execute(Tuple tuple) {
    List<List<String>> database = new ArrayList<>();

    database.add(Arrays.asList("a", "b", "c", "d"));
    database.add(Arrays.asList("a", "d"));
    database.add(Arrays.asList("a", "e"));
    database.add(Arrays.asList("c", "e"));

    AssocRuleMiner method = new Apriori();
    method.setMinSupportLevel(2);

    MetaData metaData = new MetaData(database);
        
    ItemSets max_frequent_item_sets = method.findMaxPatterns(database, metaData.getUniqueItems());
    
    for(ItemSet itemSet : max_frequent_item_sets.getSets()){
      System.out.println("item-set: " + itemSet);
    }
  }

  @Override
  public void declareOutputFields(OutputFieldsDeclarer declarer) {
  }

}
